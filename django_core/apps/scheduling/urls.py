from django.urls import path
from .views import AvailableSlotsView, ReserveSlotView

urlpatterns = [
    path('available/', AvailableSlotsView.as_view(), name='available-slots'),
    path('reserve/', ReserveSlotView.as_view(), name='reserve-slot'),
]
