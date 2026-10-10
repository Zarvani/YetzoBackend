import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
settings.ELASTICSEARCH_DSL_AUTOSYNC = False

from django.contrib.gis.geos import Polygon

from apps.locations.models import City, Zone, Area
from apps.services.models import Category, Subcategory, Service, ServiceVariant, ServiceAddon, ServiceQuestion, ServiceQuestionOption, ServiceAvailability
from apps.pricing.models import ServicePricingRule, AddonPricing, QuestionOptionPricing, TaxRule
from apps.cms.models import Banner

print("Starting Yetzo Platform Seeding...")

# 1. Locations
print("Seeding Locations...")
cities_data = ['Delhi NCR', 'Bangalore', 'Pune', 'Noida', 'Greater Noida']
cities = {}
for c in cities_data:
    city, _ = City.objects.get_or_create(name=c, defaults={'state': 'State', 'country': 'India', 'is_active': True})
    cities[c] = city

# Delhi Zones
delhi_south, _ = Zone.objects.get_or_create(city=cities['Delhi NCR'], name="South Delhi", defaults={'is_active': True})
delhi_gurgaon, _ = Zone.objects.get_or_create(city=cities['Delhi NCR'], name="Gurgaon", defaults={'is_active': True})

# Noida & Greater Noida Zones
noida_sec18, _ = Zone.objects.get_or_create(city=cities['Noida'], name="Sector 18", defaults={'is_active': True})
greater_noida_alpha, _ = Zone.objects.get_or_create(city=cities['Greater Noida'], name="Alpha 1", defaults={'is_active': True})

# Bangalore Zones
blr_koramangala, _ = Zone.objects.get_or_create(city=cities['Bangalore'], name="Koramangala", defaults={'is_active': True})
blr_whitefield, _ = Zone.objects.get_or_create(city=cities['Bangalore'], name="Whitefield", defaults={'is_active': True})

# Pune Zones
pune_viman, _ = Zone.objects.get_or_create(city=cities['Pune'], name="Viman Nagar", defaults={'is_active': True})
pune_kothrud, _ = Zone.objects.get_or_create(city=cities['Pune'], name="Kothrud", defaults={'is_active': True})

# Mock Boundary (Polygon for a bounding box)
dummy_poly = Polygon.from_bbox((77.0, 28.0, 77.5, 28.5))

areas_data = [
    (delhi_south, "Hauz Khas", "110016"),
    (delhi_gurgaon, "DLF Phase 4", "122002"),
    (noida_sec18, "Sector 18 Market", "201301"),
    (greater_noida_alpha, "Alpha 1 Commercial", "201310"),
    (blr_koramangala, "1st Block", "560034"),
    (pune_viman, "Kalyani Nagar", "411014"),
]
for zone, name, pin in areas_data:
    Area.objects.get_or_create(zone=zone, name=name, defaults={'pincode': pin, 'boundary': dummy_poly, 'is_active': True})

# 2. Tax Rules
print("Seeding Tax Rules...")
standard_tax, _ = TaxRule.objects.get_or_create(name="Standard 18% GST", defaults={'cgst_percent': 9, 'sgst_percent': 9, 'igst_percent': 18})

# 3. Categories & Services
print("Seeding Massive Service Catalog...")
from seed_data import CATALOG_DATA
import random

for c_idx, cat_dict in enumerate(CATALOG_DATA):
    c_name = cat_dict['category_name']
    c_img = cat_dict['image_url']
    cat, _ = Category.objects.update_or_create(
        name=c_name, 
        defaults={'slug': c_name.lower().replace(' ', '-'), 'image_url': c_img, 'sort_order': c_idx}
    )
    
    for subcat_dict in cat_dict['subcategories']:
        sub_name = subcat_dict['name']
        subcat, _ = Subcategory.objects.update_or_create(
            category=cat, name=sub_name, 
            defaults={'slug': sub_name.lower().replace(' ', '-')}
        )
        
        for srv_dict in subcat_dict['services']:
            srv_name = srv_dict['name']
            srv_slug = srv_name.lower().replace(' ', '-').replace('/', '-')
            
            srv, _ = Service.objects.update_or_create(
                slug=srv_slug,
                defaults={
                    'category': cat,
                    'subcategory': subcat,
                    'name': srv_name,
                    'description': srv_dict['desc'],
                    'status': 'PUBLISHED',
                    'image_url': c_img,
                    'starting_price': srv_dict['price']['Delhi NCR'],
                    'rating': round(random.uniform(4.5, 4.9), 1),
                    'reviews_count': random.randint(100, 5000),
                    'estimated_duration_minutes': srv_dict['duration']
                }
            )
            
            # Pricing rules
            for city_name, base_price in srv_dict['price'].items():
                ServicePricingRule.objects.update_or_create(
                    service=srv, city=cities[city_name],
                    defaults={'pricing_type': 'FIXED', 'base_price': base_price, 'minimum_price': base_price}
                )
                
            # Variants
            for var_name in srv_dict['variants']:
                ServiceVariant.objects.update_or_create(
                    service=srv, name=var_name, 
                    defaults={'description': "Standard option"}
                )
                
            # Addons
            for addon_name, addon_price, addon_dur in srv_dict['addons']:
                addon, _ = ServiceAddon.objects.update_or_create(
                    service=srv, name=addon_name, 
                    defaults={'duration_minutes': addon_dur}
                )
                for city_name in ['Delhi NCR', 'Bangalore', 'Pune', 'Noida', 'Greater Noida']:
                    AddonPricing.objects.update_or_create(
                        addon=addon, city=cities[city_name], 
                        defaults={'price': addon_price}
                    )
            
            # Questions
            for q_idx, (q_text, opts) in enumerate(srv_dict['questions']):
                q, _ = ServiceQuestion.objects.update_or_create(
                    service=srv, question_text=q_text, 
                    defaults={'question_type': 'SINGLE_CHOICE', 'sort_order': q_idx}
                )
                for opt_text in opts:
                    ServiceQuestionOption.objects.update_or_create(
                        question=q, label=opt_text, 
                        defaults={'value': opt_text.lower().replace(' ', '-')}
                    )
                    
            # Availability
            for city_name in ['Delhi NCR', 'Bangalore', 'Pune', 'Noida', 'Greater Noida']:
                for zone in Zone.objects.filter(city=cities[city_name]):
                    ServiceAvailability.objects.update_or_create(service=srv, city=cities[city_name], zone=zone)


# Banners
print("Seeding Banners...")
Banner.objects.update_or_create(
    title="Summer AC Sale",
    defaults={
        'image_url': 'https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621780/yetzo_seed/e8adnq5qn3rkgd6jkx2o.jpg',
        'cta_text': 'Book Now',
        'cta_url': '/service/split-ac-deep-clean',
        'display_order': 1,
        'is_active': True
    }
)
Banner.objects.update_or_create(
    title="Deep Cleaning Festival",
    defaults={
        'image_url': 'https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621768/yetzo_seed/rkxfewrcu9h1j3yehu6a.jpg',
        'cta_text': 'Explore',
        'cta_url': '/service/intense-home-deep-cleaning',
        'display_order': 2,
        'is_active': True
    }
)
print("Database Seeding Completed Successfully! The MASSIVE complete catalog is now live!")
