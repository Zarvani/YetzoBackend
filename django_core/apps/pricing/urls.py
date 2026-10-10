from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServicePricingRuleViewSet,
    AddonPricingViewSet,
    QuestionOptionPricingViewSet,
    TaxRuleViewSet
)

router = DefaultRouter()
router.register(r'service-pricing', ServicePricingRuleViewSet, basename='service-pricing')
router.register(r'addon-pricing', AddonPricingViewSet, basename='addon-pricing')
router.register(r'question-pricing', QuestionOptionPricingViewSet, basename='question-pricing')
router.register(r'tax-rules', TaxRuleViewSet, basename='tax-rules')

urlpatterns = [
    path('', include(router.urls)),
]
