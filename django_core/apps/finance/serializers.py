from rest_framework import serializers
from .models import Invoice, ProfessionalEarning, ProfessionalPayout

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class ProfessionalEarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalEarning
        fields = '__all__'

class ProfessionalPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalPayout
        fields = '__all__'
