from django.db import models
import uuid
from django.conf import settings
from apps.services.models import Service
from apps.locations.models import City, Zone

class BookingSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    capacity = models.IntegerField(default=10)
    available_capacity = models.IntegerField(default=10)
    reserved_capacity = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='OPEN')

class RecurringBooking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    frequency = models.CharField(max_length=20) # WEEKLY, BIWEEKLY, MONTHLY
    day_of_week = models.IntegerField()
    time = models.TimeField()
    duration_minutes = models.IntegerField()
    
    start_date = models.DateField()
    end_date = models.DateField()
    timezone = models.CharField(max_length=50, default='UTC')
    
    status = models.CharField(max_length=20, default='ACTIVE')
    next_booking_at = models.DateTimeField(null=True, blank=True)

class RecurringBookingInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recurring_booking = models.ForeignKey(RecurringBooking, on_delete=models.CASCADE)
    booking_id = models.UUIDField(null=True, blank=True) # Ref to actual Booking
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, default='SCHEDULED')
