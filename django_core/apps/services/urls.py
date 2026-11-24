from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, SubcategoryListView,
    ServiceListView, ServiceDetailView,
    ServiceQuestionsView, CheckServiceabilityView,
    AdminServiceListCreateView, AdminServiceDetailView,
    SystemPingView
)

urlpatterns = [
    path('system/ping/', SystemPingView.as_view(), name='system-ping'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('services/categories/', CategoryListView.as_view(), name='services-category-list'),
    path('categories/<uuid:id>/', CategoryDetailView.as_view(), name='category-detail-by-id'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('services/categories/<uuid:id>/', CategoryDetailView.as_view(), name='services-category-detail-by-id'),
    path('services/categories/<slug:slug>/', CategoryDetailView.as_view(), name='services-category-detail'),
    path('categories/<uuid:category_id>/subcategories/', SubcategoryListView.as_view(), name='category-subcategories-by-id'),
    path('categories/<slug:category_slug>/subcategories/', SubcategoryListView.as_view(), name='category-subcategories-by-slug'),
    path('services/categories/<uuid:category_id>/subcategories/', SubcategoryListView.as_view(), name='services-category-subcategories-by-id'),
    path('services/categories/<slug:category_slug>/subcategories/', SubcategoryListView.as_view(), name='services-category-subcategories-by-slug'),
    path('subcategories/', SubcategoryListView.as_view(), name='subcategory-list'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/services/', ServiceListView.as_view(), name='services-service-list'),
    path('services/<uuid:id>/', ServiceDetailView.as_view(), name='service-detail-by-id'),
    path('services/<slug:slug>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/<uuid:service_id>/questions/', ServiceQuestionsView.as_view(), name='service-questions'),
    path('serviceability/', CheckServiceabilityView.as_view(), name='check-serviceability'),
    path('admin/services/', AdminServiceListCreateView.as_view(), name='admin-service-list-create'),
    path('services/admin/services/', AdminServiceListCreateView.as_view(), name='services-admin-service-list-create'),
    path('admin/services/<uuid:id>/', AdminServiceDetailView.as_view(), name='admin-service-detail'),
    path('services/admin/services/<uuid:id>/', AdminServiceDetailView.as_view(), name='services-admin-service-detail'),
]
