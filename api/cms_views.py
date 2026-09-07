"""
WSSP Complaint Management System (CMS) — Data API Layer
Provides secure, server-side scoped endpoints for the Mobile Dashboard,
Complaint Directory, and Filtering.
"""
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator

from Dashboard.models import (
    Complaint, Location, UC, ComplaintType, ComplaintSubType,
    ComplaintSource, ComplaintResolution, ComplaintActionLog
)
from .cms_auth import IsCMSAuthorized, get_user_allowed_location_ids


class CMSDashboardView(APIView):
    """
    GET /api/cms/dashboard/
    Returns high-level departmental metrics and recent complaints scoped to the authenticated officer.
    """
    permission_classes = [permissions.IsAuthenticated, IsCMSAuthorized]

    def get(self, request):
        allowed_ids = get_user_allowed_location_ids(request.user)
        base_qs = Complaint.objects.filter(location_id__in=allowed_ids)

        today = timezone.now().date()

        # Key Metrics
        total_count = base_qs.count()
        pending_count = base_qs.filter(status='pending').count()
        resolved_count = base_qs.filter(status='resolved').count()
        today_count = base_qs.filter(date=today).count()

        # Top recent complaints (last 10)
        recent_qs = base_qs.select_related(
            'location', 'uc', 'complaint_type', 'SubType'
        ).order_by('-date', '-id')[:10]

        recent_complaints = []
        for c in recent_qs:
            recent_complaints.append({
                "id": c.id,
                "complaint_no": f"CMS-{c.id}",
                "title": c.title or (c.SubType.type_name if c.SubType else (c.complaint_type.type_name if c.complaint_type else "Complaint")),
                "category": c.complaint_type.type_name if c.complaint_type else "General",
                "subtype": c.SubType.type_name if c.SubType else None,
                "citizen_name": f"{c.first_name} {c.last_name}".strip() or "Citizen",
                "cell_number": c.cell_number or "N/A",
                "location": c.location.location_name if c.location else "N/A",
                "uc": c.uc.uc_name if c.uc else "N/A",
                "area": c.area or c.address or "Peshawar",
                "date": c.date.strftime("%Y-%m-%d") if c.date else None,
                "status": c.status or "pending",
                "before_image": c.before_image.url if c.before_image else None,
            })

        # Category distribution
        type_counts = base_qs.values('complaint_type__type_name').annotate(
            count=Count('id')
        ).order_by('-count')

        type_distribution = [
            {"category": item['complaint_type__type_name'] or "Uncategorized", "count": item['count']}
            for item in type_counts[:6]
        ]

        # Zone distribution
        zone_counts = base_qs.values('location__location_name').annotate(
            count=Count('id')
        ).order_by('-count')

        zone_distribution = [
            {"zone": item['location__location_name'] or "Unknown", "count": item['count']}
            for item in zone_counts
        ]

        return Response({
            "metrics": {
                "total": total_count,
                "pending": pending_count,
                "resolved": resolved_count,
                "today": today_count,
            },
            "recent_complaints": recent_complaints,
            "type_distribution": type_distribution,
            "zone_distribution": zone_distribution,
        }, status=status.HTTP_200_OK)


