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


class CMSComplaintOptionsView(APIView):
    """
    GET /api/cms/complaints/options/
    Returns cascading metadata for the Complaint creation form:
    - locations (scoped to officer)
    - ucs (grouped/filterable by location_id)
    - sources (complaint sources)
    - types (categories)
    - subtypes (grouped/filterable by complaint_type_id)
    - choices (genders, consumer_types)
    """
    permission_classes = [permissions.IsAuthenticated, IsCMSAuthorized]

    def get(self, request):
        allowed_location_ids = get_user_allowed_location_ids(request.user)

        locations = list(Location.objects.filter(id__in=allowed_location_ids).values('id', 'location_name').order_by('location_name'))
        ucs = list(UC.objects.filter(location_id__in=allowed_location_ids).values('id', 'uc_name', 'location_id').order_by('uc_name'))
        sources = list(ComplaintSource.objects.values('id', 'source_name').order_by('source_name'))
        types = list(ComplaintType.objects.values('id', 'type_name').order_by('type_name'))
        subtypes = list(ComplaintSubType.objects.values('id', 'type_name', 'complaint_type_id').order_by('type_name'))

        return Response({
            "locations": [{"id": l['id'], "name": l['location_name']} for l in locations],
            "ucs": [{"id": u['id'], "name": u['uc_name'], "location_id": u['location_id']} for u in ucs],
            "sources": [{"id": s['id'], "name": s['source_name']} for s in sources],
            "types": [{"id": t['id'], "name": t['type_name']} for t in types],
            "subtypes": [{"id": st['id'], "name": st['type_name'], "type_id": st['complaint_type_id']} for st in subtypes],
            "genders": [
                {"value": "male", "label": "Male"},
                {"value": "female", "label": "Female"},
            ],
            "consumer_types": [
                {"value": "domestic", "label": "Domestic"},
                {"value": "commercial", "label": "Commercial"},
                {"value": "industrial", "label": "Industrial"},
            ],
        }, status=status.HTTP_200_OK)


class CMSComplaintCreateView(APIView):
    """
    POST /api/cms/complaints/create/
    Creates a new complaint.
    Accepts multipart/form-data or JSON.
    Enforces server-side zonal permission check.
    """
    permission_classes = [permissions.IsAuthenticated, IsCMSAuthorized]

    def post(self, request):
        allowed_location_ids = get_user_allowed_location_ids(request.user)
        data = request.data

        # 1. Validate required fields
        first_name = str(data.get('first_name', '')).strip()
        cell_number = str(data.get('cell_number', '')).strip()
        location_id = data.get('location_id')
        complaint_type_id = data.get('complaint_type_id')
        complaint_detail = str(data.get('complaint_detail', '')).strip()

        errors = {}
        if not first_name:
            errors['first_name'] = 'Applicant first name is required.'
        if not cell_number:
            errors['cell_number'] = 'Cell number is required.'
        if not location_id:
            errors['location_id'] = 'Location (Zone) is required.'
        if not complaint_type_id:
            errors['complaint_type_id'] = 'Complaint category (type) is required.'
        if not complaint_detail:
            errors['complaint_detail'] = 'Complaint detail / description is required.'

        if errors:
            return Response({"detail": "Validation error.", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Server-side location authorization check
        try:
            loc_id = int(location_id)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid location ID."}, status=status.HTTP_400_BAD_REQUEST)

        if loc_id not in allowed_location_ids:
            return Response(
                {"detail": "You do not have departmental authorization to create complaints in this zone."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 3. Resolve Foreign Keys
        try:
            location = Location.objects.get(id=loc_id)
        except Location.DoesNotExist:
            return Response({"detail": "Selected location not found."}, status=status.HTTP_400_BAD_REQUEST)

        uc = None
        uc_id = data.get('uc_id')
        if uc_id:
            try:
                uc = UC.objects.get(id=int(uc_id))
            except (UC.DoesNotExist, ValueError):
                pass

        complaint_source = None
        source_id = data.get('complaint_source_id')
        if source_id:
            try:
                complaint_source = ComplaintSource.objects.get(id=int(source_id))
            except (ComplaintSource.DoesNotExist, ValueError):
                pass
        else:
            complaint_source = ComplaintSource.objects.filter(source_name__icontains='mobile').first() or ComplaintSource.objects.first()

        try:
            complaint_type = ComplaintType.objects.get(id=int(complaint_type_id))
        except (ComplaintType.DoesNotExist, ValueError):
            return Response({"detail": "Selected complaint type not found."}, status=status.HTTP_400_BAD_REQUEST)

        subtype = None
        subtype_id = data.get('subtype_id')
        if subtype_id:
            try:
                subtype = ComplaintSubType.objects.get(id=int(subtype_id))
            except (ComplaintSubType.DoesNotExist, ValueError):
                pass

        # 4. Handle GPS coordinates if provided
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        address = str(data.get('address', '')).strip()
        if latitude and longitude:
            gps_tag = f"\n[GPS: {latitude}, {longitude}]"
            if gps_tag not in address:
                address = f"{address} {gps_tag}".strip()

        # 5. Create Complaint Instance
        complaint = Complaint(
            location=location,
            uc=uc,
            complaint_source=complaint_source,
            complaint_type=complaint_type,
            SubType=subtype,
            first_name=first_name,
            last_name=str(data.get('last_name', '')).strip(),
            cnic=str(data.get('cnic', '')).strip() or None,
            cell_number=cell_number,
            phone_number=str(data.get('phone_number', '')).strip() or None,
            bill_number=str(data.get('bill_number', '')).strip() or None,
            gender=str(data.get('gender', 'male')).lower(),
            consumer_type=str(data.get('consumer_type', 'domestic')).lower(),
            area=str(data.get('area', '')).strip(),
            tehsil=str(data.get('tehsil', '')).strip(),
            address=address,
            title=str(data.get('title', '')).strip() or (subtype.type_name if subtype else complaint_type.type_name),
            type=str(data.get('type', '')).strip() or None,
            complaint_detail=complaint_detail,
            date=timezone.now().date(),
            status='pending',
        )

        # 6. Handle before_image upload
        if 'before_image' in request.FILES:
            complaint.before_image = request.FILES['before_image']

        complaint.save()

        # Update action log with user
        ComplaintActionLog.objects.filter(complaint=complaint, action='created').update(user=request.user)

        return Response({
            "success": True,
            "message": "Complaint successfully registered.",
            "complaint": {
                "id": complaint.id,
                "complaint_no": f"CMS-{complaint.id}",
                "title": complaint.title,
                "citizen_name": f"{complaint.first_name} {complaint.last_name}".strip(),
                "cell_number": complaint.cell_number,
                "location": location.location_name,
                "uc": uc.uc_name if uc else "N/A",
                "category": complaint_type.type_name,
                "subtype": subtype.type_name if subtype else None,
                "date": complaint.date.strftime("%Y-%m-%d"),
                "status": complaint.status,
                "before_image": complaint.before_image.url if complaint.before_image else None,
            }
        }, status=status.HTTP_201_CREATED)
