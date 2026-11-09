from rest_framework import viewsets, permissions
from .models import CMSPage, Banner, Blog, SEOMetadata
from .serializers import (
    CMSPageSerializer,
    BannerSerializer,
    BlogSerializer,
    SEOMetadataSerializer
)

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or (request.user.role and request.user.role.name in ['ADMIN', 'SUPER_ADMIN', 'CONTENT_MANAGER'])))

class CMSPageViewSet(viewsets.ModelViewSet):
    queryset = CMSPage.objects.filter(status='PUBLISHED')
    serializer_class = CMSPageSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.filter(is_active=True).order_by('display_order')
    serializer_class = BannerSerializer
    permission_classes = [IsAdminOrReadOnly]

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.filter(status='PUBLISHED')
    serializer_class = BlogSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

