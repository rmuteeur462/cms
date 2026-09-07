"""
WSSP Complaint Management System (CMS) — Authentication & Security Layer
Provides JWT-based authentication, user profile extraction, and strict server-side
LocationPermission enforcement for mobile & web clients.
"""
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from Dashboard.models import Location, LocationPermission, UserViewPermission, Complaint


def get_user_allowed_locations(user):
    """
    Core security rule: Server-side location resolution.
    Returns a QuerySet of Location objects that the user is permitted to view.
    Superusers can view all locations.
    Regular staff are restricted strictly to their LocationPermission records.
    """
    if not user or not user.is_authenticated:
        return Location.objects.none()

    if user.is_superuser:
        return Location.objects.all().order_by('location_name')

    # Query all active LocationPermission rules for this user
    user_perms = LocationPermission.objects.filter(user=user, can_view=True)
    if not user_perms.exists():
        return Location.objects.none()

    # Extract distinct location IDs
    allowed_loc_ids = set()
    for perm in user_perms:
        for loc in perm.locations.all():
            allowed_loc_ids.add(loc.id)

    return Location.objects.filter(id__in=allowed_loc_ids).order_by('location_name')


def get_user_allowed_location_ids(user):
    """Returns a list of integer IDs for allowed locations."""
    return list(get_user_allowed_locations(user).values_list('id', flat=True))


def get_user_cms_profile(user):
    """
    Extracts a rich, mobile-ready profile including role title and permitted zones.
    """
    allowed_locs = get_user_allowed_locations(user)
    loc_list = [{'id': loc.id, 'name': loc.location_name} for loc in allowed_locs]

    # Determine departmental role title
    if user.is_superuser:
        role = "System Administrator"
    elif len(loc_list) >= 5:
        role = "Head Office Complaint Officer"
    elif len(loc_list) == 1:
        role = f"{loc_list[0]['name']} Complaint Officer"
    elif len(loc_list) > 1:
        role = "Zonal Complaint Officer"
    else:
        role = "WSSP Officer (Restricted)"

    full_name = f"{user.first_name} {user.last_name}".strip()
    if not full_name:
        full_name = user.username

    has_cms_perm = user.is_superuser or len(loc_list) > 0 or UserViewPermission.objects.filter(
        user=user,
        view_name__name__in=['complaint_management_view', 'complaint_management_report'],
        can_view=True
    ).exists()

    return {
        "id": user.id,
        "username": user.username,
        "full_name": full_name,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_staff": user.is_staff,
        "role": role,
        "has_cms_access": has_cms_perm,
        "allowed_locations": loc_list,
        "allowed_location_count": len(loc_list),
    }


class IsCMSAuthorized(permissions.BasePermission):
    """
    Permission class to verify that the user is authenticated, active,
    and has valid CMS access permissions in WSSP.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False
        if request.user.is_superuser:
            return True
        allowed_ids = get_user_allowed_location_ids(request.user)
        return len(allowed_ids) > 0


class CMSLoginView(APIView):
    """
    POST /api/cms/auth/login/
    Body: {"username": "<username>", "password": "<password>"}
    Returns JWT access & refresh tokens alongside user profile and allowed zones.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")

        if not username or not password:
            return Response(
                {"detail": "Both username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid credentials. Please check your username and password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"detail": "This account is inactive. Please contact WSSP MIS department."},
                status=status.HTTP_403_FORBIDDEN
            )

        profile = get_user_cms_profile(user)

        if not profile["has_cms_access"]:
            return Response(
                {"detail": "Access denied. You do not have permission to access the Complaint Management System."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh["username"] = user.username
        refresh["is_superuser"] = user.is_superuser
        refresh["role"] = profile["role"]

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": profile,
            "message": f"Welcome, {profile['full_name']}."
        }, status=status.HTTP_200_OK)


class CMSUserProfileView(APIView):
    """
    GET /api/cms/auth/me/
    Header: Authorization: Bearer <access_token>
    Returns current authenticated officer's profile, role, and zone permissions.
    """
    permission_classes = [IsAuthenticated, IsCMSAuthorized]

    def get(self, request):
        profile = get_user_cms_profile(request.user)
        return Response({"user": profile}, status=status.HTTP_200_OK)


class CMSSecurityTestView(APIView):
    """
    GET /api/cms/auth/test-security/
    Header: Authorization: Bearer <access_token>
    Verification endpoint demonstrating strict server-side LocationPermission enforcement.
    """
    permission_classes = [IsAuthenticated, IsCMSAuthorized]

    def get(self, request):
        allowed_ids = get_user_allowed_location_ids(request.user)
        allowed_names = list(Location.objects.filter(id__in=allowed_ids).values_list('location_name', flat=True))

        # Scoped complaint counts
        scoped_complaints = Complaint.objects.filter(location_id__in=allowed_ids)
        total_accessible = scoped_complaints.count()
        pending_accessible = scoped_complaints.filter(status='pending').count()
        resolved_accessible = scoped_complaints.filter(status='resolved').count()

        # Recent sample complaints (only from permitted locations)
        sample_complaints = scoped_complaints.order_by('-date', '-id')[:5].values(
            'id', 'location__location_name', 'uc__uc_name', 'complaint_type__type_name', 'status', 'date'
        )

        return Response({
            "security_enforcement": "ACTIVE - Server-Side Scoped",
            "officer": request.user.username,
            "allowed_locations": allowed_names,
            "scoped_stats": {
                "total_accessible_complaints": total_accessible,
                "pending_accessible": pending_accessible,
                "resolved_accessible": resolved_accessible,
            },
            "recent_accessible_sample": list(sample_complaints)
        }, status=status.HTTP_200_OK)
