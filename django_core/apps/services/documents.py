from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Service

@registry.register_document
class ServiceDocument(Document):
    # Map the category name as a string field for fuzzy searching
    category_name = fields.TextField(attr='category.name')
    
    class Index:
        # Name of the Elasticsearch index
        name = 'services'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}
                    
    class Django:
        model = Service # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
            'description',
            'slug',
        ]
