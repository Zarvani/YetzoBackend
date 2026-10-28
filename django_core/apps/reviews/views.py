from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Review, WarrantyClaim
from .serializers import ReviewSerializer, ReviewCreateSerializer, WarrantyClaimSerializer
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
            
            return Response({"success": True, "data": ReviewSerializer(review).data}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WarrantyClaimCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        issue_description = request.data.get('issue_description')

        if not booking_id or not issue_description:
            return Response({"success": False, "error": "booking_id and issue_description are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id, customer=request.user)
        except (Booking.DoesNotExist, ValueError):
            return Response({"success": False, "error": "Booking not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)

        if booking.status != 'COMPLETED':
            return Response({"success": False, "error": "Warranty claims can only be filed on completed bookings"}, status=status.HTTP_400_BAD_REQUEST)

        # Urban Company style 30-Day Guarantee Policy
        if booking.created_at and timezone.now() - booking.created_at > timedelta(days=30):
            return Response({"success": False, "error": "Warranty claim window has expired (30 days from service)"}, status=status.HTTP_400_BAD_REQUEST)

        claim = WarrantyClaim.objects.create(
            original_booking=booking,
            customer=request.user,
            issue_description=issue_description,
            status='PENDING'
        )

        return Response({"success": True, "data": WarrantyClaimSerializer(claim).data, "message": "Warranty claim registered. A free re-work visit will be dispatched."}, status=status.HTTP_201_CREATED)


class WarrantyClaimListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        claims = WarrantyClaim.objects.filter(customer=request.user).order_by('-created_at')
        return Response({"success": True, "data": WarrantyClaimSerializer(claims, many=True).data})

