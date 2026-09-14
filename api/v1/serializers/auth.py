"""
API v1 Authentication Serializers
=================================
Validates authentication payloads (login, logout) and formats
the authenticated WSSP user profile and security roles.

Existing WSSP Django users (`auth_user`) are the sole source of truth.
No separate mobile user database is created or used.
"""

from rest_framework import serializers
from django.contrib.auth.models import User


class LoginRequestSerializer(serializers.Serializer):
    """
    Validates incoming login credentials.
    Ensures username and password are provided and non-empty.
    """
    username = serializers.CharField(
        max_length=150,
        required=True,
        trim_whitespace=True,
        error_messages={"blank": "Username is required."}
    )
    password = serializers.CharField(
        max_length=128,
        required=True,
        write_only=True,
        error_messages={"blank": "Password is required."}
    )


class LocationSummarySerializer(serializers.Serializer):
    """
    Serializes basic location metadata (Zone / Head Office).
    """
    id = serializers.IntegerField()
    name = serializers.CharField()


class UserProfileSerializer(serializers.Serializer):
    """
    Formats the authenticated WSSP user profile including
    departmental role title and allowed zonal locations.
    """
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    email = serializers.EmailField(allow_blank=True)
    is_superuser = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    role = serializers.CharField()
    has_cms_access = serializers.BooleanField()
    allowed_locations = LocationSummarySerializer(many=True)
    allowed_location_count = serializers.IntegerField()


class LogoutRequestSerializer(serializers.Serializer):
    """
    Validates optional refresh token payload for token invalidation / logout.
    """
    refresh = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional refresh token to blacklist upon logout."
    )
