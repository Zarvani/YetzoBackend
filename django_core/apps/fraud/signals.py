from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FraudFlag
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=FraudFlag)
def check_fraud_threshold(sender, instance, created, **kwargs):
    if created and instance.user_id:
        # Count open fraud flags for this user
        open_flags_count = FraudFlag.objects.filter(
            user_id=instance.user_id,
            status='OPEN'
        ).count()
        
        # Suspend account if 3 or more flags
        if open_flags_count >= 3:
            try:
                user = User.objects.get(id=instance.user_id)
                user.is_active = False
                user.save()
            except User.DoesNotExist:
                pass
