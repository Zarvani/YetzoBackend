from rest_framework import viewsets, permissions
from .models import ServicePricingRule, AddonPricing, QuestionOptionPricing, TaxRule
from .serializers import (
    ServicePricingRuleSerializer,
    AddonPricingSerializer,
    QuestionOptionPricingSerializer,
    TaxRuleSerializer
)

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or (request.user.role and request.user.role.name in ['ADMIN', 'SUPER_ADMIN'])))

class ServicePricingRuleViewSet(viewsets.ModelViewSet):
    queryset = ServicePricingRule.objects.all()
    serializer_class = ServicePricingRuleSerializer
    permission_classes = [IsAdminOrReadOnly]

class AddonPricingViewSet(viewsets.ModelViewSet):
    queryset = AddonPricing.objects.all()
    serializer_class = AddonPricingSerializer
    permission_classes = [IsAdminOrReadOnly]

class QuestionOptionPricingViewSet(viewsets.ModelViewSet):
    queryset = QuestionOptionPricing.objects.all()
    serializer_class = QuestionOptionPricingSerializer
    permission_classes = [IsAdminOrReadOnly]

class TaxRuleViewSet(viewsets.ModelViewSet):
    queryset = TaxRule.objects.all()
    serializer_class = TaxRuleSerializer
    permission_classes = [IsAdminOrReadOnly]

