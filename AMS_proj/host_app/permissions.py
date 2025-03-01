from rest_framework.permissions import BasePermission
from role_app.models import Role

class HasRolePermission(BasePermission):
    """
    Requires role-based permission for access
    """
    def has_permission(self, request, view):
        required_permission = getattr(view, 'required_permission', None)
        
        if not request.user.is_authenticated:
            return False
        #This enable superuser to bypass any role from client side.    
        # if request.user.is_superuser:
        #     return False

        if not required_permission:
            return True
        #Get all roles for the user
        # user_roles = request.user.role.all()
        # if not user_roles:
        #     return False
        
        # for role in user_roles:
        #     if role.permissions.filter(code=required_permission).exists():
        #         return True
        
        # Fetch roles and their permissions in a single query
        user_roles = request.user.role.prefetch_related('permissions').all()
        if not user_roles:
            return False
            
        # Check if any role has the required permission
        for role in user_roles:
            if any(permission.code == required_permission for permission in role.permissions.all()):
                return True
        return False
    
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser