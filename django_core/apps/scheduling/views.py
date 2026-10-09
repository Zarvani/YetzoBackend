from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import BookingSlot
from .serializers import BookingSlotSerializer
from apps.services.models import Service

class AvailableSlotsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        service_id = request.query_params.get('service_id')
        date = request.query_params.get('date')
        
        if not service_id or not date:
            return Response({"error": "service_id and date are required parameters"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Logic to find available slots for a given service and date
        # In production, this complex query checks ProfessionalAvailability
        # vs Existing Bookings vs Travel Time
        slots = BookingSlot.objects.filter(
            service_id=service_id,
            date=date,
            status='OPEN',
            available_capacity__gt=0
        ).order_by('start_time')
        
        return Response({
            "success": True,
            "data": BookingSlotSerializer(slots, many=True).data
        })

class ReserveSlotView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        slot_id = request.data.get('slot_id')
        
        try:
            slot = BookingSlot.objects.get(id=slot_id)
        except BookingSlot.DoesNotExist:
            return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if slot.available_capacity <= 0:
            return Response({"error": "Slot is fully booked"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Atomic reservation
        from django.db import transaction
        with transaction.atomic():
            # Refresh from DB with lock to prevent race condition
            locked_slot = BookingSlot.objects.select_for_update().get(id=slot_id)
            if locked_slot.available_capacity > 0:
                locked_slot.available_capacity -= 1
                locked_slot.reserved_capacity += 1
                if locked_slot.available_capacity == 0:
                    locked_slot.status = 'FULL'
                locked_slot.save()
                return Response({"success": True, "message": "Slot reserved"})
            else:
                return Response({"error": "Slot just got fully booked by another user"}, status=status.HTTP_409_CONFLICT)
