from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, 
    ServiceListView, ServiceDetailView,
    ServiceQuestionsView, CheckServiceabilityView,
    AdminServiceListCreateView, AdminServiceDetailView,
    SystemPingView
)

urlpatterns = [
    path('system/ping/', SystemPingView.as_view(), name='system-ping'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/<slug:slug>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/<uuid:service_id>/questions/', ServiceQuestionsView.as_view(), name='service-questions'),
    path('serviceability/', CheckServiceabilityView.as_view(), name='check-serviceability'),
    path('admin/services/', AdminServiceListCreateView.as_view(), name='admin-service-list-create'),
    path('admin/services/<uuid:id>/', AdminServiceDetailView.as_view(), name='admin-service-detail'),
]
