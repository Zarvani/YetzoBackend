from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import Address, City, Zone, Area

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    address_line_1 = serializers.SerializerMethodField(read_only=True)
    address_line_2 = serializers.SerializerMethodField(read_only=True)
    latitude = serializers.SerializerMethodField(read_only=True)
    longitude = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Address
        fields = [
            'id', 'user', 'area', 'address_type',
            'house_flat', 'building', 'street', 'landmark',
            'pincode', 'city', 'state', 'instructions',
            'address_line_1', 'address_line_2', 'latitude', 'longitude',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_address_line_1(self, obj):
        parts = [p for p in [obj.house_flat, obj.building] if p]
        return ", ".join(parts) if parts else obj.street

    def get_address_line_2(self, obj):
        parts = [p for p in [obj.street, obj.landmark] if p]
        return ", ".join(parts) if parts else ""

    def get_latitude(self, obj):
        if obj.location:
            return obj.location.y
        return None

    def get_longitude(self, obj):
        if obj.location:
            return obj.location.x
        return None

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        # Adapt legacy or alternative frontend payloads
        if 'address_line_1' in data and not data.get('house_flat'):
            data['house_flat'] = data.get('address_line_1', '')
        if 'address_line_2' in data and not data.get('street'):
            data['street'] = data.get('address_line_2', '')
        if not data.get('street'):
            data['street'] = data.get('house_flat', 'Main Street')
        if not data.get('state'):
            data['state'] = 'Delhi NCR'
        if not data.get('city'):
            data['city'] = 'New Delhi'
        if not data.get('pincode'):
            data['pincode'] = '110001'

        lat = data.get('latitude')
        lng = data.get('longitude')
        ret = super().to_internal_value(data)
        if lat is not None and lng is not None:
            try:
                ret['location'] = Point(float(lng), float(lat))
            except Exception:
                pass
        return ret

