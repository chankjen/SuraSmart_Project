"""Role-based access control permissions and utilities."""
from rest_framework import permissions
from functools import wraps


class IsFamilyMember(permissions.BasePermission):
    """Allow access only to Family Member users."""
    message = 'Only Family Members can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'family_member'
        )


class IsPoliceOfficer(permissions.BasePermission):
    """Allow access only to Police Officer users."""
    message = 'Only Police Officers can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'police_officer'
        )


class IsGovernmentOfficial(permissions.BasePermission):
    """Allow access only to Government Official users."""
    message = 'Only Government Officials can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'government_official'
        )


class IsAuthenticated(permissions.BasePermission):
    """Allow access only to authenticated users."""
    message = 'You must be authenticated to access this resource.'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsPoliceOrGovernment(permissions.BasePermission):
    """Allow access to Police Officers and Government Officials."""
    message = 'Only Police Officers and Government Officials can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['police_officer', 'government_official']
        )


class IsGovernmentOrAdmin(permissions.BasePermission):
    """Allow access to Government Officials and Admins."""
    message = 'Only Government Officials and Administrators can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.role == 'government_official' or request.user.is_staff)
        )


# Role definitions
ROLE_PERMISSIONS = {
    'family_member': {
        'can_report_missing_person': True,
        'can_upload_image': True,
        'can_view_own_cases': True,
        'can_verify_matches': False,
        'can_access_all_cases': False,
        'can_modify_other_cases': False,
    },
    'police_officer': {
        'can_report_missing_person': True,
        'can_upload_image': True,
        'can_view_own_cases': True,
        'can_verify_matches': True,
        'can_access_all_cases': True,
        'can_modify_other_cases': True,
    },
    'government_official': {
        'can_report_missing_person': True,
        'can_upload_image': True,
        'can_view_own_cases': True,
        'can_verify_matches': True,
        'can_access_all_cases': True,
        'can_modify_other_cases': True,
    },
    'admin': {
        'can_report_missing_person': True,
        'can_upload_image': True,
        'can_view_own_cases': True,
        'can_verify_matches': True,
        'can_access_all_cases': True,
        'can_modify_other_cases': True,
    },
}


def get_user_permissions(user):
    """Get permissions for a user based on their role."""
    if user.is_staff:
        role = 'admin'
    else:
        role = getattr(user, 'role', 'family_member')
    
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS['family_member'])


def require_role(*roles):
    """Decorator to require specific roles for a view function."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                from rest_framework.response import Response
                return Response(
                    {'detail': 'Authentication required.'},
                    status=401
                )
            
            user_role = getattr(request.user, 'role', 'family_member')
            if user_role not in roles:
                from rest_framework.response import Response
                return Response(
                    {'detail': f'This action requires one of these roles: {", ".join(roles)}'},
                    status=403
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
