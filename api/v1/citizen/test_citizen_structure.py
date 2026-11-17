"""
Tests for Phase C1: Citizen API Structure & Base Permissions
============================================================
Verifies:
1. URL resolution for citizen v1 namespace.
2. Health check endpoint (GET /api/citizen/v1/status/).
3. IsCitizenUser permission enforcement:
   - Citizens granted access.
   - Staff, superusers, and users with LocationPermission denied.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from rest_framework import status

from Dashboard.models import Location, LocationPermission
from api.v1.permissions.citizen import IsCitizenUser
from api.v1.citizen.urls import CitizenStatusView


class CitizenStructureTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.permission = IsCitizenUser()

        # Regular Citizen user
        self.citizen = User.objects.create_user(
            username="03001234567",
            password="StrongPassword123!",
            first_name="Ahmad",
            last_name="Khan",
            is_staff=False,
            is_superuser=False,
        )

        # Staff user
        self.staff_user = User.objects.create_user(
            username="staff_officer",
            password="StrongPassword123!",
            is_staff=True,
            is_superuser=False,
        )

        # Superuser
        self.admin_user = User.objects.create_superuser(
            username="wssp_admin",
            password="StrongPassword123!",
            email="admin@wssp.gov.pk",
        )

        # User with LocationPermission (Internal WSSP Staff)
        self.location_user = User.objects.create_user(
            username="zonal_inspector",
            password="StrongPassword123!",
            is_staff=False,
            is_superuser=False,
        )
        self.location = Location.objects.create(location_name="Zone Test A")
        self.loc_perm = LocationPermission.objects.create(can_view=True)
        self.loc_perm.user.add(self.location_user)
        self.loc_perm.locations.add(self.location)

    def test_citizen_status_endpoint(self):
        """Verifies GET /api/citizen/v1/status/ returns 200 with service metadata."""
        request = self.factory.get("/api/citizen/v1/status/")
        view = CitizenStatusView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("success"))
        self.assertEqual(response.data.get("service"), "WSSP Citizen Portal API")
        self.assertEqual(response.data.get("version"), "v1")
        self.assertEqual(response.data.get("auth_type"), "mobile_password")
        self.assertFalse(response.data.get("otp_required"))

    def test_is_citizen_permission_allows_citizen(self):
        """Citizens must be granted access by IsCitizenUser."""
        request = self.factory.get("/api/citizen/v1/status/")
        request.user = self.citizen
        self.assertTrue(self.permission.has_permission(request, None))

    def test_is_citizen_permission_denies_anonymous(self):
        """Unauthenticated requests must be denied by IsCitizenUser."""
        request = self.factory.get("/api/citizen/v1/status/")
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))

    def test_is_citizen_permission_denies_staff(self):
        """Staff members must be denied by IsCitizenUser."""
        request = self.factory.get("/api/citizen/v1/status/")
        request.user = self.staff_user
        self.assertFalse(self.permission.has_permission(request, None))

    def test_is_citizen_permission_denies_superuser(self):
        """Superusers must be denied by IsCitizenUser."""
        request = self.factory.get("/api/citizen/v1/status/")
        request.user = self.admin_user
        self.assertFalse(self.permission.has_permission(request, None))

    def test_is_citizen_permission_denies_location_permission_holders(self):
        """Users with internal LocationPermission must be denied by IsCitizenUser."""
        request = self.factory.get("/api/citizen/v1/status/")
        request.user = self.location_user
        self.assertFalse(self.permission.has_permission(request, None))

