from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/', include('apps.services.urls')),
    path('api/v1/bookings/', include('apps.bookings.urls')),
    path('api/v1/professionals/', include('apps.professionals.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/support/', include('apps.support.urls')),
    path('api/v1/reviews/', include('apps.reviews.urls')),
    path('api/v1/locations/', include('apps.locations.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/scheduling/', include('apps.scheduling.urls')),
    path('api/v1/finance/', include('apps.finance.urls')),
    path('api/v1/fraud/', include('apps.fraud.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/pricing/', include('apps.pricing.urls')),
    path('api/v1/carts/', include('apps.carts.urls')),
    path('api/v1/admin-core/', include('apps.admin_core.urls')),
    path('api/v1/cms/', include('apps.cms.urls')),
]
