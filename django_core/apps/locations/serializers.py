from rest_framework import serializers
from .models import Address, City, Zone

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'address_line_1', 'address_line_2', 'landmark', 'city', 'pincode', 'latitude', 'longitude', 'is_default', 'address_type', 'created_at']
        read_only_fields = ['user', 'created_at']
