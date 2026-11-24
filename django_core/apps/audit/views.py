from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        if u.is_staff or u.is_superuser or (u.role and u.role.name in ['ADMIN', 'OPERATIONS_MANAGER']):
            return AuditLog.objects.select_related('user').all().order_by('-created_at')[:200]
        return AuditLog.objects.none()


# Create your views here.
