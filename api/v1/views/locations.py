"""
API v1 Location & UC Reference Data Views
=========================================
Endpoints for geographical reference data:
- GET /api/cms/v1/locations/  -> List of Zones / Headoffice
- GET /api/cms/v1/ucs/        -> List of Union Councils (UCs)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from Dashboard.models import Location, UC
from api.v1.serializers.reference import LocationSerializer, UCSerializer
from api.v1.permissions.base import get_user_allowed_locations


class LocationListView(APIView):
    """
    GET /api/cms/v1/locations/
    ==========================
    Returns list of locations (Headoffice, Zone A, Zone B, etc.).
    If the requesting officer is authenticated and regular staff,
    returns their authorized locations unless ?all=true is specified.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        fetch_all = request.query_params.get("all", "false").lower() == "true"

        if user and user.is_authenticated and not fetch_all:
            qs = get_user_allowed_locations(user)
            if not qs.exists():
                qs = Location.objects.all().order_by("location_name")
        else:
            qs = Location.objects.all().order_by("location_name")

        serializer = LocationSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Locations retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )


class UCListView(APIView):
    """
    GET /api/cms/v1/ucs/
    ====================
    Returns Union Councils (UCs).
    Optional Query Parameters:
    - ?location_id=<id>: Filters UCs belonging to a specific Zone.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        location_id = request.query_params.get("location_id")
        qs = UC.objects.select_related("location").all()

        if location_id:
            qs = qs.filter(location_id=location_id)

        qs = qs.order_by("uc_name")
        serializer = UCSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Union councils retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )
