# permissions.py
from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsUserType(BasePermission):
    allowed_types = []

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_type in self.allowed_types
        )
    # def has_permission(self, request, view):
    #     # First, check if the user is authenticated
    #     if not request.user.is_authenticated:
    #         self.message = "Authentication required."
    #         return False

    #     # Then check if the user's type is in the allowed types
    #     if request.user.user_type not in self.allowed_types:
    #         self.message = f"User type {request.user.user_type} not allowed."
    #         return False
        
        # return True

class IsAdmin(IsUserType):
    allowed_types = ['ADMIN']
    message = "Admin access required."

class IsManager(IsUserType):
    allowed_types = ['MANAGER']
    message = "Manager access required."

class IsStaff(IsUserType):
    allowed_types = ['STAFF']
    message = "Staff access required."

class IsAdminOrManager(IsUserType):
    allowed_types = ['ADMIN', 'MANAGER']
    message = "Admin or Manager access required."

# class IsOwner(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return obj.visiting_to == request.user

# class IsAdminOrManagerOrOwner(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return (request.user.user_type in ['ADMIN', 'MANAGER']) or (obj.visiting_to == request.user)

# class IsAllowedUserType(BasePermission):
#     def has_permission(self, request, view):
#         return (
#             IsStaff().has_permission(request, view) or
#             IsAdmin().has_permission(request, view) or
#             IsAdminOrManager().has_permission(request, view) or
#             IsAdminOrManagerOrOwner().has_permission(request, view) or
#             IsManager().has_permission(request, view) or
#             IsOwner().has_permission(request, view)
#         )
# class IsAllowedUserType(BasePermission):
#     def has_permission(self, request, view):
#         if not request.user.is_authenticated:
#             return False
#         allowed_types = ['ADMIN', 'MANAGER', 'STAFF']
#         return request.user.user_type in allowed_types or IsOwner().has_object_permission(request, view, None)
class IsHost(IsUserType):
    def has_object_permission(self, request, view, obj):
        if not super().has_permission(request, view):  # Check authentication and user type if needed
            return False
        return obj.visiting_to == request.user
    
class IsAdminOrManagerOrHost(IsUserType):
    allowed_types = ['ADMIN', 'MANAGER']

    def has_object_permission(self, request, view, obj):
        if not super().has_permission(request, view):  # Check authentication and if user type matches
            return False
        return obj.visiting_to == request.user or request.user.user_type in self.allowed_types
    
class IsAllowedUserType(IsUserType):
    allowed_types = ['ADMIN', 'MANAGER', 'STAFF']

    def has_permission(self, request, view):
        # Check authentication and allowed user types from IsUserType
        if not super().has_permission(request, view):
            return False
        
        return (
            IsStaff().has_permission(request, view) or
            IsAdmin().has_permission(request, view) or
            IsAdminOrManager().has_permission(request, view) or
            IsAdminOrManagerOrHost().has_permission(request, view) or
            IsManager().has_permission(request, view) or
            IsHost().has_permission(request, view)
        )
    # class IsAllowedUserType(BasePermission):
    #     def has_permission(self, request, view):
    #         if not request.user.is_authenticated:
    #             return False
    #         allowed_types = ['ADMIN', 'MANAGER', 'STAFF']
    #         return request.user.user_type in allowed_types or IsHost().has_object_permission(request, view, None)