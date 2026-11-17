"""
Automated Tests for Phase C2: Citizen Registration & Login WITHOUT OTP
=====================================================================
Covers:
- Registration validation (full_name, mobile_number, password, confirm_password)
- Password hashing & PBKDF2 verification (no plaintext passwords)
- Mobile format normalization (+923... and 03...)
- Duplicate mobile rejection
- Citizen login and JWT token issuance
- Account separation (Staff denied on Citizen login)
- Citizen logout
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from api.models import CitizenProfile
from Dashboard.models import Location, LocationPermission


class CitizenAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("api:citizen_register")
        self.login_url = reverse("api:citizen_login")
        self.logout_url = reverse("api:citizen_logout")

    def test_successful_citizen_registration(self):
        """Citizens can register with valid mobile and password without OTP."""
        payload = {
            "full_name": "Tariq Mehmood",
            "mobile_number": "03331234567",
            "password": "Password789!",
            "confirm_password": "Password789!",
            "email": "tariq@example.com",
            "address": "Sector F-3, Phase 6, Hayatabad, Peshawar",
        }
        response = self.client.post(self.register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get("success"))
        self.assertEqual(response.data.get("message"), "Your account has been created successfully.")

        # Verify DB records
        user = User.objects.get(username="03331234567")
        self.assertEqual(user.first_name, "Tariq")
        self.assertEqual(user.last_name, "Mehmood")
        self.assertEqual(user.email, "tariq@example.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("Password789!"))
        self.assertNotEqual(user.password, "Password789!")  # Securely hashed

        # Verify CitizenProfile
        profile = CitizenProfile.objects.get(user=user)
        self.assertEqual(profile.mobile_number, "03331234567")
        self.assertIn("Hayatabad", profile.address)

    def test_mobile_number_normalization_on_registration(self):
        """+92 prefix must normalize to standard 03XXXXXXXXX format."""
        payload = {
            "full_name": "Kamran Khan",
            "mobile_number": "+92345-9876543",
            "password": "SecurePass123!",
            "confirm_password": "SecurePass123!",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Username and profile must be normalized
        self.assertTrue(User.objects.filter(username="03459876543").exists())
        self.assertTrue(CitizenProfile.objects.filter(mobile_number="03459876543").exists())

    def test_duplicate_mobile_registration_rejected(self):
        """Cannot register twice with the same mobile number."""
        payload = {
            "full_name": "Original User",
            "mobile_number": "03121234567",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }
        resp1 = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Attempt duplicate registration
        resp2 = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(resp2.data.get("success"))
        self.assertIn("mobile_number", resp2.data.get("errors", {}))

    def test_password_mismatch_rejected(self):
        """Mismatched confirm_password must be rejected."""
        payload = {
            "full_name": "Test User",
            "mobile_number": "03009999999",
            "password": "Password123!",
            "confirm_password": "DifferentPassword123!",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirm_password", response.data.get("errors", {}))

    def test_short_password_rejected(self):
        """Passwords shorter than 8 characters must be rejected."""
        payload = {
            "full_name": "Test User",
            "mobile_number": "03009999999",
            "password": "short",
            "confirm_password": "short",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data.get("errors", {}))

    def test_invalid_mobile_format_rejected(self):
        """Invalid mobile numbers (wrong prefix, wrong length) must be rejected."""
        invalid_numbers = ["12345", "04001234567", "0300123456", "030012345678", "abcdefghijk"]
        for num in invalid_numbers:
            payload = {
                "full_name": "Invalid Tester",
                "mobile_number": num,
                "password": "Password123!",
                "confirm_password": "Password123!",
            }
            response = self.client.post(self.register_url, payload, format="json")
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                f"Failed to reject invalid mobile: {num}",
            )

    def test_successful_citizen_login(self):
        """Citizens can log in with their mobile number and password, receiving JWT."""
        # 1. Register
        user = User.objects.create_user(
            username="03015555555",
            password="ValidPassword123!",
            first_name="Asad",
            last_name="Ali",
            is_staff=False,
            is_superuser=False,
        )
        CitizenProfile.objects.create(
            user=user,
            mobile_number="03015555555",
            address="Gulbahar No. 2, Peshawar",
        )

        # 2. Login
        login_payload = {
            "mobile_number": "03015555555",
            "password": "ValidPassword123!",
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("success"))
        data = response.data.get("data", {})
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(data.get("user", {}).get("role"), "Citizen")
        self.assertEqual(data.get("user", {}).get("account_type"), "citizen")
        self.assertFalse(data.get("user", {}).get("is_staff"))

    def test_login_with_international_mobile_prefix(self):
        """Logging in with +92 prefix should match normalized username."""
        user = User.objects.create_user(
            username="03027777777",
            password="ValidPassword123!",
            first_name="Zahid",
            is_staff=False,
        )
        CitizenProfile.objects.create(user=user, mobile_number="03027777777")

        response = self.client.post(
            self.login_url,
            {"mobile_number": "+92302-7777777", "password": "ValidPassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data.get("data", {}))

    def test_login_with_wrong_password_fails(self):
        """Incorrect password returns 400."""
        User.objects.create_user(username="03008888888", password="CorrectPass123!")
        CitizenProfile.objects.create(user=User.objects.get(username="03008888888"), mobile_number="03008888888")

        response = self.client.post(
            self.login_url,
            {"mobile_number": "03008888888", "password": "WrongPassword999!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get("success"))

    def test_login_with_unknown_mobile_fails(self):
        """Non-existent mobile returns 400."""
        response = self.client.post(
            self.login_url,
            {"mobile_number": "03000000000", "password": "AnyPassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_account_denied_on_citizen_login(self):
        """Staff members cannot use the citizen login endpoint."""
        staff_user = User.objects.create_user(
            username="03001112233",
            password="StaffPassword123!",
            is_staff=True,
        )
        response = self.client.post(
            self.login_url,
            {"mobile_number": "03001112233", "password": "StaffPassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Staff members must log in through the WSSP Staff Portal", str(response.data))

    def test_location_permission_holder_denied_on_citizen_login(self):
        """Internal users with LocationPermission cannot use citizen login."""
        loc_user = User.objects.create_user(
            username="03004445566",
            password="OfficerPassword123!",
            is_staff=False,
        )
        loc = Location.objects.create(location_name="Zone B Test")
        perm = LocationPermission.objects.create(can_view=True)
        perm.user.add(loc_user)
        perm.locations.add(loc)

        response = self.client.post(
            self.login_url,
            {"mobile_number": "03004445566", "password": "OfficerPassword123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Staff members must log in through the WSSP Staff Portal", str(response.data))

    def test_citizen_logout(self):
        """Authenticated citizens can log out cleanly."""
        user = User.objects.create_user(
            username="03006667788",
            password="Password123!",
            is_staff=False,
        )
        CitizenProfile.objects.create(user=user, mobile_number="03006667788")

        # Login to get JWT
        login_resp = self.client.post(
            self.login_url,
            {"mobile_number": "03006667788", "password": "Password123!"},
            format="json",
        )
        token = login_resp.data["data"]["access"]
        refresh = login_resp.data["data"]["refresh"]

        # Logout with token in header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        logout_resp = self.client.post(self.logout_url, {"refresh": refresh}, format="json")
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)
        self.assertTrue(logout_resp.data.get("success"))

