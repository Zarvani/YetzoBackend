from rest_framework import serializers
from .models import (
    Category, Subcategory, Service, ServiceVariant,
    ServiceAddon, ServiceQuestion, ServiceQuestionOption
)
from apps.pricing.serializers import ServicePricingRuleSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = '__all__'


class ServiceVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceVariant
        fields = '__all__'


class ServiceAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAddon
        fields = '__all__'


class ServiceQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceQuestionOption
        fields = '__all__'


class ServiceQuestionSerializer(serializers.ModelSerializer):
    options = ServiceQuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceQuestion
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    subcategory = SubcategorySerializer(read_only=True)
    subcategory_id = serializers.PrimaryKeyRelatedField(
        queryset=Subcategory.objects.all(), source='subcategory', write_only=True, required=False, allow_null=True
    )
    variants = ServiceVariantSerializer(many=True, read_only=True)
    addons = ServiceAddonSerializer(many=True, read_only=True)
    pricing_rules = ServicePricingRuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = '__all__'
