from django.urls import path
from .views import PermissionCategoryListCreateView, PermissionCategoryDetailView
from .role_views import RoleListCreateView, RoleDetailView


urlpatterns = [
    path('role/', RoleListCreateView.as_view(), name='role-list-create'),
    path('role/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
    path('permissioncategory/', PermissionCategoryListCreateView.as_view(), name='permissioncategory-list-create'),
    path('permissioncategory/<int:pk>/', PermissionCategoryDetailView.as_view(), name='permissioncategory-detail'), 
]