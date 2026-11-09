from django.urls import path
from .views import (
    AddressListCreateView, 
    AddressDetailView,
    CityListCreateView,
    CityDetailView,
    ZoneListCreateView,
    ZoneDetailView,
)

urlpatterns = [
    path('cities/', CityListCreateView.as_view(), name='city-list-create'),
    path('cities/<uuid:id>/', CityDetailView.as_view(), name='city-detail'),
    path('zones/', ZoneListCreateView.as_view(), name='zone-list-create'),
    path('zones/<uuid:id>/', ZoneDetailView.as_view(), name='zone-detail'),
    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<uuid:id>/', AddressDetailView.as_view(), name='address-detail'),
]
