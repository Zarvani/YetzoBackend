from rest_framework import serializers
from .models import Booking, BookingItem, BookingAnswer, BookingStatusHistory

class BookingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingItem
        fields = '__all__'

class BookingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingAnswer
        fields = '__all__'

class BookingStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingStatusHistory
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    items = BookingItemSerializer(many=True, read_only=True)
    answers = BookingAnswerSerializer(many=True, read_only=True)
    status_history = BookingStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('booking_reference', 'total_amount', 'status', 'created_at', 'updated_at')

class BookingCreateSerializer(serializers.Serializer):
    service_id = serializers.UUIDField()
    address_id = serializers.UUIDField()
    scheduled_date = serializers.DateField(required=False)
    scheduled_time = serializers.TimeField(required=False)
    is_instant = serializers.BooleanField(default=False)
    
    # Items: list of dicts with variant_id, addon_id, quantity
    items = serializers.ListField(child=serializers.DictField(), required=False)
    # Answers: list of dicts with question_id, answer_text
    answers = serializers.ListField(child=serializers.DictField(), required=False)

class BookingStatusUpdateSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES)
    reason = serializers.CharField(required=False, allow_blank=True)
