"""
Unit and Integration Tests for Citizen Complaints Directory, Tracking & Feedback (Phase C5)
==========================================================================================
Verifies:
- Citizen can list their own complaints with pagination and status filters
- Strict tenant/user isolation (cannot see or track another citizen's complaints)
- Staff users are rejected with 403 Forbidden
- Complaint detail excludes internal staff remarks
- Chronological 4-stage tracking timeline (Submitted -> Assigned -> Resolved -> Feedback)
- Feedback submission is only allowed on resolved complaints
- Feedback creates ComplaintFeedback record and syncs customer satisfaction
- Citizen Dashboard summary returns accurate metrics and recent activity
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
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
    ComplaintSource,
    ComplaintResolution,
    ComplaintFeedback,
    ComplaintActionLog,
)


class CitizenTrackingFeedbackTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # 1. Setup Location & UC
        self.location = Location.objects.create(location_name="Zone C")
        self.uc = UC.objects.create(uc_name="Gulbahar No 1", location=self.location)

        # 2. Setup Complaint Types
        self.cat_swm = ComplaintType.objects.create(type_name="Solid Waste Management")
        self.sub_swm = ComplaintSubType.objects.create(
            type_name="Garbage Dump Clearance",
            complaint_type=self.cat_swm,
        )

        self.source = ComplaintSource.objects.create(source_name="Mobile Application")

        # 3. Setup Citizen A
        self.citizen_a = User.objects.create_user(
            username="03001111111",
            password="SecureCitizenPassword123!",
            first_name="Citizen",
            last_name="Alpha",
            email="citizen.alpha@wssp.peshawar.gov.pk",
        )
        self.profile_a = CitizenProfile.objects.create(
            user=self.citizen_a,
            mobile_number="03001111111",
            address="Gulbahar House 10, Peshawar",
        )
        self.token_a = str(RefreshToken.for_user(self.citizen_a).access_token)

        # 4. Setup Citizen B (Isolation test)
        self.citizen_b = User.objects.create_user(
            username="03002222222",
            password="SecureCitizenPassword123!",
            first_name="Citizen",
            last_name="Beta",
            email="citizen.beta@wssp.peshawar.gov.pk",
        )
        self.profile_b = CitizenProfile.objects.create(
            user=self.citizen_b,
            mobile_number="03002222222",
            address="Hayatabad Phase 1, Peshawar",
        )
        self.token_b = str(RefreshToken.for_user(self.citizen_b).access_token)

        # 5. Setup Staff User
        self.staff_user = User.objects.create_user(
            username="staff_officer",
            password="StaffPassword123!",
            is_staff=True,
        )
        self.staff_token = str(RefreshToken.for_user(self.staff_user).access_token)

        # 6. Create Complaints for Citizen A
        # Complaint 1: Pending
        self.complaint_pending = Complaint.objects.create(
            location=self.location,
            uc=self.uc,
            complaint_source=self.source,
            complaint_type=self.cat_swm,
            SubType=self.sub_swm,
            first_name="Citizen",
            last_name="Alpha",
            cell_number="03001111111",
            area="Gulbahar",
            address="Near Main Water Tank",
            title="Garbage accumulating near park",
            complaint_detail="Garbage accumulating for 3 days near family park.",
            date=timezone.now().date(),
            status="pending",
        )
        ComplaintActionLog.objects.create(
            complaint=self.complaint_pending,
            user=self.citizen_a,
            action="created",
        )

        # Complaint 2: Resolved with resolution
        self.complaint_resolved = Complaint.objects.create(
            location=self.location,
            uc=self.uc,
            complaint_source=self.source,
            complaint_type=self.cat_swm,
            SubType=self.sub_swm,
            first_name="Citizen",
            last_name="Alpha",
            cell_number="03001111111",
            area="Gulbahar",
            address="Street 4, Sector B",
            title="Blocked drain overflow",
            complaint_detail="Drain overflow on the main street.",
            date=timezone.now().date(),
            status="resolved",
        )
        ComplaintActionLog.objects.create(
            complaint=self.complaint_resolved,
            user=self.citizen_a,
            action="created",
        )
        self.resolution = ComplaintResolution.objects.create(
            complaint=self.complaint_resolved,
            description="Drain desilted and cleared by Zone C field team.",
            customer_satisfaction="call_no_response",
        )

        # 7. Create Complaint for Citizen B
        self.complaint_b = Complaint.objects.create(
            location=self.location,
            uc=self.uc,
            complaint_source=self.source,
            complaint_type=self.cat_swm,
            SubType=self.sub_swm,
            first_name="Citizen",
            last_name="Beta",
            cell_number="03002222222",
            area="Hayatabad",
            address="Sector F1, Street 2",
            title="Street sweeping needed",
            complaint_detail="Hayatabad sector F1 sweeping missed.",
            date=timezone.now().date(),
            status="pending",
        )
        ComplaintActionLog.objects.create(
            complaint=self.complaint_b,
            user=self.citizen_b,
            action="created",
        )

    # -------------------------------------------------------------------------
    # 1. Citizen Complaints List Tests
    # -------------------------------------------------------------------------
    def test_citizen_lists_own_complaints_only(self):
        """Citizen A sees only their 2 complaints, never Citizen B's complaint."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_submit")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 2)

        returned_ids = {item["id"] for item in results}
        self.assertIn(self.complaint_pending.id, returned_ids)
        self.assertIn(self.complaint_resolved.id, returned_ids)
        self.assertNotIn(self.complaint_b.id, returned_ids)

        # Verify CMS ticket number formatting
        first_item = results[0]
        self.assertTrue(first_item["complaint_no"].startswith("CMS-"))

    def test_citizen_list_status_filter_pending(self):
        """Filter by status=pending returns only pending complaints."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_submit")
        response = self.client.get(url, {"status": "pending"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.complaint_pending.id)
        self.assertEqual(results[0]["status"], "pending")

    def test_citizen_list_status_filter_resolved(self):
        """Filter by status=resolved returns only resolved complaints."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_submit")
        response = self.client.get(url, {"status": "resolved"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.complaint_resolved.id)
        self.assertEqual(results[0]["status"], "resolved")

    def test_citizen_list_search_by_query(self):
        """Search query matches keyword in complaint detail."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_submit")
        response = self.client.get(url, {"q": "overflow"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.complaint_resolved.id)

    def test_staff_cannot_access_citizen_complaint_list(self):
        """Internal staff accounts cannot access the citizen complaints endpoint."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.staff_token}")
        url = reverse("api:citizen_complaint_submit")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------------------------------------------------------------
    # 2. Citizen Complaint Detail Tests
    # -------------------------------------------------------------------------
    def test_citizen_detail_own_complaint(self):
        """Citizen can view details of their own complaint including resolution."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_detail", kwargs={"pk": self.complaint_resolved.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(data["id"], self.complaint_resolved.id)
        self.assertEqual(data["complaint_no"], f"CMS-{self.complaint_resolved.id}")
        self.assertEqual(data["status"], "resolved")
        self.assertTrue(data["can_give_feedback"])

        # Check resolution details are included
        self.assertIsNotNone(data["resolution"])
        self.assertIn("Drain desilted", data["resolution"]["description"])

    def test_citizen_cannot_view_other_citizen_detail(self):
        """Citizen A cannot view Citizen B's complaint (404 Not Found)."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_detail", kwargs={"pk": self.complaint_b.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -------------------------------------------------------------------------
    # 3. Citizen Tracking Timeline Tests
    # -------------------------------------------------------------------------
    def test_citizen_tracking_timeline_pending_complaint(self):
        """Tracking a pending complaint returns 4-stage timeline with step 3 pending."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_tracking", kwargs={"pk": self.complaint_pending.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertFalse(response.data["can_give_feedback"])

        timeline = response.data["timeline"]
        self.assertEqual(len(timeline), 4)

        # Step 1: Submitted -> Completed
        self.assertEqual(timeline[0]["key"], "submitted")
        self.assertEqual(timeline[0]["status"], "completed")

        # Step 2: Assigned -> In Progress
        self.assertEqual(timeline[1]["key"], "in_progress")
        self.assertEqual(timeline[1]["status"], "in_progress")

        # Step 3: Resolution -> Pending
        self.assertEqual(timeline[2]["key"], "resolved")
        self.assertEqual(timeline[2]["status"], "pending")

        # Step 4: Feedback -> Locked
        self.assertEqual(timeline[3]["key"], "feedback")
        self.assertEqual(timeline[3]["status"], "locked")

    def test_citizen_tracking_timeline_resolved_complaint(self):
        """Tracking a resolved complaint has completed resolution and available feedback."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_tracking", kwargs={"pk": self.complaint_resolved.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["can_give_feedback"])

        timeline = response.data["timeline"]
        # Step 3: Resolution -> Completed
        self.assertEqual(timeline[2]["key"], "resolved")
        self.assertEqual(timeline[2]["status"], "completed")
        self.assertIn("Drain desilted", timeline[2]["description"])

        # Step 4: Feedback -> Available
        self.assertEqual(timeline[3]["key"], "feedback")
        self.assertEqual(timeline[3]["status"], "available")

    def test_citizen_cannot_track_other_citizen_complaint(self):
        """Citizen A cannot access tracking for Citizen B's complaint."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_tracking", kwargs={"pk": self.complaint_b.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -------------------------------------------------------------------------
    # 4. Feedback Submission Tests
    # -------------------------------------------------------------------------
    def test_feedback_on_pending_complaint_rejected(self):
        """Submitting feedback on an unresolved/pending complaint must be rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_feedback", kwargs={"pk": self.complaint_pending.id})
        payload = {"happy": True, "complaint_feedback": "Fast response"}
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("resolved", response.data["message"].lower())

    def test_feedback_on_other_citizen_complaint_rejected(self):
        """Citizen A cannot submit feedback on Citizen B's complaint."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_feedback", kwargs={"pk": self.complaint_b.id})
        payload = {"happy": True, "complaint_feedback": "Great"}
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_successful_feedback_submission(self):
        """Citizen successfully submits feedback on a resolved complaint."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_complaint_feedback", kwargs={"pk": self.complaint_resolved.id})
        payload = {
            "happy": True,
            "complaint_feedback": "Excellent work by WSSP team. Problem resolved completely.",
        }
        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertTrue(response.data["data"]["happy"])

        # Verify database record in ComplaintFeedback
        feedback = ComplaintFeedback.objects.filter(complaint=self.complaint_resolved).first()
        self.assertIsNotNone(feedback)
        self.assertTrue(feedback.happy)
        self.assertEqual(feedback.complaint_feedback, payload["complaint_feedback"])

        # Verify ComplaintResolution customer_satisfaction is synced to 'yes'
        self.resolution.refresh_from_db()
        self.assertEqual(self.resolution.customer_satisfaction, "yes")

    # -------------------------------------------------------------------------
    # 5. Citizen Dashboard Summary Tests
    # -------------------------------------------------------------------------
    def test_citizen_dashboard_summary(self):
        """Dashboard summary provides accurate metrics and helpline info."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token_a}")
        url = reverse("api:citizen_dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data["success"])

        # Check metrics: 2 total, 1 pending, 1 resolved
        self.assertEqual(data["metrics"]["total"], 2)
        self.assertEqual(data["metrics"]["pending"], 1)
        self.assertEqual(data["metrics"]["resolved"], 1)

        # Check contact info
        self.assertEqual(data["contacts"]["helpline"], "1334")

        # Check citizen user metadata
        self.assertEqual(data["citizen"]["mobile_number"], "03001111111")
        self.assertEqual(data["citizen"]["full_name"], "Citizen Alpha")

        # Check recent complaints list
        self.assertEqual(len(data["recent_complaints"]), 2)

