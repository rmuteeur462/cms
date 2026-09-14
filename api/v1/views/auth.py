"""
API v1 Authentication Views
===========================
Handles authentication, user session profile, and logout.

Endpoints:
- POST /api/cms/v1/auth/login/   -> Authenticate existing WSSP user and return JWT tokens
- GET  /api/cms/v1/auth/me/      -> Get authenticated officer's profile and zone permissions
- POST /api/cms/v1/auth/logout/  -> End session and invalidate token

Security Guarantee:
- Uses existing WSSP Django User (`auth_user`) database.
- Enforces strict LocationPermission and UserViewPermission.
- No separate mobile user database is created or maintained.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate

# Reuse established location security logic to maintain single source of truth
from api.cms_auth import (
    get_user_cms_profile,
    get_user_allowed_location_ids,
    IsCMSAuthorized,
)
from api.v1.serializers.auth import (
    LoginRequestSerializer,
    UserProfileSerializer,
    LogoutRequestSerializer,
)


class LoginView(APIView):
    """
    POST /api/cms/v1/auth/login/
    ============================
    Authenticate an existing WSSP staff/officer user.

    Request Body:
        {
            "username": "<username>",
            "password": "<password>"
        }

    Response (200 OK):
        {
            "success": true,
            "data": {
                "access": "<jwt_access_token>",
                "refresh": "<jwt_refresh_token>",
                "user": { ... }
            },
            "message": "Welcome, <full_name>."
        }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        # Authenticate against Django's existing WSSP auth_user database
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {
                    "success": False,
                    "message": "Invalid credentials. Please check your username and password.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {
                    "success": False,
                    "message": "This account is inactive. Please contact WSSP MIS department.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Extract WSSP CMS profile and permission rules
        profile = get_user_cms_profile(user)

        if not profile.get("has_cms_access", False):
            return Response(
                {
                    "success": False,
                    "message": "Access denied. You do not have permission to access the Complaint Management System.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate JWT tokens with claims
        refresh = RefreshToken.for_user(user)
        refresh["username"] = user.username
        refresh["is_superuser"] = user.is_superuser
        refresh["role"] = profile.get("role", "Officer")

        return Response(
            {
                "success": True,
                "data": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": profile,
                },
                "message": f"Welcome, {profile.get('full_name', user.username)}.",
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    """
    GET /api/cms/v1/auth/me/
    ========================
    Returns the currently authenticated officer's profile, role,
    and assigned zonal location permissions.

    Header:
        Authorization: Bearer <access_token>

    Response (200 OK):
        {
            "success": true,
            "data": { ... user profile ... },
            "message": "User profile retrieved successfully."
        }
    """
    permission_classes = [IsAuthenticated, IsCMSAuthorized]

    def get(self, request):
        profile = get_user_cms_profile(request.user)
        return Response(
            {
                "success": True,
                "data": profile,
                "message": "User profile retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/cms/v1/auth/logout/
    =============================
    Logs out the user. Optionally blacklists the refresh token if provided.

    Header:
        Authorization: Bearer <access_token>

    Request Body (optional):
        {
            "refresh": "<jwt_refresh_token>"
        }

    Response (200 OK):
        {
            "success": true,
            "data": null,
            "message": "Logged out successfully."
        }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutRequestSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data.get("refresh")
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except (TokenError, Exception):
                    # Even if blacklist fails or blacklist app isn't installed,
                    # return successful logout acknowledgment to client
                    pass

        return Response(
            {
                "success": True,
                "data": None,
                "message": "Logged out successfully.",
            },
            status=status.HTTP_200_OK,
        )
