import uuid
from django.db import models
from apps.services.models import Service, ServiceVariant, ServiceAddon, ServiceQuestionOption
from apps.locations.models import City, Zone

class ServicePricingRule(models.Model):
    PRICING_TYPES = (
        ('FIXED', 'Fixed Price'),
        ('HOURLY', 'Hourly Rate'),
        ('INSPECTION', 'Inspection Only'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='pricing_rules')
    variant = models.ForeignKey(ServiceVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='pricing_rules')
    
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES, default='FIXED')
    base_price = models.BigIntegerField(help_text="Stored in smallest currency unit (e.g. paise)")
    minimum_price = models.BigIntegerField(null=True, blank=True)
    
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'service_pricing_rules'

    def __str__(self):
        return f"Pricing for {self.service.name}"


class AddonPricing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    addon = models.ForeignKey(ServiceAddon, on_delete=models.CASCADE, related_name='pricing')
    price = models.BigIntegerField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'addon_pricing'


class QuestionOptionPricing(models.Model):
    """
    If a user answers a question with a specific option, it might affect the price.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    option = models.ForeignKey(ServiceQuestionOption, on_delete=models.CASCADE, related_name='price_adjustments')
    price_adjustment = models.BigIntegerField(default=0)
    
    class Meta:
        db_table = 'question_option_pricing'


class TaxRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100) # e.g. "Standard GST 18%"
    cgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=9.00)
    sgst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=9.00)
    igst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tax_rules'
