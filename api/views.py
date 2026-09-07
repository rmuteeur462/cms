import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum

from .authentication import fintech_auth_required
from Dashboard.models import Revenue, Disbursement  


# -------------------------------
# API STATUS CHECK
# -------------------------------
@fintech_auth_required
def ApiStatusCheck(request):
    return HttpResponse(
        "Api Version 2.2 is running",
        content_type="text/plain"
    )


# --------------------------------
# MONTH WISE DATA API (WSSP)
# --------------------------------
@csrf_exempt
@fintech_auth_required
def dshbMonthWiseData(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    department_id = body.get("departmentId")
    start_date = body.get("startdate")
    end_date = body.get("enddate")

    if not department_id or not start_date or not end_date:
        return JsonResponse({"error": "Missing required parameters"}, status=400)

    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # -----------------------------
    # HELPER: iterate month by month
    # -----------------------------
    def month_year_iter(start, end):
        current = start.replace(day=1)
        while current <= end:
            yield current.year, current.month
            # move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

    services_data = []

    for year, month in month_year_iter(start_date, end_date):
        # start and end of month
        month_start = datetime(year, month, 1).date()
        if month == 12:
            month_end = datetime(year, 12, 31).date()
        else:
            month_end = (datetime(year, month + 1, 1) - timedelta(days=1)).date()

        # ensure within overall range
        month_start = max(month_start, start_date)
        month_end = min(month_end, end_date)

        # REVENUE
        revenues = Revenue.objects.filter(date__range=(month_start, month_end))
        water_collected = revenues.aggregate(total=Sum("recovery_day_water_supply"))["total"] or Decimal(0)
        solid_collected = revenues.aggregate(total=Sum("recovery_day_solid_waste_management"))["total"] or Decimal(0)

        # DISBURSEMENT
        disbursements = Disbursement.objects.filter(date__range=(month_start, month_end))
        water_disbursed = disbursements.aggregate(total=Sum("disbursement_amount_water_supply"))["total"] or Decimal(0)
        solid_disbursed = disbursements.aggregate(total=Sum("disbursement_amount_solid_waste_management"))["total"] or Decimal(0)

        # ADD TO RESPONSE
        services_data.append({
            "serviceId": 1,
            "serviceCode": "WSSP-WS",
            "serviceName": "Water Supply",
            "collectedAmount": float(water_collected / Decimal(1_000_000)),
            "disbursedAmount": float(water_disbursed / Decimal(1_000_000)),
            "monthNo": month,
            "yearNo": year
        })
        services_data.append({
            "serviceId": 2,
            "serviceCode": "WSSP-Conservancy",
            "serviceName": "Conservancy Management",
            "collectedAmount": float(solid_collected / Decimal(1_000_000)),
            "disbursedAmount": float(solid_disbursed / Decimal(1_000_000)),
            "monthNo": month,
            "yearNo": year
        })

    return JsonResponse({
        "departmentId": department_id,
        "departmentName": "Water and Sanitation Services Peshawar (WSSP)",
        "services": services_data
    })





import base64
import requests
from django.conf import settings
from django.shortcuts import render


def revenuedashboard(request):
    data = None

    if request.method == "POST":
        payload = {
            "departmentId": request.POST.get("departmentId"),
            "startdate": request.POST.get("startdate"),
            "enddate": request.POST.get("enddate"),
        }

        credentials = f"{settings.FINTECH_API_USERNAME}:{settings.FINTECH_API_PASSWORD}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded}",
            "X-API-KEY": settings.FINTECH_API_KEY,
            "Content-Type": "application/json",
        }

        response = requests.post(
            "http://172.16.17.100:8002/api/dshbMonthWiseData",
            json=payload,
            headers=headers
        )


        print(response.status_code)
        print(response.text)

        if response.status_code == 200:
            data = response.json()
        else:
            data = {"services": []}

    return render(request, "api/dashboard.html", {"data": data})
