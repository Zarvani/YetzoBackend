import uuid
from django.contrib.gis.db import models
from django.conf import settings

class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cities'
        verbose_name_plural = 'Cities'

    def __str__(self):
        return f"{self.name}, {self.state}"


class Zone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'zones'
        unique_together = ('city', 'name')

    def __str__(self):
        return f"{self.name} - {self.city.name}"


class Area(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='areas')
    name = models.CharField(max_length=150)
    pincode = models.CharField(max_length=20)
    boundary = models.PolygonField(null=True, blank=True, help_text="Geospatial boundary for this area")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'areas'

    def __str__(self):
        return f"{self.name} ({self.pincode})"


class Address(models.Model):
    ADDRESS_TYPES = (
        ('HOME', 'Home'),
        ('WORK', 'Work'),
        ('OTHER', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='addresses', null=True, blank=True)
    
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='HOME')
    house_flat = models.CharField(max_length=100)
    building = models.CharField(max_length=150, blank=True, null=True)
    street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    
    # Redundant/Direct fields in case area isn't strictly defined
    pincode = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    
    location = models.PointField(null=True, blank=True, help_text="Exact GPS coordinates for geospatial routing")
    
    instructions = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'addresses'

    def __str__(self):
        return f"{self.house_flat}, {self.street} - {self.address_type}"
