from django.urls import path
from .views import TicketListCreateView, TicketDetailView, TicketMessageListCreateView

urlpatterns = [
    path('tickets/', TicketListCreateView.as_view(), name='ticket-list'),
    path('tickets/<uuid:id>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('tickets/<uuid:ticket_id>/messages/', TicketMessageListCreateView.as_view(), name='ticket-messages'),
]
