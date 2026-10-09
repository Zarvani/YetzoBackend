import uuid
from django.db import models
from django.conf import settings
from apps.bookings.models import Booking
from apps.services.models import Service
from apps.professionals.models import ProfessionalProfile


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='reviews')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField(blank=True, null=True)
    
    is_published = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'


class ReviewMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='media')
    file_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_media'


class WarrantyClaim(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='warranty_claims')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    issue_description = models.TextField()
    status = models.CharField(max_length=30, choices=(('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('RESOLVED', 'Resolved')), default='PENDING')
    
    # If a revisit is required, it maps to a new booking instance under the hood
    revisit_booking = models.OneToOneField(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='warranty_parent')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'warranty_claims'
