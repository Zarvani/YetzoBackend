import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, phone=None, email=None, password=None, **extra_fields):
        if not phone and not email:
            raise ValueError(_('Users must have either a phone number or an email address'))
        
        email = self.normalize_email(email) if email else None
        user = self.model(phone=phone, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email=email, password=password, **extra_fields)


class Role(models.Model):
    """
    Role-Based Access Control (RBAC) System
    SUPER_ADMIN, ADMIN, OPERATIONS_MANAGER, DISPATCHER, CUSTOMER_SUPPORT,
    FINANCE, SERVICE_MANAGER, MARKETING_MANAGER, CONTENT_MANAGER,
    KYC_MANAGER, PROFESSIONAL_MANAGER, ANALYST, CUSTOMER, PROFESSIONAL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'roles'
        
    def __str__(self):
        return self.name


class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codename = models.CharField(max_length=100, unique=True) # e.g. 'service.create'
    description = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'permissions'

    def __str__(self):
        return self.codename


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'role_permissions'
        unique_together = ('role', 'permission')


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True, related_name='users')
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # Required for Django Admin
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email or self.phone or str(self.id)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default='en')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'


class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255)
    device_type = models.CharField(max_length=50) # iOS, Android, Web
    fcm_token = models.TextField(blank=True, null=True)
    last_active = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_devices'
        unique_together = ('user', 'device_id')


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_sessions')
    refresh_token_jti = models.UUIDField(unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'sessions'
