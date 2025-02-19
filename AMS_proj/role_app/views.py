from .permission_serializers import PermissionCategoryCreateSerializer, PermissionCategoryListSerializer, PermissionCategoryDetailSerializer
from .models import PermissionCategory
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSuperUser
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from user.pagination import CustomPagination
# from django_filters.rest_framework import DjangoFilterBackend

class PermissionCategoryListCreateView(generics.ListCreateAPIView):
    queryset = PermissionCategory.objects.all()
    filterset_fields = ['is_active']
    search_fields = ['name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PermissionCategoryCreateSerializer
        return PermissionCategoryListSerializer

class PermissionCategoryDetailView(generics.RetrieveUpdateAPIView):
    queryset = PermissionCategory.objects.all()
    serializer_class = PermissionCategoryDetailSerializer
    permission_classes = [IsSuperUser]

