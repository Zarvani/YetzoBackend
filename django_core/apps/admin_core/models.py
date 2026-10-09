import uuid
from django.db import models
from django.conf import settings
from apps.services.models import Service
from apps.locations.models import City


class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=(('PERCENTAGE', 'Percentage'), ('FIXED', 'Fixed Amount')))
    discount_value = models.BigIntegerField(help_text="For fixed, stored in paise. For percentage, stored as normal integer.")
    
    min_order_amount = models.BigIntegerField(default=0)
    max_discount_amount = models.BigIntegerField(null=True, blank=True)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    usage_limit = models.IntegerField(null=True, blank=True) # Total uses
    per_user_limit = models.IntegerField(default=1)
    
    is_active = models.BooleanField(default=True)
    
    # Specificity
    specific_service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    specific_city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    new_users_only = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'coupons'

    def __str__(self):
        return self.code


class CouponUsage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking_reference = models.CharField(max_length=50) # Link to booking
    discount_applied = models.BigIntegerField()
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'coupon_usage'


class MembershipPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.BigIntegerField()
    duration_months = models.IntegerField(default=1)
    
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    free_visits_count = models.IntegerField(default=0)
    priority_support = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'membership_plans'


class UserMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_memberships'
