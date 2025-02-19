from .models import Role
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsSuperUser
# from user.pagination import CustomPagination
# from django_filters.rest_framework import DjangoFilterBackend
from .role_serializers import RoleCreateSerializer, RoleListSerializer, RoleDetailSerializer

class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsSuperUser]
    # pagination_class = CustomPagination
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']

    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoleCreateSerializer
        return RoleListSerializer
    
class RoleDetailView(generics.RetrieveUpdateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleDetailSerializer
    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUser]
