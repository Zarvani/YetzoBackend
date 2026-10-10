from rest_framework import serializers
from .models import CMSPage, Banner, Blog, SEOMetadata

class CMSPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSPage
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'

class SEOMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOMetadata
        fields = '__all__'
