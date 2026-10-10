from rest_framework import serializers
from .models import ServicePricingRule, AddonPricing, QuestionOptionPricing, TaxRule

class ServicePricingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePricingRule
        fields = '__all__'

class AddonPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddonPricing
        fields = '__all__'

class QuestionOptionPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOptionPricing
        fields = '__all__'

class TaxRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRule
        fields = '__all__'
