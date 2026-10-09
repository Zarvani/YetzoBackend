from django.urls import path
from .views import (
    ProfessionalProfileView, ProfessionalDocumentUploadView, ProfessionalAvailabilityView,
    AdminProfessionalListView
)

urlpatterns = [
    path('me/', ProfessionalProfileView.as_view(), name='professional-me'),
    path('me/documents/', ProfessionalDocumentUploadView.as_view(), name='professional-documents'),
    path('me/availability/', ProfessionalAvailabilityView.as_view(), name='professional-availability'),
    path('', AdminProfessionalListView.as_view(), name='admin-professionals'),
]
