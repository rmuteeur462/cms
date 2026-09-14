"""
API v1 Complaint Type & Reference Data Views
============================================
Endpoints for complaint taxonomy reference data:
- GET /api/cms/v1/complaint-types/
- GET /api/cms/v1/subtypes/
- GET /api/cms/v1/complaint-sources/
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from Dashboard.models import ComplaintType, ComplaintSubType, ComplaintSource
from api.v1.serializers.reference import (
    ComplaintTypeSerializer,
    ComplaintSubTypeSerializer,
    ComplaintSourceSerializer,
)


class ComplaintTypeListView(APIView):
    """
    GET /api/cms/v1/complaint-types/
    ================================
    Returns all core complaint types (Water Supply, Solid Waste, Drainage, Billing).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        types = ComplaintType.objects.all().order_by("type_name")
        serializer = ComplaintTypeSerializer(types, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Complaint types retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ComplaintSubTypeListView(APIView):
    """
    GET /api/cms/v1/subtypes/
    =========================
    Returns complaint sub-categories.
    Optional Query Parameters:
    - ?complaint_type_id=<id>: Filters sub-types to a specific parent category.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        complaint_type_id = request.query_params.get("complaint_type_id")
        qs = ComplaintSubType.objects.select_related("complaint_type").all()

        if complaint_type_id:
            qs = qs.filter(complaint_type_id=complaint_type_id)

        qs = qs.order_by("type_name")
        serializer = ComplaintSubTypeSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Complaint sub-types retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ComplaintSourceListView(APIView):
    """
    GET /api/cms/v1/complaint-sources/
    ==================================
    Returns all valid intake channels (Walk-In, Phone, Mobile App, etc.).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        sources = ComplaintSource.objects.all().order_by("source_name")
        serializer = ComplaintSourceSerializer(sources, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Complaint sources retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )
