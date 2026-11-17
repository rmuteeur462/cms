from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ApiStatusCheck, dshbMonthWiseData
from . import views
from .cms_auth import CMSLoginView, CMSUserProfileView, CMSSecurityTestView
from .cms_views import (
    CMSDashboardView, CMSComplaintListView, CMSComplaintDetailView,
    CMSComplaintOptionsView, CMSComplaintCreateView
)

app_name = "api"

urlpatterns = [
    # Legacy Fintech APIs
    path("ApiStatusCheck", ApiStatusCheck),
    path("dshbMonthWiseData", dshbMonthWiseData),
    path("revenue/dashboard/", views.revenuedashboard, name="dashboard"),

    # WSSP CMS Mobile Authentication & Security APIs
    path("cms/auth/login/", CMSLoginView.as_view(), name="cms_login"),
    path("cms/auth/refresh/", TokenRefreshView.as_view(), name="cms_token_refresh"),
    path("cms/auth/me/", CMSUserProfileView.as_view(), name="cms_user_profile"),
    path("cms/auth/test-security/", CMSSecurityTestView.as_view(), name="cms_security_test"),

    # WSSP CMS Mobile Data APIs
    path("cms/dashboard/", CMSDashboardView.as_view(), name="cms_dashboard"),
    path("cms/complaints/", CMSComplaintListView.as_view(), name="cms_complaints"),
    path("cms/complaints/<int:complaint_id>/", CMSComplaintDetailView.as_view(), name="cms_complaint_detail"),
    path("cms/complaints/options/", CMSComplaintOptionsView.as_view(), name="cms_complaint_options"),
    path("cms/complaints/create/", CMSComplaintCreateView.as_view(), name="cms_complaint_create"),

    # WSSP CMS API v1 Modular Namespace
    path("cms/v1/", include("api.v1.urls")),

    # WSSP Citizen Portal API v1 Modular Namespace
    path("citizen/v1/", include("api.v1.citizen.urls")),
    path("cms/v1/citizen/", include("api.v1.citizen.urls")),
]
