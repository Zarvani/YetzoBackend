from django.urls import path
from .views import UpdateFCMTokenView

urlpatterns = [
    path('fcm-token/', UpdateFCMTokenView.as_view(), name='update_fcm_token'),
]
