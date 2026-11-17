"""
Phase C7 — Security & Regression Tests
======================================
Tests:
  GROUP 1: Citizens cannot access staff APIs (using citizen token against cms endpoints)
  GROUP 2: Staff (superuser) cannot access citizen APIs (403 from IsCitizenUser)
  GROUP 3: Cross-citizen data isolation (Citizen A cannot see Citizen B's data)
  GROUP 4: Unauthenticated requests are rejected from protected citizen endpoints
  GROUP 5: Public citizen endpoints remain accessible to anyone
  GROUP 6: Citizen login regression — returns account_type=citizen, is_staff=False
  GROUP 7: Staff superuser login regression — /api/cms/auth/login/ still works unchanged

NOTES ON SYSTEM DESIGN:
- Staff login (/api/cms/auth/login/) requires is_superuser=True OR a LocationPermission with
  can_view=True. A bare is_staff=True user without either gets 403 — this is correct behavior.
- IsCitizenUser rejects: is_staff=True, is_superuser=True, or has a LocationPermission record.
- The citizen JWT uses Bearer scheme (same as staff JWT).
- Citizen login response wraps payload: { success, message, data: { access, refresh, user } }
- Staff login response is flat: { access, refresh, user, message }
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from api.models import CitizenProfile
from Dashboard.models import (
    Complaint, ComplaintType, ComplaintSubType, Location, UC, LocationPermission,
)

User = get_user_model()


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _make_citizen(mobile: str, password: str = 'Test@12345', name: str = 'Test Citizen') -> User:
    """
    Create a citizen user that matches how CitizenRegisterView creates accounts.
    The citizen login serializer calls authenticate(username=normalized_mobile, password=...)
    so the Django username MUST equal the mobile number itself.
    """
    user = User.objects.create_user(
        username=mobile,       # mobile number IS the Django username for citizens
        password=password,
        first_name=name,
        is_staff=False,
        is_superuser=False,
    )
    CitizenProfile.objects.create(user=user, mobile_number=mobile)
    return user


def _make_superuser_staff(username: str, password: str = 'Staff@12345') -> User:
    """
    Create a superuser — the only staff type that can log in without LocationPermission.
    is_superuser grants full CMS access via CMSLoginView's has_cms_access check.
    """
    return User.objects.create_superuser(
        username=username,
        password=password,
        email=f'{username}@wssp.gov.pk',
    )


def _citizen_bearer_token(mobile: str, password: str = 'Test@12345') -> str | None:
    """
    Log in as citizen and return the Bearer token string, or None on failure.
    Citizen login response wraps data: { success, message, data: { access, refresh, user } }
    """
    anon = APIClient()
    resp = anon.post(
        '/api/citizen/v1/login/',
        {'mobile_number': mobile, 'password': password},
        format='json',
    )
    if resp.status_code == 200:
        # Try flat response first, then wrapped
        token = (
            resp.data.get('access')
            or resp.data.get('token')
            or (resp.data.get('data') or {}).get('access')
            or (resp.data.get('data') or {}).get('token')
        )
        return token
    return None


def _staff_bearer_token(username: str, password: str = 'Staff@12345') -> str | None:
    """
    Log in as staff and return the Bearer token string, or None on failure.
    Staff login response is flat: { access, refresh, user, message }
    """
    anon = APIClient()
    resp = anon.post(
        '/api/cms/auth/login/',
        {'username': username, 'password': password},
        format='json',
    )
    if resp.status_code == 200:
        return resp.data.get('access') or resp.data.get('token')
    return None


def _authed_client(token: str) -> APIClient:
    """Return an APIClient authenticated with the given Bearer token."""
    client = APIClient()
    if token:
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


def _extract_citizen_response_data(resp_data: dict) -> dict:
    """
    Citizen login wraps response: { success, message, data: { access, refresh, user } }.
    Returns the inner 'data' dict, or the response itself if already flat.
    """
    if 'data' in resp_data and isinstance(resp_data['data'], dict):
        return resp_data['data']
    return resp_data


# ──────────────────────────────────────────────────────────────
# GROUP 1: Citizen cannot access staff (CMS) APIs
# ──────────────────────────────────────────────────────────────

class CitizenCannotAccessStaffAPIsTest(TestCase):
    """
    A valid citizen JWT must be rejected by every staff-only CMS endpoint.
    CMS views use [IsAuthenticated, IsCMSAuthorized].
    IsCMSAuthorized checks: is_superuser OR len(allowed_location_ids) > 0.
    Citizens have neither → 403.
    """

    def setUp(self):
        self.user = _make_citizen('03111000001')
        self.token = _citizen_bearer_token('03111000001')
        self.assertIsNotNone(self.token, "Pre-condition: citizen token must be obtained")
        self.client = _authed_client(self.token)

    def test_citizen_cannot_list_cms_complaints(self):
        """GET /api/cms/complaints/ → 403 for citizen."""
        resp = self.client.get('/api/cms/complaints/')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")

    def test_citizen_cannot_access_cms_dashboard(self):
        """GET /api/cms/dashboard/ → 403 for citizen."""
        resp = self.client.get('/api/cms/dashboard/')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")

    def test_citizen_cannot_create_cms_complaint(self):
        """POST /api/cms/complaints/create/ → 403 for citizen."""
        resp = self.client.post('/api/cms/complaints/create/', {}, format='json')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")

    def test_citizen_cannot_access_cms_complaint_detail(self):
        """GET /api/cms/complaints/1/ → 403 for citizen (not 200 or 404)."""
        resp = self.client.get('/api/cms/complaints/1/')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")

    def test_citizen_cannot_access_cms_v1_analytics(self):
        """GET /api/cms/v1/ — analytics endpoint must reject citizens with 403."""
        resp = self.client.get('/api/cms/v1/dashboard/analytics/')
        self.assertIn(resp.status_code, [403, 404],
                      f"Expected 403/404, got {resp.status_code}: {resp.data}")


# ──────────────────────────────────────────────────────────────
# GROUP 2: Staff superuser cannot access citizen APIs
# ──────────────────────────────────────────────────────────────

class StaffCannotAccessCitizenAPIsTest(TestCase):
    """
    A valid staff JWT (superuser) must be rejected by IsCitizenUser on all citizen endpoints.
    IsCitizenUser denies: is_superuser=True, is_staff=True, or has LocationPermission.
    Expected: 403
    """

    def setUp(self):
        self.staff = _make_superuser_staff('staff_c7_super')
        self.token = _staff_bearer_token('staff_c7_super')
        self.assertIsNotNone(self.token, "Pre-condition: staff token must be obtained")
        self.client = _authed_client(self.token)

    def test_staff_cannot_list_citizen_complaints(self):
        """GET /api/citizen/v1/complaints/ → 403 for staff."""
        resp = self.client.get('/api/citizen/v1/complaints/')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")

    def test_staff_cannot_post_citizen_complaint(self):
        """POST /api/citizen/v1/complaints/ → 403 for staff."""
        resp = self.client.post('/api/citizen/v1/complaints/', {}, format='json')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")

    def test_staff_cannot_access_citizen_profile(self):
        """GET /api/citizen/v1/profile/ → 403 for staff."""
        resp = self.client.get('/api/citizen/v1/profile/')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")

    def test_staff_cannot_access_citizen_dashboard(self):
        """GET /api/citizen/v1/dashboard/ → 403 for staff."""
        resp = self.client.get('/api/citizen/v1/dashboard/')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")

    def test_staff_cannot_view_complaint_tracking(self):
        """GET /api/citizen/v1/complaints/1/tracking/ → 403 for staff."""
        resp = self.client.get('/api/citizen/v1/complaints/1/tracking/')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")

    def test_staff_cannot_post_complaint_feedback(self):
        """POST /api/citizen/v1/complaints/1/feedback/ → 403 for staff."""
        resp = self.client.post('/api/citizen/v1/complaints/1/feedback/', {}, format='json')
        self.assertEqual(resp.status_code, 403,
                         f"Expected 403, got {resp.status_code}: {resp.data}")


# ──────────────────────────────────────────────────────────────
# GROUP 3: Cross-citizen data isolation
# ──────────────────────────────────────────────────────────────

class CitizenDataIsolationTest(TestCase):
    """Citizen A cannot read or interact with Citizen B's complaints."""

    def setUp(self):
        self.citizen_a = _make_citizen('03111000002')
        self.citizen_b = _make_citizen('03111000003')

        # Minimal DB objects for a complaint — use correct field names from Dashboard models
        # ComplaintType.type_name, ComplaintSubType.type_name, Location.location_name, UC.uc_name
        self.comp_type = ComplaintType.objects.create(type_name='Sewerage')
        self.comp_sub = ComplaintSubType.objects.create(
            type_name='Blockage', complaint_type=self.comp_type
        )
        self.location = Location.objects.create(location_name='Zone A')
        self.uc = UC.objects.create(uc_name='UC1', location=self.location)

        # Complaint belongs to citizen B (by mobile number)
        profile_b = CitizenProfile.objects.get(user=self.citizen_b)
        self.complaint_b = Complaint.objects.create(
            complaint_type=self.comp_type,
            complaint_sub_type=self.comp_sub,
            location=self.location,
            uc=self.uc,
            address='Test Address B',
            cell_number=profile_b.mobile_number,
            status='pending',
            source='citizen',
        )

        # Authenticate as citizen A
        token_a = _citizen_bearer_token('03111000002')
        self.assertIsNotNone(token_a, "Pre-condition: citizen A token must be obtained")
        self.client_a = _authed_client(token_a)

    def test_citizen_a_cannot_see_citizen_b_complaint(self):
        """Citizen A must receive 404 when fetching Citizen B's complaint detail."""
        resp = self.client_a.get(f'/api/citizen/v1/complaints/{self.complaint_b.id}/')
        self.assertEqual(resp.status_code, 404,
                         f"Expected 404 (ownership-filtered), got {resp.status_code}: {resp.data}")

    def test_citizen_a_cannot_track_citizen_b_complaint(self):
        """Citizen A must receive 404 on the tracking endpoint of Citizen B's complaint."""
        resp = self.client_a.get(f'/api/citizen/v1/complaints/{self.complaint_b.id}/tracking/')
        self.assertEqual(resp.status_code, 404,
                         f"Expected 404, got {resp.status_code}: {resp.data}")

    def test_citizen_a_cannot_feedback_citizen_b_complaint(self):
        """Citizen A must receive 404 on the feedback endpoint of Citizen B's complaint."""
        resp = self.client_a.post(
            f'/api/citizen/v1/complaints/{self.complaint_b.id}/feedback/',
            {'rating': 5},
            format='json',
        )
        self.assertEqual(resp.status_code, 404,
                         f"Expected 404, got {resp.status_code}: {resp.data}")

    def test_citizen_a_list_does_not_include_citizen_b_complaints(self):
        """Citizen A's complaints list must not include Citizen B's complaint."""
        resp = self.client_a.get('/api/citizen/v1/complaints/')
        self.assertEqual(resp.status_code, 200,
                         f"Citizen A's list failed: {resp.status_code}")
        results = resp.data.get('results', resp.data)
        ids = [c['id'] for c in (results if isinstance(results, list) else [])]
        self.assertNotIn(self.complaint_b.id, ids,
                         "Citizen B's complaint appeared in Citizen A's list!")


