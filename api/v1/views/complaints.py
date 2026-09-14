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


from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from api.v1.services.complaint_service import ComplaintService
from api.v1.permissions.complaints import CanViewComplaint, CanUpdateComplaint, CanResolveComplaint
from api.v1.serializers.complaints import (
    ComplaintListSerializer,
    ComplaintDetailSerializer,
    ComplaintResponseCreateSerializer,
    ComplaintResolveSerializer,
    ComplaintUpdateSerializer,
)


class ComplaintDetailView(APIView):
    """
    GET /api/cms/v1/complaints/{id}/
    ================================
    Returns detailed complaint information including citizen profile and media URLs.
    Enforces object-level CanViewComplaint permission check.

    PATCH /api/cms/v1/complaints/{id}/
    ==================================
    Partially updates complaint attributes (detail, title, sub-type, address, uc, status).
    Enforces object-level CanUpdateComplaint permission check.
    """
    permission_classes = [IsAuthenticated, IsCMSStaffUser, CanViewComplaint]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

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

    def patch(self, request, complaint_id):
        complaint = get_object_or_404(Complaint, id=complaint_id)

        # Check update permission
        update_perm = CanUpdateComplaint()
        if not update_perm.has_object_permission(request, self, complaint):
            return Response(
                {"success": False, "message": "You do not have permission to update this complaint."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ComplaintUpdateSerializer(complaint, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "Validation failed.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_complaint = ComplaintService.update_complaint(
            complaint=complaint,
            user=request.user,
            validated_data=serializer.validated_data,
        )

        out_serializer = ComplaintDetailSerializer(updated_complaint, context={"request": request})
        return Response(
            {
                "success": True,
                "data": out_serializer.data,
                "message": "Complaint updated successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ComplaintHistoryView(APIView):
    """
    GET /api/cms/v1/complaints/{id}/history/
    ========================================
    Returns full timeline history for a complaint:
    - Audit logs (ComplaintActionLog)
    - Officer responses (ComplaintResponse)
    - Citizen feedback (ComplaintFeedback)
    - Resolution summary (ComplaintResolution)
    """
    permission_classes = [IsAuthenticated, IsCMSStaffUser, CanViewComplaint]

    def get(self, request, complaint_id):
        complaint = get_object_or_404(Complaint, id=complaint_id)
        self.check_object_permissions(request, complaint)

        history_data = ComplaintService.get_complaint_history(complaint, request=request)
        return Response(
            {
                "success": True,
                "data": history_data,
                "message": "Complaint history retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ComplaintResponseView(APIView):
    """
    POST /api/cms/v1/complaints/{id}/response/
    ==========================================
    Records an official officer response to a complaint.
    Payload:
        {
            "feedback": "yes" | "no" | "neutral" | "not_responded",
            "officer_name": "Officer Name" (optional)
        }
    """
    permission_classes = [IsAuthenticated, IsCMSStaffUser, CanUpdateComplaint]

    def post(self, request, complaint_id):
        complaint = get_object_or_404(Complaint, id=complaint_id)
        self.check_object_permissions(request, complaint)

        serializer = ComplaintResponseCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "Validation failed.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        resp_obj = ComplaintService.add_response(
            complaint=complaint,
            user=request.user,
            feedback=serializer.validated_data["feedback"],
            officer_name=serializer.validated_data.get("officer_name"),
        )

        return Response(
            {
                "success": True,
                "data": {
                    "id": resp_obj.id,
                    "complaint_id": resp_obj.complaint_id,
                    "officer_name": resp_obj.officer_name,
                    "feedback": resp_obj.feedback,
                    "created_at": resp_obj.created_at,
                },
                "message": "Response recorded successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class ComplaintResolveView(APIView):
    """
    POST /api/cms/v1/complaints/{id}/resolve/
    =========================================
    Resolves a complaint, updating status to 'resolved' and storing resolution data.
    Supports multipart/form-data for optional after_image upload.
    Payload:
        - description (text)
        - customer_satisfaction ("yes", "no", "call_no_response")
        - after_image (file upload, optional)
    """
    permission_classes = [IsAuthenticated, IsCMSStaffUser, CanResolveComplaint]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, complaint_id):
        complaint = get_object_or_404(Complaint, id=complaint_id)
        self.check_object_permissions(request, complaint)

        serializer = ComplaintResolveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "message": "Validation failed.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        after_image = request.FILES.get("after_image")

        resolution_obj = ComplaintService.resolve_complaint(
            complaint=complaint,
            user=request.user,
            description=serializer.validated_data.get("description"),
            customer_satisfaction=serializer.validated_data.get("customer_satisfaction", "yes"),
            after_image=after_image,
        )

        after_image_url = None
        if resolution_obj.after_image:
            try:
                after_image_url = request.build_absolute_uri(resolution_obj.after_image.url)
            except Exception:
                after_image_url = resolution_obj.after_image.url

        return Response(
            {
                "success": True,
                "data": {
                    "complaint_id": complaint.id,
                    "status": complaint.status,
                    "resolution": {
                        "id": resolution_obj.id,
                        "description": resolution_obj.description,
                        "customer_satisfaction": resolution_obj.customer_satisfaction,
                        "after_image_url": after_image_url,
                    },
                },
                "message": "Complaint resolved successfully.",
            },
            status=status.HTTP_200_OK,
        )

