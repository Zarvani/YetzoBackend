from django.db import models
import uuid
from django.conf import settings
from apps.professionals.models import ProfessionalProfile
from apps.bookings.models import Booking

class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.SET_NULL, null=True, blank=True)
    
    subtotal = models.BigIntegerField()
    discount = models.BigIntegerField(default=0)
    tax = models.BigIntegerField(default=0)
    service_fee = models.BigIntegerField(default=0)
    platform_fee = models.BigIntegerField(default=0)
    additional_charges = models.BigIntegerField(default=0)
    total = models.BigIntegerField()
    currency = models.CharField(max_length=10, default='INR')
    
    status = models.CharField(max_length=20, default='ISSUED')
    invoice_date = models.DateTimeField(auto_now_add=True)
    pdf_url = models.URLField(null=True, blank=True)

class ProfessionalEarning(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    
    gross_amount = models.BigIntegerField()
    platform_commission = models.BigIntegerField()
    tax_deduction = models.BigIntegerField()
    incentive = models.BigIntegerField(default=0)
    bonus = models.BigIntegerField(default=0)
    penalty = models.BigIntegerField(default=0)
    refund_adjustment = models.BigIntegerField(default=0)
    other_adjustment = models.BigIntegerField(default=0)
    net_amount = models.BigIntegerField()
    
    status = models.CharField(max_length=20, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

class ProfessionalPayout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    currency = models.CharField(max_length=10, default='INR')
    
    payout_reference = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default='REQUESTED')
    
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)
