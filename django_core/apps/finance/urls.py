from django.urls import path
from .views import InvoiceDetailView, ProfessionalEarningsListView, ProfessionalPayoutRequestView

urlpatterns = [
    path('invoices/<uuid:id>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('earnings/', ProfessionalEarningsListView.as_view(), name='professional-earnings'),
    path('payouts/request/', ProfessionalPayoutRequestView.as_view(), name='request-payout'),
]
