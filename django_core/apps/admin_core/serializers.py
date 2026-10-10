from rest_framework import serializers
from .models import Coupon, CouponUsage, MembershipPlan, UserMembership

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class CouponUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponUsage
        fields = '__all__'

class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = '__all__'

class UserMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMembership
        fields = '__all__'
