"""
WSSP CMS API v1 URL Routing
===========================
Defines the routing table for API version 1.
All endpoints configured here are served under:
    /api/cms/v1/

Design Rules:
- Routes must point to dedicated v1 views.
- Keep business logic out of this file.
- Document every route clearly with its HTTP method and role.
"""

from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class APIStatusView(APIView):
    """
    Health check and status endpoint for WSSP CMS API v1.
    
    URL: GET /api/cms/v1/status/
    Access: Public (AllowAny)
    Response:
        {
            "success": true,
            "service": "WSSP CMS API",
            "version": "v1",
            "status": "online"
        }
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "success": True,
                "service": "WSSP CMS API",
                "version": "v1",
                "status": "online",
            },
            status=status.HTTP_200_OK
        )


from api.v1.views.auth import LoginView, UserProfileView, LogoutView
from api.v1.views.complaint_types import (
    ComplaintTypeListView,
    ComplaintSubTypeListView,
    ComplaintSourceListView,
)
from api.v1.views.locations import LocationListView, UCListView
from api.v1.views.complaints import (
    ComplaintListView,
    ComplaintDetailView,
    ComplaintHistoryView,
    ComplaintResponseView,
    ComplaintResolveView,
)
from api.v1.views.dashboard import CMSDashboardAnalyticsView

urlpatterns = [
    # Health Check & Service Status
    path("status/", APIStatusView.as_view(), name="api_status"),

    # Authentication & Profile (Existing WSSP Users)
    path("auth/login/", LoginView.as_view(), name="auth_login"),
    path("auth/me/", UserProfileView.as_view(), name="auth_me"),
    path("auth/logout/", LogoutView.as_view(), name="auth_logout"),

    # Dashboard Role-Scoped Analytics
    path("dashboard/analytics/", CMSDashboardAnalyticsView.as_view(), name="dashboard_analytics"),

    # Reference Metadata & Dropdowns (Phase API-5)
    path("complaint-types/", ComplaintTypeListView.as_view(), name="complaint_types"),
    path("subtypes/", ComplaintSubTypeListView.as_view(), name="complaint_subtypes"),
    path("complaint-sources/", ComplaintSourceListView.as_view(), name="complaint_sources"),
    path("locations/", LocationListView.as_view(), name="locations"),
    path("ucs/", UCListView.as_view(), name="ucs"),

    # Complaint Listing & Details (Phase API-6)
    path("complaints/", ComplaintListView.as_view(), name="complaint_list"),
    path("complaints/<int:complaint_id>/", ComplaintDetailView.as_view(), name="complaint_detail"),

    # Complaint Actions & Management (Phase API-7)
    path("complaints/<int:complaint_id>/history/", ComplaintHistoryView.as_view(), name="complaint_history"),
    path("complaints/<int:complaint_id>/response/", ComplaintResponseView.as_view(), name="complaint_response"),
    path("complaints/<int:complaint_id>/resolve/", ComplaintResolveView.as_view(), name="complaint_resolve"),
]