# ──────────────────────────────────────────────────────────────
# GROUP 4: Unauthenticated access is rejected
# ──────────────────────────────────────────────────────────────

class UnauthenticatedAccessTest(TestCase):
    """Requests with no token must be rejected with 401 from all protected citizen endpoints."""

    def setUp(self):
        self.anon = APIClient()

    def _assert_protected(self, method: str, url: str, body: dict = None):
        fn = getattr(self.anon, method)
        resp = fn(url, body or {}, format='json') if body is not None else fn(url)
        self.assertIn(resp.status_code, [401, 403],
                      f"{method.upper()} {url} → expected 401/403, got {resp.status_code}")

    def test_unauthenticated_cannot_list_complaints(self):
        self._assert_protected('get', '/api/citizen/v1/complaints/')

    def test_unauthenticated_cannot_submit_complaint(self):
        self._assert_protected('post', '/api/citizen/v1/complaints/', {})

    def test_unauthenticated_cannot_view_profile(self):
        self._assert_protected('get', '/api/citizen/v1/profile/')

    def test_unauthenticated_cannot_view_dashboard(self):
        self._assert_protected('get', '/api/citizen/v1/dashboard/')

    def test_unauthenticated_cannot_view_complaint_detail(self):
        self._assert_protected('get', '/api/citizen/v1/complaints/1/')

    def test_unauthenticated_cannot_track_complaint(self):
        self._assert_protected('get', '/api/citizen/v1/complaints/1/tracking/')

    def test_unauthenticated_cannot_post_feedback(self):
        self._assert_protected('post', '/api/citizen/v1/complaints/1/feedback/', {'rating': 5})


