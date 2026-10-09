import uuid
from django.db import models
from apps.locations.models import City, Zone

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'subcategories'
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return f"{self.category.name} > {self.name}"


class Service(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('COMING_SOON', 'Coming Soon'),
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('TEMPORARILY_DISABLED', 'Temporarily Disabled'),
        ('ARCHIVED', 'Archived'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='services')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='services')
    
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField()
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='DRAFT')
    
    # UI Display Fields
    image_url = models.URLField(blank=True, null=True)
    starting_price = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    reviews_count = models.IntegerField(default=0)
    
    # Booking configuration
    supports_instant = models.BooleanField(default=False)
    supports_scheduled = models.BooleanField(default=True)
    supports_recurring = models.BooleanField(default=False)
    
    # Duration and Warranty
    estimated_duration_minutes = models.IntegerField(default=60)
    warranty_days = models.IntegerField(default=0)
    cancellation_allowed = models.BooleanField(default=True)
    
    # SEO
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services'

    def __str__(self):
        return self.name


class ServiceVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100) # e.g. Split AC, Window AC
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'service_variants'

    def __str__(self):
        return f"{self.service.name} - {self.name}"


class ServiceAddon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='addons')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'service_addons'

    def __str__(self):
        return self.name


class ServiceQuestion(models.Model):
    QUESTION_TYPES = (
        ('RADIO', 'Radio'),
        ('CHECKBOX', 'Checkbox'),
        ('DROPDOWN', 'Dropdown'),
        ('TEXT', 'Text'),
        ('NUMBER', 'Number'),
        ('YES_NO', 'Yes/No'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='questions')
    variant = models.ForeignKey(ServiceVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='specific_questions')
    
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=True)
    conditional_logic = models.JSONField(blank=True, null=True) # Used to show this question only if another answer matches
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'service_questions'
        ordering = ['sort_order']

    def __str__(self):
        return self.question_text


class ServiceQuestionOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(ServiceQuestion, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=150)
    value = models.CharField(max_length=150)
    
    class Meta:
        db_table = 'service_question_options'

    def __str__(self):
        return f"{self.question.question_text} - {self.label}"


class ServiceAvailability(models.Model):
    """
    Controls which services are available in which cities/zones.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='availabilities')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='service_availabilities')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True, blank=True, related_name='service_availabilities')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'service_availability'
        unique_together = ('service', 'city', 'zone')

class ServicePackage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    package_price = models.BigIntegerField()
    original_price = models.BigIntegerField()
    discount_amount = models.BigIntegerField(default=0)
    duration_minutes = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ServicePackageItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ServiceVariant, on_delete=models.SET_NULL, null=True, blank=True)
    addon = models.ForeignKey(ServiceAddon, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price_snapshot = models.BigIntegerField(default=0)
