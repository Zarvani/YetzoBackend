from rest_framework import serializers
from .models import Cart, CartItem
from apps.services.serializers import ServiceSerializer, ServiceVariantSerializer

class CartItemSerializer(serializers.ModelSerializer):
    # Depending on frontend needs, you can nest the actual service details here
    service_details = ServiceSerializer(source='service', read_only=True)
    variant_details = ServiceVariantSerializer(source='variant', read_only=True)
    
    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = '__all__'
