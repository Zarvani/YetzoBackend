import uuid
import random
import string
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import SupportTicket, SupportMessage
from .serializers import SupportTicketSerializer, SupportMessageSerializer

def generate_ticket_number():
    return 'TK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class TicketListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupportTicketSerializer

    def get_queryset(self):
        return SupportTicket.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            customer=self.request.user,
            ticket_number=generate_ticket_number()
        )

class TicketDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupportTicketSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return SupportTicket.objects.filter(customer=self.request.user)


class TicketMessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupportMessageSerializer

    def get_queryset(self):
        ticket_id = self.kwargs['ticket_id']
        return SupportMessage.objects.filter(ticket_id=ticket_id, ticket__customer=self.request.user, is_internal_note=False)

    def perform_create(self, serializer):
        ticket_id = self.kwargs['ticket_id']
        ticket = SupportTicket.objects.get(id=ticket_id, customer=self.request.user)
        serializer.save(
            ticket=ticket,
            sender=self.request.user,
            is_internal_note=False
        )
