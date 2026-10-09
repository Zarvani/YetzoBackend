from rest_framework import serializers
from .models import (
    ProfessionalProfile, ProfessionalDocument, 
    ProfessionalSkill, ProfessionalAvailability, ProfessionalZone
)

class ProfessionalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalDocument
        fields = '__all__'
        read_only_fields = ('is_verified', 'verified_at')


class ProfessionalSkillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = ProfessionalSkill
        fields = '__all__'
        read_only_fields = ('is_verified',)


class ProfessionalAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalAvailability
        fields = '__all__'


class ProfessionalZoneSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    
    class Meta:
        model = ProfessionalZone
        fields = '__all__'


class ProfessionalProfileSerializer(serializers.ModelSerializer):
    documents = ProfessionalDocumentSerializer(many=True, read_only=True)
    skills = ProfessionalSkillSerializer(many=True, read_only=True)
    availability = ProfessionalAvailabilitySerializer(read_only=True)
    zones = ProfessionalZoneSerializer(many=True, read_only=True)
    
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = ProfessionalProfile
        fields = '__all__'
        read_only_fields = (
            'kyc_status', 'rating', 'total_reviews', 'total_jobs_completed',
            'acceptance_rate', 'completion_rate', 'cancellation_rate'
        )
