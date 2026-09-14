"""
API v1 Staff Role Permissions
=============================
Defines standard Django REST Framework permission classes:
- IsCMSStaffUser: Baseline verification of active WSSP CMS access
- IsHeadOffice: Grants access to head-office level actions / cross-zonal reports
- IsZonalManager: Zonal manager or Head Office
- IsDepartmentManager: Departmental manager (SWM, WS, SDS) or higher
"""

from rest_framework.permissions import BasePermission
from .base import get_user_role_context, get_user_allowed_location_ids


class IsCMSStaffUser(BasePermission):
    """
    Ensures the user is authenticated, active, and has at least one
    authorized WSSP location permission.
    """
    message = "Access denied. You do not have active WSSP CMS permissions."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        if user.is_superuser:
            return True
        allowed_ids = get_user_allowed_location_ids(user)
        return len(allowed_ids) > 0


class IsHeadOffice(BasePermission):
    """
    Allows access only to Head Office officers or Superusers.
    """
    message = "Access restricted to Head Office administration."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        ctx = get_user_role_context(user)
        return ctx["is_head_office"]


class IsZonalManager(BasePermission):
    """
    Allows access to Zonal Managers or Head Office staff.
    """
    message = "Access restricted to Zonal Managers or Head Office."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        ctx = get_user_role_context(user)
        return ctx["is_zonal_manager"] or ctx["is_head_office"]


class IsDepartmentManager(BasePermission):
    """
    Allows access to Department Managers (SWM, WS, SDS) or higher.
    """
    message = "Access restricted to Departmental Managers or higher."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_active):
            return False
        ctx = get_user_role_context(user)
        return (
            ctx["is_department_manager"]
            or ctx["is_zonal_manager"]
            or ctx["is_head_office"]
        )
