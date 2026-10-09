from rest_framework import serializers
from .models import Review, ReviewMedia, WarrantyClaim

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['booking', 'professional', 'service', 'rating', 'text']
