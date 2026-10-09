from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class ProfessionalProfileView(generics.RetrieveAPIView):
    pass

class ProfessionalDocumentUploadView(generics.CreateAPIView):
    pass

class ProfessionalAvailabilityView(generics.RetrieveUpdateAPIView):
    pass

class AdminProfessionalListView(generics.ListAPIView):
    pass
