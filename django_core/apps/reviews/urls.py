from django.urls import path
from .views import ReviewCreateView, WarrantyClaimCreateView, WarrantyClaimListView

urlpatterns = [
    path('create/', ReviewCreateView.as_view(), name='create-review'),
    path('warranty/claim/', WarrantyClaimCreateView.as_view(), name='create-warranty-claim'),
    path('warranty/claims/', WarrantyClaimListView.as_view(), name='list-warranty-claims'),
]
