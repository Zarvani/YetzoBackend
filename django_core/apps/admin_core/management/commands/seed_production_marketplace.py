import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.cms.models import Banner, CMSPage, Blog
from apps.admin_core.models import Coupon
from apps.locations.models import City, Zone, Area

class Command(BaseCommand):
    help = "Seed real marketplace records: Banners, CMS Policy Pages, Coupons, and Dark-Cluster Zones into PostgreSQL."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting Yetzo production marketplace database seeding..."))

        # ---------------------------------------------------------------------
        # 1. SEED PROMOTIONAL BANNERS
        # ---------------------------------------------------------------------
        banners_data = [
            {
                "title": "Welcome to Yetzo - Flat 50% Off First Chore",
                "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621765/yetzo_seed/banner_welcome_offer.jpg",
                "mobile_image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621765/yetzo_seed/banner_welcome_mobile.jpg",
                "cta_text": "Book in 15 Mins",
                "cta_url": "https://yetzo.com/services",
                "display_order": 1,
                "is_active": True,
            },
            {
                "title": "100% Verified Specialists - 30-Day Happiness Guarantee",
                "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621765/yetzo_seed/banner_safety_guarantee.jpg",
                "mobile_image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621765/yetzo_seed/banner_safety_mobile.jpg",
                "cta_text": "Explore Services",
                "cta_url": "https://yetzo.com/services",
                "display_order": 2,
                "is_active": True,
            },
            {
                "title": "Instant Emergency Electrician & Plumber Dispatch",
                "image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621765/yetzo_seed/banner_emergency_dispatch.jpg",
                "mobile_image_url": "https://res.cloudinary.com/dysg6gvlf/image/upload/v1791621765/yetzo_seed/banner_emergency_mobile.jpg",
                "cta_text": "Get Instant Help",
                "cta_url": "https://yetzo.com/services/home-repairs",
                "display_order": 3,
                "is_active": True,
            },
        ]

        for b in banners_data:
            obj, created = Banner.objects.update_or_create(
                title=b["title"],
                defaults={
                    "image_url": b["image_url"],
                    "mobile_image_url": b["mobile_image_url"],
                    "cta_text": b["cta_text"],
                    "cta_url": b["cta_url"],
                    "display_order": b["display_order"],
                    "is_active": b["is_active"],
                    "start_at": timezone.now(),
                    "end_at": timezone.now() + datetime.timedelta(days=365),
                }
            )
            self.stdout.write(f"  [Banner] {'Created' if created else 'Updated'}: {obj.title}")

        # ---------------------------------------------------------------------
        # 2. SEED OFFICIAL CMS POLICY PAGES
        # ---------------------------------------------------------------------
        pages_data = [
            {
                "title": "About Yetzo Technologies",
                "slug": "about-us",
                "content": (
                    "Yetzo Technologies is India's next-generation on-demand hyperlocal home services "
                    "and rapid chore marketplace. Operating from our headquarters at Priyadarshini Vihar, "
                    "Delhi 110092, Yetzo is engineered to dispatch verified professionals to your doorstep "
                    "in as fast as 15 minutes. From emergency electrical and plumbing repairs to AC maintenance "
                    "and rapid home chores, Yetzo blends high-frequency IoT telemetry with rigorous quality assurance."
                ),
                "seo_title": "About Yetzo - Rapid On-Demand Home Services Platform",
                "seo_description": "Learn about Yetzo's mission to revolutionize on-demand home chores and repair services across India's top metropolitan hubs.",
            },
            {
                "title": "Terms & Conditions of Service",
                "slug": "terms-and-conditions",
                "content": (
                    "These Terms govern your access to the Yetzo customer platform, mobile applications, and "
                    "partner services. By booking a chore through Yetzo, you agree to mutual 4-digit OTP "
                    "verification upon service commencement. Payments are securely held in escrow until the "
                    "service is completed with photo proof verification. Cancellations made prior to partner "
                    "dispatch are 100% refundable without penalty."
                ),
                "seo_title": "Terms & Conditions | Yetzo Marketplace",
                "seo_description": "Review the official Yetzo user agreement, booking terms, and escrow payment guidelines.",
            },
            {
                "title": "Privacy & Data Protection Policy",
                "slug": "privacy-policy",
                "content": (
                    "Yetzo respects your privacy and is committed to protecting your personal information. "
                    "We collect background location data strictly when you are tracking an active en-route "
                    "specialist or broadcasting partner telemetry. We never sell or monetize your location or "
                    "contact data. All financial transactions are processed securely through RBI-compliant payment gateways."
                ),
                "seo_title": "Privacy Policy | Yetzo Safe & Secure",
                "seo_description": "Understand how Yetzo handles your geolocation, account credentials, and transactional privacy.",
            },
            {
                "title": "Cancellation & 100% Refund Policy",
                "slug": "cancellation-refund-policy",
                "content": (
                    "Yetzo offers a transparent 100% refund policy. If you cancel a booking before a professional "
                    "is dispatched, the entire amount is refunded instantly to your original payment method or Yetzo Wallet. "
                    "In the unlikely event of unsatisfactory service quality, our 30-Day Happiness Guarantee entitles you "
                    "to a free re-work or dispute resolution via our operations desk."
                ),
                "seo_title": "Cancellation and Refund Policy | Yetzo Guarantee",
                "seo_description": "Read our 30-day guarantee and cancellation policy for home chore and repair services.",
            },
        ]

        for p in pages_data:
            obj, created = CMSPage.objects.update_or_create(
                slug=p["slug"],
                defaults={
                    "title": p["title"],
                    "content": p["content"],
                    "status": "PUBLISHED",
                    "seo_title": p["seo_title"],
                    "seo_description": p["seo_description"],
                    "published_at": timezone.now(),
                }
            )
            self.stdout.write(f"  [CMS Page] {'Created' if created else 'Updated'}: {obj.slug}")

        # ---------------------------------------------------------------------
        # 3. SEED OFFICIAL MARKETING COUPONS
        # ---------------------------------------------------------------------
        now = timezone.now()
        one_year_later = now + datetime.timedelta(days=365)

        coupons_data = [
            {
                "code": "FIRST50",
                "discount_type": "PERCENTAGE",
                "discount_value": 50,  # 50%
                "min_order_amount": 19900,  # ₹199 in paise
                "max_discount_amount": 15000,  # ₹150 in paise
                "usage_limit": 50000,
                "per_user_limit": 1,
                "new_users_only": True,
            },
            {
                "code": "CHORE15",
                "discount_type": "FIXED",
                "discount_value": 5000,  # Flat ₹50 in paise
                "min_order_amount": 14900,  # ₹149 in paise
                "max_discount_amount": 5000,
                "usage_limit": 100000,
                "per_user_limit": 3,
                "new_users_only": False,
            },
            {
                "code": "YETZOPRO",
                "discount_type": "FIXED",
                "discount_value": 10000,  # Flat ₹100 in paise
                "min_order_amount": 49900,  # ₹499 in paise
                "max_discount_amount": 10000,
                "usage_limit": 50000,
                "per_user_limit": 2,
                "new_users_only": False,
            },
        ]

        for c in coupons_data:
            obj, created = Coupon.objects.update_or_create(
                code=c["code"],
                defaults={
                    "discount_type": c["discount_type"],
                    "discount_value": c["discount_value"],
                    "min_order_amount": c["min_order_amount"],
                    "max_discount_amount": c["max_discount_amount"],
                    "valid_from": now,
                    "valid_until": one_year_later,
                    "usage_limit": c["usage_limit"],
                    "per_user_limit": c["per_user_limit"],
                    "new_users_only": c["new_users_only"],
                    "is_active": True,
                }
            )
            self.stdout.write(f"  [Coupon] {'Created' if created else 'Updated'}: {obj.code}")

        # ---------------------------------------------------------------------
        # 4. SEED MICRO-CLUSTER EXPANSIONS (DELHI NCR)
        # ---------------------------------------------------------------------
        delhi = City.objects.filter(name__icontains="Delhi").first()
        if delhi:
            clusters_data = [
                ("Preet Vihar & Laxmi Nagar Micro-Cluster", "110092"),
                ("Lajpat Nagar & Defence Colony Cluster", "110024"),
                ("Indirapuram & Vaishali Sector Hub", "201014"),
            ]
            for zone_name, pin in clusters_data:
                zone, _ = Zone.objects.get_or_create(
                    city=delhi,
                    name=zone_name,
                    defaults={"is_active": True}
                )
                area, created = Area.objects.get_or_create(
                    zone=zone,
                    name=zone_name,
                    pincode=pin,
                    defaults={"is_active": True}
                )
                self.stdout.write(f"  [Dark Cluster] {'Created' if created else 'Updated'}: {zone_name} ({pin})")

        self.stdout.write(self.style.SUCCESS("All production marketplace seed data successfully populated!"))
