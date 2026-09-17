"""
WSSP CMS Dashboard Analytics Service
====================================
Centralized business logic for role-scoped, time-filtered complaint analytics.

CRITICAL SECURITY DIRECTIVE:
---------------------------
Every count, group by, and trend calculation is performed strictly on the
authorized queryset produced by get_allowed_complaints(user).
Under NO circumstances is unrestricted data retrieved or leaked.
"""

import calendar
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth, ExtractDay, ExtractYear

from Dashboard.models import Complaint, ComplaintType, ComplaintSubType, Location
from api.v1.permissions.base import (
    get_allowed_complaints,
    get_user_role_context,
)


class DashboardAnalyticsService:
    """
    Computes secure, role-aware complaint statistics, distributions,
    and trends over configurable calendar periods.
    """

    @staticmethod
    def parse_period(params):
        """
        Parses and validates time filters from query parameters.
        Supports:
          - year (e.g., 2026)
          - month (1-12)
          - start_date & end_date (YYYY-MM-DD)
        Defaults to current calendar year and current month.
        """
        today = timezone.now().date()
        current_year = today.year
        current_month = today.month

        year_param = params.get("year")
        month_param = params.get("month")
        start_date_param = params.get("start_date")
        end_date_param = params.get("end_date")

        # 0. All Years (Lifetime)
        if str(year_param).lower() in ["all", "all_years", "-1"] or params.get("all_years") in [True, "true", "1"]:
            start_date = date(2021, 1, 1)
            end_date = date(current_year, 12, 31)
            return {
                "year": "all",
                "month": None,
                "start_date": start_date,
                "end_date": end_date,
                "label": "All Years (Lifetime)",
                "period_type": "all_years",
            }

        # 1. Custom Date Range
        if start_date_param and end_date_param:
            try:
                start_date = datetime.strptime(start_date_param.strip(), "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_param.strip(), "%Y-%m-%d").date()
                if start_date > end_date:
                    start_date, end_date = end_date, start_date
                label = f"{start_date.strftime('%d %b %Y')} – {end_date.strftime('%d %b %Y')}"
                return {
                    "year": None,
                    "month": None,
                    "start_date": start_date,
                    "end_date": end_date,
                    "label": label,
                    "period_type": "custom",
                }
            except ValueError:
                pass  # Fallback to year/month on invalid custom dates

        # 2. Year & Month or Year only
        try:
            year = int(year_param) if year_param else current_year
        except (ValueError, TypeError):
            year = current_year

        if month_param:
            try:
                month = int(month_param)
                if 1 <= month <= 12:
                    _, num_days = calendar.monthrange(year, month)
                    start_date = date(year, month, 1)
                    end_date = date(year, month, num_days)
                    label = f"{calendar.month_name[month]} {year}"
                    return {
                        "year": year,
                        "month": month,
                        "start_date": start_date,
                        "end_date": end_date,
                        "label": label,
                        "period_type": "month",
                    }
            except (ValueError, TypeError):
                pass

        # 3. Full Year
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        label = f"Year {year}"
        return {
            "year": year,
            "month": None,
            "start_date": start_date,
            "end_date": end_date,
            "label": label,
            "period_type": "year",
        }

    @classmethod
    def get_analytics(cls, user, params):
        """
        Main entry point for dashboard analytics.
        Enforces backend permission scoping first, then calculates
        all metrics within the requested date window.
        """
        # ---------------------------------------------------------
        # 1. SCOPED BASE QUERYSET
        # ---------------------------------------------------------
        base_qs = get_allowed_complaints(user)
        role_ctx = get_user_role_context(user)

        # ---------------------------------------------------------
        # 2. DATE FILTERING
        # ---------------------------------------------------------
        period = cls.parse_period(params)
        start_date = period["start_date"]
        end_date = period["end_date"]

        period_qs = base_qs.filter(date__gte=start_date, date__lte=end_date)

        # ---------------------------------------------------------
        # 3. SUMMARY METRICS
        # ---------------------------------------------------------
        total_count = period_qs.count()
        pending_count = period_qs.filter(status="pending").count()
        resolved_count = period_qs.filter(status="resolved").count()
        in_progress_count = 0  # In existing WSSP schema, statuses are strictly pending/resolved

        summary = {
            "total": total_count,
            "pending": pending_count,
            "in_progress": in_progress_count,
            "resolved": resolved_count,
            "registered_this_period": total_count,
        }

        # ---------------------------------------------------------
        # 4. STATUS DISTRIBUTION
        # ---------------------------------------------------------
        pending_pct = round((pending_count / total_count * 100), 1) if total_count > 0 else 0.0
        resolved_pct = round((resolved_count / total_count * 100), 1) if total_count > 0 else 0.0

        status_distribution = [
            {
                "status": "pending",
                "label": "Pending",
                "count": pending_count,
                "percentage": pending_pct,
                "color": "#F59E0B",
            },
            {
                "status": "resolved",
                "label": "Resolved",
                "count": resolved_count,
                "percentage": resolved_pct,
                "color": "#10B981",
            },
        ]

        # ---------------------------------------------------------
        # 5. CATEGORY & SUBTYPE DISTRIBUTION (Role-Aware)
        # ---------------------------------------------------------
        is_single_dept = role_ctx["is_department_manager"]

        # 5.1 Complaint Type Distribution (Head Office / Zonal Manager)
        type_distribution = []
        if not is_single_dept:
            type_counts = (
                period_qs.values("complaint_type__id", "complaint_type__type_name")
                .annotate(count=Count("id"))
                .order_by("-count")
            )
            for item in type_counts:
                name = item["complaint_type__type_name"] or "General / Uncategorized"
                cnt = item["count"]
                pct = round((cnt / total_count * 100), 1) if total_count > 0 else 0.0
                type_distribution.append({
                    "id": item["complaint_type__id"],
                    "name": name,
                    "count": cnt,
                    "percentage": pct,
                })

        # 5.2 Subtype Distribution (Primary for Department Managers, secondary for all)
        subtype_counts = (
            period_qs.values("SubType__id", "SubType__type_name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        subtype_distribution = []
        for item in subtype_counts:
            name = item["SubType__type_name"] or "General / Uncategorized"
            cnt = item["count"]
            pct = round((cnt / total_count * 100), 1) if total_count > 0 else 0.0
            subtype_distribution.append({
                "id": item["SubType__id"],
                "name": name,
                "count": cnt,
                "percentage": pct,
            })

        # ---------------------------------------------------------
        # 6. TIME TREND (Adaptive)
        # ---------------------------------------------------------
        trend = cls._calculate_trend(period_qs, period)

        # ---------------------------------------------------------
        # 7. CONSTRUCT RESPONSE
        # ---------------------------------------------------------
        # Derive zone label
        zone_label = "ALL"
        if role_ctx["allowed_location_ids"]:
            locs = Location.objects.filter(id__in=role_ctx["allowed_location_ids"])
            if len(role_ctx["allowed_location_ids"]) == 1:
                loc = locs.first()
                zone_label = loc.location_name if loc else "Zonal"
            elif role_ctx["is_head_office"]:
                zone_label = "ALL"
            else:
                zone_label = ", ".join(locs.values_list("location_name", flat=True))

        dept_label = role_ctx["department_name"] if role_ctx["department_name"] else "ALL"

        role_key = "staff"
        if role_ctx["is_head_office"]:
            role_key = "head_office"
        elif role_ctx["is_zonal_manager"]:
            role_key = "zonal_manager"
        elif role_ctx["is_department_manager"]:
            role_key = "department_manager"

        return {
            "success": True,
            "period": {
                "year": period["year"],
                "month": period["month"],
                "start_date": period["start_date"].strftime("%Y-%m-%d"),
                "end_date": period["end_date"].strftime("%Y-%m-%d"),
                "label": period["label"],
                "period_type": period["period_type"],
            },
            "scope": {
                "role": role_key,
                "role_title": role_ctx["role_title"],
                "zone": zone_label,
                "department": dept_label,
                "is_single_department": is_single_dept,
            },
            "summary": summary,
            "status_distribution": status_distribution,
            "type_distribution": type_distribution,
            "subtype_distribution": subtype_distribution,
            "trend": trend,
        }

    @staticmethod
    def _calculate_trend(period_qs, period):
        """
        Constructs continuous time trend data matching the selected period.
        - Month / Short Range (<= 31 days): Daily breakdown (e.g. Day 01 .. Day 31)
        - Year / Long Range (> 31 days): Monthly breakdown (e.g. Jan .. Dec)
        """
        start_date = period["start_date"]
        end_date = period["end_date"]
        delta_days = (end_date - start_date).days + 1

        # A. ALL YEARS BREAKDOWN (by Year)
        if period["period_type"] == "all_years":
            year_counts_qs = (
                period_qs.annotate(y=ExtractYear("date"))
                .values("y")
                .annotate(count=Count("id"))
                .order_by("y")
            )
            count_map = {item["y"]: item["count"] for item in year_counts_qs if item["y"]}
            trend = []
            for y in sorted(count_map.keys()):
                trend.append({
                    "year": y,
                    "label": str(y),
                    "full_label": f"Year {y}",
                    "count": count_map[y],
                })
            return trend

        # B. DAILY BREAKDOWN (Monthly view or custom <= 31 days)
        if period["period_type"] == "month" or delta_days <= 31:
            day_counts_qs = (
                period_qs.values("date")
                .annotate(count=Count("id"))
                .order_by("date")
            )
            count_map = {item["date"]: item["count"] for item in day_counts_qs if item["date"]}

            trend = []
            curr_date = start_date
            while curr_date <= end_date:
                count = count_map.get(curr_date, 0)
                trend.append({
                    "date": curr_date.strftime("%Y-%m-%d"),
                    "label": curr_date.strftime("%d"),
                    "full_label": curr_date.strftime("%d %b"),
                    "count": count,
                })
                curr_date += timedelta(days=1)
            return trend

        # B. MONTHLY BREAKDOWN (Full year or custom > 31 days)
        month_counts_qs = (
            period_qs.annotate(m=ExtractMonth("date"))
            .values("m")
            .annotate(count=Count("id"))
            .order_by("m")
        )
        count_map = {item["m"]: item["count"] for item in month_counts_qs if item["m"]}

        month_labels = [
            (1, "Jan"), (2, "Feb"), (3, "Mar"), (4, "Apr"),
            (5, "May"), (6, "Jun"), (7, "Jul"), (8, "Aug"),
            (9, "Sep"), (10, "Oct"), (11, "Nov"), (12, "Dec")
        ]

        trend = []
        for m_num, m_name in month_labels:
            trend.append({
                "month": m_num,
                "label": m_name,
                "count": count_map.get(m_num, 0),
            })
        return trend
