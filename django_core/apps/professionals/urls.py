from django.urls import path
from .views import (
    ProfessionalProfileView, ProfessionalDocumentUploadView, ProfessionalAvailabilityView,
    AdminProfessionalListView, AdminProfessionalDetailView, ProfessionalStatusToggleView, ProfessionalLocationUpdateView,
    ProfessionalPendingJobsView, ProfessionalActiveJobsView, ProfessionalSkillsView,
    AdminProfessionalKYCUpdateView, AdminDocumentVerifyView
)

urlpatterns = [
    path('me/', ProfessionalProfileView.as_view(), name='professional-me'),
    path('me/status/', ProfessionalStatusToggleView.as_view(), name='professional-status'),
    path('me/location/', ProfessionalLocationUpdateView.as_view(), name='professional-location'),
    path('jobs/pending/', ProfessionalPendingJobsView.as_view(), name='professional-jobs-pending'),
    path('jobs/active/', ProfessionalActiveJobsView.as_view(), name='professional-jobs-active'),
    path('me/documents/', ProfessionalDocumentUploadView.as_view(), name='professional-documents'),
    path('me/availability/', ProfessionalAvailabilityView.as_view(), name='professional-availability'),
    path('me/skills/', ProfessionalSkillsView.as_view(), name='professional-skills'),
    path('<uuid:id>/kyc/', AdminProfessionalKYCUpdateView.as_view(), name='admin-professional-kyc'),
    path('<uuid:id>/documents/<uuid:doc_id>/verify/', AdminDocumentVerifyView.as_view(), name='admin-document-verify'),
    path('<uuid:id>/', AdminProfessionalDetailView.as_view(), name='admin-professional-detail'),
    path('', AdminProfessionalListView.as_view(), name='admin-professionals'),
]
