import uuid
from django.db import models
from django.conf import settings


class NotificationTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True) # e.g. 'BOOKING_CONFIRMED'
    channel = models.CharField(max_length=20, choices=(('EMAIL', 'Email'), ('SMS', 'SMS'), ('PUSH', 'Push'), ('IN_APP', 'In-App'), ('WHATSAPP', 'WhatsApp')))
    subject_template = models.CharField(max_length=255, blank=True, null=True)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'notification_templates'


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    title = models.CharField(max_length=255)
    body = models.TextField()
    data_payload = models.JSONField(blank=True, null=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    channel = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='PENDING') # PENDING, SENT, FAILED
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
