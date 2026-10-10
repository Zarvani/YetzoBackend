import uuid
import random
import string
from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Booking, BookingItem, BookingAnswer, BookingStatusHistory
from .serializers import (
    BookingSerializer, BookingCreateSerializer, BookingStatusUpdateSerializer
)
from apps.services.models import Service, ServiceVariant, ServiceAddon
from apps.locations.models import Address
from apps.pricing.models import ServicePricingRule, TaxRule
from apps.admin_core.models import UserMembership
from .permissions import IsBookingParticipantOrAdmin
from .tasks import dispatch_booking_to_professionals
import datetime

def generate_booking_reference():
    return 'YZ' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class BookingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role and request.user.role.name in ['ADMIN', 'DISPATCHER']:
            bookings = Booking.objects.all().order_by('-created_at')
        elif request.user.role and request.user.role.name == 'PROFESSIONAL':
            bookings = Booking.objects.filter(professional=request.user).order_by('-created_at')
        else:
            bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response({"success": True, "data": serializer.data})

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                data = serializer.validated_data
                
                # Verify Address
                try:
                    address = Address.objects.get(id=data['address_id'], user=request.user)
                except Address.DoesNotExist:
                    return Response({"success": False, "error": "Address not found or does not belong to user."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Get Service
                try:
                    service = Service.objects.get(id=data['service_id'])
                except Service.DoesNotExist:
                    return Response({"success": False, "error": "Service not found."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Dynamic Pricing Engine Calculation
                # 1. Get Base Price for the specific city/service
                pricing_rule = ServicePricingRule.objects.filter(service=service, city=address.city, is_active=True).first()
                if not pricing_rule:
                    # Fallback to generic pricing rule if city-specific doesn't exist
                    pricing_rule = ServicePricingRule.objects.filter(service=service, city__isnull=True, is_active=True).first()
                
                if not pricing_rule:
                    return Response({"success": False, "error": "Pricing not configured for this service."}, status=status.HTTP_400_BAD_REQUEST)
                
                base_price = float(pricing_rule.base_price) # Assuming paise/cents, we handle it as float for this logic
                
                # Dynamically calculate addons loop
                addons_price = 0.00
                addons_data = data.get('addons', [])
                for addon_id in addons_data:
                    # Query AddonPricing (assuming relationship exists)
                    addon_pricing = ServicePricingRule.objects.filter(service=service, city=address.city, is_active=True).first() # Simplified for brevity, normally AddonPricing
                    # Here we would add to addons_price based on actual AddonPricing model
                    addons_price += 299.00 # Placeholder math applied for loop
                
                subtotal = base_price + addons_price
                
                # 2. Apply Membership Discount (UC Plus logic)
                discount = 0.00
                membership = UserMembership.objects.filter(user=request.user, is_active=True, end_date__gte=datetime.timezone.now()).first()
                if membership:
                    # 15% flat discount for members
                    discount = subtotal * 0.15
                    
                subtotal_after_discount = subtotal - discount
                
                # 3. Calculate Taxes
                tax_rule = TaxRule.objects.filter(is_active=True).first()
                tax_multiplier = 0.18 # Default 18%
                if tax_rule:
                    tax_multiplier = float(tax_rule.cgst_percent + tax_rule.sgst_percent) / 100.0
                    
                taxes = subtotal_after_discount * tax_multiplier
                total_amount = subtotal_after_discount + taxes
                
                booking = Booking.objects.create(
                    booking_reference=generate_booking_reference(),
                    customer=request.user,
                    service=service,
                    address=address,
                    is_instant=data.get('is_instant', False),
                    scheduled_date=data.get('scheduled_date'),
                    scheduled_time=data.get('scheduled_time'),
                    start_otp=f"{random.randint(1000, 9999)}",
                    end_otp=f"{random.randint(1000, 9999)}",
                    base_price=base_price,
                    addons_price=addons_price,
                    taxes=taxes,
                    total_amount=total_amount,
                    status='PENDING_PAYMENT'
                )
                
                BookingStatusHistory.objects.create(
                    booking=booking,
                    old_status='NONE',
                    new_status='PENDING_PAYMENT',
                    changed_by=request.user
                )
                
                response_serializer = BookingSerializer(booking)
                return Response({"success": True, "data": response_serializer.data}, status=status.HTTP_201_CREATED)
                
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class BookingDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsBookingParticipantOrAdmin]
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()
    lookup_field = 'id'


class BookingStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, id):
        try:
            booking = Booking.objects.get(id=id)
        except Booking.DoesNotExist:
            return Response({"success": False, "error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
            
        # Manually check object permissions for APIView
        permission = IsBookingParticipantOrAdmin()
        if not permission.has_object_permission(request, self, booking):
            return Response({"success": False, "error": "You do not have permission to modify this booking."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = BookingStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            new_status = serializer.validated_data['new_status']
            old_status = booking.status
            
            # Cancellation Penalty Logic
            if new_status == 'CANCELLED' and old_status in ['CONFIRMED', 'ASSIGNED', 'IN_PROGRESS']:
                if booking.scheduled_date and booking.scheduled_time:
                    booking_dt = datetime.datetime.combine(booking.scheduled_date, booking.scheduled_time)
                    booking_dt = datetime.timezone.make_aware(booking_dt)
                    time_until_service = booking_dt - datetime.timezone.now()
                    
                    if time_until_service.total_seconds() < 86400: # Less than 24 hours
                        # Apply cancellation penalty (e.g. 150 INR)
                        # We would deduct from wallet or hold on card here
                        pass
                        
            # Job Start OTP Verification Logic
            if new_status == 'IN_PROGRESS' and old_status == 'ARRIVED':
                provided_otp = request.data.get('start_otp')
                if not provided_otp or str(provided_otp) != str(booking.start_otp):
                    return Response({"success": False, "error": "Invalid or missing Start OTP."}, status=status.HTTP_400_BAD_REQUEST)
                    
            # Job End OTP & Escrow Release Logic
            if new_status == 'COMPLETED' and old_status == 'IN_PROGRESS':
                provided_otp = request.data.get('end_otp')
                if not provided_otp or str(provided_otp) != str(booking.end_otp):
                    return Response({"success": False, "error": "Invalid or missing End OTP."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Release Escrow logic
                from apps.payments.models import EscrowLedger, Wallet, WalletTransaction
                escrow = EscrowLedger.objects.filter(booking=booking, status='HELD').first()
                if escrow and booking.assigned_professional:
                    escrow.status = 'RELEASED'
                    escrow.save()
                    
                    wallet, _ = Wallet.objects.get_or_create(professional=booking.assigned_professional)
                    platform_fee_percent = 0.20 # 20% platform cut
                    payout_amount = escrow.amount_held * (1.0 - platform_fee_percent)
                    
                    wallet.balance += int(payout_amount)
                    wallet.save()
                    
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_type='CREDIT',
                        amount=int(payout_amount),
                        reference_id=str(booking.id),
                        description=f"Payout for booking {booking.booking_reference}"
                    )
            
            with transaction.atomic():
                booking.status = new_status
                booking.save()
                
                # Calendar Locking Logic
                if new_status == 'ACCEPTED' and booking.assigned_professional:
                    from apps.scheduling.models import ProfessionalTimeSlot
                    end_time = (datetime.datetime.combine(datetime.date.today(), booking.scheduled_time) + datetime.timedelta(hours=2)).time()
                    ProfessionalTimeSlot.objects.create(
                        professional=booking.assigned_professional,
                        booking=booking,
                        date=booking.scheduled_date,
                        start_time=booking.scheduled_time,
                        end_time=end_time,
                        status='LOCKED_FOR_JOB'
                    )
                
                BookingStatusHistory.objects.create(
                    booking=booking,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    reason=serializer.validated_data.get('reason', '')
                )
                
            # If transitioning to SEARCHING, trigger matching engine asynchronously
            if new_status == 'SEARCHING':
                dispatch_booking_to_professionals.delay(booking.id)
                
            return Response({"success": True, "data": {"status": new_status}})
            
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
