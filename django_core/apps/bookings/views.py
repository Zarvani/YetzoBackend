import uuid
import random
import string
import logging
from django.db import transaction

logger = logging.getLogger(__name__)
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Booking, BookingItem, BookingAnswer, BookingStatusHistory
from .serializers import (
    BookingSerializer, BookingCreateSerializer, BookingStatusUpdateSerializer
)
from apps.services.models import Service, ServiceVariant, ServiceAddon, ServiceQuestion
from apps.locations.models import Address
from apps.pricing.models import ServicePricingRule, TaxRule
from apps.admin_core.models import UserMembership
from .permissions import IsBookingParticipantOrAdmin
from .tasks import dispatch_booking_to_professionals
import datetime
from django.utils import timezone

def generate_booking_reference():
    return 'YZ' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class BookingListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        base_qs = Booking.objects.select_related(
            'customer', 'service', 'assigned_professional', 'assigned_professional__user', 'address'
        )
        if request.user.role and request.user.role.name in ['ADMIN', 'DISPATCHER', 'OPERATIONS_MANAGER']:
            bookings = base_qs.all().order_by('-created_at')
        elif request.user.role and request.user.role.name in ['PROFESSIONAL', 'PARTNER']:
            bookings = base_qs.filter(assigned_professional__user=request.user).order_by('-created_at')
        else:
            bookings = base_qs.filter(customer=request.user).order_by('-created_at')
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
                from apps.locations.models import City
                city_obj = City.objects.filter(name__iexact=address.city).first() if address.city else None
                if not city_obj and address.area and address.area.zone:
                    city_obj = address.area.zone.city
                
                pricing_rule = None
                if city_obj:
                    pricing_rule = ServicePricingRule.objects.filter(service=service, city=city_obj, is_active=True).first()
                if not pricing_rule:
                    pricing_rule = ServicePricingRule.objects.filter(service=service, city__isnull=True, is_active=True).first()
                
                if pricing_rule:
                    base_price = float(pricing_rule.base_price)
                elif service.starting_price:
                    base_price = float(service.starting_price)
                else:
                    base_price = 199.00
                
                # Dynamically calculate addons/items loop
                items_data = data.get('items', [])
                addons_price = 0.00
                addons_data = data.get('addons', [])
                for addon_id in addons_data:
                    addons_price += 149.00
                
                subtotal = base_price + addons_price
                
                # 2. Pronto Task Stacking Discount (15% if 2+ chores stacked)
                discount = 0.00
                if len(items_data) >= 2:
                    discount += subtotal * 0.15
                
                # Membership Discount (UC Plus / Yetzo VIP logic)
                membership = UserMembership.objects.filter(user=request.user, is_active=True, end_date__gte=timezone.now()).first()
                if membership:
                    # Additional 10% flat discount for VIP members
                    discount += subtotal * 0.10
                    
                subtotal_after_discount = max(0.0, subtotal - discount)
                
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
                    is_verified_session=data.get('is_verified_session', False),
                    scheduled_date=data.get('scheduled_date'),
                    scheduled_time=data.get('scheduled_time'),
                    start_otp=f"{random.randint(1000, 9999)}",
                    end_otp=f"{random.randint(1000, 9999)}",
                    base_price=int(base_price),
                    addons_price=int(addons_price),
                    taxes=int(taxes),
                    discount=int(discount),
                    total_amount=int(total_amount),
                    status='PENDING_PAYMENT'
                )
                
                # Persist Task Stacking items
                for itm in items_data:
                    v_id = itm.get('variant_id')
                    a_id = itm.get('addon_id')
                    variant = ServiceVariant.objects.filter(id=v_id).first() if v_id else None
                    addon = ServiceAddon.objects.filter(id=a_id).first() if a_id else None
                    qty = itm.get('quantity', 1)
                    price = itm.get('price', base_price)
                    BookingItem.objects.create(
                        booking=booking,
                        variant=variant,
                        addon=addon,
                        quantity=qty,
                        price_at_booking=int(price)
                    )
                
                # Persist Answers
                for ans in data.get('answers', []):
                    q_id = ans.get('question_id')
                    q = ServiceQuestion.objects.filter(id=q_id).first() if q_id else None
                    if q:
                        BookingAnswer.objects.create(
                            booking=booking,
                            question=q,
                            answer_text=ans.get('answer_text', '')
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
    queryset = Booking.objects.select_related(
        'customer', 'service', 'assigned_professional', 'assigned_professional__user', 'address'
    ).all()
    lookup_field = 'id'


class BookingStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, id):
        with transaction.atomic():
            try:
                booking = Booking.objects.select_for_update().get(id=id)
            except Booking.DoesNotExist:
                return Response({"success": False, "error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
                
            # Manually check object permissions for APIView
            permission = IsBookingParticipantOrAdmin()
            if not permission.has_object_permission(request, self, booking):
                return Response({"success": False, "error": "You do not have permission to modify this booking."}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = BookingStatusUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
            new_status = serializer.validated_data['new_status']
            old_status = booking.status
            
            # Partner Declining Offer / Automatic Sequencing to Next Pro
            if new_status in ['REJECTED', 'CANCELLED', 'TIMEOUT'] and old_status == 'ASSIGNED' and booking.assigned_professional and booking.assigned_professional.user == request.user:
                from apps.bookings.models import BookingAssignment
                assign_status = 'TIMEOUT' if new_status == 'TIMEOUT' else 'REJECTED'
                BookingAssignment.objects.filter(booking=booking, professional=booking.assigned_professional).update(status=assign_status)
                booking.assigned_professional.current_status = 'ONLINE'
                booking.assigned_professional.save(update_fields=['current_status', 'updated_at'])
                booking.assigned_professional = None
                new_status = 'SEARCHING'
            
            # Manual Admin / Dispatcher Override Assignment
            elif new_status == 'ASSIGNED' and request.data.get('professional_id'):
                pro_id = request.data.get('professional_id')
                from apps.professionals.models import ProfessionalProfile
                try:
                    target_pro = ProfessionalProfile.objects.select_for_update().get(id=pro_id)
                    booking.assigned_professional = target_pro
                    target_pro.current_status = 'BUSY'
                    target_pro.save(update_fields=['current_status', 'updated_at'])
                    
                    from apps.bookings.models import BookingAssignment
                    BookingAssignment.objects.update_or_create(
                        booking=booking,
                        professional=target_pro,
                        defaults={'status': 'PENDING'}
                    )
                except ProfessionalProfile.DoesNotExist:
                    return Response({"success": False, "error": "Selected professional not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Cancellation Penalty Logic
            elif new_status == 'CANCELLED' and old_status in ['CONFIRMED', 'ASSIGNED', 'IN_PROGRESS']:
                if booking.scheduled_date and booking.scheduled_time:
                    booking_dt = datetime.datetime.combine(booking.scheduled_date, booking.scheduled_time)
                    booking_dt = timezone.make_aware(booking_dt)
                    time_until_service = booking_dt - timezone.now()
                    
                    if time_until_service.total_seconds() < 86400: # Less than 24 hours
                        # Reserved for cancellation fee deduction
                        pass
                        
            # Job Start OTP Verification Logic
            if new_status == 'IN_PROGRESS' and old_status == 'ARRIVED':
                provided_otp = request.data.get('start_otp')
                if not provided_otp or str(provided_otp) != str(booking.start_otp):
                    return Response({"success": False, "error": "Invalid or missing Start OTP."}, status=status.HTTP_400_BAD_REQUEST)
                    
            # Job End OTP & Escrow Release Logic (Atomic)
            if new_status == 'COMPLETED' and old_status == 'IN_PROGRESS':
                provided_otp = request.data.get('end_otp')
                if not provided_otp or str(provided_otp) != str(booking.end_otp):
                    return Response({"success": False, "error": "Invalid or missing End OTP."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Release Escrow logic
                from apps.payments.models import EscrowLedger, Wallet, WalletTransaction
                escrow = EscrowLedger.objects.select_for_update().filter(booking=booking, status='HELD').first()
                if escrow and booking.assigned_professional:
                    escrow.status = 'RELEASED'
                    escrow.save()
                    
                    wallet, _ = Wallet.objects.select_for_update().get_or_create(professional=booking.assigned_professional)
                    platform_fee_percent = 0.20 # 20% platform cut
                    payout_amount = int(escrow.amount_held * (1.0 - platform_fee_percent))
                    
                    from django.db.models import F
                    Wallet.objects.filter(id=wallet.id).update(balance=F('balance') + payout_amount)
                    
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_type='CREDIT',
                        amount=payout_amount,
                        reference_id=str(booking.id),
                        description=f"Payout for booking {booking.booking_reference}"
                    )
            
            booking.status = new_status
            booking.save()
            
            # Calendar Locking & Assignment Acceptance Logic
            if new_status == 'ACCEPTED' and booking.assigned_professional:
                from apps.bookings.models import BookingAssignment
                BookingAssignment.objects.filter(booking=booking, professional=booking.assigned_professional).update(status='ACCEPTED')
                from apps.scheduling.models import ProfessionalTimeSlot
                sched_date = booking.scheduled_date or datetime.date.today()
                sched_time = booking.scheduled_time or datetime.time(10, 0)
                end_time = (datetime.datetime.combine(sched_date, sched_time) + datetime.timedelta(hours=2)).time()
                ProfessionalTimeSlot.objects.get_or_create(
                    professional=booking.assigned_professional,
                    date=sched_date,
                    start_time=sched_time,
                    defaults={
                        'booking': booking,
                        'end_time': end_time,
                        'status': 'LOCKED_FOR_JOB'
                    }
                )
            
            BookingStatusHistory.objects.create(
                booking=booking,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                reason=serializer.validated_data.get('reason', '')
            )
            
        # If transitioning to SEARCHING, trigger matching engine outside transaction block
        if new_status == 'SEARCHING':
            try:
                dispatch_booking_to_professionals.delay(booking.id)
            except Exception as e:
                logger.warning(f"Celery dispatch task enqueue failed ({e}), executing synchronously fallback.")
                dispatch_booking_to_professionals(booking.id)
            
        return Response({"success": True, "data": {"status": new_status}})
