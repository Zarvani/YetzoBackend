from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer
import os
import firebase_admin
from firebase_admin import credentials, messaging

# Initialize Firebase only once
if not firebase_admin._apps:
    cert_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH')
    if cert_path and os.path.exists(cert_path):
        cred = credentials.Certificate(cert_path)
        firebase_admin.initialize_app(cred)

class UserNotificationsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        try:
            notification = Notification.objects.get(id=id, user=request.user)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
            
        import django.utils.timezone
        notification.is_read = True
        notification.read_at = django.utils.timezone.now()
        notification.save()
        
        return Response({"success": True})


class InternalSendNotificationView(APIView):
    """
    Internal API used by Celery or other microservices to trigger a notification.
    In production, this should be protected by an internal API key or VPC.
    """
    def post(self, request):
        user_id = request.data.get('user_id')
        title = request.data.get('title')
        body = request.data.get('body')
        channel = request.data.get('channel', 'IN_APP')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        notification = Notification.objects.create(
            user=user,
            title=title,
            body=body,
            channel=channel,
            status='PENDING'
        )
        
        # Trigger FCM Push
        if channel in ['PUSH', 'IN_APP'] and firebase_admin._apps:
            # Assuming user profile has a stored fcm_token
            fcm_token = getattr(user, 'fcm_token', None)
            if fcm_token:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    token=fcm_token,
                )
                try:
                    response = messaging.send(message)
                    notification.status = 'SENT'
                    notification.save()
                except Exception as e:
                    notification.status = 'FAILED'
                    notification.save()
                    return Response({"error": f"FCM send failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Can't push if no token is registered for user
                pass
        
        return Response({"success": True, "id": notification.id})
