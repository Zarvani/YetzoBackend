from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CMSPageViewSet, BannerViewSet, BlogViewSet

router = DefaultRouter()
router.register(r'pages', CMSPageViewSet, basename='cms-pages')
router.register(r'banners', BannerViewSet, basename='banners')
router.register(r'blogs', BlogViewSet, basename='blogs')

urlpatterns = [
    path('', include(router.urls)),
]
