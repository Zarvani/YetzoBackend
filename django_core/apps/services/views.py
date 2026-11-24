from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Category, Subcategory, Service, ServiceQuestion, ServiceAvailability
from .serializers import (
    CategorySerializer, SubcategorySerializer, ServiceSerializer, ServiceQuestionSerializer
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
        u = self.request.user
        if u.is_staff or u.is_superuser or (hasattr(u, 'role') and u.role and u.role.name in ['ADMIN', 'OPERATIONS_MANAGER']):
            return Service.objects.select_related('category', 'subcategory').prefetch_related('variants', 'addons', 'pricing_rules').order_by('-created_at')
        return Service.objects.none()

class AdminServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        u = self.request.user
        if u.is_staff or u.is_superuser or (hasattr(u, 'role') and u.role and u.role.name in ['ADMIN', 'OPERATIONS_MANAGER']):
            return Service.objects.select_related('category', 'subcategory').prefetch_related('variants', 'addons', 'pricing_rules')
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

    def get_object(self):
        lookup = self.kwargs.get('slug') or self.kwargs.get('id')
        try:
            return Category.objects.get(id=lookup, is_active=True)
        except (Category.DoesNotExist, ValueError, Exception):
            return get_object_or_404(Category.objects.filter(is_active=True), slug=lookup)

class SubcategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        cat_id = self.kwargs.get('category_id') or self.kwargs.get('category_slug')
        qs = Subcategory.objects.filter(is_active=True)
        if cat_id:
            from django.db.models import Q
            qs = qs.filter(Q(category_id=cat_id) | Q(category__slug=cat_id))
        return qs

class ServiceListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    
    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        category_slug = self.request.query_params.get('category', None)
        
        if query:
            # Route to Elasticsearch Fuzzy AI Search Engine with resilient DB fallback
            try:
                search = ServiceDocument.search().query(
                    "multi_match", 
                    query=query, 
                    fields=['name^3', 'description', 'category_name^2'], 
                    fuzziness='AUTO'
                )
                queryset = search.to_queryset().exclude(status='ARCHIVED')
            except Exception:
                from django.db.models import Q
                queryset = Service.objects.filter(
                    Q(name__icontains=query) | Q(description__icontains=query)
                ).exclude(status='ARCHIVED')
        else:
            # Fallback to standard DB if no search term provided
            queryset = Service.objects.exclude(status='ARCHIVED').select_related('category', 'subcategory').prefetch_related('variants', 'addons', 'pricing_rules').order_by('name')
            
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        sub_category = self.request.query_params.get('sub_category', None)
        if sub_category:
            from django.db.models import Q
            queryset = queryset.filter(Q(subcategory_id=sub_category) | Q(subcategory__slug=sub_category))
            
        return queryset

class ServiceDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ServiceSerializer
    queryset = Service.objects.exclude(status='ARCHIVED')

    def get_object(self):
        lookup = self.kwargs.get('slug') or self.kwargs.get('id')
        try:
            return Service.objects.exclude(status='ARCHIVED').get(id=lookup)
        except (Service.DoesNotExist, ValueError, Exception):
            return get_object_or_404(Service.objects.exclude(status='ARCHIVED'), slug=lookup)

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
