from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Invoice, ProfessionalEarning, ProfessionalPayout
from .serializers import (
    InvoiceSerializer, ProfessionalEarningSerializer, ProfessionalPayoutSerializer
)
from apps.bookings.models import Booking

class InvoiceDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer
    lookup_field = 'id'

    def get_queryset(self):
        # Allow admins or the customer/professional involved
        if self.request.user.role and self.request.user.role.name in ['ADMIN', 'DISPATCHER']:
            return Invoice.objects.all()
        return Invoice.objects.filter(user=self.request.user)


class ProfessionalEarningsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfessionalEarningSerializer

    def get_queryset(self):
        if self.request.user.role and self.request.user.role.name == 'PROFESSIONAL':
            return ProfessionalEarning.objects.filter(professional__user=self.request.user).order_by('-created_at')
        if self.request.user.role and self.request.user.role.name in ['ADMIN', 'FINANCE']:
            return ProfessionalEarning.objects.all().order_by('-created_at')
        return ProfessionalEarning.objects.none()


class ProfessionalPayoutRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not (request.user.role and request.user.role.name == 'PROFESSIONAL'):
            return Response({"error": "Only professionals can request payouts."}, status=status.HTTP_403_FORBIDDEN)
            
        amount = request.data.get('amount')
        if not amount or float(amount) <= 0:
            return Response({"error": "Invalid payout amount."}, status=status.HTTP_400_BAD_REQUEST)
            
        profile = request.user.professional_profile
        
        import os
        import razorpay
        
        # Calculate available balance (Total settled earnings - Total requested/processed payouts)
        total_earnings = sum([e.net_amount for e in ProfessionalEarning.objects.filter(professional=profile, status='SETTLED')])
        total_payouts = sum([p.amount for p in ProfessionalPayout.objects.filter(professional=profile, status__in=['REQUESTED', 'PROCESSED'])])
        
        available_balance = total_earnings - total_payouts
        
        if float(amount) > available_balance:
            return Response({"error": "Insufficient balance for payout."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Initialize Razorpay Client
        razorpay_key_id = os.environ.get('RAZORPAY_KEY_ID')
        razorpay_key_secret = os.environ.get('RAZORPAY_KEY_SECRET')
        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
        
        linked_account_id = getattr(profile, 'razorpay_account_id', None)
        if not linked_account_id:
            return Response(
                {"error": "Professional has no linked bank account or Razorpay Account ID configured."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create a Transfer via Razorpay Route (from platform balance to Pro's linked account)
            transfer_data = {
                "account": linked_account_id,
                "amount": int(float(amount) * 100),
                "currency": "INR",
                "notes": {
                    "pro_id": str(profile.id)
                }
            }
            transfer = client.transfer.create(transfer_data)
            
            payout = ProfessionalPayout.objects.create(
                professional=profile,
                amount=float(amount),
                status='PROCESSED',
                payout_reference=transfer['id']
            )
            
            return Response({"success": True, "data": ProfessionalPayoutSerializer(payout).data, "transfer": transfer}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If Razorpay fails, log it as failed or return error
            return Response({"error": f"Razorpay Route Transfer Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
