from django.db import models
import uuid

class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_id = models.UUIDField(null=True, blank=True)
    actor_type = models.CharField(max_length=50) # ADMIN, SYSTEM, etc.
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)
    entity_id = models.UUIDField()
    
    before_data = models.JSONField(null=True, blank=True)
    after_data = models.JSONField(null=True, blank=True)
    
    reason = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AnalyticsEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    event_name = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50, null=True, blank=True)
    entity_id = models.UUIDField(null=True, blank=True)
    properties = models.JSONField(default=dict)
    
    device_type = models.CharField(max_length=50, null=True, blank=True)
    platform = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class FeatureFlag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    enabled = models.BooleanField(default=False)
    rollout_percentage = models.IntegerField(default=100)
    config = models.JSONField(null=True, blank=True)
