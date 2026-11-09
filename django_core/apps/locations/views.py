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

class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

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
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
