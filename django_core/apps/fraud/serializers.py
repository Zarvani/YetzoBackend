from rest_framework import serializers
from .models import FraudRule, FraudFlag, SafetyIncident

class FraudRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudRule
        fields = '__all__'

class FraudFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudFlag
        fields = '__all__'

class SafetyIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyIncident
        fields = '__all__'
