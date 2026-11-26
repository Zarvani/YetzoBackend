import random
import string
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.bookings.models import Booking, BookingItem, BookingStatusHistory
from apps.bookings.serializers import BookingSerializer
from apps.locations.models import Address
from apps.pricing.models import ServicePricingRule
from apps.admin_core.models import UserMembership
from apps.bookings.tasks import dispatch_booking_to_professionals

def generate_booking_reference():
    return 'YZ' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def recalculate_cart(cart):
    """
    Recalculates cart subtotal, multi-chore stacking discount (Pronto style),
    membership discount (UC Plus style), GST (18%), and platform fee.
    """
    items = cart.items.all()
    subtotal = sum(item.total_price for item in items)
    
    # 1. Multi-chore stacking bundle discount (Yetzo style):
    # 10% discount when 2 or more chores are stacked in a single visit
    chore_discount = 0
    if items.count() >= 2:
        chore_discount = int(subtotal * 0.10)
    
    # 2. UC Plus Membership discount (15% off)
    is_member = UserMembership.objects.filter(
        user=cart.user, is_active=True, end_date__gte=timezone.now()
    ).exists()
    membership_discount = 0
    if is_member:
        membership_discount = int((subtotal - chore_discount) * 0.15)
        
    discount = chore_discount + membership_discount
    discounted_subtotal = max(0, subtotal - discount)
    
    # 3. GST Tax (18%)
    tax = int(discounted_subtotal * 0.18)
    
    # 4. Platform fee (₹49, waived for members or empty cart)
    service_fee = 0 if is_member or subtotal == 0 else 49
    
    cart.subtotal = subtotal
    cart.discount = discount
    cart.tax = tax
    cart.service_fee = service_fee
    cart.total = discounted_subtotal + tax + service_fee
    cart.save()
    return cart


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        recalculate_cart(cart)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Creates a Booking from the active Cart items (multi-chore stack).
        Accepts: address_id, scheduled_date, scheduled_time, is_instant, is_verified_session
        """
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        if not items.exists():
            return Response({"success": False, "error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        address_id = request.data.get('address_id')
        if not address_id:
            return Response({"success": False, "error": "address_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"success": False, "error": "Address not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        recalculate_cart(cart)

        with transaction.atomic():
            first_service = items.first().service
            is_instant = request.data.get('is_instant', False)
            is_verified_session = request.data.get('is_verified_session', False)
            
            scheduled_date = request.data.get('scheduled_date')
            scheduled_time = request.data.get('scheduled_time')
            if is_instant:
                scheduled_date = timezone.now().date()
                scheduled_time = timezone.now().time()

            booking = Booking.objects.create(
                booking_reference=generate_booking_reference(),
                customer=request.user,
                service=first_service,
                address=address,
                is_instant=is_instant,
                is_verified_session=is_verified_session,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                start_otp=f"{random.randint(1000, 9999)}",
                end_otp=f"{random.randint(1000, 9999)}",
                base_price=cart.subtotal,
                discount=cart.discount,
                taxes=cart.tax,
                platform_fee=cart.service_fee,
                total_amount=cart.total,
                status='PENDING_PAYMENT'
            )

            for item in items:
                BookingItem.objects.create(
                    booking=booking,
                    variant=item.variant,
                    quantity=item.quantity,
                    price_at_booking=item.total_price
                )

            BookingStatusHistory.objects.create(
                booking=booking,
                old_status='NONE',
                new_status='PENDING_PAYMENT',
                changed_by=request.user,
                reason="Created via Cart Checkout with Multi-Chore Stacking"
            )

            # Clear cart
            cart.items.all().delete()
            recalculate_cart(cart)

            # If instant booking, transition to SEARCHING and trigger candidate dispatch immediately
            if is_instant:
                booking.status = 'SEARCHING'
                booking.save(update_fields=['status'])
                dispatch_booking_to_professionals.delay(booking.id)

            return Response({
                "success": True,
                "data": BookingSerializer(booking).data
            }, status=status.HTTP_201_CREATED)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        # Determine unit price if not explicitly provided
        unit_price = serializer.validated_data.get('unit_price')
        if not unit_price or unit_price == 0:
            service = serializer.validated_data.get('service')
            pricing_rule = ServicePricingRule.objects.filter(service=service, is_active=True).first()
            if pricing_rule:
                unit_price = pricing_rule.base_price
            else:
                unit_price = 499

        qty = serializer.validated_data.get('quantity', 1)
        total_price = unit_price * qty
        item = serializer.save(cart=cart, unit_price=unit_price, total_price=total_price)
        recalculate_cart(cart)

    def perform_update(self, serializer):
        qty = serializer.validated_data.get('quantity', serializer.instance.quantity)
        unit_price = serializer.validated_data.get('unit_price', serializer.instance.unit_price)
        total_price = unit_price * qty
        item = serializer.save(unit_price=unit_price, total_price=total_price)
        recalculate_cart(item.cart)

    def perform_destroy(self, instance):
        cart = instance.cart
        instance.delete()
        recalculate_cart(cart)

