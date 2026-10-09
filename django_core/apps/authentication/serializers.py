from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = ('id', 'role')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('phone', 'email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class AuthResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        password = attrs.get('password')

        if not (email or phone):
            raise serializers.ValidationError("Must include either 'email' or 'phone'.")

        return attrs
