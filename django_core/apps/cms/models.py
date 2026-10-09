from django.db import models
import uuid

class CMSPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    status = models.CharField(max_length=20, default='DRAFT')
    
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    canonical_url = models.URLField(null=True, blank=True)
    
    published_at = models.DateTimeField(null=True, blank=True)

class Banner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    image_url = models.URLField()
    mobile_image_url = models.URLField(null=True, blank=True)
    cta_text = models.CharField(max_length=100, null=True, blank=True)
    cta_url = models.URLField(null=True, blank=True)
    
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField()
    content = models.TextField()
    cover_image = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=20, default='DRAFT')

class SEOMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    keywords = models.TextField(null=True, blank=True)
    schema_json = models.JSONField(null=True, blank=True)
