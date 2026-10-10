from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Coupon, CouponUsage, MembershipPlan, UserMembership
from .serializers import (
    CouponSerializer,
    CouponUsageSerializer,
    MembershipPlanSerializer,
    UserMembershipSerializer
)

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Coupon code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
            
            # Basic validation
            if coupon.valid_from and coupon.valid_from > timezone.now():
                return Response({'error': 'Coupon is not yet active'}, status=status.HTTP_400_BAD_REQUEST)
            if coupon.valid_until and coupon.valid_until < timezone.now():
                return Response({'error': 'Coupon has expired'}, status=status.HTTP_400_BAD_REQUEST)
                
            # If valid, return coupon data for the frontend to calculate discount
            return Response(self.get_serializer(coupon).data)
            
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_404_NOT_FOUND)

class MembershipPlanViewSet(viewsets.ModelViewSet):
    queryset = MembershipPlan.objects.all()
    serializer_class = MembershipPlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
