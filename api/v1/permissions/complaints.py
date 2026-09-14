"""
API v1 Complaint Object-Level Permissions
=========================================
Guarantees object-level access security on specific complaint instances:
- CanViewComplaint: Officer can view complaint only if it matches their zone & department
- CanUpdateComplaint: Officer can update complaint only within their zone & department
- CanResolveComplaint: Officer can mark complaint resolved/closed within their jurisdiction
"""

from rest_framework.permissions import BasePermission
from .base import get_user_role_context, get_user_allowed_location_ids


class CanViewComplaint(BasePermission):
    """
    Object-level permission: Verifies that the complaint falls within
    the officer's assigned zone and department.
    """
    message = "You do not have permission to view this complaint."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        ctx = get_user_role_context(user)

        # Head office can view any complaint within their locations
        if ctx["is_head_office"]:
            loc_ids = ctx["allowed_location_ids"]
            if not loc_ids:
                return True
            return obj.location_id in loc_ids

        # Check location matches
        if obj.location_id not in ctx["allowed_location_ids"]:
            return False

        # If department manager, complaint type must match
        if ctx["is_department_manager"] and ctx["department_type_ids"]:
            return obj.complaint_type_id in ctx["department_type_ids"]

        # Zonal manager can view all complaint types in their zone
        return True


class CanUpdateComplaint(BasePermission):
    """
    Object-level permission: Only authorized zonal or departmental managers
    for this complaint's zone/dept can add responses or update details.
    """
    message = "You do not have permission to update or modify this complaint."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active)

    def has_object_permission(self, request, view, obj):
        # Update follows the exact same jurisdictional boundary as CanView
        return CanViewComplaint().has_object_permission(request, view, obj)


class CanResolveComplaint(BasePermission):
    """
    Object-level permission: Resolving complaints requires valid
    departmental or zonal management jurisdiction.
    """
    message = "You do not have permission to mark this complaint as resolved."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True

        ctx = get_user_role_context(user)
        if ctx["is_head_office"] or ctx["is_zonal_manager"] or ctx["is_department_manager"]:
            return CanViewComplaint().has_object_permission(request, view, obj)

        return False
