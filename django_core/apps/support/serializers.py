from rest_framework import serializers
from .models import SupportTicket, SupportMessage

class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = '__all__'
        read_only_fields = ('sender', 'created_at')

class SupportTicketSerializer(serializers.ModelSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = '__all__'
        read_only_fields = ('ticket_number', 'customer', 'status', 'created_at', 'updated_at', 'assigned_agent')
