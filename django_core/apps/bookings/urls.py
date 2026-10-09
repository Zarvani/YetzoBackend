from django.urls import path
from .views import BookingListCreateView, BookingDetailView, BookingStatusUpdateView

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list-create'),
    path('<uuid:id>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<uuid:id>/status/', BookingStatusUpdateView.as_view(), name='booking-status-update'),
]
