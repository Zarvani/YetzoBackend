from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserDevice, Role, User
from .serializers import RoleSerializer, UserAdminSerializer
import uuid

class RoleListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoleSerializer
    queryset = Role.objects.all().order_by('name')

class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoleSerializer
    queryset = Role.objects.all()
    lookup_field = 'id'

class UserAdminListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAdminSerializer
    queryset = User.objects.all().order_by('-date_joined')

class UpdateFCMTokenView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        fcm_token = request.data.get('fcm_token')
        device_id = request.data.get('device_id', str(uuid.uuid4()))
        device_type = request.data.get('device_type', 'Mobile')
        
        if not fcm_token:
            return Response({"success": False, "error": "fcm_token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = request.user
        
        # Update or create the device token
        device, created = UserDevice.objects.update_or_create(
            user=user,
            device_id=device_id,
            defaults={
                'fcm_token': fcm_token,
                'device_type': device_type,
                'is_active': True
            }
        )
        
        return Response({"success": True, "message": "FCM token registered successfully"})

