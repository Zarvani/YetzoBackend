from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, MeView, SendOTPView, VerifyOTPView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('otp/send/', SendOTPView.as_view(), name='send_otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify_otp'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]
