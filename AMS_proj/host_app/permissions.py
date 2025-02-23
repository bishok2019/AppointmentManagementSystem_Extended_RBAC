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
        user_roles = request.user.role.all()
        if not user_roles:
            return False
        
        for role in user_roles:
            if role.permissions.filter(code=required_permission).exists():
                return True
            return False
            
        # return user_role.permissions.filter(code=required_permission).exists()

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser