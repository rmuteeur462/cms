from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ApiStatusCheck, dshbMonthWiseData
from . import views
from .cms_auth import CMSLoginView, CMSUserProfileView, CMSSecurityTestView

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
]
