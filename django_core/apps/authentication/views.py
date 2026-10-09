from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
import random
import os
from twilio.rest import Client
from .serializers import RegisterSerializer, AuthResponseSerializer, LoginSerializer, UserSerializer

User = get_user_model()

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


class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({"success": False, "error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Store OTP in cache for 5 minutes
        cache.set(f"otp_{phone_number}", otp, timeout=300)

        # Send via Twilio
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        messaging_service_sid = os.environ.get('TWILIO_SERVICE_SID')
        
        try:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                messaging_service_sid=messaging_service_sid,
                body=f"Your Yetzo verification code is {otp}. Do not share this with anyone.",
                to=phone_number
            )
            return Response({"success": True, "message": "OTP sent successfully", "sid": message.sid})
        except Exception as e:
            # Fallback if Twilio fails (e.g. invalid number, unpaid account)
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp_input = request.data.get('otp')
        
        if not phone_number or not otp_input:
            return Response({"success": False, "error": "Phone number and OTP required"}, status=status.HTTP_400_BAD_REQUEST)
            
        cached_otp = cache.get(f"otp_{phone_number}")
        
        if cached_otp and str(cached_otp) == str(otp_input):
            # OTP verified, delete from cache
            cache.delete(f"otp_{phone_number}")
            
            # Find or Create User
            user, created = User.objects.get_or_create(phone_number=phone_number, defaults={
                'username': phone_number,
                'role': 'CUSTOMER' # Default role, can be modified via profile
            })
            
            tokens = get_tokens_for_user(user)
            response_data = {
                **tokens,
                'user': UserSerializer(user).data
            }
            return Response({"success": True, "data": response_data, "is_new_user": created}, status=status.HTTP_200_OK)
            
        return Response({"success": False, "error": "Invalid or expired OTP"}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"success": True, "data": {"user": serializer.data}})
