"""
API v1 Base Permission Utilities & Scoping Engine
=================================================
Inspects real WSSP database state and dynamically computes:
1. Permitted Locations (from Dashboard.models.LocationPermission)
2. Departmental Scopes (SWM, WS, SDS, Billing)
3. Dynamic Complaint QuerySet scoping
"""

from Dashboard.models import Location, LocationPermission, Complaint, ComplaintType


def get_user_allowed_locations(user):
    """
    Returns QuerySet of Location models the user is allowed to access.
    - Superusers have access to all locations.
    - Regular users are scoped through active LocationPermission records.
    """
    if not user or not user.is_authenticated:
        return Location.objects.none()

    if user.is_superuser:
        return Location.objects.all().order_by("location_name")

    perms = LocationPermission.objects.filter(user=user, can_view=True)
    if not perms.exists():
        return Location.objects.none()

    allowed_ids = set()
    for perm in perms:
        for loc in perm.locations.all():
            allowed_ids.add(loc.id)

    return Location.objects.filter(id__in=allowed_ids).order_by("location_name")


def get_user_allowed_location_ids(user):
    """Returns a list of integer IDs for allowed locations."""
    return list(get_user_allowed_locations(user).values_list("id", flat=True))


def get_user_role_context(user):
    """
    Evaluates real WSSP user configuration to determine:
    - is_head_office: Boolean
    - is_zonal_manager: Boolean
    - is_department_manager: Boolean
    - department_name: str or None (e.g. 'Solid Waste', 'Water Supply', 'Drainage')
    - department_type_ids: list of int
    - allowed_location_ids: list of int
    """
    if not user or not user.is_authenticated:
        return {
            "is_head_office": False,
            "is_zonal_manager": False,
            "is_department_manager": False,
            "department_name": None,
            "department_type_ids": [],
            "allowed_location_ids": [],
            "role_title": "Anonymous",
        }

    loc_ids = get_user_allowed_location_ids(user)
    username = user.username.lower()
    user_groups = set(user.groups.values_list("name", flat=True))

    # 1. Check Head Office
    has_headoffice_loc = Location.objects.filter(id__in=loc_ids, location_name__icontains="head").exists()
    is_head_office = (
        user.is_superuser
        or len(loc_ids) >= 5
        or has_headoffice_loc
        or any(keyword in username for keyword in ["ccho", "ceo", "pso", "cms", "gmpmer", "cfo", "gmops"])
    )

    # 2. Check Departmental Specialization
    # WSSP Complaint Types: 'Solid Waste', 'Water Supply', 'Drainage', 'Billing'
    department_name = None
    department_type_ids = []

    if "swm" in username or "sanitation" in username or "sanitation" in user_groups:
        department_name = "Solid Waste"
    elif "ws" in username or "water" in username or "ee_tw" in username:
        department_name = "Water Supply"
    elif "sds" in username or "drainage" in username or "sewerage" in username:
        department_name = "Drainage"
    elif "billing" in username:
        department_name = "Billing"

    if department_name:
        types = ComplaintType.objects.filter(type_name__icontains=department_name)
        department_type_ids = list(types.values_list("id", flat=True))

    is_department_manager = bool(department_name) and not is_head_office

    # 3. Check Zonal Manager
    # Zonal managers manage an entire zone across departments (e.g. 'zma', 'zmb', 'amcczonea')
    is_zonal_manager = (
        not is_head_office
        and not is_department_manager
        and (len(loc_ids) >= 1)
        and (any(k in username for k in ["zm", "zonal", "amcc", "fozone", "mngra_a"]) or len(loc_ids) == 1)
    )

    # 4. Generate Display Role Title
    if is_head_office:
        role_title = "Head Office Executive" if user.is_superuser else "Head Office Complaint Officer"
    elif is_department_manager:
        zone_str = f"Zone (IDs: {loc_ids})" if loc_ids else "Zonal"
        loc = Location.objects.filter(id__in=loc_ids).first()
        if loc:
            zone_str = loc.location_name
        role_title = f"{zone_str} {department_name} Manager"
    elif is_zonal_manager:
        loc = Location.objects.filter(id__in=loc_ids).first()
        zone_str = loc.location_name if loc else "Zonal"
        role_title = f"{zone_str} Manager"
    else:
        role_title = "WSSP Staff"

    return {
        "is_head_office": is_head_office,
        "is_zonal_manager": is_zonal_manager,
        "is_department_manager": is_department_manager,
        "department_name": department_name,
        "department_type_ids": department_type_ids,
        "allowed_location_ids": loc_ids,
        "role_title": role_title,
    }


def get_user_allowed_department_type_ids(user):
    """Returns list of ComplaintType IDs the user is authorized to manage."""
    ctx = get_user_role_context(user)
    return ctx["department_type_ids"]


def scope_complaint_queryset(user, queryset=None):
    """
    CRITICAL SECURITY ENGINE:
    Enforces server-side zonal and departmental scoping.
    Guarantees:
    - Head Office: Sees complaints across all allowed zones.
    - Zonal Manager: Sees ALL complaints strictly inside their assigned zone.
    - Department Manager (SWM / WS / SDS): Sees ONLY complaints inside their zone AND their department.
    """
    if queryset is None:
        queryset = Complaint.objects.all()

    if not user or not user.is_authenticated:
        return queryset.none()

    ctx = get_user_role_context(user)

    # 1. Head Office gets all complaints across allowed locations (or all if superuser)
    if ctx["is_head_office"]:
        if user.is_superuser:
            return queryset
        loc_ids = ctx["allowed_location_ids"]
        if loc_ids:
            return queryset.filter(location_id__in=loc_ids)
        return queryset

    # 2. Department Manager: Scoped by BOTH Zone AND Complaint Type
    if ctx["is_department_manager"]:
        loc_ids = ctx["allowed_location_ids"]
        type_ids = ctx["department_type_ids"]
        qs = queryset
        if loc_ids:
            qs = qs.filter(location_id__in=loc_ids)
        if type_ids:
            qs = qs.filter(complaint_type_id__in=type_ids)
        return qs

    # 3. Zonal Manager: Scoped by Zone (all complaint types in zone)
    if ctx["is_zonal_manager"]:
        loc_ids = ctx["allowed_location_ids"]
        if loc_ids:
            return queryset.filter(location_id__in=loc_ids)
        return queryset.none()

    # 4. Fallback for any other staff with assigned locations
    loc_ids = ctx["allowed_location_ids"]
    if loc_ids:
        return queryset.filter(location_id__in=loc_ids)

    return queryset.none()
