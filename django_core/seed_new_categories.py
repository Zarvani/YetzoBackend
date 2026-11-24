import os
import sys
import uuid
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils.text import slugify
from apps.services.models import (
    Category, Subcategory, Service, ServiceVariant, ServiceAddon,
    ServiceQuestion, ServiceQuestionOption, ServiceAvailability
)
from apps.pricing.models import ServicePricingRule
from apps.locations.models import City

NEW_CATEGORIES_DATA = [
    {
        "category_name": "Carpentry",
        "slug": "carpentry",
        "icon_name": "carpenter",
        "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80",
        "description": "Professional carpenters for furniture repair, assembly, door locks, drill and hang services.",
        "subcategories": [
            {
                "name": "Furniture Assembly & Repair",
                "slug": "furniture-assembly-repair",
                "services": [
                    {
                        "name": "Bed & Wardrobe Assembly / Repair",
                        "slug": "bed-wardrobe-assembly-repair",
                        "desc": "Professional assembly, hydraulic hinge fixing, channel alignment, and lock fitting for beds and wardrobes.",
                        "starting_price": 399,
                        "duration": 90,
                        "variants": ["Single / Queen Bed", "King Bed / Hydraulic", "2-3 Door Wardrobe", "Sliding Wardrobe"],
                        "addons": [("Hydraulic Shock Pump Replacement", 650, 20), ("Soft-Close Hinge Fitting", 250, 15)],
                        "questions": [("Service required?", ["New Assembly", "Repair / Joint Tightening", "Hinge / Channel Issue"])],
                        "prices": {"Delhi NCR": 399, "Bangalore": 449, "Pune": 349, "Noida": 399, "Greater Noida": 399}
                    },
                    {
                        "name": "Table & Chair Repair",
                        "slug": "table-chair-repair",
                        "desc": "Fixing wobbly legs, loose joints, broken castor wheels, and drawer channel replacements.",
                        "starting_price": 249,
                        "duration": 45,
                        "variants": ["Dining / Study Table", "Office Revolving Chair", "Wooden Chair (Set of 2)"],
                        "addons": [("Heavy Duty Castor Wheel (Set of 5)", 400, 15), ("Drawer Telescopic Channel (Pair)", 350, 20)],
                        "questions": [("Type of repair?", ["Joint tightening / glueing", "Wheel replacement", "Drawer slide repair"])],
                        "prices": {"Delhi NCR": 249, "Bangalore": 299, "Pune": 229, "Noida": 249, "Greater Noida": 249}
                    }
                ]
            },
            {
                "name": "Drill & Hang Services",
                "slug": "drill-hang-services",
                "services": [
                    {
                        "name": "Wall Hangings & Shelf Installation",
                        "slug": "wall-hangings-shelf-installation",
                        "desc": "Precision laser-aligned wall drilling for TV mounts, curtains, photo frames, mirrors, and wall shelves.",
                        "starting_price": 199,
                        "duration": 40,
                        "variants": ["Up to 3 Items", "Up to 6 Items", "Up to 10 Items"],
                        "addons": [("Heavy Duty Anchor Plugs & Screws", 100, 5), ("Curtain Bracket Set", 200, 10)],
                        "questions": [("What are we mounting?", ["Photo frames / Mirrors", "Curtain rods", "Wall shelves / Cabinets"])],
                        "prices": {"Delhi NCR": 199, "Bangalore": 249, "Pune": 179, "Noida": 199, "Greater Noida": 199}
                    }
                ]
            },
            {
                "name": "Doors & Windows",
                "slug": "doors-windows-carpentry",
                "services": [
                    {
                        "name": "Door Lock & Latch Repair / Installation",
                        "slug": "door-lock-latch-repair-installation",
                        "desc": "Installation and servicing of mortise locks, cylindrical knob locks, tower bolts, and magnetic stoppers.",
                        "starting_price": 299,
                        "duration": 50,
                        "variants": ["Main Door Mortise Lock", "Internal Cylindrical Lock", "Sliding Door Latch"],
                        "addons": [("Magnetic Door Stopper", 180, 10), ("Heavy Brass Tower Bolt", 250, 15)],
                        "questions": [("Service type?", ["Install new lock", "Repair existing lock", "Door scraping / alignment"])],
                        "prices": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 269, "Noida": 299, "Greater Noida": 299}
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Water Purifier",
        "slug": "water-purifier",
        "icon_name": "water_drop",
        "image_url": "https://images.unsplash.com/photo-1548839140-29a749e1bc4e?auto=format&fit=crop&w=800&q=80",
        "description": "Comprehensive RO service, membrane replacement, filter kits, and TDS calibration for all top brands.",
        "subcategories": [
            {
                "name": "RO Service & Maintenance",
                "slug": "ro-service-maintenance",
                "services": [
                    {
                        "name": "Comprehensive RO Service",
                        "slug": "comprehensive-ro-service",
                        "desc": "Complete multistage system sanitization, sediment & carbon filter inspection, TDS testing, and membrane flushing.",
                        "starting_price": 349,
                        "duration": 60,
                        "variants": ["Standard RO", "RO + UV + UF", "Alkaline / Copper RO"],
                        "addons": [("Pre-Filter Bowl Service & Spun Candle", 250, 10), ("TDS Reducer Calibration Valve", 350, 15)],
                        "questions": [("Purifier Brand?", ["Kent", "Aquaguard / Eureka Forbes", "Pureit", "Livpure", "Other"])],
                        "prices": {"Delhi NCR": 349, "Bangalore": 399, "Pune": 299, "Noida": 349, "Greater Noida": 349}
                    },
                    {
                        "name": "RO Repair Visit",
                        "slug": "ro-repair-visit",
                        "desc": "Expert diagnostics for low water flow, vibration, continuous beeping, booster pump failure, or bad taste.",
                        "starting_price": 299,
                        "duration": 45,
                        "variants": ["General Diagnostic", "Booster Pump Failure", "Electrical / SMPS Issue"],
                        "addons": [("Replacement SMPS Power Adapter (24V)", 650, 15), ("Solenoid Valve (SV)", 450, 15)],
                        "questions": [("Primary Issue?", ["No water output", "Continuous beep/noise", "Water leaking", "Bad taste/smell"])],
                        "prices": {"Delhi NCR": 299, "Bangalore": 349, "Pune": 259, "Noida": 299, "Greater Noida": 299}
                    }
                ]
            },
            {
                "name": "Filter & Membrane Replacement",
                "slug": "filter-membrane-replacement",
                "services": [
                    {
                        "name": "Complete Filter & Membrane Replacement Kit",
                        "slug": "complete-filter-membrane-replacement-kit",
                        "desc": "100% genuine replacement kit: 80 GPD RO Membrane, Carbon Block, Sediment Filter, and Post-Carbon with 1-year warranty.",
                        "starting_price": 1999,
                        "duration": 75,
                        "variants": ["Standard 80 GPD Kit", "High TDS 100 GPD Kit", "Alkaline Mineralizer Kit"],
                        "addons": [("Copper Cartridge Upgrade", 450, 10), ("Heavy Duty Spun Filter Housing", 400, 15)],
                        "questions": [("Current water source?", ["Borewell (High TDS)", "Treated Municipal Tap", "Tanker Water"])],
                        "prices": {"Delhi NCR": 1999, "Bangalore": 2199, "Pune": 1899, "Noida": 1999, "Greater Noida": 1999}
                    }
                ]
            },
            {
                "name": "Installation & Uninstallation",
                "slug": "ro-installation-uninstallation",
                "services": [
                    {
                        "name": "Water Purifier Installation / Uninstallation",
                        "slug": "water-purifier-installation-uninstallation",
                        "desc": "Secure wall mounting, diverter valve tap connection, food-grade pipe routing, and wastewater drain line setup.",
                        "starting_price": 499,
                        "duration": 60,
                        "variants": ["New RO Installation", "RO Uninstallation Only", "Uninstallation + Reinstallation"],
                        "addons": [("Extra Food Grade Pipe (5m)", 150, 5), ("Brass Diverter Valve", 250, 10)],
                        "questions": [("Wall type?", ["Tiled kitchen wall", "Concrete / Plastered", "Under-sink setup"])],
                        "prices": {"Delhi NCR": 499, "Bangalore": 549, "Pune": 449, "Noida": 499, "Greater Noida": 499}
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Home Moving",
        "slug": "home-moving",
        "icon_name": "local_shipping",
        "image_url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80",
        "description": "Professional packers and movers for seamless local house shifting, outstation relocation, and mini-moves.",
        "subcategories": [
            {
                "name": "Within City Relocation (Local)",
                "slug": "within-city-relocation",
                "services": [
                    {
                        "name": "Complete Home Shifting (1-3 BHK)",
                        "slug": "complete-home-shifting",
                        "desc": "End-to-end relocation: multi-layer bubble & corrugated wrapping, loading, dedicated container truck, transport, unloading, and furniture reassembly.",
                        "starting_price": 3999,
                        "duration": 360,
                        "variants": ["1 BHK Complete", "2 BHK Complete", "3 BHK Complete", "4 BHK / Villa"],
                        "addons": [("Wardrobe Carton Box (Per unit)", 300, 0), ("Fragile Crockery Foam Box", 400, 0)],
                        "questions": [("Floors & Lift?", ["Lift available at both ends", "No lift at pickup (stairs)", "No lift at delivery"])],
                        "prices": {"Delhi NCR": 3999, "Bangalore": 4499, "Pune": 3699, "Noida": 3999, "Greater Noida": 3999}
                    },
                    {
                        "name": "Few Items / Mini Move (Tata Ace / Pickup)",
                        "slug": "mini-move-few-items",
                        "desc": "Economical transport for single appliances (fridge, washing machine, sofa) or up to 10 moving boxes.",
                        "starting_price": 1499,
                        "duration": 120,
                        "variants": ["1-3 Heavy Items", "4-8 Medium Items", "Up to 15 Boxes"],
                        "addons": [("Helper for Loading/Unloading (Per person)", 500, 0), ("Bubble Wrap Layer", 250, 0)],
                        "questions": [("Heavy appliances included?", ["Yes (Fridge/Washing Machine)", "Furniture Only", "Only Cartons"])],
                        "prices": {"Delhi NCR": 1499, "Bangalore": 1699, "Pune": 1399, "Noida": 1499, "Greater Noida": 1499}
                    }
                ]
            },
            {
                "name": "Inter-City Relocation (Outstation)",
                "slug": "inter-city-relocation",
                "services": [
                    {
                        "name": "Outstation Relocation with Transit Insurance",
                        "slug": "outstation-relocation-transit-insurance",
                        "desc": "Inter-city container movement with customized 5-layer export packaging, real-time GPS tracking, and comprehensive transit insurance coverage.",
                        "starting_price": 8999,
                        "duration": 480,
                        "variants": ["1 BHK Inter-City", "2 BHK Inter-City", "3 BHK Inter-City"],
                        "addons": [("Wood Crating for TV & Electronics", 800, 0), ("Vehicle Transportation (Bike/Car)", 3500, 0)],
                        "questions": [("Estimated moving date?", ["Within 3 Days", "Within 1-2 Weeks", "This Month"])],
                        "prices": {"Delhi NCR": 8999, "Bangalore": 9999, "Pune": 8499, "Noida": 8999, "Greater Noida": 8999}
                    }
                ]
            },
            {
                "name": "Packing & Unpacking Services",
                "slug": "packing-unpacking-services",
                "services": [
                    {
                        "name": "Professional Packing Assistance",
                        "slug": "professional-packing-assistance",
                        "desc": "Certified packing crew equipped with heavy-duty carton boxes, bubble wrap, stretch film, edge protectors, and barcode labelling.",
                        "starting_price": 999,
                        "duration": 180,
                        "variants": ["Kitchen & Fragile Only", "Single Room Full Pack", "Full House Packing"],
                        "addons": [("Bundle of 10 Heavy Boxes", 600, 0), ("Air Bubble Roll (50m)", 500, 0)],
                        "questions": [("What needs packaging?", ["Fragile Glassware / Kitchen", "Books & Wardrobe", "Everything"])],
                        "prices": {"Delhi NCR": 999, "Bangalore": 1199, "Pune": 899, "Noida": 999, "Greater Noida": 999}
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Pest Control",
        "slug": "pest-control",
        "icon_name": "pest_control",
        "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80",
        "description": "Government-approved, odorless, and pet-friendly pest eradication for cockroaches, termites, bed bugs, and rodents.",
        "subcategories": [
            {
                "name": "Cockroach & Ant Control",
                "slug": "cockroach-ant-control",
                "services": [
                    {
                        "name": "Intense Cockroach & Ant Gel Treatment",
                        "slug": "intense-cockroach-ant-gel-treatment",
                        "desc": "Bayer Maxforce odorless gel dots placed in hinge corners and cracks, combined with micro-emulsion chemical barrier along skirting.",
                        "starting_price": 699,
                        "duration": 45,
                        "variants": ["1 BHK", "2 BHK", "3 BHK", "4 BHK / Villa"],
                        "addons": [("Drainage Larvicide & Sanitizer", 200, 10), ("Kitchen Cabinet Dusting Treatment", 250, 15)],
                        "questions": [("Severity level?", ["Mild (occasional sighting)", "Heavy (daytime sightings in kitchen)"])],
                        "prices": {"Delhi NCR": 699, "Bangalore": 749, "Pune": 649, "Noida": 699, "Greater Noida": 699}
                    }
                ]
            },
            {
                "name": "Termite & Bed Bug Control",
                "slug": "termite-bed-bug-control",
                "services": [
                    {
                        "name": "Anti-Termite Drill-Fill-Seal Treatment",
                        "slug": "anti-termite-drill-fill-seal-treatment",
                        "desc": "Drilling 12mm holes at skirting junctions, injecting Premise (Imidacloprid) termiticide under pressure, and sealing with matching chalk. Includes 2-year warranty.",
                        "starting_price": 1799,
                        "duration": 120,
                        "variants": ["1 BHK Termite Protection", "2 BHK Termite Protection", "3 BHK Termite Protection"],
                        "addons": [("Wooden Wardrobe Drill & Injection", 500, 30), ("Door Frame Termite Barrier", 350, 20)],
                        "questions": [("Visible damage?", ["Mud tubes on walls", "Hollow wooden doors/cabinets", "Preventive treatment"])],
                        "prices": {"Delhi NCR": 1799, "Bangalore": 1999, "Pune": 1699, "Noida": 1799, "Greater Noida": 1799}
                    },
                    {
                        "name": "Bed Bug Thermal & Chemical Eradication",
                        "slug": "bed-bug-thermal-chemical-eradication",
                        "desc": "High-temperature steam treatment on mattresses followed by specialized contact insecticide spray across bed frames and crevices. (Includes 2 visits).",
                        "starting_price": 1199,
                        "duration": 90,
                        "variants": ["1 Bedroom (1 Bed)", "2 Bedrooms (2 Beds)", "3 Bedrooms (3 Beds)"],
                        "addons": [("Mattress Encasement Cover", 650, 0), ("Living Room Sofa Treatment", 400, 20)],
                        "questions": [("Beds infested?", ["Single Bed only", "Multiple Bedrooms", "Living Room Couch too"])],
                        "prices": {"Delhi NCR": 1199, "Bangalore": 1299, "Pune": 1099, "Noida": 1199, "Greater Noida": 1199}
                    }
                ]
            },
            {
                "name": "Rodent & Mosquito Control",
                "slug": "rodent-mosquito-control",
                "services": [
                    {
                        "name": "Rodent Trapping & Entry-Point Sealing",
                        "slug": "rodent-trapping-entry-point-sealing",
                        "desc": "Tamper-proof bait stations, industrial glue pads, and wire mesh sealing of drain pipes and wall intrusions.",
                        "starting_price": 599,
                        "duration": 60,
                        "variants": ["Standard Home Pack", "Villa / Large Estate"],
                        "addons": [("Extra Heavy Duty Glue Pad (Pair)", 150, 0), ("Stainless Steel Wire Mesh Patch", 200, 15)],
                        "questions": [("Location of activity?", ["Kitchen / False Ceiling", "Balcony / Utility", "Whole House"])],
                        "prices": {"Delhi NCR": 599, "Bangalore": 649, "Pune": 549, "Noida": 599, "Greater Noida": 599}
                    }
                ]
            }
        ]
    },
    {
        "category_name": "Painting & Waterproofing",
        "slug": "painting-waterproofing",
        "icon_name": "format_paint",
        "image_url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=800&q=80",
        "description": "Premium interior & exterior painting with Asian Paints/Berger, laser measurement, and crystalline waterproofing.",
        "subcategories": [
            {
                "name": "Full Home Painting",
                "slug": "full-home-painting",
                "services": [
                    {
                        "name": "Interior Home Repainting",
                        "slug": "interior-home-repainting",
                        "desc": "Complete wall prep: masking floors, crack filling, two coats of primer, sanding, and two coats of premium luxury emulsion.",
                        "starting_price": 5999,
                        "duration": 480,
                        "variants": ["1 BHK Fresh / Repaint", "2 BHK Fresh / Repaint", "3 BHK Fresh / Repaint"],
                        "addons": [("Ceiling Painting Addon (Per Room)", 800, 60), ("Washable Anti-Fungal Royale Sheen Upgrade", 1500, 0)],
                        "questions": [("Current wall condition?", ["Good (just color change)", "Cracks & peeling paint", "Severe dampness / seepage"])],
                        "prices": {"Delhi NCR": 5999, "Bangalore": 6499, "Pune": 5499, "Noida": 5999, "Greater Noida": 5999}
                    },
                    {
                        "name": "Single Room / Accent Wall Painting",
                        "slug": "single-room-accent-wall-painting",
                        "desc": "Feature wall makeover with designer metallic stencils, textures (Royale Play), or single bedroom color refreshment.",
                        "starting_price": 1499,
                        "duration": 180,
                        "variants": ["Single Accent Wall", "Complete Single Bedroom", "Kids Theme Room"],
                        "addons": [("Stencil Design Pattern", 500, 30), ("Metallic Gold / Silver Finish", 400, 0)],
                        "questions": [("Finish preference?", ["Matte", "Silky Sheen / Satin", "Texture / Stencil"])],
                        "prices": {"Delhi NCR": 1499, "Bangalore": 1699, "Pune": 1399, "Noida": 1499, "Greater Noida": 1499}
                    }
                ]
            },
            {
                "name": "Waterproofing & Damp Treatment",
                "slug": "waterproofing-damp-treatment",
                "services": [
                    {
                        "name": "Ceiling & Wall Leakage Crystalline Waterproofing",
                        "slug": "ceiling-wall-leakage-waterproofing",
                        "desc": "Moisture meter thermal imaging, scraping efflorescence, applying deep crystalline penetrating barrier, and waterproof polymer putty.",
                        "starting_price": 1999,
                        "duration": 150,
                        "variants": ["Up to 50 Sq Ft Patch", "Up to 100 Sq Ft Patch", "Bathroom External Seepage"],
                        "addons": [("Epoxy Tile Grouting (Bathroom Floor)", 800, 60), ("Anti-Efflorescence Salt Barrier", 400, 30)],
                        "questions": [("Source of dampness?", ["Bathroom back wall", "Ceiling seepage from above", "External balcony wall"])],
                        "prices": {"Delhi NCR": 1999, "Bangalore": 2199, "Pune": 1899, "Noida": 1999, "Greater Noida": 1999}
                    }
                ]
            }
        ]
    }
]

def seed_database():
    print("=== SEEDING NEW HOME MARKETPLACE CATEGORIES ===")
    cities = list(City.objects.all())
    city_map = {c.name: c for c in cities}
    print(f"Loaded {len(cities)} cities from DB.")

    created_cats = 0
    created_subcats = 0
    created_services = 0
    created_rules = 0

    for cat_data in NEW_CATEGORIES_DATA:
        cat, c_created = Category.objects.get_or_create(
            slug=cat_data["slug"],
            defaults={
                "name": cat_data["category_name"],
                "icon_name": cat_data.get("icon_name", ""),
                "image_url": cat_data.get("image_url", ""),
                "description": cat_data.get("description", ""),
                "is_active": True,
                "sort_order": 10 + created_cats
            }
        )
        if c_created:
            created_cats += 1
            print(f"[CATEGORY CREATED] {cat.name}")
        else:
            cat.name = cat_data["category_name"]
            cat.icon_name = cat_data.get("icon_name", "")
            cat.image_url = cat_data.get("image_url", "")
            cat.description = cat_data.get("description", "")
            cat.is_active = True
            cat.save()
            print(f"[CATEGORY UPDATED] {cat.name}")

        for sc_data in cat_data["subcategories"]:
            sc, sc_created = Subcategory.objects.get_or_create(
                slug=sc_data["slug"],
                defaults={
                    "category": cat,
                    "name": sc_data["name"],
                    "is_active": True
                }
            )
            if sc_created:
                created_subcats += 1
                print(f"  [SUBCATEGORY CREATED] {sc.name}")
            else:
                sc.category = cat
                sc.name = sc_data["name"]
                sc.is_active = True
                sc.save()

            for s_data in sc_data["services"]:
                s, s_created = Service.objects.get_or_create(
                    slug=s_data["slug"],
                    defaults={
                        "category": cat,
                        "subcategory": sc,
                        "name": s_data["name"],
                        "description": s_data["desc"],
                        "starting_price": s_data["starting_price"],
                        "status": "ACTIVE",
                        "supports_instant": True,
                        "supports_scheduled": True,
                        "estimated_duration_minutes": s_data.get("duration", 60),
                        "warranty_days": 30
                    }
                )
                if s_created:
                    created_services += 1
                    print(f"    * [SERVICE CREATED] {s.name} (₹{s.starting_price})")
                else:
                    s.category = cat
                    s.subcategory = sc
                    s.name = s_data["name"]
                    s.description = s_data["desc"]
                    s.starting_price = s_data["starting_price"]
                    s.status = "ACTIVE"
                    s.supports_instant = True
                    s.supports_scheduled = True
                    s.estimated_duration_minutes = s_data.get("duration", 60)
                    s.warranty_days = 30
                    s.save()
                    print(f"    * [SERVICE UPDATED] {s.name}")

                # Variants
                for v_name in s_data.get("variants", []):
                    ServiceVariant.objects.get_or_create(
                        service=s,
                        name=v_name,
                        defaults={"is_active": True}
                    )

                # Addons
                for addon_tuple in s_data.get("addons", []):
                    a_name = addon_tuple[0]
                    a_dur = addon_tuple[2] if len(addon_tuple) > 2 else 0
                    ServiceAddon.objects.get_or_create(
                        service=s,
                        name=a_name,
                        defaults={"duration_minutes": a_dur, "is_active": True}
                    )

                # Questions & Options
                for q_tuple in s_data.get("questions", []):
                    q_text = q_tuple[0]
                    q_opts = q_tuple[1]
                    q, _ = ServiceQuestion.objects.get_or_create(
                        service=s,
                        question_text=q_text,
                        defaults={"question_type": "RADIO", "is_required": True}
                    )
                    for opt_val in q_opts:
                        ServiceQuestionOption.objects.get_or_create(
                            question=q,
                            label=opt_val,
                            defaults={"value": slugify(opt_val)}
                        )

                # Availabilities across all cities
                for city in cities:
                    ServiceAvailability.objects.get_or_create(
                        service=s,
                        city=city,
                        zone=None,
                        defaults={"is_active": True}
                    )

                # Pricing Rules across defined cities
                prices = s_data.get("prices", {})
                for city_name, price_val in prices.items():
                    if city_name in city_map:
                        target_city = city_map[city_name]
                        rule, r_created = ServicePricingRule.objects.get_or_create(
                            service=s,
                            city=target_city,
                            variant=None,
                            defaults={
                                "pricing_type": "FIXED",
                                "base_price": price_val,
                                "is_active": True
                            }
                        )
                        if not r_created:
                            rule.base_price = price_val
                            rule.is_active = True
                            rule.save()
                        created_rules += 1

    print("\n" + "="*50)
    print("NEW CATEGORIES SEED COMPLETE:")
    print(f"Categories Processed: {len(NEW_CATEGORIES_DATA)}")
    print(f"Total Subcategories: {created_subcats}")
    print(f"Total Services: {created_services}")
    print(f"Pricing Rules Configured: {created_rules}")
    print("="*50)

if __name__ == "__main__":
    seed_database()