class CMSComplaintListView(APIView):
    """
    GET /api/cms/complaints/
    Query params:
      - search: string (ID, cell_number, name, area)
      - status: 'all' | 'pending' | 'resolved'
      - location_id: int
      - page: int (default 1)
      - page_size: int (default 20)
    """
    permission_classes = [permissions.IsAuthenticated, IsCMSAuthorized]

    def get(self, request):
        allowed_ids = get_user_allowed_location_ids(request.user)
        qs = Complaint.objects.filter(location_id__in=allowed_ids).select_related(
            'location', 'uc', 'complaint_type', 'SubType'
        )

        # 1. Filter by Status
        status_param = request.GET.get('status', 'all').lower()
        if status_param in ['pending', 'resolved']:
            qs = qs.filter(status=status_param)

        # 2. Filter by Location
        location_param = request.GET.get('location_id')
        if location_param:
            try:
                loc_id = int(location_param)
                if loc_id in allowed_ids:
                    qs = qs.filter(location_id=loc_id)
            except ValueError:
                pass

        # 3. Filter by Search Query
        search_query = request.GET.get('search', '').strip()
        if search_query:
            if search_query.isdigit():
                qs = qs.filter(Q(id=int(search_query)) | Q(cell_number__icontains=search_query))
            else:
                qs = qs.filter(
                    Q(first_name__icontains=search_query) |
                    Q(last_name__icontains=search_query) |
                    Q(area__icontains=search_query) |
                    Q(address__icontains=search_query) |
                    Q(title__icontains=search_query) |
                    Q(complaint_detail__icontains=search_query)
                )

        # Order by newest date & ID
        qs = qs.order_by('-date', '-id')

        # Pagination
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)
        paginator = Paginator(qs, page_size)

        try:
            paginated_page = paginator.page(page)
        except Exception:
            paginated_page = paginator.page(1)

        complaints_data = []
        for c in paginated_page.object_list:
            complaints_data.append({
                "id": c.id,
                "complaint_no": f"CMS-{c.id}",
                "title": c.title or (c.SubType.type_name if c.SubType else (c.complaint_type.type_name if c.complaint_type else "Complaint")),
                "category": c.complaint_type.type_name if c.complaint_type else "General",
                "subtype": c.SubType.type_name if c.SubType else None,
                "citizen_name": f"{c.first_name} {c.last_name}".strip() or "Citizen",
                "cell_number": c.cell_number or "N/A",
                "location": c.location.location_name if c.location else "N/A",
                "uc": c.uc.uc_name if c.uc else "N/A",
                "area": c.area or c.address or "Peshawar",
                "detail": c.complaint_detail or "",
                "date": c.date.strftime("%Y-%m-%d") if c.date else None,
                "status": c.status or "pending",
                "before_image": c.before_image.url if c.before_image else None,
            })

        return Response({
            "total_count": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": paginated_page.number,
            "has_next": paginated_page.has_next(),
            "has_previous": paginated_page.has_previous(),
            "results": complaints_data,
        }, status=status.HTTP_200_OK)


class CMSComplaintDetailView(APIView):
    """
    GET /api/cms/complaints/<id>/
    Full detail with citizen info, before/after images, resolution remarks, and audit trail.
    """
    permission_classes = [permissions.IsAuthenticated, IsCMSAuthorized]

    def get(self, request, complaint_id):
        allowed_ids = get_user_allowed_location_ids(request.user)

        try:
            complaint = Complaint.objects.select_related(
                'location', 'uc', 'complaint_type', 'SubType', 'complaint_source', 'resolution'
            ).prefetch_related('actions', 'responses').get(id=complaint_id)
        except Complaint.DoesNotExist:
            return Response({"detail": "Complaint not found."}, status=status.HTTP_404_NOT_FOUND)

        # Server-side security: verify complaint belongs to officer's permitted zones
        if complaint.location_id not in allowed_ids:
            return Response(
                {"detail": "Access forbidden. This complaint belongs to a zone outside your assigned area."},
                status=status.HTTP_403_FORBIDDEN
            )

        resolution_data = None
        if hasattr(complaint, 'resolution') and complaint.resolution:
            res = complaint.resolution
            resolution_data = {
                "description": res.description,
                "customer_satisfaction": res.customer_satisfaction,
                "after_image": res.after_image.url if res.after_image else None,
            }

        actions_data = [
            {
                "action": a.action,
                "performed_by": a.user.username if a.user else "System",
                "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S") if a.timestamp else None,
            }
            for a in complaint.actions.all().order_by('-timestamp')
        ]

        data = {
            "id": complaint.id,
            "complaint_no": f"CMS-{complaint.id}",
            "title": complaint.title or "Complaint Details",
            "type": complaint.type or "Short Term",
            "category": complaint.complaint_type.type_name if complaint.complaint_type else "General",
            "subtype": complaint.SubType.type_name if complaint.SubType else None,
            "source": complaint.complaint_source.source_name if complaint.complaint_source else "1334",
            "detail": complaint.complaint_detail,
            "date": complaint.date.strftime("%Y-%m-%d") if complaint.date else None,
            "status": complaint.status,
            "before_image": complaint.before_image.url if complaint.before_image else None,

            # Location
            "location": complaint.location.location_name if complaint.location else "N/A",
            "uc": complaint.uc.uc_name if complaint.uc else "N/A",
            "area": complaint.area,
            "address": complaint.address,
            "tehsil": complaint.tehsil,

            # Citizen / Applicant Info
            "citizen_name": f"{complaint.first_name} {complaint.last_name}".strip() or "Citizen",
            "cell_number": complaint.cell_number,
            "phone_number": complaint.phone_number,
            "cnic": complaint.cnic,
            "gender": complaint.gender,
            "consumer_type": complaint.consumer_type,
            "bill_number": complaint.bill_number,

            # Reference numbers
            "pcp_no": complaint.Pcp_compalin_no,
            "eak_no": complaint.Eak_compalin_no,
            "ebaldia_no": complaint.Ebaldia_compalin_no,

            # Resolution & Audit
            "resolution": resolution_data,
            "actions": actions_data,
        }

        return Response(data, status=status.HTTP_200_OK)
