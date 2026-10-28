from django.urls import path
from .views import UpdateFCMTokenView, RoleListCreateView, RoleDetailView, UserAdminListView

urlpatterns = [
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<uuid:id>/', RoleDetailView.as_view(), name='role-detail'),
    path('admin/list/', UserAdminListView.as_view(), name='user-admin-list'),
    path('fcm-token/', UpdateFCMTokenView.as_view(), name='update_fcm_token'),
]
