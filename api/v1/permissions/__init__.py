"""
API v1 Permissions Package
==========================
Defines role-based and object-level permission classes for WSSP CMS:
- base: Core location and department scoping utilities
- staff: Role checks (IsHeadOffice, IsZonalManager, IsDepartmentManager)
- complaints: Action permissions (CanViewComplaint, CanUpdateComplaint, CanResolveComplaint)
"""

from .base import (
    get_user_role_context,
    get_user_allowed_locations,
    get_user_allowed_location_ids,
    get_user_allowed_department_type_ids,
    scope_complaint_queryset,
)
from .staff import (
    IsCMSStaffUser,
    IsHeadOffice,
    IsZonalManager,
    IsDepartmentManager,
)
from .citizen import (
    IsCitizenUser,
)
from .complaints import (
    CanViewComplaint,
    CanUpdateComplaint,
    CanResolveComplaint,
)

__all__ = [
    "get_user_role_context",
    "get_user_allowed_locations",
    "get_user_allowed_location_ids",
    "get_user_allowed_department_type_ids",
    "scope_complaint_queryset",
    "IsCMSStaffUser",
    "IsCitizenUser",
    "IsHeadOffice",
    "IsZonalManager",
    "IsDepartmentManager",
    "CanViewComplaint",
    "CanUpdateComplaint",
    "CanResolveComplaint",
]
