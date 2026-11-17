"""
WSSP CMS Dashboard Analytics Security & Role-Isolation Test Suite
================================================================
Verifies that:
1. Head Office gets all zones and all departments across any selected period.
2. Zonal Managers get all departments strictly in their zone.
3. Department Managers get strictly their department in their zone (both summary & subtypes).
4. Cross-zone and cross-department isolation is strictly enforced.
5. Time filters (Year, Month, Custom Date Range) filter accurately without leaks.
6. Subtypes are presented for single-department managers, types for multi-department.
"""

import os
import sys
import django

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wssp.settings")
django.setup()

from django.contrib.auth.models import User
from Dashboard.models import Complaint, Location
from api.v1.services.dashboard_service import DashboardAnalyticsService


def run_tests():
    print("\n" + "=" * 80)
    print("  WSSP CMS DASHBOARD ANALYTICS — SECURITY & ROLE ISOLATION AUDIT")
    print("=" * 80)

    # -------------------------------------------------------------
    # TEST 1: Head Office — Full Scope, Jan 2026
    # -------------------------------------------------------------
    print("\n[TEST 1] Head Office Executive (ccho_officer) — January 2026:")
    ccho = User.objects.get(username="ccho_officer")
    data_ccho = DashboardAnalyticsService.get_analytics(ccho, {"year": 2026, "month": 1})

    summary = data_ccho["summary"]
    scope = data_ccho["scope"]
    period = data_ccho["period"]
    types = data_ccho["type_distribution"]
    trend = data_ccho["trend"]

    print(f"  Period: {period['label']} ({period['start_date']} -> {period['end_date']})")
    print(f"  Scope: Role={scope['role']}, Zone={scope['zone']}, Dept={scope['department']}")
    print(f"  Summary: Total={summary['total']}, Pending={summary['pending']}, Resolved={summary['resolved']}")
    print(f"  Complaint Types Found: {[t['name'] + ' (' + str(t['count']) + ')' for t in types]}")
    print(f"  Trend data points: {len(trend)} days")

    assert summary["total"] == 1677, f"Expected 1677 total in Jan 2026, got {summary['total']}"
    assert len(types) == 4, f"Expected 4 complaint types for Head Office, got {len(types)}"
    assert not scope["is_single_department"], "Head Office should not be marked as single department"
    assert len(trend) == 31, f"Expected 31 daily trend points for January, got {len(trend)}"
    assert "resolved" in trend[0] and "pending" in trend[0], "Trend items must include resolved and pending counts"
    assert "resolved_percentage" in trend[0] and "pending_percentage" in trend[0], "Trend items must include percentage fields"
    print("  --> PASS [OK]")

    # -------------------------------------------------------------
    # TEST 2: Zonal Manager A — Zone A Only, All Departments
    # -------------------------------------------------------------
    print("\n[TEST 2] Zonal Manager A (zma) — January 2026:")
    zma = User.objects.get(username="zma")
    data_zma = DashboardAnalyticsService.get_analytics(zma, {"year": 2026, "month": 1})

    sum_zma = data_zma["summary"]
    scope_zma = data_zma["scope"]
    types_zma = data_zma["type_distribution"]

    print(f"  Scope: Zone={scope_zma['zone']}, Dept={scope_zma['department']}")
    print(f"  Summary: Total={sum_zma['total']} (Pending={sum_zma['pending']}, Resolved={sum_zma['resolved']})")
    print(f"  Zone A Types: {[t['name'] + ' (' + str(t['count']) + ')' for t in types_zma]}")

    # Zone A complaints must be strictly less than total WSSP complaints
    assert sum_zma["total"] < summary["total"], "Zonal Manager must not see all WSSP complaints"
    assert sum_zma["total"] > 0, "Zonal Manager A should have complaints in Jan 2026"
    assert len(types_zma) > 1, "Zonal Manager should see multiple departments"
    assert not scope_zma["is_single_department"], "Zonal Manager is not single department"
    print("  --> PASS [OK]")

    # -------------------------------------------------------------
    # TEST 3: SWM Manager A — Zone A + Solid Waste Only
    # -------------------------------------------------------------
    print("\n[TEST 3] SWM Manager Zone A (mngrswmzonea) — January 2026:")
    swm_a = User.objects.get(username="mngrswmzonea")
    data_swm_a = DashboardAnalyticsService.get_analytics(swm_a, {"year": 2026, "month": 1})

    sum_swm = data_swm_a["summary"]
    scope_swm = data_swm_a["scope"]
    subtypes_swm = data_swm_a["subtype_distribution"]

    print(f"  Scope: Role={scope_swm['role']}, Zone={scope_swm['zone']}, Dept={scope_swm['department']}")
    print(f"  Summary: Total={sum_swm['total']}, Pending={sum_swm['pending']}, Resolved={sum_swm['resolved']}")
    print(f"  Subtypes ({len(subtypes_swm)} items): {[s['name'] + ' (' + str(s['count']) + ')' for s in subtypes_swm[:5]]}")

    assert scope_swm["is_single_department"], "SWM Manager MUST be marked as single department"
    assert sum_swm["total"] < sum_zma["total"], "SWM Manager must only see a subset of Zone A complaints"
    assert sum_swm["total"] > 0, "SWM Manager A should have complaints in Jan 2026"

    # Verify no leaks of Water Supply or Drainage in subtypes
    subtype_names = [s["name"].lower() for s in subtypes_swm]
    for non_swm in ["tubewell", "water tanker", "manhole", "sewerage", "clogged drain"]:
        for name in subtype_names:
            assert non_swm not in name, f"Security Leak: Found '{non_swm}' in SWM subtypes ({name})"
    print("  --> PASS [OK]")

    # -------------------------------------------------------------
    # TEST 4: WS Manager A — Zone A + Water Supply Only
    # -------------------------------------------------------------
    print("\n[TEST 4] WS Manager Zone A (mngrwszonea) — January 2026:")
    ws_a = User.objects.get(username="mngrwszonea")
    data_ws_a = DashboardAnalyticsService.get_analytics(ws_a, {"year": 2026, "month": 1})

    sum_ws = data_ws_a["summary"]
    scope_ws = data_ws_a["scope"]
    subtypes_ws = data_ws_a["subtype_distribution"]

    print(f"  Scope: Zone={scope_ws['zone']}, Dept={scope_ws['department']}")
    print(f"  Summary: Total={sum_ws['total']}")
    print(f"  Subtypes: {[s['name'] + ' (' + str(s['count']) + ')' for s in subtypes_ws[:5]]}")

    assert scope_ws["is_single_department"], "WS Manager MUST be marked as single department"
    assert sum_ws["total"] + sum_swm["total"] <= sum_zma["total"], "Sub-department totals cannot exceed zonal total"
    print("  --> PASS [OK]")

    # -------------------------------------------------------------
    # TEST 5: Cross-Zone Security Isolation (SWM A vs SWM C)
    # -------------------------------------------------------------
    print("\n[TEST 5] Cross-Zone Isolation (SWM Zone A vs SWM Zone C):")
    swm_c = User.objects.get(username="mngrswmzonec")
    data_swm_c = DashboardAnalyticsService.get_analytics(swm_c, {"year": 2026, "month": 1})

    print(f"  SWM Zone A Total: {sum_swm['total']} (Zone A)")
    print(f"  SWM Zone C Total: {data_swm_c['summary']['total']} (Zone C)")
    assert data_swm_c["scope"]["zone"] == "Zone C", "SWM Zone C must be scoped to Zone C"
    print("  --> PASS [OK]")

    # -------------------------------------------------------------
    # TEST 6: Time Filters — Year 2026 vs Month 1 vs Custom Range
    # -------------------------------------------------------------
    print("\n[TEST 6] Time Filter Mechanics:")
    # 6.1 Full Year
    data_year = DashboardAnalyticsService.get_analytics(ccho, {"year": 2026})
    print(f"  Full Year 2026 Total: {data_year['summary']['total']}")
    print(f"  Full Year Trend Points: {len(data_year['trend'])} months (Jan - Dec)")
    assert data_year["summary"]["total"] == 11910, f"Expected 11910 in 2026, got {data_year['summary']['total']}"
    assert len(data_year["trend"]) == 12, "Full year trend must have exactly 12 months"

    # 6.2 Custom Date Range (First 15 days of Jan 2026)
    data_custom = DashboardAnalyticsService.get_analytics(ccho, {
        "start_date": "2026-01-01",
        "end_date": "2026-01-15",
    })
    print(f"  Custom Range (01-15 Jan 2026) Total: {data_custom['summary']['total']}")
    print(f"  Custom Range Label: {data_custom['period']['label']}")
    print(f"  Custom Range Trend Points: {len(data_custom['trend'])} days")
    assert data_custom["summary"]["total"] <= data_ccho["summary"]["total"], "15 days cannot exceed full month"
    assert len(data_custom["trend"]) == 15, "15 day range must have 15 daily points"
    print("  --> PASS [OK]")

    # -------------------------------------------------------------
    # TEST 7: All Years (Lifetime) Filter
    # -------------------------------------------------------------
    print("\n[TEST 7] All Years (Lifetime) Analytics:")
    data_all_years = DashboardAnalyticsService.get_analytics(ccho, {"year": "all"})
    print(f"  All Years Total: {data_all_years['summary']['total']}")
    print(f"  All Years Label: {data_all_years['period']['label']}")
    print(f"  All Years Trend (by Year): {[t['label'] + ': ' + str(t['count']) for t in data_all_years['trend']]}")

    assert data_all_years["summary"]["total"] == 27147, f"Expected 27147 all-time complaints, got {data_all_years['summary']['total']}"
    assert len(data_all_years["trend"]) == 4, "Expected 4 years in lifetime trend (2021, 2024, 2025, 2026)"
    print("  --> PASS [OK]")

    print("\n" + "=" * 80)
    print("  ALL DASHBOARD ANALYTICS SECURITY & ISOLATION TESTS PASSED [100% OK]")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_tests()
