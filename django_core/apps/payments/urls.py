from django.urls import path
from .views import (
    InitiatePaymentView, PaymentWebhookView, 
    WalletView, WalletTransactionListView
)

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='payment-initiate'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('wallet/', WalletView.as_view(), name='wallet-detail'),
    path('wallet/transactions/', WalletTransactionListView.as_view(), name='wallet-transactions'),
]
