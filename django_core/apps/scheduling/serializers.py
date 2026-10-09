from rest_framework import serializers
from .models import BookingSlot, RecurringBooking, RecurringBookingInstance

class BookingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingSlot
        fields = '__all__'

class RecurringBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringBooking
        fields = '__all__'

class RecurringBookingInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringBookingInstance
        fields = '__all__'
