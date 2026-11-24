from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Address, City, Zone, Area
from .serializers import AddressSerializer, CitySerializer, ZoneSerializer, AreaSerializer

class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.all().order_by('name')
    serializer_class = CitySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        from django.core.cache import cache
        cache_key = "yetzo_active_cities_v1"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            from rest_framework.response import Response
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        if response.status_code == 200:
            cache.set(cache_key, response.data, timeout=3600)
        return response

    def perform_create(self, serializer):
        from django.core.cache import cache
        cache.delete("yetzo_active_cities_v1")
        serializer.save()

class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        from django.core.cache import cache
        cache.delete("yetzo_active_cities_v1")
        serializer.save()

    def perform_destroy(self, instance):
        from django.core.cache import cache
        cache.delete("yetzo_active_cities_v1")
        instance.delete()

class ZoneListCreateView(generics.ListCreateAPIView):
    serializer_class = ZoneSerializer

    def get_queryset(self):
        qs = Zone.objects.all().select_related('city').order_by('name')
        city_id = self.request.query_params.get('city_id')
        if city_id:
            qs = qs.filter(city_id=city_id)
        return qs

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class ZoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).select_related('city', 'area')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
