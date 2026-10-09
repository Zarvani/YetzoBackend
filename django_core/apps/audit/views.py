from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role and self.request.user.role.name in ['ADMIN']:
            return AuditLog.objects.all().order_by('-created_at')
        return AuditLog.objects.none()


# Create your views here.
