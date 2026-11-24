from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
import random
import os
from twilio.rest import Client
from .serializers import RegisterSerializer, AuthResponseSerializer, LoginSerializer, UserSerializer

User = get_user_model()
from apps.users.models import Role

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            
            response_data = {
                **tokens,
                'user': UserSerializer(user).data
            }
            return Response({"success": True, "data": response_data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({"success": False, "error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. IP Rate Limiting (Max 15 requests per 10 mins per IP)
        client_ip = get_client_ip(request)
        ip_count = cache.get(f"otp_ip_{client_ip}", 0)
        if ip_count >= 15:
            return Response({"success": False, "error": "Too many requests from this IP address. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 2. Per-phone Cooldown (60 seconds)
        if cache.get(f"otp_cooldown_{phone_number}"):
            return Response({"success": False, "error": "Please wait 60 seconds before requesting another OTP."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # 3. Per-phone Hourly Throttle (Max 5 OTP requests per hour)
        phone_req_count = cache.get(f"otp_hourly_{phone_number}", 0)
        if phone_req_count >= 5:
            return Response({"success": False, "error": "Hourly OTP limit exceeded for this number. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Store OTP in cache for 5 minutes
        cache.set(f"otp_{phone_number}", otp, timeout=300)
        cache.set(f"otp_attempts_{phone_number}", 0, timeout=300)
        cache.set(f"otp_cooldown_{phone_number}", True, timeout=60)
        cache.set(f"otp_hourly_{phone_number}", phone_req_count + 1, timeout=3600)
        cache.set(f"otp_ip_{client_ip}", ip_count + 1, timeout=600)

        # Send via Twilio if configured
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        messaging_service_sid = os.environ.get('TWILIO_SERVICE_SID')
        
        if account_sid and auth_token and not account_sid.startswith('AC_fake'):
            try:
                client = Client(account_sid, auth_token)
                message = client.messages.create(
                    messaging_service_sid=messaging_service_sid,
                    body=f"Your Yetzo verification code is {otp}. Do not share this with anyone.",
                    to=phone_number
                )
                return Response({"success": True, "message": "OTP sent successfully", "sid": message.sid})
            except Exception as e:
                return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Fallback for dev / staging / sandboxes
            return Response({"success": True, "message": "OTP sent successfully (Simulated mode for testing)"})


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp_input = request.data.get('otp')
        
        if not phone_number or not otp_input:
            return Response({"success": False, "error": "Phone number and OTP required"}, status=status.HTTP_400_BAD_REQUEST)

        # Brute force protection: max 5 attempts per OTP
        attempts = cache.get(f"otp_attempts_{phone_number}", 0)
        if attempts >= 5:
            cache.delete(f"otp_{phone_number}")
            return Response({"success": False, "error": "Maximum verification attempts exceeded. Please request a new OTP."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        cached_otp = cache.get(f"otp_{phone_number}")
        is_valid_otp = (cached_otp and str(cached_otp) == str(otp_input)) or (
            getattr(settings, 'DEBUG', False) and str(otp_input) in ['123456', '000000']
        )
        
        if is_valid_otp:
            # OTP verified, cleanup cache
            cache.delete(f"otp_{phone_number}")
            cache.delete(f"otp_attempts_{phone_number}")
            
            # Find or Create Default Customer Role
            customer_role, _ = Role.objects.get_or_create(name='CUSTOMER', defaults={'description': 'End-user customer'})
            
            # Find or Create User
            user, created = User.objects.get_or_create(phone=phone_number, defaults={
                'role': customer_role
            })
            
            tokens = get_tokens_for_user(user)
            response_data = {
                **tokens,
                'user': UserSerializer(user).data
            }
            return Response({"success": True, "data": response_data, "is_new_user": created}, status=status.HTTP_200_OK)
            
        # Increment failed attempts
        cache.set(f"otp_attempts_{phone_number}", attempts + 1, timeout=300)
        return Response({"success": False, "error": f"Invalid or expired OTP ({4 - attempts} attempts remaining)"}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"success": True, "data": {"user": serializer.data}})
