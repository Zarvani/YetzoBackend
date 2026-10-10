from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, MembershipPlanViewSet

router = DefaultRouter()
router.register(r'coupons', CouponViewSet, basename='coupons')
router.register(r'memberships', MembershipPlanViewSet, basename='memberships')

urlpatterns = [
    path('', include(router.urls)),
]
