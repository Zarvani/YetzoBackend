from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Category, Service, ServiceQuestion, ServiceAvailability
from .serializers import (
    CategorySerializer, ServiceSerializer, ServiceQuestionSerializer
)
from apps.locations.models import City, Zone
from rest_framework.permissions import IsAuthenticated
from .documents import ServiceDocument

class SystemPingView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"status": "ok", "message": "YETZO Core Systems Online", "version": "1.0.0"})

class AdminServiceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        if self.request.user.role and self.request.user.role.name == 'ADMIN':
            return Service.objects.all().order_by('-created_at')
        return Service.objects.none()

class AdminServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        if self.request.user.role and self.request.user.role.name == 'ADMIN':
            return Service.objects.all()
        return Service.objects.none()

class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)

class CategoryDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)
    lookup_field = 'slug'

class ServiceListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        category_slug = self.request.query_params.get('category', None)
        
        if query:
            # Route to Elasticsearch Fuzzy AI Search Engine
            search = ServiceDocument.search().query(
                "multi_match", 
                query=query, 
                fields=['name^3', 'description', 'category_name^2'], 
                fuzziness='AUTO'
            )
            # Convert elasticsearch Results to standard Django QuerySet for the serializer
            queryset = search.to_queryset().exclude(status='ARCHIVED')
        else:
            # Fallback to standard DB if no search term provided
            queryset = Service.objects.exclude(status='ARCHIVED')
            
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        return queryset

class ServiceDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    queryset = Service.objects.exclude(status='ARCHIVED')
    lookup_field = 'slug'

class ServiceQuestionsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServiceQuestionSerializer
    
    def get_queryset(self):
        service_id = self.kwargs['service_id']
        return ServiceQuestion.objects.filter(service_id=service_id)

class CheckServiceabilityView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        service_id = request.data.get('service_id')
        city_id = request.data.get('city_id')
        zone_id = request.data.get('zone_id', None)
        
        if not service_id or not city_id:
            return Response({"success": False, "error": {"message": "service_id and city_id are required"}}, status=status.HTTP_400_BAD_REQUEST)
        
        availability = ServiceAvailability.objects.filter(
            service_id=service_id, 
            city_id=city_id, 
            is_active=True
        )
        
        if zone_id:
            availability = availability.filter(zone_id=zone_id)
            
        is_serviceable = availability.exists()
        
        return Response({
            "success": True,
            "data": {
                "serviceable": is_serviceable,
                "instant_available": True if is_serviceable else False, # Will tie to professional availability later
                "scheduled_available": True if is_serviceable else False
            }
        })
