from rest_framework import viewsets, permissions
from .models import CMSPage, Banner, Blog, SEOMetadata
from .serializers import (
    CMSPageSerializer,
    BannerSerializer,
    BlogSerializer,
    SEOMetadataSerializer
)

class CMSPageViewSet(viewsets.ModelViewSet):
    queryset = CMSPage.objects.filter(status='PUBLISHED')
    serializer_class = CMSPageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.filter(is_active=True).order_by('display_order')
    serializer_class = BannerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.filter(status='PUBLISHED')
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
