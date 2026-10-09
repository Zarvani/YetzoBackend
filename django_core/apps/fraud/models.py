from django.db import models
import uuid

class FraudRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=50)
    configuration = models.JSONField(default=dict)
    risk_score = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

class FraudFlag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True)
    booking_id = models.UUIDField(null=True, blank=True)
    professional_id = models.UUIDField(null=True, blank=True)
    rule = models.ForeignKey(FraudRule, on_delete=models.SET_NULL, null=True)
    risk_score = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default='OPEN') # OPEN, REVIEWED, DISMISSED
    created_at = models.DateTimeField(auto_now_add=True)

class SafetyIncident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident_number = models.CharField(max_length=50, unique=True)
    booking_id = models.UUIDField(null=True, blank=True)
    customer_id = models.UUIDField(null=True, blank=True)
    professional_id = models.UUIDField(null=True, blank=True)
    
    incident_type = models.CharField(max_length=50) # HARASSMENT, PROPERTY_DAMAGE, etc.
    severity = models.CharField(max_length=20) # LOW, MEDIUM, HIGH, CRITICAL
    description = models.TextField()
    
    status = models.CharField(max_length=20, default='REPORTED')
    reported_by = models.UUIDField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
