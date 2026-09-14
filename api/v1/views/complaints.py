"""
API v1 Complaint Views
======================
Implements core complaint handling endpoints:
- GET /api/cms/v1/complaints/       -> Paginated, role-scoped complaints list
- GET /api/cms/v1/complaints/{id}/  -> Rich complaint details with strict object-level security
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from Dashboard.models import Complaint
from api.v1.permissions.base import scope_complaint_queryset
from api.v1.permissions.staff import IsCMSStaffUser
from api.v1.permissions.complaints import CanViewComplaint
from api.v1.serializers.complaints import ComplaintListSerializer, ComplaintDetailSerializer
from api.v1.pagination import StandardResultsSetPagination


class ComplaintListView(APIView):
    """
    GET /api/cms/v1/complaints/
    ===========================
    Returns paginated list of complaints strictly scoped to officer's role, zone, and department.

    Query Parameters:
    - page: int (default: 1)
    - page_size: int (default: 20, max: 100)
    - status: str ('pending', 'resolved')
    - complaint_type_id: int
    - location_id: int
    - uc_id: int
    - search: str (searches ticket id, citizen name, cell, address, detail)
    """
    permission_classes = [IsAuthenticated, IsCMSStaffUser]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        # 1. Base query strictly scoped server-side by officer's jurisdictional permissions
        base_qs = Complaint.objects.select_related(
            "location", "uc", "complaint_type", "SubType"
        ).all()

        qs = scope_complaint_queryset(request.user, base_qs)

        # 2. Apply query parameter filters
        complaint_status = request.query_params.get("status")
        if complaint_status:
            qs = qs.filter(status__iexact=complaint_status.strip())

        complaint_type_id = request.query_params.get("complaint_type_id")
        if complaint_type_id:
            qs = qs.filter(complaint_type_id=complaint_type_id)

        location_id = request.query_params.get("location_id")
        if location_id:
            qs = qs.filter(location_id=location_id)

        uc_id = request.query_params.get("uc_id")
        if uc_id:
            qs = qs.filter(uc_id=uc_id)

        search = request.query_params.get("search")
        if search:
            search = search.strip()
            # If search is pure numeric, allow direct ID match
            if search.isdigit():
                qs = qs.filter(
                    Q(id=int(search))
                    | Q(cell_number__icontains=search)
                    | Q(first_name__icontains=search)
                    | Q(last_name__icontains=search)
                    | Q(complaint_detail__icontains=search)
                )
            else:
                qs = qs.filter(
                    Q(first_name__icontains=search)
                    | Q(last_name__icontains=search)
                    | Q(address__icontains=search)
                    | Q(area__icontains=search)
                    | Q(complaint_detail__icontains=search)
                )

        # Order by newest first
        qs = qs.order_by("-date", "-id")

        # 3. Paginate
        paginator = self.pagination_class()
        paginated_records = paginator.paginate_queryset(qs, request, view=self)
        serializer = ComplaintListSerializer(paginated_records, many=True, context={"request": request})

        return paginator.get_paginated_response(serializer.data)


class ComplaintDetailView(APIView):
    """
    GET /api/cms/v1/complaints/{id}/
    ================================
    Returns detailed complaint information including citizen profile and media URLs.
    Enforces object-level CanViewComplaint permission check.
    """
    permission_classes = [IsAuthenticated, IsCMSStaffUser, CanViewComplaint]

    def get(self, request, complaint_id):
        complaint = get_object_or_404(
            Complaint.objects.select_related(
                "location", "uc", "complaint_type", "SubType", "complaint_source"
            ),
            id=complaint_id,
        )

        # Enforce jurisdictional object-level check
        self.check_object_permissions(request, complaint)

        serializer = ComplaintDetailSerializer(complaint, context={"request": request})
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Complaint details retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )
