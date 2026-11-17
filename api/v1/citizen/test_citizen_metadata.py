"""
Automated Tests for Phase C3: Citizen Profile & Dynamic Metadata APIs
====================================================================
Covers:
- GET /api/citizen/v1/profile/ (profile retrieval)
- PATCH /api/citizen/v1/profile/ (partial profile update: full_name, email, address)
- GET /api/citizen/v1/complaint-types/ (dynamic complaint categories)
- GET /api/citizen/v1/subtypes/ (cascading subcategories by type_id)
- GET /api/citizen/v1/locations/ (operational zones, head office excluded by default)
- GET /api/citizen/v1/ucs/ (cascading UCs by location_id)
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import CitizenProfile
from Dashboard.models import ComplaintType, ComplaintSubType, Location, UC


class CitizenMetadataTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Create a Citizen
        self.citizen_user = User.objects.create_user(
            username="03009876543",
            password="SecurePass123!",
            first_name="Haroon",
            last_name="Bilal",
            email="haroon@example.com",
            is_staff=False,
            is_superuser=False,
        )
        self.profile = CitizenProfile.objects.create(
            user=self.citizen_user,
            mobile_number="03009876543",
            address="University Town, Peshawar",
        )
        refresh = RefreshToken.for_user(self.citizen_user)
        self.citizen_token = str(refresh.access_token)

        # 2. Create Staff user
        self.staff_user = User.objects.create_user(
            username="wssp_staff_1",
            password="StaffPass123!",
            is_staff=True,
        )
        staff_refresh = RefreshToken.for_user(self.staff_user)
        self.staff_token = str(staff_refresh.access_token)

        # 3. Create Taxonomy Data (Complaint Types & Subtypes)
        self.type_swm = ComplaintType.objects.create(type_name="Solid Waste Management")
        self.type_ws = ComplaintType.objects.create(type_name="Water Supply")

        self.sub_swm_1 = ComplaintSubType.objects.create(
            complaint_type=self.type_swm,
            type_name="Garbage Dump / Heap",
        )
        self.sub_swm_2 = ComplaintSubType.objects.create(
            complaint_type=self.type_swm,
            type_name="Missed Waste Collection",
        )
        self.sub_ws_1 = ComplaintSubType.objects.create(
            complaint_type=self.type_ws,
            type_name="Pipeline Leakage",
        )

        # 4. Create Locations (Zones & Head Office) & UCs
        self.zone_a = Location.objects.create(location_name="Zone A")
        self.zone_b = Location.objects.create(location_name="Zone B")
        self.headoffice = Location.objects.create(location_name="Head Office")

        self.uc_a1 = UC.objects.create(uc_name="UC-01 City", location=self.zone_a)
        self.uc_a2 = UC.objects.create(uc_name="UC-02 Ganj", location=self.zone_a)
        self.uc_b1 = UC.objects.create(uc_name="UC-30 Hayatabad", location=self.zone_b)

        # URLs
        self.profile_url = reverse("api:citizen_profile")
        self.types_url = reverse("api:citizen_complaint_types")
        self.subtypes_url = reverse("api:citizen_subtypes")
        self.locations_url = reverse("api:citizen_locations")
        self.ucs_url = reverse("api:citizen_ucs")

    def test_get_citizen_profile_authenticated(self):
        """Authenticated citizen can retrieve their own profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("success"))
        data = response.data.get("data", {})
        self.assertEqual(data.get("mobile_number"), "03009876543")
        self.assertEqual(data.get("full_name"), "Haroon Bilal")
        self.assertEqual(data.get("email"), "haroon@example.com")
        self.assertEqual(data.get("address"), "University Town, Peshawar")
        self.assertEqual(data.get("role"), "Citizen")
        self.assertEqual(data.get("account_type"), "citizen")

    def test_get_citizen_profile_anonymous_denied(self):
        """Unauthenticated caller cannot view profile."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_citizen_profile_staff_denied(self):
        """Staff members are rejected from citizen profile endpoint."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.staff_token}")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_citizen_profile_success(self):
        """Citizen can update address, full_name, and email."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        patch_payload = {
            "full_name": "Haroon Khan Bilal",
            "email": "haroon.updated@example.com",
            "address": "House 12, Street 4, Hayatabad Phase 2, Peshawar",
        }
        response = self.client.patch(self.profile_url, patch_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("success"))
        data = response.data.get("data", {})
        self.assertEqual(data.get("full_name"), "Haroon Khan Bilal")
        self.assertEqual(data.get("email"), "haroon.updated@example.com")
        self.assertIn("Hayatabad Phase 2", data.get("address"))

        # Verify DB persisted
        self.citizen_user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.citizen_user.first_name, "Haroon")
        self.assertEqual(self.citizen_user.last_name, "Khan Bilal")
        self.assertEqual(self.citizen_user.email, "haroon.updated@example.com")
        self.assertEqual(self.profile.address, "House 12, Street 4, Hayatabad Phase 2, Peshawar")

    def test_patch_profile_cannot_change_mobile_number(self):
        """Mobile number is read-only and cannot be changed via profile update."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        response = self.client.patch(
            self.profile_url,
            {"mobile_number": "03000000000"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.mobile_number, "03009876543")  # Unchanged

    def test_get_complaint_types(self):
        """Complaint types are dynamically returned from database."""
        response = self.client.get(self.types_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("success"))
        names = [item["type_name"] for item in response.data.get("data", [])]
        self.assertIn("Solid Waste Management", names)
        self.assertIn("Water Supply", names)

    def test_get_subtypes_all(self):
        """Subtypes list returns all subcategories when unconstrained."""
        response = self.client.get(self.subtypes_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data.get("count", 0), 3)

    def test_get_subtypes_cascading(self):
        """Subtypes list cascades strictly by parent category type_id."""
        response = self.client.get(f"{self.subtypes_url}?type_id={self.type_swm.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", [])
        self.assertEqual(len(data), 2)
        names = [item["type_name"] for item in data]
        self.assertIn("Garbage Dump / Heap", names)
        self.assertIn("Missed Waste Collection", names)
        self.assertNotIn("Pipeline Leakage", names)

    def test_get_locations_excludes_headoffice(self):
        """Locations endpoint lists municipal operational zones and excludes Head Office."""
        response = self.client.get(self.locations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["location_name"] for item in response.data.get("data", [])]
        self.assertIn("Zone A", names)
        self.assertIn("Zone B", names)
        self.assertNotIn("Head Office", names)

    def test_get_locations_include_all(self):
        """?include_all=true includes administrative Head Office."""
        response = self.client.get(f"{self.locations_url}?include_all=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["location_name"] for item in response.data.get("data", [])]
        self.assertIn("Head Office", names)

    def test_get_ucs_cascading(self):
        """UCs list cascades strictly by location_id."""
        response = self.client.get(f"{self.ucs_url}?location_id={self.zone_a.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("data", [])
        self.assertEqual(len(data), 2)
        names = [item["uc_name"] for item in data]
        self.assertIn("UC-01 City", names)
        self.assertIn("UC-02 Ganj", names)
        self.assertNotIn("UC-30 Hayatabad", names)

