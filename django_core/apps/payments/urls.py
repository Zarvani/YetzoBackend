from django.urls import path
from .views import (
    InitiatePaymentView, PaymentWebhookView, 
    WalletView, WalletTransactionListView,
    RefundListView, RefundProcessView
)

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='payment-initiate'),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('wallet/', WalletView.as_view(), name='wallet-detail'),
    path('wallet/transactions/', WalletTransactionListView.as_view(), name='wallet-transactions'),
    path('refunds/', RefundListView.as_view(), name='refund-list'),
    path('refunds/<uuid:id>/process/', RefundProcessView.as_view(), name='refund-process'),
]
