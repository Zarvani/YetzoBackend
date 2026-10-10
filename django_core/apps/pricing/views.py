from rest_framework import viewsets, permissions
from .models import ServicePricingRule, AddonPricing, QuestionOptionPricing, TaxRule
from .serializers import (
    ServicePricingRuleSerializer,
    AddonPricingSerializer,
    QuestionOptionPricingSerializer,
    TaxRuleSerializer
)

class ServicePricingRuleViewSet(viewsets.ModelViewSet):
    queryset = ServicePricingRule.objects.all()
    serializer_class = ServicePricingRuleSerializer
    permission_classes = [permissions.AllowAny] # Using AllowAny temporarily for ease of dev testing; should be IsAdminUser in prod

class AddonPricingViewSet(viewsets.ModelViewSet):
    queryset = AddonPricing.objects.all()
    serializer_class = AddonPricingSerializer
    permission_classes = [permissions.AllowAny]

class QuestionOptionPricingViewSet(viewsets.ModelViewSet):
    queryset = QuestionOptionPricing.objects.all()
    serializer_class = QuestionOptionPricingSerializer
    permission_classes = [permissions.AllowAny]

class TaxRuleViewSet(viewsets.ModelViewSet):
    queryset = TaxRule.objects.all()
    serializer_class = TaxRuleSerializer
    permission_classes = [permissions.AllowAny]
