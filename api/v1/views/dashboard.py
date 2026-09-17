"""
WSSP CMS API v1 Dashboard Views
===============================
Provides secure, role-scoped, time-filtered complaint analytics for WSSP CMS.

Endpoint:
  GET /api/cms/v1/dashboard/analytics/

Query Parameters:
  - year: Integer (e.g., 2026)
  - month: Integer (1-12)
  - start_date: Date string YYYY-MM-DD
  - end_date: Date string YYYY-MM-DD

Security:
  - Scoping is enforced by DashboardAnalyticsService on the backend queryset.
  - Client cannot bypass scoping with arbitrary query parameters.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from api.v1.permissions.staff import IsCMSStaffUser
from api.v1.services.dashboard_service import DashboardAnalyticsService


class CMSDashboardAnalyticsView(APIView):
    """
    GET /api/cms/v1/dashboard/analytics/
    Returns summary cards, status distribution, type/subtype distribution,
    and adaptive time trend data strictly scoped to the authenticated user.
    """
    permission_classes = [IsAuthenticated, IsCMSStaffUser]

    def get(self, request):
        try:
            data = DashboardAnalyticsService.get_analytics(request.user, request.query_params)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Unable to calculate analytics for the requested period.",
                    "detail": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
