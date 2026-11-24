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
            
            # Live GPS streaming to active customer tracking room
            active_booking = Booking.objects.filter(
                assigned_professional=profile,
                status__in=['ACCEPTED', 'ON_THE_WAY', 'ARRIVED']
            ).first()
            if active_booking:
                try:
                    from channels.layers import get_channel_layer
                    from asgiref.sync import async_to_sync
                    channel_layer = get_channel_layer()
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            f'tracking_{active_booking.id}',
                            {
                                'type': 'location_update',
                                'latitude': float(lat),
                                'longitude': float(lng)
                            }
                        )
                except Exception:
                    pass
                    
            return Response({"success": True, "message": "Location updated successfully"})
        return Response({"success": False, "error": "latitude and longitude required"}, status=status.HTTP_400_BAD_REQUEST)


class ProfessionalPendingJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=request.user)
        pending_bookings = Booking.objects.select_related(
            'customer', 'service', 'address'
        ).filter(assigned_professional=profile, status='ASSIGNED').order_by('-created_at')
        serializer = BookingSerializer(pending_bookings, many=True)
        return Response({"success": True, "data": serializer.data})


class ProfessionalActiveJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=request.user)
        active_statuses = ['ACCEPTED', 'ON_THE_WAY', 'ARRIVED', 'OTP_VERIFIED', 'IN_PROGRESS']
        active_bookings = Booking.objects.select_related(
            'customer', 'service', 'address'
        ).filter(assigned_professional=profile, status__in=active_statuses).order_by('-created_at')
        serializer = BookingSerializer(active_bookings, many=True)
        return Response({"success": True, "data": serializer.data})


class ProfessionalDocumentUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalDocumentSerializer

    def perform_create(self, serializer):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)


class ProfessionalAvailabilityView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalAvailabilitySerializer

    def get_object(self):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=self.request.user)
        avail, _ = ProfessionalAvailability.objects.get_or_create(profile=profile)
        return avail

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class AdminProfessionalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalProfileSerializer
    queryset = ProfessionalProfile.objects.select_related('user').prefetch_related('skills', 'skills__service').all().order_by('-created_at')


class AdminProfessionalDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalProfileSerializer
    queryset = ProfessionalProfile.objects.select_related('user').prefetch_related('skills', 'skills__service').all()
    queryset = ProfessionalProfile.objects.all()
    lookup_field = 'id'


class AdminProfessionalKYCUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        is_admin = request.user.is_staff or request.user.is_superuser or (
            request.user.role and request.user.role.name in ['ADMIN', 'SUPER_ADMIN', 'KYC_MANAGER', 'OPERATIONS_MANAGER']
        )
        if not is_admin:
            return Response({"error": "Admin permission required."}, status=status.HTTP_403_FORBIDDEN)
        try:
            profile = ProfessionalProfile.objects.get(id=id)
        except ProfessionalProfile.DoesNotExist:
            return Response({"error": "Professional not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('kyc_status')
        if new_status == 'VERIFIED':
            new_status = 'ACTIVE'

        if new_status not in [c[0] for c in ProfessionalProfile.STATUS_CHOICES]:
            return Response({"error": f"Invalid status: {new_status}"}, status=status.HTTP_400_BAD_REQUEST)

        profile.kyc_status = new_status
        if new_status in ['APPROVED', 'ACTIVE']:
            profile.current_status = 'ONLINE'
            profile.is_online = True
        profile.save(update_fields=['kyc_status', 'current_status', 'is_online', 'updated_at'])
        return Response({"success": True, "data": ProfessionalProfileSerializer(profile).data})


class AdminDocumentVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id, doc_id):
        is_admin = request.user.is_staff or request.user.is_superuser or (
            request.user.role and request.user.role.name in ['ADMIN', 'SUPER_ADMIN', 'KYC_MANAGER', 'OPERATIONS_MANAGER']
        )
        if not is_admin:
            return Response({"error": "Admin permission required."}, status=status.HTTP_403_FORBIDDEN)
        try:
            doc = ProfessionalDocument.objects.get(id=doc_id, profile_id=id)
        except ProfessionalDocument.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        is_verified = request.data.get('is_verified', True)
        doc.is_verified = bool(is_verified)
        if is_verified:
            doc.verified_at = timezone.now()
        doc.save(update_fields=['is_verified', 'verified_at'])
        return Response({"success": True, "data": ProfessionalDocumentSerializer(doc).data})


class ProfessionalSkillsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=request.user)
        from .serializers import ProfessionalSkillSerializer
        skills = profile.skills.all()
        return Response({"success": True, "data": ProfessionalSkillSerializer(skills, many=True).data})

    def post(self, request):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=request.user)
        service_id = request.data.get('service_id')
        category_id = request.data.get('category_id')
        from .models import ProfessionalSkill
        from .serializers import ProfessionalSkillSerializer
        skill, created = ProfessionalSkill.objects.get_or_create(
            profile=profile,
            service_id=service_id,
            defaults={'category_id': category_id, 'is_verified': True}
        )
        return Response({"success": True, "data": ProfessionalSkillSerializer(skill).data}, status=status.HTTP_201_CREATED)

