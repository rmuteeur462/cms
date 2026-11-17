"""
API v1 Citizen Permissions
==========================
Enforces access control specifically for public citizen accounts.
Guarantees that staff/superuser credentials cannot be used on citizen
endpoints, and that citizen users cannot access staff endpoints.
"""

from rest_framework.permissions import BasePermission
from api.v1.permissions.base import get_user_allowed_location_ids


class IsCitizenUser(BasePermission):
    """
    Allows access only to authenticated, active citizen accounts.
    Rejects staff, superusers, or any user possessing internal LocationPermission records.
    """
    message = "Access restricted to registered citizen accounts."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False

        # Reject staff or superusers
        if user.is_staff or user.is_superuser:
            return False

        # Reject users possessing internal staff LocationPermission records
        allowed_ids = get_user_allowed_location_ids(user)
        if len(allowed_ids) > 0:
            return False

        return True

