import uuid
from django.db import models
from django.conf import settings
from apps.locations.models import Zone
from apps.services.models import Category, Service

class ProfessionalProfile(models.Model):
    STATUS_CHOICES = (
        ('APPLIED', 'Applied'),
        ('DOCUMENT_PENDING', 'Document Pending'),
        ('VERIFICATION', 'Verification in Progress'),
        ('TRAINING', 'Training'),
        ('ASSESSMENT', 'Assessment'),
        ('APPROVED', 'Approved'),
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('REJECTED', 'Rejected'),
        ('BLOCKED', 'Blocked'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='professional_profile')
    
    kyc_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='APPLIED')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.IntegerField(default=0)
    total_jobs_completed = models.IntegerField(default=0)
    
    acceptance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    cancellation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    experience_years = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False)
    
    current_status = models.CharField(max_length=20, default='OFFLINE') # ONLINE, OFFLINE, BUSY, ON_JOB
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'professional_profiles'

    def __str__(self):
        return f"Pro: {self.user.email or self.user.phone}"


class ProfessionalDocument(models.Model):
    DOC_TYPES = (
        ('ID_PROOF', 'ID Proof'),
        ('ADDRESS_PROOF', 'Address Proof'),
        ('CERTIFICATION', 'Certification'),
        ('BACKGROUND_CHECK', 'Background Check'),
        ('BANK_DETAILS', 'Bank Details'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOC_TYPES)
    file_url = models.URLField()
    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'professional_documents'


class ProfessionalSkill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='skills')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'professional_skills'


class ProfessionalAvailability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(ProfessionalProfile, on_delete=models.CASCADE, related_name='availability')
    
    monday_start = models.TimeField(null=True, blank=True)
    monday_end = models.TimeField(null=True, blank=True)
    tuesday_start = models.TimeField(null=True, blank=True)
    tuesday_end = models.TimeField(null=True, blank=True)
    # ... extensible to other days
    
    service_radius_km = models.IntegerField(default=10)
    max_jobs_per_day = models.IntegerField(default=5)
    
    accepts_instant = models.BooleanField(default=True)
    accepts_scheduled = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'professional_availability'


class ProfessionalZone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='zones')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'professional_zones'
        unique_together = ('profile', 'zone')
