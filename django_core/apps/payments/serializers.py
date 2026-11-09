from rest_framework import serializers
from .models import Payment, Refund, Wallet, WalletTransaction

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('status', 'provider_transaction_id', 'provider_order_id')


class RefundSerializer(serializers.ModelSerializer):
    booking = serializers.SerializerMethodField()

    class Meta:
        model = Refund
        fields = '__all__'
        read_only_fields = ('status', 'provider_refund_id')

    def get_booking(self, obj):
        if obj.payment and obj.payment.booking:
            return {
                'id': str(obj.payment.booking.id),
                'booking_number': str(obj.payment.booking.id)[:8].upper()
            }
        return None


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('balance', 'user', 'professional')
