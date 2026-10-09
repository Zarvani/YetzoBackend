from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import SafetyIncident, FraudFlag
from .serializers import SafetyIncidentSerializer, FraudFlagSerializer
import uuid

class ReportSafetyIncidentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        booking_id = data.get('booking_id')
        incident_type = data.get('incident_type')
        description = data.get('description')
        
        if not incident_type or not description:
            return Response({"error": "Type and description are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        incident = SafetyIncident.objects.create(
            incident_number=f"INC-{uuid.uuid4().hex[:8].upper()}",
            booking_id=booking_id,
            incident_type=incident_type,
            description=description,
            severity='HIGH', # Default for manual reports
            reported_by=request.user.id
        )
        
        # Trigger Admin Alert via Celery (TODO)
        
        return Response({"success": True, "data": SafetyIncidentSerializer(incident).data}, status=status.HTTP_201_CREATED)

class FraudCheckWebhookView(APIView):
    """Internal webhook for payment gateway or rule engine to trigger fraud flags"""
    def post(self, request):
        user_id = request.data.get('user_id')
        reason = request.data.get('reason')
        score = request.data.get('risk_score', 50)
        
        flag = FraudFlag.objects.create(
            user_id=user_id,
            risk_score=score,
            reason=reason,
            status='OPEN'
        )
        
        return Response({"success": True, "flag_id": flag.id})
