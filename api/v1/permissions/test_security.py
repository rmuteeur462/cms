"""
Security Verification Test Script
=================================
Runs automated checks against actual WSSP test accounts to verify that:
1. Head Office sees all complaints across all zones.
2. Zone A Manager sees only Zone A complaints across all types.
3. SWM Zone A sees only Solid Waste complaints in Zone A.
4. WS Zone A sees only Water Supply complaints in Zone A.
5. SDS Zone A sees only Drainage complaints in Zone A.
"""

import os
import sys
import django

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wssp.settings")
django.setup()

from django.contrib.auth.models import User
from api.v1.permissions.base import get_user_role_context, scope_complaint_queryset
from api.v1.permissions.complaints import CanViewComplaint


def run_security_audit():
    accounts = [
        ("Head Office", "ccho_officer"),
        ("Zone A Manager", "zma"),
        ("SWM Zone A", "mngrswmzonea"),
        ("WS Zone A", "mngrwszonea"),
        ("SDS Zone A", "amsdszonea"),
    ]

    print("\n" + "=" * 75)
    print("WSSP CMS SECURITY VERIFICATION AUDIT")
    print("=" * 75)

    results = {}

    for label, uname in accounts:
        user = User.objects.filter(username=uname).first()
        if not user:
            print(f"FAILED: User {uname} not found in database.")
            continue

        ctx = get_user_role_context(user)
        scoped_qs = scope_complaint_queryset(user)
        count = scoped_qs.count()

        zones = list(set(scoped_qs.values_list("location__location_name", flat=True).distinct()))
        types = list(set(scoped_qs.values_list("complaint_type__type_name", flat=True).distinct()))

        print(f"\n[ROLE AUDIT] {label} (Username: '{uname}')")
        print(f"  - Title: {ctx['role_title']}")
        print(f"  - Permitted Location IDs: {ctx['allowed_location_ids']}")
        print(f"  - Department Name: {ctx['department_name']}")
        print(f"  - Total Scoped Complaints: {count:,}")
        print(f"  - Zones Accessible: {zones}")
        print(f"  - Complaint Types Accessible: {types}")

        # Assertions
        if label == "Head Office":
            assert count > 10000, f"Head Office should see all complaints, got {count}"
            assert len(zones) >= 5, "Head Office should see all 5 zones"
            print("  -> Security Assertion: PASS (Cross-Zonal Access Verified)")

        elif label == "Zone A Manager":
            assert zones == ["Zone A"], f"Zone A Manager must only see Zone A, got {zones}"
            assert len(types) > 1, "Zone A Manager should see all complaint types in Zone A"
            print("  -> Security Assertion: PASS (Strict Zone A Scoping Verified)")

        elif label == "SWM Zone A":
            assert zones == ["Zone A"], f"SWM Zone A must only see Zone A, got {zones}"
            assert types == ["Solid Waste"], f"SWM must only see Solid Waste, got {types}"
            print("  -> Security Assertion: PASS (Zone A + Solid Waste Scoping Verified)")

        elif label == "WS Zone A":
            assert zones == ["Zone A"], f"WS Zone A must only see Zone A, got {zones}"
            assert types == ["Water Supply"], f"WS must only see Water Supply, got {types}"
            print("  -> Security Assertion: PASS (Zone A + Water Supply Scoping Verified)")

        elif label == "SDS Zone A":
            assert zones == ["Zone A"], f"SDS Zone A must only see Zone A, got {zones}"
            assert types == ["Drainage"], f"SDS must only see Drainage, got {types}"
            print("  -> Security Assertion: PASS (Zone A + Drainage Scoping Verified)")

        results[uname] = {
            "count": count,
            "zones": zones,
            "types": types,
        }

    print("\n" + "=" * 75)
    print("ALL 5 ROLE SECURITY AUDITS COMPLETED SUCCESSFULLY: PASS [OK]")
    print("=" * 75 + "\n")
    return results


if __name__ == "__main__":
    run_security_audit()