# ──────────────────────────────────────────────────────────────
# GROUP 5: Public endpoints remain open
# ──────────────────────────────────────────────────────────────

class PublicEndpointsTest(TestCase):
    """Public citizen endpoints must be reachable without authentication."""

    def setUp(self):
        self.anon = APIClient()

    def test_status_endpoint_is_public(self):
        """GET /api/citizen/v1/status/ → 200 for anyone."""
        resp = self.anon.get('/api/citizen/v1/status/')
        self.assertEqual(resp.status_code, 200,
                         f"Status endpoint not public: {resp.status_code}")

    def test_register_endpoint_is_accessible(self):
        """POST /api/citizen/v1/register/ → reachable (400 on validation failure is OK)."""
        resp = self.anon.post('/api/citizen/v1/register/', {}, format='json')
        self.assertIn(resp.status_code, [200, 201, 400],
                      f"Register endpoint unreachable: {resp.status_code}")

    def test_login_endpoint_is_accessible(self):
        """POST /api/citizen/v1/login/ → reachable (400/401 on bad creds is OK)."""
        resp = self.anon.post(
            '/api/citizen/v1/login/',
            {'mobile_number': '00000000000', 'password': 'wrong'},
            format='json',
        )
        self.assertIn(resp.status_code, [200, 400, 401],
                      f"Login endpoint unreachable: {resp.status_code}")

    def test_complaint_types_public_or_auth_required(self):
        """GET /api/citizen/v1/complaint-types/ → not a 500."""
        resp = self.anon.get('/api/citizen/v1/complaint-types/')
        self.assertNotEqual(resp.status_code, 500,
                            "Complaint types endpoint returned 500")


