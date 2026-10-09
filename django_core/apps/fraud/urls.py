from django.urls import path
from .views import ReportSafetyIncidentView, FraudCheckWebhookView

urlpatterns = [
    path('incidents/report/', ReportSafetyIncidentView.as_view(), name='report-incident'),
    path('webhooks/check/', FraudCheckWebhookView.as_view(), name='fraud-webhook'),
]
