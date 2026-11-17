"""
Automated Tests for Phase C4: Citizen Complaint Submission & Automatic Complaint Routing
========================================================================================
Covers:
- POST /api/citizen/v1/complaints/ (submission endpoint)
- Automatic Zone resolution from UC hierarchy
- GPS coordinates attachment
- Optional photograph upload (validation of size and extension)
- Subtype parent category mismatch rejection
- Short detail validation
- Audit logging (ComplaintActionLog action='created')
- Rapid duplicate submission prevention
- Access control (anonymous & staff rejected)
- Automatic routing verification in respective staff queues via scope_complaint_queryset
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import CitizenProfile
from Dashboard.models import (
    Complaint,
    ComplaintType,
    ComplaintSubType,
    Location,
    UC,
    LocationPermission,
    ComplaintActionLog,
)
from api.v1.permissions.base import scope_complaint_queryset


class CitizenComplaintSubmissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Create Citizen User
        self.citizen = User.objects.create_user(
            username="03339123456",
            password="Password123!",
            first_name="Noor",
            last_name="Rehman",
            email="noor@example.com",
            is_staff=False,
            is_superuser=False,
        )
        self.profile = CitizenProfile.objects.create(
            user=self.citizen,
            mobile_number="03339123456",
            address="Hayatabad Phase 4, Peshawar",
        )
        refresh = RefreshToken.for_user(self.citizen)
        self.citizen_token = str(refresh.access_token)

        # 2. Create Staff user
        self.staff_user = User.objects.create_user(
            username="officer_1",
            password="StaffPass123!",
            is_staff=True,
        )
        staff_refresh = RefreshToken.for_user(self.staff_user)
        self.staff_token = str(staff_refresh.access_token)

        # 3. Create Locations (Zones)
        self.zone_a = Location.objects.create(location_name="Zone A")
        self.zone_b = Location.objects.create(location_name="Zone B")
        self.headoffice = Location.objects.create(location_name="Head Office")

        # 4. Create UCs under Zones
        self.uc_a = UC.objects.create(uc_name="UC-01 Lahori Gate", location=self.zone_a)
        self.uc_b = UC.objects.create(uc_name="UC-25 Hayatabad", location=self.zone_b)

        # 5. Create Complaint Types & Subtypes
        self.type_swm = ComplaintType.objects.create(type_name="Solid Waste")
        self.type_ws = ComplaintType.objects.create(type_name="Water Supply")

        self.sub_swm = ComplaintSubType.objects.create(
            complaint_type=self.type_swm,
            type_name="Garbage Dump",
        )
        self.sub_ws = ComplaintSubType.objects.create(
            complaint_type=self.type_ws,
            type_name="Broken Pipeline",
        )

        # 6. Setup Staff for Automatic Routing Verification
        # SWM Manager Zone A
        self.swm_mgr_a = User.objects.create_user(username="mngra_swm", is_staff=True)
        perm_swm_a = LocationPermission.objects.create(can_view=True)
        perm_swm_a.user.add(self.swm_mgr_a)
        perm_swm_a.locations.add(self.zone_a)

        # Water Manager Zone A
        self.ws_mgr_a = User.objects.create_user(username="mngra_ws", is_staff=True)
        perm_ws_a = LocationPermission.objects.create(can_view=True)
        perm_ws_a.user.add(self.ws_mgr_a)
        perm_ws_a.locations.add(self.zone_a)

        # SWM Manager Zone B
        self.swm_mgr_b = User.objects.create_user(username="mngrb_swm", is_staff=True)
        perm_swm_b = LocationPermission.objects.create(can_view=True)
        perm_swm_b.user.add(self.swm_mgr_b)
        perm_swm_b.locations.add(self.zone_b)

        # Zonal Manager A (sees all types in Zone A)
        self.zm_a = User.objects.create_user(username="zma", is_staff=True)
        perm_zm_a = LocationPermission.objects.create(can_view=True)
        perm_zm_a.user.add(self.zm_a)
        perm_zm_a.locations.add(self.zone_a)

        # Head Office Executive (superuser or sees all)
        self.ho_exec = User.objects.create_superuser(username="ccho_admin", email="ccho@wssp.gov.pk")

        self.submit_url = reverse("api:citizen_complaint_submit")

    def test_successful_complaint_submission(self):
        """Citizen can successfully submit a complaint with required fields."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        payload = {
            "complaint_type_id": self.type_swm.id,
            "subtype_id": self.sub_swm.id,
            "uc_id": self.uc_a.id,
            "area": "Lahori Gate Market",
            "address": "Shop 4, Main Bazar, Lahori Gate",
            "complaint_detail": "Large pile of municipal garbage accumulated on the street corner.",
        }
        response = self.client.post(self.submit_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get("success"))
        data = response.data.get("data", {})
        self.assertTrue(data.get("complaint_no").startswith("CMS-"))
        self.assertEqual(data.get("category"), "Solid Waste")
        self.assertEqual(data.get("subcategory"), "Garbage Dump")
        self.assertEqual(data.get("location_name"), "Zone A")  # Auto-resolved from UC
        self.assertEqual(data.get("uc_name"), "UC-01 Lahori Gate")
        self.assertEqual(data.get("status"), "pending")

        # Verify DB Persistence
        complaint = Complaint.objects.get(id=data["id"])
        self.assertEqual(complaint.cell_number, "03339123456")
        self.assertEqual(complaint.first_name, "Noor")
        self.assertEqual(complaint.last_name, "Rehman")
        self.assertEqual(complaint.location, self.zone_a)
        self.assertEqual(complaint.uc, self.uc_a)
        self.assertEqual(complaint.status, "pending")

        # Verify Audit Log
        action_log = ComplaintActionLog.objects.filter(complaint=complaint, action="created").first()
        self.assertIsNotNone(action_log)
        self.assertEqual(action_log.user, self.citizen)

    def test_submission_with_gps_coordinates(self):
        """GPS coordinates are captured in the address."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        payload = {
            "complaint_type_id": self.type_swm.id,
            "subtype_id": self.sub_swm.id,
            "uc_id": self.uc_a.id,
            "address": "Street 2, Near Water Tank",
            "complaint_detail": "Overflowing waste bin causing blockage on the road.",
            "latitude": "34.015200",
            "longitude": "71.524900",
        }
        response = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        complaint = Complaint.objects.get(id=response.data["data"]["id"])
        self.assertIn("[GPS: 34.015200, 71.524900]", complaint.address)

    def test_submission_with_image_upload(self):
        """Citizen can upload an image with their complaint."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        fake_image = SimpleUploadedFile("waste.jpg", b"fake_jpeg_content", content_type="image/jpeg")

        payload = {
            "complaint_type_id": self.type_swm.id,
            "subtype_id": self.sub_swm.id,
            "uc_id": self.uc_a.id,
            "address": "Main Street",
            "complaint_detail": "Photo attached of the accumulated solid waste.",
            "before_image": fake_image,
        }
        response = self.client.post(self.submit_url, payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        complaint = Complaint.objects.get(id=response.data["data"]["id"])
        self.assertTrue(bool(complaint.before_image))
        self.assertIn("waste", complaint.before_image.name)

    def test_invalid_image_extension_rejected(self):
        """Uploading non-image files (.exe, .pdf, etc.) must be rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        fake_file = SimpleUploadedFile("script.exe", b"malicious_bytes", content_type="application/octet-stream")

        payload = {
            "complaint_type_id": self.type_swm.id,
            "uc_id": self.uc_a.id,
            "complaint_detail": "Trying to upload invalid file.",
            "before_image": fake_file,
        }
        response = self.client.post(self.submit_url, payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("before_image", str(response.data))

    def test_subtype_mismatch_rejected(self):
        """Subcategory belonging to a different category must be rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        payload = {
            "complaint_type_id": self.type_swm.id,  # Solid Waste
            "subtype_id": self.sub_ws.id,           # Broken Pipeline (Water Supply)
            "uc_id": self.uc_a.id,
            "complaint_detail": "Testing mismatch between type and subtype.",
        }
        response = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("subtype_id", str(response.data))

    def test_invalid_complaint_type_rejected(self):
        """Non-existent complaint type ID must be rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        payload = {
            "complaint_type_id": 99999,
            "uc_id": self.uc_a.id,
            "complaint_detail": "Testing non-existent category.",
        }
        response = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_uc_rejected(self):
        """Non-existent UC ID must be rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        payload = {
            "complaint_type_id": self.type_swm.id,
            "uc_id": 99999,
            "complaint_detail": "Testing non-existent Union Council.",
        }
        response = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_detail_rejected(self):
        """Complaint description shorter than 10 characters must be rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        payload = {
            "complaint_type_id": self.type_swm.id,
            "uc_id": self.uc_a.id,
            "complaint_detail": "Short",
        }
        response = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("complaint_detail", str(response.data))

    def test_anonymous_submission_denied(self):
        """Unauthenticated caller cannot submit complaints."""
        payload = {
            "complaint_type_id": self.type_swm.id,
            "uc_id": self.uc_a.id,
            "complaint_detail": "Anonymous attempt to submit.",
        }
        response = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_submission_denied(self):
        """Staff members are rejected from citizen submission endpoint."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.staff_token}")
        payload = {
            "complaint_type_id": self.type_swm.id,
            "uc_id": self.uc_a.id,
            "complaint_detail": "Staff attempt to submit on citizen API.",
        }
        response = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_automatic_complaint_routing_to_staff_queues(self):
        """
        Validates core routing rule:
        Solid Waste + Zone A must route to:
        - SWM Manager A (YES)
        - Zonal Manager A (YES)
        - Head Office (YES)
        - Water Manager A (NO)
        - SWM Manager B (NO)
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        payload = {
            "complaint_type_id": self.type_swm.id,
            "subtype_id": self.sub_swm.id,
            "uc_id": self.uc_a.id,
            "address": "Routing Test Location",
            "complaint_detail": "Automated routing test complaint for Solid Waste in Zone A.",
        }
        response = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        complaint_id = response.data["data"]["id"]
        complaint = Complaint.objects.get(id=complaint_id)

        # 1. SWM Manager A (Solid Waste + Zone A) -> MUST SEE
        qs_swm_a = scope_complaint_queryset(self.swm_mgr_a)
        self.assertIn(complaint, qs_swm_a)

        # 2. Water Manager A (Water Supply + Zone A) -> MUST NOT SEE
        qs_ws_a = scope_complaint_queryset(self.ws_mgr_a)
        self.assertNotIn(complaint, qs_ws_a)

        # 3. SWM Manager B (Solid Waste + Zone B) -> MUST NOT SEE
        qs_swm_b = scope_complaint_queryset(self.swm_mgr_b)
        self.assertNotIn(complaint, qs_swm_b)

        # 4. Zonal Manager A (All types in Zone A) -> MUST SEE
        qs_zm_a = scope_complaint_queryset(self.zm_a)
        self.assertIn(complaint, qs_zm_a)

        # 5. Head Office Executive -> MUST SEE
        qs_ho = scope_complaint_queryset(self.ho_exec)
        self.assertIn(complaint, qs_ho)

    def test_duplicate_submission_prevention(self):
        """Submitting an identical complaint twice within 60s is blocked."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.citizen_token}")
        payload = {
            "complaint_type_id": self.type_swm.id,
            "subtype_id": self.sub_swm.id,
            "uc_id": self.uc_a.id,
            "complaint_detail": "Identical complaint submitted in rapid succession.",
        }
        # First submission succeeds
        resp1 = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Second submission immediately rejected
        resp2 = self.client.post(self.submit_url, payload, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("identical details was just submitted", str(resp2.data))

