import uuid
from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Payment, Refund, Wallet, WalletTransaction
from apps.bookings.models import Booking
from .serializers import (
    PaymentSerializer, WalletSerializer, WalletTransactionSerializer
)

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import os
        import razorpay
        
        booking_id = request.data.get('booking_id')
        payment_method = request.data.get('payment_method', 'CARD')
        
        try:
            booking = Booking.objects.get(id=booking_id, customer=request.user)
        except Booking.DoesNotExist:
            return Response({"success": False, "error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
            
        if booking.status != 'PENDING_PAYMENT':
            return Response({"success": False, "error": f"Booking is in {booking.status} state, cannot initiate payment."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Initialize Razorpay Client
        razorpay_key_id = os.environ.get('RAZORPAY_KEY_ID')
        razorpay_key_secret = os.environ.get('RAZORPAY_KEY_SECRET')
        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
        
        # Create Razorpay Order (amount is in paise)
        order_amount = int(booking.total_amount * 100)
        order_currency = 'INR'
        order_receipt = f"receipt_{booking.booking_reference}"
        
        try:
            razorpay_order = client.order.create(dict(amount=order_amount, currency=order_currency, receipt=order_receipt))
            provider_order_id = razorpay_order['id']
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=booking.total_amount,
            provider_order_id=provider_order_id,
            payment_method=payment_method,
            status='INITIATED'
        )
        
        serializer = PaymentSerializer(payment)
        return Response({
            "success": True, 
            "data": {
                "payment": serializer.data,
                "provider_order_id": provider_order_id,
                "razorpay_key_id": razorpay_key_id,
                "amount": order_amount,
                "currency": order_currency
            }
        })

class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        import os
        import razorpay
        
        # 1. Razorpay Signature Verification
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        if not webhook_signature:
            return Response({"success": False, "error": "Missing webhook signature"}, status=status.HTTP_401_UNAUTHORIZED)
            
        razorpay_key_id = os.environ.get('RAZORPAY_KEY_ID')
        razorpay_key_secret = os.environ.get('RAZORPAY_KEY_SECRET')
        webhook_secret = os.environ.get('RAZORPAY_WEBHOOK_SECRET')
        
        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
        
        try:
            client.utility.verify_webhook_signature(request.body.decode('utf-8'), webhook_signature, webhook_secret)
        except Exception as e:
            return Response({"success": False, "error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        # Parse Event
        import json
        event = json.loads(request.body)
        
        if event.get('event') == 'payment.captured':
            payment_entity = event['payload']['payment']['entity']
            provider_order_id = payment_entity['order_id']
            payment_status = 'SUCCESS'
            provider_transaction_id = payment_entity['id']
        elif event.get('event') == 'payment.failed':
            payment_entity = event['payload']['payment']['entity']
            provider_order_id = payment_entity['order_id']
            payment_status = 'FAILED'
            provider_transaction_id = payment_entity['id']
        else:
            return Response({"success": True, "message": "Event ignored"})
        
        try:
            payment = Payment.objects.get(provider_order_id=provider_order_id)
        except Payment.DoesNotExist:
            return Response({"success": False, "error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # 2. Idempotency Check
        if payment.status in ['CAPTURED', 'FAILED']:
            return Response({"success": True, "message": "Webhook already processed"})
            
        # 3. Transaction-safe state update
        with transaction.atomic():
            if payment_status == 'SUCCESS':
                payment.status = 'CAPTURED'
                payment.provider_transaction_id = provider_transaction_id
                payment.save()
                
                # Update Booking Status
                booking = payment.booking
                booking.status = 'CONFIRMED'
                booking.save()
                
                # Implement Live Dispatch Engine
                from apps.professionals.models import ProfessionalSkill, ProfessionalProfile
                from apps.bookings.models import Booking as BookingModel
                import firebase_admin
                from firebase_admin import messaging
                
                # Exclude pros who already have a job on the same day/time (Overlap Protection)
                # In a real scheduling engine, this would calculate exact time durations.
                # For this MVP, if they have an active booking on this date, exclude them.
                busy_pro_ids = BookingModel.objects.filter(
                    scheduled_date=booking.scheduled_date,
                    status__in=['CONFIRMED', 'ASSIGNED', 'ACCEPTED', 'IN_PROGRESS', 'ON_THE_WAY', 'ARRIVED']
                ).exclude(id=booking.id).values_list('assigned_professional_id', flat=True)
                
                # Find available pros with the skill for this service and no overlaps
                available_pros = ProfessionalProfile.objects.filter(
                    is_online=True, 
                    current_status='ONLINE',
                    skills__service=booking.service
                ).exclude(
                    id__in=busy_pro_ids
                ).distinct()
                
                if available_pros.exists():
                    # Take the first available pro (In prod: calculate nearest by lat/lng)
                    assigned_pro = available_pros.first()
                    booking.professional = assigned_pro.user
                    booking.status = 'ASSIGNED'
                    booking.save()
                    
                    assigned_pro.current_status = 'BUSY'
                    assigned_pro.save()
                    
                    # Fire Push Notification
                    if firebase_admin._apps:
                        fcm_token = getattr(assigned_pro.user, 'fcm_token', None)
                        if fcm_token:
                            msg = messaging.Message(
                                notification=messaging.Notification(
                                    title="New Booking Assigned!",
                                    body=f"You have been assigned to a {booking.service.name} job.",
                                ),
                                token=fcm_token,
                            )
                            try:
                                messaging.send(msg)
                            except Exception:
                                pass
                else:
                    # No pros available, keep it CONFIRMED to stay in open pool
                    pass
            else:
                payment.status = 'FAILED'
                payment.provider_transaction_id = provider_transaction_id
                payment.save()
                
        return Response({"success": True})


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if hasattr(request.user, 'role') and request.user.role and request.user.role.name == 'PROFESSIONAL':
            profile = request.user.professional_profile
            wallet, created = Wallet.objects.get_or_create(professional=profile)
        else:
            wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response({"success": True, "data": serializer.data})


class WalletTransactionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletTransactionSerializer
    
    def get_queryset(self):
        if hasattr(self.request.user, 'role') and self.request.user.role and self.request.user.role.name == 'PROFESSIONAL':
            profile = self.request.user.professional_profile
            wallet, created = Wallet.objects.get_or_create(professional=profile)
        else:
            wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        return WalletTransaction.objects.filter(wallet=wallet)
