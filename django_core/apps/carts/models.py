from django.db import models
import uuid
from django.conf import settings
from apps.services.models import Service, ServiceVariant, ServiceAddon, ServicePackage

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='ACTIVE')
    currency = models.CharField(max_length=10, default='INR')
    
    subtotal = models.BigIntegerField(default=0)
    discount = models.BigIntegerField(default=0)
    tax = models.BigIntegerField(default=0)
    service_fee = models.BigIntegerField(default=0)
    total = models.BigIntegerField(default=0)
    
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    variant = models.ForeignKey(ServiceVariant, on_delete=models.SET_NULL, null=True, blank=True)
    package = models.ForeignKey(ServicePackage, on_delete=models.SET_NULL, null=True, blank=True)
    
    quantity = models.IntegerField(default=1)
    duration_minutes = models.IntegerField(default=0)
    unit_price = models.BigIntegerField(default=0)
    total_price = models.BigIntegerField(default=0)
    
    answers = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict)
