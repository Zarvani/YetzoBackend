from django.urls import path
from .views import AddressListCreateView, AddressDetailView

urlpatterns = [
    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<uuid:id>/', AddressDetailView.as_view(), name='address-detail'),
]
