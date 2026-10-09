from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Review, WarrantyClaim
from .serializers import ReviewSerializer, ReviewCreateSerializer
from apps.bookings.models import Booking

class ReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            booking_id = serializer.validated_data['booking'].id
            
            try:
                booking = Booking.objects.get(id=booking_id, customer=request.user)
            except Booking.DoesNotExist:
                return Response({"error": "Booking not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)
                
            if booking.status != 'COMPLETED':
                return Response({"error": "Can only review completed bookings"}, status=status.HTTP_400_BAD_REQUEST)
                
            if hasattr(booking, 'review'):
                return Response({"error": "Booking already reviewed"}, status=status.HTTP_400_BAD_REQUEST)
                
            review = Review.objects.create(
                customer=request.user,
                **serializer.validated_data
            )
            
            # TODO: Update aggregate rating on ProfessionalProfile in a background task
            
            return Response({"success": True, "data": ReviewSerializer(review).data}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
