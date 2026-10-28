from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import ProfessionalProfile, ProfessionalDocument, ProfessionalAvailability
from .serializers import (
    ProfessionalProfileSerializer, ProfessionalDocumentSerializer,
    ProfessionalAvailabilitySerializer
)
from apps.bookings.models import Booking
from apps.bookings.serializers import BookingSerializer

class ProfessionalProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalProfileSerializer

    def get_object(self):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=self.request.user)
        return profile


class ProfessionalStatusToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=request.user)
        is_online = request.data.get('is_online', not profile.is_online)
        profile.is_online = bool(is_online)
        profile.current_status = 'ONLINE' if is_online else 'OFFLINE'
        profile.save(update_fields=['is_online', 'current_status', 'updated_at'])
        return Response({"success": True, "data": {"is_online": profile.is_online, "current_status": profile.current_status}})


class ProfessionalLocationUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=request.user)
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        if lat is not None and lng is not None:
            profile.current_latitude = lat
            profile.current_longitude = lng
            profile.last_location_at = timezone.now()
            profile.save(update_fields=['current_latitude', 'current_longitude', 'last_location_at', 'updated_at'])
            return Response({"success": True, "message": "Location updated successfully"})
        return Response({"success": False, "error": "latitude and longitude required"}, status=status.HTTP_400_BAD_REQUEST)


class ProfessionalPendingJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=request.user)
        pending_bookings = Booking.objects.filter(assigned_professional=profile, status='ASSIGNED').order_by('-created_at')
        serializer = BookingSerializer(pending_bookings, many=True)
        return Response({"success": True, "data": serializer.data})


class ProfessionalActiveJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=request.user)
        active_statuses = ['ACCEPTED', 'ON_THE_WAY', 'ARRIVED', 'OTP_VERIFIED', 'IN_PROGRESS']
        active_bookings = Booking.objects.filter(assigned_professional=profile, status__in=active_statuses).order_by('-created_at')
        serializer = BookingSerializer(active_bookings, many=True)
        return Response({"success": True, "data": serializer.data})


class ProfessionalDocumentUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalDocumentSerializer

    def perform_create(self, serializer):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=self.request.user)
        serializer.save(professional=profile)


class ProfessionalAvailabilityView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalAvailabilitySerializer

    def get_object(self):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=self.request.user)
        avail, _ = ProfessionalAvailability.objects.get_or_create(professional=profile)
        return avail


class AdminProfessionalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalProfileSerializer
    queryset = ProfessionalProfile.objects.all().order_by('-created_at')
