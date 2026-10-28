from django.urls import path
from .views import (
    ProfessionalProfileView, ProfessionalDocumentUploadView, ProfessionalAvailabilityView,
    AdminProfessionalListView, ProfessionalStatusToggleView, ProfessionalLocationUpdateView,
    ProfessionalPendingJobsView, ProfessionalActiveJobsView
)

urlpatterns = [
    path('me/', ProfessionalProfileView.as_view(), name='professional-me'),
    path('me/status/', ProfessionalStatusToggleView.as_view(), name='professional-status'),
    path('me/location/', ProfessionalLocationUpdateView.as_view(), name='professional-location'),
    path('jobs/pending/', ProfessionalPendingJobsView.as_view(), name='professional-jobs-pending'),
    path('jobs/active/', ProfessionalActiveJobsView.as_view(), name='professional-jobs-active'),
    path('me/documents/', ProfessionalDocumentUploadView.as_view(), name='professional-documents'),
    path('me/availability/', ProfessionalAvailabilityView.as_view(), name='professional-availability'),
    path('', AdminProfessionalListView.as_view(), name='admin-professionals'),
]
