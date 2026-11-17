"""
WSSP CMS Citizen API v1 URL Routing
===================================
Defines the routing table for Citizen operations.
Served under:
    /api/citizen/v1/
    and /api/cms/v1/citizen/

Endpoints:
- GET  status/              -> Service status and health check (C1)
- POST register/            -> Citizen registration (C2)
- POST login/               -> Citizen login (C2)
- POST logout/              -> Citizen logout (C2)
- GET  profile/             -> Citizen profile view (C3)
- PATCH profile/            -> Citizen profile update (C3)
- GET  complaint-types/     -> Public complaint categories (C3)
- GET  subtypes/            -> Cascading subcategories (C3)
- GET  locations/           -> WSSP operational zones (C3)
- GET  ucs/                 -> Cascading Union Councils (C3)
- POST complaints/          -> Submit complaint (Phase C5)
- GET  complaints/          -> Citizen's own complaint directory (Phase C8)
- GET  complaints/<id>/     -> Single complaint detail (Phase C8)
- GET  complaints/<id>/tracking/ -> Public timeline (Phase C8)
- POST complaints/<id>/feedback/ -> Post-resolution feedback (Phase C9)
"""

from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from api.v1.citizen.views import (
    CitizenRegisterView,
    CitizenLoginView,
    CitizenLogoutView,
    CitizenProfileView,
    CitizenComplaintTypeListView,
    CitizenComplaintSubTypeListView,
    CitizenLocationListView,
    CitizenUCListView,
    CitizenComplaintSubmissionView,
    CitizenComplaintListView,
    CitizenComplaintDetailView,
    CitizenComplaintTrackingView,
    CitizenComplaintFeedbackView,
    CitizenDashboardSummaryView,
)


class CitizenStatusView(APIView):
    """
    Health check and status endpoint for WSSP Citizen Module API v1.
    URL: GET /api/citizen/v1/status/
    Access: Public (AllowAny)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "success": True,
                "service": "WSSP Citizen Portal API",
                "version": "v1",
                "status": "online",
                "auth_type": "mobile_password",
                "otp_required": False,
            },
            status=status.HTTP_200_OK,
        )


urlpatterns = [
    # Health Check & Service Status (Phase C1)
    path("status/", CitizenStatusView.as_view(), name="citizen_status"),

    # Citizen Authentication (Phase C2)
    path("register/", CitizenRegisterView.as_view(), name="citizen_register"),
    path("login/", CitizenLoginView.as_view(), name="citizen_login"),
    path("logout/", CitizenLogoutView.as_view(), name="citizen_logout"),

    # Citizen Profile (Phase C3)
    path("profile/", CitizenProfileView.as_view(), name="citizen_profile"),

    # Dynamic Metadata & Cascading Lookups (Phase C3)
    path("complaint-types/", CitizenComplaintTypeListView.as_view(), name="citizen_complaint_types"),
    path("subtypes/", CitizenComplaintSubTypeListView.as_view(), name="citizen_subtypes"),
    path("locations/", CitizenLocationListView.as_view(), name="citizen_locations"),
    path("ucs/", CitizenUCListView.as_view(), name="citizen_ucs"),

    # Citizen Dashboard Summary (Phase C5)
    path("dashboard/", CitizenDashboardSummaryView.as_view(), name="citizen_dashboard"),

    # Complaint Directory & Submission (Phases C4, C5)
    path("complaints/", CitizenComplaintListView.as_view(), name="citizen_complaint_submit"),
    path("complaints/list/", CitizenComplaintListView.as_view(), name="citizen_complaint_list"),
    path("complaints/<int:pk>/", CitizenComplaintDetailView.as_view(), name="citizen_complaint_detail"),
    path("complaints/<int:pk>/tracking/", CitizenComplaintTrackingView.as_view(), name="citizen_complaint_tracking"),
    path("complaints/<int:pk>/feedback/", CitizenComplaintFeedbackView.as_view(), name="citizen_complaint_feedback"),
]
