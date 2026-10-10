import uuid
from django.db import models
from django.conf import settings
from apps.bookings.models import Booking
from apps.professionals.models import ProfessionalProfile


class Payment(models.Model):
    STATUS_CHOICES = (
        ('INITIATED', 'Initiated'),
        ('AUTHORIZED', 'Authorized'),
        ('CAPTURED', 'Captured'),
        ('FAILED', 'Failed'),
        ('REFUND_PENDING', 'Refund Pending'),
        ('REFUNDED', 'Refunded'),
        ('PARTIALLY_REFUNDED', 'Partially Refunded'),
    )
    
    METHOD_CHOICES = (
        ('UPI', 'UPI'),
        ('CARD', 'Credit/Debit Card'),
        ('NET_BANKING', 'Net Banking'),
        ('WALLET', 'Digital Wallet'),
        ('COD', 'Cash on Delivery'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    provider_transaction_id = models.CharField(max_length=255, blank=True, null=True) # e.g. Razorpay payment ID
    provider_order_id = models.CharField(max_length=255, blank=True, null=True)
    
    amount = models.BigIntegerField()
    currency = models.CharField(max_length=10, default='INR')
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='INITIATED')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'


class Refund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.BigIntegerField()
    provider_refund_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=30, default='PENDING')
    reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'refunds'


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet', null=True, blank=True)
    professional = models.OneToOneField(ProfessionalProfile, on_delete=models.CASCADE, related_name='wallet', null=True, blank=True)
    
    balance = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wallets'


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.BigIntegerField()
    reference_id = models.CharField(max_length=100, blank=True, null=True) # Could be booking ID, payout ID, etc.
    description = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wallet_transactions'
        ordering = ['-created_at']

class EscrowLedger(models.Model):
    """
    Holds funds paid by the customer securely until the job is completed.
    Once completed, funds are split to the platform and the professional's wallet.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='escrow')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='escrows', null=True, blank=True)
    
    amount_held = models.BigIntegerField()
    status = models.CharField(max_length=30, choices=(('HELD', 'Held'), ('RELEASED', 'Released'), ('REFUNDED', 'Refunded')), default='HELD')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'escrow_ledgers'
