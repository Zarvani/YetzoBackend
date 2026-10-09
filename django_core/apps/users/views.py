from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import UserDevice
import uuid

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
