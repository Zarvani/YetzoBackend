from django.urls import path
from .views import UserNotificationsListView, MarkNotificationReadView, InternalSendNotificationView

urlpatterns = [
    path('me/', UserNotificationsListView.as_view(), name='my-notifications'),
    path('<uuid:id>/read/', MarkNotificationReadView.as_view(), name='read-notification'),
    path('internal/send/', InternalSendNotificationView.as_view(), name='internal-send'),
]
