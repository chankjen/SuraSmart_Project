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
# Role definitions with enhanced security/privacy flags (TRD §4.2)
ROLE_PERMISSIONS = {
    'family_member': {
        'can_report_missing_person': True,
        'can_upload_image': True,
        'can_view_own_cases': True,
        'can_follow_up_case': True,
        'can_confirm_closure': True,  # Requires dual-signature with Police
        'can_view_match_details': False, # Only see status 'Match Found', not raw data until verified
        'can_access_all_cases': False,
        'can_modify_other_cases': False,
        'requires_mfa': True,
        'data_visibility': 'own_pii_only'
    },
    'police_officer': {
        'can_report_missing_person': True,
        'can_upload_image': True,
        'can_view_assigned_cases': True,
        'can_execute_ai_search': True,
        'can_verify_matches': True,
        'can_update_case_status': True,
        'can_view_family_contact': True, # For coordination
        'can_access_all_cases': False, # Only jurisdiction-specific
        'can_modify_other_cases': False,
        'requires_mfa': True,
        'data_visibility': 'operational_need'
    },
    'government_official': {
        'can_report_missing_person': False,
        'can_upload_image': False,
        'can_view_own_cases': False,
        'can_view_all_cases': True, # Read-only oversight
        'can_view_reports': True,
        'can_verify_matches': False,
        'can_access_all_cases': True,
        'can_modify_other_cases': False,
        'requires_mfa': True,
        'data_visibility': 'aggregated_anonymized' # PII masked unless escalated
    },
    'admin': {
        'can_manage_users': True,
        'can_system_config': True,
        'can_view_audit_logs': True,
        'can_access_all_cases': False, # Separation of duties: Admin should not interfere with cases
        'can_modify_other_cases': False,
        'requires_mfa': True,
        'data_visibility': 'system_metadata_only'
    }
}


def anonymize_pii(data, user):
    """
    Anonymize PII based on user role and data visibility rules (TRD §5.2).
    """
    permissions = get_user_permissions(user)
    visibility = permissions.get('data_visibility', 'system_metadata_only')
    
    if visibility == 'aggregated_anonymized':
        # Mask names and exact locations
        if isinstance(data, dict):
            if 'full_name' in data:
                data['full_name'] = data['full_name'][0] + '***'
            if 'last_seen_location' in data:
                data['last_seen_location'] = 'REDACTED'
    elif visibility == 'system_metadata_only':
        # Return only IDs and status
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if k in ['id', 'status', 'jurisdiction']}
            
    return data


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
