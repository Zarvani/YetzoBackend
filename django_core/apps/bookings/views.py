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
from .permissions import IsBookingParticipantOrAdmin

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
                
                # Mock Pricing Engine Calculation
                # In production, this would query ServicePricingRule and AddonPricing
                base_price = 499.00 # Stub
                addons_price = 0.00
                taxes = 90.00
                total_amount = base_price + addons_price + taxes
                
                booking = Booking.objects.create(
                    booking_reference=generate_booking_reference(),
                    customer=request.user,
                    service=service,
                    address=address,
                    is_instant=data.get('is_instant', False),
                    scheduled_date=data.get('scheduled_date'),
                    scheduled_time=data.get('scheduled_time'),
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
            
            with transaction.atomic():
                booking.status = new_status
                booking.save()
                
                BookingStatusHistory.objects.create(
                    booking=booking,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    reason=serializer.validated_data.get('reason', '')
                )
                
            # If transitioning to SEARCHING, trigger matching engine (Celery/FastAPI hook goes here)
                
            return Response({"success": True, "data": {"status": new_status}})
            
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
