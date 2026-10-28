from rest_framework import serializers
from .models import Role, Permission, User

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ('id', 'name', 'description', 'created_at', 'user_count')

    def get_user_count(self, obj):
        return obj.user_set.count()

class UserAdminSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone', 'email', 'first_name', 'last_name', 'role', 'role_name', 'is_active', 'is_staff', 'date_joined')
