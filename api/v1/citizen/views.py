"""
API v1 Citizen Views
====================
Provides endpoints for citizen registration, login, logout, profile management,
and dynamic complaint categories/locations.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from api.models import CitizenProfile
from api.v1.permissions.citizen import IsCitizenUser
from Dashboard.models import (
    Complaint,
    ComplaintFeedback,
    ComplaintResolution,
    ComplaintType,
    ComplaintSubType,
    Location,
    UC,
)
from api.v1.serializers.reference import (
    ComplaintTypeSerializer,
    ComplaintSubTypeSerializer,
    LocationSerializer,
    UCSerializer,
)
from api.v1.citizen.serializers import (
    CitizenRegistrationSerializer,
    CitizenLoginSerializer,
    CitizenProfileSerializer,
    CitizenComplaintCreateSerializer,
    CitizenComplaintResponseSerializer,
    CitizenComplaintListItemSerializer,
    CitizenComplaintDetailSerializer,
    CitizenFeedbackCreateSerializer,
    CitizenFeedbackSerializer,
)
from api.v1.citizen.services import CitizenComplaintSubmissionService


class CitizenRegisterView(APIView):
    """
    POST /api/citizen/v1/register/
    ==============================
    Public citizen account registration.
    Required fields: full_name, mobile_number, password, confirm_password
    Optional fields: email, address

    No OTP, SMS, or email verification is required.
    Passwords are hashed using standard Django PBKDF2 hashing.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CitizenRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Registration validation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated = serializer.validated_data
        full_name = validated["full_name"].strip()
        mobile_number = validated["mobile_number"]
        password = validated["password"]
        email = validated.get("email", "").strip()
        address = validated.get("address", "").strip()

        # Split full_name into first and last name
        parts = full_name.split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        try:
            with transaction.atomic():
                # 1. Create standard Django User (username = mobile_number)
                user = User.objects.create_user(
                    username=mobile_number,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    is_staff=False,
                    is_superuser=False,
                    is_active=True,
                )

                # 2. Create companion CitizenProfile
                profile = CitizenProfile.objects.create(
                    user=user,
                    mobile_number=mobile_number,
                    address=address,
                )

            return Response(
                {
                    "success": True,
                    "message": "Your account has been created successfully.",
                    "data": {
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "full_name": full_name,
                            "mobile_number": mobile_number,
                            "email": email,
                            "address": address,
                            "role": "Citizen",
                            "account_type": "citizen",
                        }
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "An error occurred during account registration. Please try again.",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CitizenLoginView(APIView):
    """
    POST /api/citizen/v1/login/
    ===========================
    Authenticates a citizen using mobile number and password.
    Returns JWT access and refresh tokens and citizen profile metadata.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CitizenLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Login failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]
        normalized_mobile = serializer.validated_data["normalized_mobile"]

        # Ensure citizen profile exists (self-healing for edge cases)
        profile, _ = CitizenProfile.objects.get_or_create(
            user=user,
            defaults={"mobile_number": normalized_mobile},
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh["account_type"] = "citizen"
        refresh["role"] = "Citizen"
        refresh["username"] = user.username

        full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        return Response(
            {
                "success": True,
                "message": f"Welcome back, {full_name}.",
                "data": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": full_name,
                        "mobile_number": profile.mobile_number,
                        "email": user.email,
                        "address": profile.address,
                        "role": "Citizen",
                        "account_type": "citizen",
                        "is_staff": False,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )


class CitizenLogoutView(APIView):
    """
    POST /api/citizen/v1/logout/
    ============================
    Logs out the authenticated citizen by invalidating the refresh token.
    """
    permission_classes = [IsAuthenticated, IsCitizenUser]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except (TokenError, AttributeError):
                pass

        return Response(
            {
                "success": True,
                "message": "You have been logged out successfully.",
            },
            status=status.HTTP_200_OK,
        )


class CitizenProfileView(APIView):
    """
    GET /api/citizen/v1/profile/   -> Retrieve authenticated citizen profile
    PATCH /api/citizen/v1/profile/ -> Update full_name, email, or address
    """
    permission_classes = [IsAuthenticated, IsCitizenUser]

    def get(self, request):
        profile, _ = CitizenProfile.objects.get_or_create(
            user=request.user,
            defaults={"mobile_number": request.user.username},
        )
        serializer = CitizenProfileSerializer(profile)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        profile, _ = CitizenProfile.objects.get_or_create(
            user=request.user,
            defaults={"mobile_number": request.user.username},
        )
        serializer = CitizenProfileSerializer(profile, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Validation failed.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return Response(
            {
                "success": True,
                "message": "Profile updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CitizenComplaintTypeListView(APIView):
    """
    GET /api/citizen/v1/complaint-types/
    ====================================
    Returns available core municipal service complaint categories:
    - Solid Waste Management (SWM)
    - Water Supply (WS)
    - Sanitation & Drainage (SDS)
    - Revenue / Billing (BILL)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        types = ComplaintType.objects.all().order_by("id")
        serializer = ComplaintTypeSerializer(types, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "message": "Complaint categories retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )


class CitizenComplaintSubTypeListView(APIView):
    """
    GET /api/citizen/v1/subtypes/
    =============================
    Returns complaint subcategories dynamically.
    Optional Query Parameter:
    - ?type_id=<id> or ?complaint_type_id=<id>: Cascades subcategories to the chosen category.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        type_id = request.query_params.get("type_id") or request.query_params.get("complaint_type_id")
        qs = ComplaintSubType.objects.select_related("complaint_type").all()

        if type_id:
            try:
                qs = qs.filter(complaint_type_id=int(type_id))
            except (ValueError, TypeError):
                pass

        qs = qs.order_by("type_name")
        serializer = ComplaintSubTypeSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "count": qs.count(),
                "message": "Complaint subcategories retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )


class CitizenLocationListView(APIView):
    """
    GET /api/citizen/v1/locations/
    ==============================
    Returns municipal operational zones across Peshawar (Zone A, B, C, D, E).
    Excludes internal administrative Head Office by default.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        include_all = request.query_params.get("include_all", "false").lower() == "true"
        qs = Location.objects.all()

        if not include_all:
            qs = qs.exclude(location_name__icontains="head")

        qs = qs.order_by("location_name")
        serializer = LocationSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "count": qs.count(),
                "message": "Operational municipal zones retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )


class CitizenUCListView(APIView):
    """
    GET /api/citizen/v1/ucs/
    ========================
    Returns Union Councils (UCs).
    Optional Query Parameter:
    - ?location_id=<id>: Cascades UCs to the selected operational Zone.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        location_id = request.query_params.get("location_id")
        qs = UC.objects.select_related("location").all()

        if location_id:
            try:
                qs = qs.filter(location_id=int(location_id))
            except (ValueError, TypeError):
                pass

        qs = qs.order_by("uc_name")
        serializer = UCSerializer(qs, many=True)
        return Response(
            {
                "success": True,
                "data": serializer.data,
                "count": qs.count(),
                "message": "Union Councils retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )


class CitizenComplaintSubmissionView(APIView):
    """
    POST /api/citizen/v1/complaints/
    ================================
    Allows an authenticated citizen to submit a new municipal complaint.

    Accepts JSON or multipart/form-data:
    - complaint_type_id: int (Required)
    - subtype_id: int (Optional)
    - uc_id: int (Required)
    - complaint_detail: str (Required, min 10 chars)
    - address: str (Optional)
    - area: str (Optional)
    - title: str (Optional)
    - latitude: decimal (Optional)
    - longitude: decimal (Optional)
    - before_image: file (Optional, max 5MB, JPG/PNG/WEBP)

    Security & Routing Guarantees:
    - Authenticated citizen only (IsCitizenUser).
    - Verified municipal zone is automatically determined from the UC hierarchy.
    - Official reference number 'CMS-{id}' returned.
    - Automatically visible in target Zonal and Departmental staff queues.
    """
    permission_classes = [IsAuthenticated, IsCitizenUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = CitizenComplaintCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Complaint submission failed validation.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract optional photograph
        image_file = request.FILES.get("before_image")

        try:
            complaint = CitizenComplaintSubmissionService.submit_complaint(
                citizen_user=request.user,
                validated_data=serializer.validated_data,
                image_file=image_file,
            )

            response_serializer = CitizenComplaintResponseSerializer(
                complaint,
                context={"request": request},
            )

            return Response(
                {
                    "success": True,
                    "message": "Your complaint has been successfully submitted.",
                    "data": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as val_err:
            return Response(
                {
                    "success": False,
                    "message": "Validation error.",
                    "errors": val_err.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as err:
            return Response(
                {
                    "success": False,
                    "message": "Failed to submit complaint. Please try again.",
                    "detail": str(err),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CitizenPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 50


def _get_citizen_mobile(user):
    profile = getattr(user, "citizen_profile", None)
    if profile and profile.mobile_number:
        return profile.mobile_number
    return user.username


def _get_citizen_complaints_queryset(user):
    mobile = _get_citizen_mobile(user)
    return Complaint.objects.filter(
        Q(cell_number=mobile) | Q(actions__action="created", actions__user=user)
    ).distinct().select_related("complaint_type", "SubType", "location", "uc").prefetch_related("feedbacks")


class CitizenComplaintListView(APIView):
    """
    GET /api/citizen/v1/complaints/
    ===============================
    Returns the authenticated citizen's complaints.
    Supports filtering by status ('pending', 'resolved'), search query 'q', and pagination.

    POST /api/citizen/v1/complaints/
    ================================
    Submits a new citizen complaint.
    """
    permission_classes = [IsAuthenticated, IsCitizenUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        queryset = _get_citizen_complaints_queryset(request.user).order_by("-id")

        status_filter = request.query_params.get("status", "").strip().lower()
        if status_filter in ["pending", "resolved"]:
            queryset = queryset.filter(status=status_filter)

        search_query = request.query_params.get("q", "").strip()
        if search_query:
            if search_query.isdigit():
                queryset = queryset.filter(
                    Q(id=int(search_query)) |
                    Q(complaint_detail__icontains=search_query) |
                    Q(title__icontains=search_query)
                )
            elif search_query.upper().startswith("CMS-") and search_query[4:].isdigit():
                queryset = queryset.filter(id=int(search_query[4:]))
            else:
                queryset = queryset.filter(
                    Q(complaint_detail__icontains=search_query) |
                    Q(title__icontains=search_query) |
                    Q(area__icontains=search_query)
                )

        paginator = CitizenPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CitizenComplaintListItemSerializer(page, many=True, context={"request": request})

        response = paginator.get_paginated_response(serializer.data)
        response.data["success"] = True
        return response

    def post(self, request):
        return CitizenComplaintSubmissionView().post(request)


class CitizenComplaintDetailView(APIView):
    """
    GET /api/citizen/v1/complaints/<pk>/
    ===================================
    Returns detailed information for a single complaint submitted by or belonging
    to the authenticated citizen. Strictly omits internal staff notes.
    """
    permission_classes = [IsAuthenticated, IsCitizenUser]

    def get(self, request, pk):
        try:
            complaint = Complaint.objects.select_related(
                "complaint_type", "SubType", "location", "uc", "resolution"
            ).prefetch_related("feedbacks").get(pk=pk)
        except Complaint.DoesNotExist:
            return Response(
                {"success": False, "message": "Complaint not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mobile = _get_citizen_mobile(request.user)
        is_owner = (complaint.cell_number == mobile) or complaint.actions.filter(
            action="created", user=request.user
        ).exists()

        if not is_owner:
            return Response(
                {"success": False, "message": "Complaint not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CitizenComplaintDetailSerializer(complaint, context={"request": request})
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CitizenComplaintTrackingView(APIView):
    """
    GET /api/citizen/v1/complaints/<pk>/tracking/
    ============================================
    Returns a structured, public progress timeline for the citizen's complaint.
    Steps:
    1. Submitted (Logged in system)
    2. Assigned & In Progress (Assigned to zonal operational team)
    3. Resolution (Ground resolution & evidence photo)
    4. Feedback (Citizen satisfaction review)
    """
    permission_classes = [IsAuthenticated, IsCitizenUser]

    def get(self, request, pk):
        try:
            complaint = Complaint.objects.select_related(
                "complaint_type", "SubType", "location", "uc", "resolution"
            ).prefetch_related("feedbacks").get(pk=pk)
        except Complaint.DoesNotExist:
            return Response(
                {"success": False, "message": "Complaint not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mobile = _get_citizen_mobile(request.user)
        is_owner = (complaint.cell_number == mobile) or complaint.actions.filter(
            action="created", user=request.user
        ).exists()

        if not is_owner:
            return Response(
                {"success": False, "message": "Complaint not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_resolved = (complaint.status == "resolved")
        latest_feedback = complaint.feedbacks.order_by("-created_at").first()

        loc_name = complaint.location.location_name if complaint.location else "Zonal Office"
        cat_name = complaint.complaint_type.type_name if complaint.complaint_type else "Operations"

        after_image_url = None
        if hasattr(complaint, "resolution") and complaint.resolution and complaint.resolution.after_image:
            try:
                after_image_url = request.build_absolute_uri(complaint.resolution.after_image.url)
            except Exception:
                after_image_url = complaint.resolution.after_image.url

        timeline = [
            {
                "step": 1,
                "key": "submitted",
                "title": "Complaint Submitted",
                "subtitle": f"Ticket CMS-{complaint.id} created",
                "timestamp": complaint.created_at,
                "status": "completed",
                "badge": "Completed",
                "description": "Complaint successfully logged in WSSP Central Complaint Management System.",
            },
            {
                "step": 2,
                "key": "in_progress",
                "title": "Assigned to Field Team",
                "subtitle": f"{loc_name} - {cat_name}",
                "timestamp": complaint.created_at,
                "status": "completed" if is_resolved else "in_progress",
                "badge": "Completed" if is_resolved else "In Progress",
                "description": f"Complaint routed to {loc_name} field team for inspection and necessary action.",
            },
            {
                "step": 3,
                "key": "resolved",
                "title": "Work Completed" if is_resolved else "Resolution In Progress",
                "subtitle": f"Status: {complaint.get_status_display() if hasattr(complaint, 'get_status_display') else complaint.status.capitalize()}",
                "timestamp": (complaint.updated_at if is_resolved else None),
                "status": "completed" if is_resolved else "pending",
                "badge": "Resolved" if is_resolved else "Pending",
                "description": (
                    complaint.resolution.description
                    if (is_resolved and hasattr(complaint, "resolution") and complaint.resolution and complaint.resolution.description)
                    else ("Work completed on ground by WSSP field staff." if is_resolved else "Field team is addressing the reported issue.")
                ),
                "after_image_url": after_image_url,
            },
            {
                "step": 4,
                "key": "feedback",
                "title": "Citizen Feedback",
                "subtitle": "Rate Service" if not latest_feedback else "Feedback Recorded",
                "timestamp": (latest_feedback.created_at if latest_feedback else None),
                "status": "completed" if latest_feedback else ("available" if is_resolved else "locked"),
                "badge": "Submitted" if latest_feedback else ("Rate Now" if is_resolved else "Locked"),
                "description": (
                    f"Citizen feedback: {'Satisfied' if latest_feedback.happy else 'Unsatisfied'}."
                    + (f" Comment: \"{latest_feedback.complaint_feedback}\"" if latest_feedback and latest_feedback.complaint_feedback else "")
                    if latest_feedback
                    else ("Your feedback is valuable. Please rate your experience." if is_resolved else "Feedback unlocks upon complaint resolution.")
                ),
                "feedback_data": (
                    {
                        "id": latest_feedback.id,
                        "happy": latest_feedback.happy,
                        "comment": latest_feedback.complaint_feedback,
                        "submitted_at": latest_feedback.created_at,
                    }
                    if latest_feedback
                    else None
                ),
            },
        ]

        before_image_url = None
        if complaint.before_image:
            try:
                before_image_url = request.build_absolute_uri(complaint.before_image.url)
            except Exception:
                before_image_url = complaint.before_image.url

        return Response(
            {
                "success": True,
                "complaint": {
                    "id": complaint.id,
                    "complaint_no": f"CMS-{complaint.id}",
                    "title": complaint.title,
                    "status": complaint.status,
                    "category": cat_name,
                    "subcategory": complaint.SubType.type_name if complaint.SubType else None,
                    "location": loc_name,
                    "uc": complaint.uc.uc_name if complaint.uc else None,
                    "area": complaint.area,
                    "address": complaint.address,
                    "complaint_detail": complaint.complaint_detail,
                    "before_image_url": before_image_url,
                    "created_at": complaint.created_at,
                    "updated_at": complaint.updated_at,
                },
                "timeline": timeline,
                "can_give_feedback": is_resolved,
                "feedback_given": bool(latest_feedback),
            },
            status=status.HTTP_200_OK,
        )


class CitizenComplaintFeedbackView(APIView):
    """
    POST /api/citizen/v1/complaints/<pk>/feedback/
    ==============================================
    Records citizen satisfaction feedback for a resolved complaint.
    Required: happy (bool)
    Optional: complaint_feedback (str)
    """
    permission_classes = [IsAuthenticated, IsCitizenUser]

    def post(self, request, pk):
        try:
            complaint = Complaint.objects.select_related("resolution").prefetch_related("feedbacks").get(pk=pk)
        except Complaint.DoesNotExist:
            return Response(
                {"success": False, "message": "Complaint not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mobile = _get_citizen_mobile(request.user)
        is_owner = (complaint.cell_number == mobile) or complaint.actions.filter(
            action="created", user=request.user
        ).exists()

        if not is_owner:
            return Response(
                {"success": False, "message": "Complaint not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if complaint.status != "resolved":
            return Response(
                {
                    "success": False,
                    "message": "Feedback can only be submitted after the complaint is resolved.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CitizenFeedbackCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Invalid feedback data.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data
        citizen_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username

        with transaction.atomic():
            feedback = ComplaintFeedback.objects.create(
                complaint=complaint,
                feedback_officer_name=f"Citizen ({citizen_name})",
                complaint_feedback=validated_data.get("complaint_feedback", ""),
                happy=validated_data["happy"],
            )

            # Sync customer satisfaction to ComplaintResolution if it exists
            if hasattr(complaint, "resolution") and complaint.resolution:
                complaint.resolution.customer_satisfaction = "yes" if validated_data["happy"] else "no"
                complaint.resolution.save(update_fields=["customer_satisfaction"])

        return Response(
            {
                "success": True,
                "message": "Thank you! Your feedback has been successfully recorded.",
                "data": CitizenFeedbackSerializer(feedback).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CitizenDashboardSummaryView(APIView):
    """
    GET /api/citizen/v1/dashboard/
    ==============================
    Returns a unified dashboard summary for the citizen home screen:
    - Welcome details & Profile summary
    - Complaint metrics (Total, Pending, Resolved)
    - Recent 5 complaints
    - Official WSSP helpline & contact details
    """
    permission_classes = [IsAuthenticated, IsCitizenUser]

    def get(self, request):
        user = request.user
        profile = getattr(user, "citizen_profile", None)
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        mobile = profile.mobile_number if profile else user.username

        user_complaints = _get_citizen_complaints_queryset(user)
        total_count = user_complaints.count()
        pending_count = user_complaints.filter(status="pending").count()
        resolved_count = user_complaints.filter(status="resolved").count()

        recent_qs = user_complaints.order_by("-id")[:5]
        recent_serialized = CitizenComplaintListItemSerializer(
            recent_qs, many=True, context={"request": request}
        ).data

        return Response(
            {
                "success": True,
                "citizen": {
                    "full_name": full_name,
                    "mobile_number": mobile,
                    "email": user.email,
                    "address": profile.address if profile else "",
                },
                "metrics": {
                    "total": total_count,
                    "pending": pending_count,
                    "resolved": resolved_count,
                },
                "recent_complaints": recent_serialized,
                "contacts": {
                    "helpline": "1334",
                    "landline": "091-9213456",
                    "email": "info@wssp.peshawar.gov.pk",
                    "website": "https://wssp.org.pk",
                },
            },
            status=status.HTTP_200_OK,
        )


