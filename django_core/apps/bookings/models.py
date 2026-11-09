import uuid
from django.db import models
from django.conf import settings
from apps.services.models import Service, ServiceVariant, ServiceAddon, ServiceQuestion
from apps.locations.models import Address
from apps.professionals.models import ProfessionalProfile


class Booking(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING_PAYMENT', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed'),
        ('SEARCHING', 'Searching Professional'),
        ('ASSIGNED', 'Assigned'),
        ('ACCEPTED', 'Accepted'),
        ('ON_THE_WAY', 'On The Way'),
        ('ARRIVED', 'Arrived'),
        ('OTP_VERIFIED', 'OTP Verified'),
        ('IN_PROGRESS', 'In Progress'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('REJECTED', 'Rejected'),
        ('TIMEOUT', 'Timeout'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('NO_SHOW', 'No Show'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_reference = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    
    # Schedule
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    is_instant = models.BooleanField(default=False)
    is_verified_session = models.BooleanField(default=False, help_text="Yetzo/Pronto Verified: Encrypted bodycam session recording")
    cancellation_reason = models.TextField(blank=True, null=True)
    
    # Location
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    
    # Fraud Prevention (Job Start/End Verification)
    start_otp = models.CharField(max_length=4, blank=True, null=True, help_text="4-digit OTP customer must provide to pro to start job")
    end_otp = models.CharField(max_length=4, blank=True, null=True, help_text="4-digit OTP to finalize the job")
    
    # Pricing snapshot (stored in paise)
    base_price = models.BigIntegerField(default=0)
    addons_price = models.BigIntegerField(default=0)
    taxes = models.BigIntegerField(default=0)
    discount = models.BigIntegerField(default=0)
    platform_fee = models.BigIntegerField(default=0)
    total_amount = models.BigIntegerField(default=0)
    
    # Assignment
    assigned_professional = models.ForeignKey(ProfessionalProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bookings')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookings'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['assigned_professional', 'status']),
            models.Index(fields=['status', 'is_instant']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.booking_reference} - {self.customer.email}"


class BookingItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ServiceVariant, on_delete=models.SET_NULL, null=True, blank=True)
    addon = models.ForeignKey(ServiceAddon, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price_at_booking = models.BigIntegerField()
    
    class Meta:
        db_table = 'booking_items'


class BookingAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(ServiceQuestion, on_delete=models.PROTECT)
    answer_text = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'booking_answers'


class BookingStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=30)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'booking_status_history'
        ordering = ['-created_at']


class BookingAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='assignments')
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('TIMEOUT', 'Timeout')))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'booking_assignments'