# ──────────────────────────────────────────────────────────────
# GROUP 6: Citizen login regression
# ──────────────────────────────────────────────────────────────

class CitizenLoginRegressionTest(TestCase):
    """
    Citizen login flow must return account_type='citizen', is_staff=False, and a token.
    Response format: { success, message, data: { access, refresh, user: {...} } }
    """

    def setUp(self):
        self.user = _make_citizen('03111000010')
        self.anon = APIClient()

    def _login(self):
        return self.anon.post(
            '/api/citizen/v1/login/',
            {'mobile_number': '03111000010', 'password': 'Test@12345'},
            format='json',
        )

    def test_login_returns_200(self):
        resp = self._login()
        self.assertEqual(resp.status_code, 200, f"Citizen login failed: {resp.data}")

    def test_login_response_has_account_type_citizen(self):
        resp = self._login()
        self.assertEqual(resp.status_code, 200)
        inner = _extract_citizen_response_data(resp.data)
        user_data = inner.get('user', {})
        self.assertEqual(user_data.get('account_type'), 'citizen',
                         f"Expected account_type='citizen', got: {user_data}")

    def test_login_response_is_not_staff(self):
        resp = self._login()
        self.assertEqual(resp.status_code, 200)
        inner = _extract_citizen_response_data(resp.data)
        user_data = inner.get('user', {})
        self.assertFalse(user_data.get('is_staff', True),
                         f"Citizen should not have is_staff=True, got: {user_data}")

    def test_login_response_has_access_token(self):
        resp = self._login()
        self.assertEqual(resp.status_code, 200)
        inner = _extract_citizen_response_data(resp.data)
        has_token = bool(inner.get('access') or inner.get('token'))
        self.assertTrue(has_token, f"No access token in response data: {inner}")

    def test_citizen_cannot_login_via_staff_endpoint(self):
        """
        A citizen account must not be accepted by /api/cms/auth/login/
        because they have no LocationPermission.
        Note: citizen's Django username IS the mobile number.
        """
        resp = self.anon.post(
            '/api/cms/auth/login/',
            {'username': '03111000010', 'password': 'Test@12345'},
            format='json',
        )
        # 403 (no CMS access) or 401 (wrong credentials) — never 200
        self.assertNotEqual(resp.status_code, 200,
                            "Citizen account must not be granted CMS staff access!")


# ──────────────────────────────────────────────────────────────
# GROUP 7: Staff login regression (superuser)
# ──────────────────────────────────────────────────────────────

class StaffLoginRegressionTest(TestCase):
    """
    Staff superuser login via /api/cms/auth/login/ must remain fully functional.
    Response format is flat: { access, refresh, user: {...}, message }
    """

    def setUp(self):
        self.staff = _make_superuser_staff('staff_regression_c7')
        self.anon = APIClient()

    def _login(self):
        return self.anon.post(
            '/api/cms/auth/login/',
            {'username': 'staff_regression_c7', 'password': 'Staff@12345'},
            format='json',
        )

    def test_staff_login_returns_200(self):
        resp = self._login()
        self.assertEqual(resp.status_code, 200, f"Staff login failed: {resp.data}")

    def test_staff_login_returns_access_token(self):
        resp = self._login()
        self.assertEqual(resp.status_code, 200)
        has_token = bool(resp.data.get('access') or resp.data.get('token'))
        self.assertTrue(has_token, f"No access token in staff login response: {resp.data}")

    def test_staff_login_response_has_allowed_locations(self):
        resp = self._login()
        self.assertEqual(resp.status_code, 200)
        # Staff login nests the profile under resp.data['user']
        user_data = resp.data.get('user', resp.data)
        self.assertIn('allowed_locations', user_data,
                      f"allowed_locations missing from staff response")

    def test_staff_is_superuser_in_db(self):
        """The staff user's is_superuser flag must remain intact after all citizen code additions."""
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_superuser)

    def test_staff_can_access_cms_dashboard_with_valid_token(self):
        """A valid staff token must be accepted by /api/cms/dashboard/."""
        resp = self._login()
        self.assertEqual(resp.status_code, 200)
        token = resp.data.get('access') or resp.data.get('token')
        client = _authed_client(token)
        dashboard_resp = client.get('/api/cms/dashboard/')
        # 200 = access granted; 404 = view exists but no data — both are OK
        self.assertIn(dashboard_resp.status_code, [200, 404],
                      f"Staff dashboard denied with valid token: {dashboard_resp.status_code}")
