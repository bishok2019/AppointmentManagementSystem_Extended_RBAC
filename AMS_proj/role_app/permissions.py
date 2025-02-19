from rest_framework.permissions import BasePermission
from.models import Permission
class IsSuperUser(BasePermission):
    """
    To check user is superuser or not
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)

class HasPermission(BasePermission):
    """
    Custom permission class to check if a user has the required permission.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Extract the required permission from the view
        required_permission = getattr(view, 'required_permission', None)

        if not required_permission:
            return True # If no specific permission is required, allow access
        
        # Check if user has the required permission
        user_permissions = set(request.user.role.permissions.values_list('code', flat=True))
        return required_permission in user_permissions
        