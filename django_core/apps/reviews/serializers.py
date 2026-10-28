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


class WarrantyClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarrantyClaim
        fields = '__all__'
        read_only_fields = ('id', 'customer', 'status', 'revisit_booking', 'created_at', 'updated_at')

