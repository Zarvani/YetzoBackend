import uuid
from django.db import models
from django.conf import settings
from apps.bookings.models import Booking
from apps.professionals.models import ProfessionalProfile


class SupportTicket(models.Model):
    CATEGORY_CHOICES = (
        ('BOOKING', 'Booking Issue'),
        ('PAYMENT', 'Payment/Refund Issue'),
        ('PROFESSIONAL', 'Professional Issue'),
        ('CANCELLATION', 'Cancellation/Reschedule'),
        ('WARRANTY', 'Warranty Claim'),
        ('QUALITY', 'Service Quality'),
        ('SAFETY', 'Safety Concern'),
        ('TECHNICAL', 'Technical/App Issue'),
        ('OTHER', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('WAITING_CUSTOMER', 'Waiting for Customer'),
        ('WAITING_PROFESSIONAL', 'Waiting for Professional'),
        ('ESCALATED', 'Escalated'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True)
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.SET_NULL, null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='OPEN')
    priority = models.CharField(max_length=10, choices=(('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent')), default='MEDIUM')
    
    subject = models.CharField(max_length=255)
    description = models.TextField()
    
    assigned_agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'support_tickets'

    def __str__(self):
        return self.ticket_number


class SupportMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_text = models.TextField()
    attachment_url = models.URLField(blank=True, null=True)
    is_internal_note = models.BooleanField(default=False) # True if agent note not visible to customer
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'support_messages'
        ordering = ['created_at']
