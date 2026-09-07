from django.shortcuts import render,get_object_or_404, redirect
from dal import autocomplete
from datetime import datetime
from datetime import date
import json
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import( Employee, EmployeeAttendance, 
                      TubeWell, TubeWellAttendance, Vehicle,Sanitation, VehicleAttendance,
                      FieldVisitReport,Bin, BinAttendance,Watertest,CLC, Activity,
                     WaterSupply, Complaint,STATE_CHOICE,PostAttendance, Post, PostDetail,
                        Revenue, Location, UC, Container, VehiclePerformance)
from .forms import (WaterSupplyReportForm,ComplaintManagementForm,FieldVisitReportForm ,WatertestForm,
                    CLCFilterForm,
                    CLCForm,
                      RevenueManagementReportForm,ComplaintManagementForm, 
                     SanitationForm,PostAttendanceForm)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Location, TubeWell, TubeWellAttendance, WaterSupply, FilterAttendance, Watertest
from django.db.models import F
from django.utils import timezone
from django.shortcuts import render
from .models import Location, Complaint
from django.utils import timezone
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Count
from .forms import FieldVisitReportForm
from .models import FieldVisitReport, Location
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Location, CLC  # Ensure you have the correct imports for your models
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Tracker, TrackerAttendance 
from django.utils import timezone
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Tracker, TrackerAttendance, Location
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from datetime import datetime
from .models import Vehicle, VehiclePE, Location
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from .models import Filter, FilterAttendance, Location
from .forms import FilterAttendanceForm
from datetime import datetime
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Location, TubeWell, TubeWellAttendance, WaterSupply, FilterAttendance, Watertest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Location, Vehicle, VehicleAttendance, Tracker, TrackerAttendance
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib import messages
from datetime import datetime
from .models import EmployeeAttendance, Employee
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import EmployeeAttendance, Employee  # Make sure to import your models
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from xhtml2pdf import pisa
from .models import EmployeeAttendance, VehicleAttendance, Vehicle, Tracker  # Update your imports as necessary
from django.db.models import Count, Q
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Location, Vehicle, VehicleAttendance, Tracker, TrackerAttendance
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from .models import Location, Bin, BinAttendance, Sanitation
from .decorators import view_permission_required
from django.db import models  # Add this import
from django.db.models import Sum
from django.db.models.functions import Cast
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from .forms import FieldVisitReportForm
from .models import FieldVisitReport, Location, LocationPermission
from django.http import JsonResponse
from .models import UC, Bin




class LocationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Ensure the user is authenticated
        if not self.request.user.is_authenticated:
            return Location.objects.none()

        # Get all Location objects
        qs = Location.objects.all()

        # Filter results based on the query (self.q)
        if self.q:
            qs = qs.filter(location_name__icontains=self.q)

        return qs

class UCAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Ensure the user is authenticated
        if not self.request.user.is_authenticated:
            return UC.objects.none()

        # Filter UCs by the forwarded Location (dependent dropdown)
        location_id = self.forwarded.get('location', None)
        qs = UC.objects.all()

        if location_id:
            qs = qs.filter(location_id=location_id)

        # Further filter results based on the query (self.q)
        if self.q:
            qs = qs.filter(uc_name__icontains=self.q)

        return qs

class EmployeeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Employee.objects.none()

        uc_id = self.forwarded.get('uc', None)
        qs = Employee.objects.all()

        if uc_id:
            qs = qs.filter(uc__id=uc_id)  # Filter employees by selected UC

        if self.q:
            qs = qs.filter(name__icontains=self.q)  # Optional: filter by employee name

        return qs

class TubeWellAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return TubeWell.objects.none()

        uc_id = self.forwarded.get('uc', None)
        qs = TubeWell.objects.all()

        if uc_id:
            qs = qs.filter(uc__id=uc_id)  # Filter TubeWells by selected UC

        if self.q:
            qs = qs.filter(tubewell_name__icontains=self.q)

        return qs





@login_required
def get_post_details(request):
    post_type_id = request.GET.get('post_type')
    post_details = PostDetail.objects.filter(post_id=post_type_id).values('id', 'media_channel')
    
    details_dict = {detail['id']: detail['media_channel'] for detail in post_details}
    
    return JsonResponse({'post_details': details_dict})


@login_required
def get_uc_by_location(request):
    location_name = request.GET.get('location')
    if location_name:
        ucs = UC.objects.filter(location__location_name=location_name)
    else:
        ucs = UC.objects.all()

    uc_list = [{'uc_name': uc.uc_name} for uc in ucs]
    return JsonResponse({'ucs': uc_list})


@login_required
def fetch_uc_by_location(request):
    location_id = request.GET.get('location_id')
    ucs = UC.objects.filter(location_id=location_id)
    uc_list = [{'id': uc.id, 'uc_name': uc.uc_name} for uc in ucs]
    return JsonResponse({'uc_list': uc_list})


@login_required
def fetch_bin_by_location(request):
    location_id = request.GET.get('location_id')
    bins = Bin.objects.filter(location_id=location_id)
    bin_list = [{'id': bin.id, 'name_container': bin.name_container} for bin in bins]
    return JsonResponse({'bin_list': bin_list})


@login_required
def fetch_bin_by_uc(request):
    uc_id = request.GET.get('uc_id')
    location_id = request.GET.get('location_id')
    bins = Bin.objects.filter(uc_id=uc_id, location_id=location_id)
    bin_list = [{'id': bin.id, 'name_container': bin.name_container} for bin in bins]
    return JsonResponse({'bin_list': bin_list})


@login_required
def fetch_clc_staff_by_location(request):
    location_id = request.GET.get('location_id')
    clc_staff = CLCStaff.objects.filter(location_id=location_id)
    clc_staff_list = [{'id': staff.id, 'name': staff.name} for staff in clc_staff]
    return JsonResponse({'clc_staff_list': clc_staff_list})



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CLCStaff, Location, UC, NC

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CLCStaff, Location, UC, NC

@login_required
def fetch_clc_staff(request):
    location_id = request.GET.get('location_id')
    uc_id = request.GET.get('uc_id')
    nc_id = request.GET.get('nc_id')

    # Initial filter for CLC Staff
    filters = {}
    
    if location_id:
        filters['location_id'] = location_id
    if uc_id:
        filters['uc_id'] = uc_id
    if nc_id:
        filters['nc_id'] = nc_id
    
    # Fetch filtered CLC staff based on the selected location, UC, and/or NC
    clc_staff = CLCStaff.objects.filter(**filters)
    
    # Prepare the staff data for the response
    clc_staff_list = [{'id': staff.id, 'name': staff.name} for staff in clc_staff]
    return JsonResponse({'clc_staff_list': clc_staff_list})

@login_required
def fetch_ucs_by_location(request):
    location_id = request.GET.get('location_id')
    ucs = UC.objects.filter(location_id=location_id) if location_id else []
    uc_list = [{'id': uc.id, 'name': uc.uc_name} for uc in ucs]
    return JsonResponse({'uc_list': uc_list})

@login_required
def fetch_ncs_by_uc(request):
    uc_id = request.GET.get('uc_id')
    ncs = NC.objects.filter(uc_name_id=uc_id) if uc_id else []
    nc_list = [{'id': nc.id, 'name': nc.nc_name} for nc in ncs]
    return JsonResponse({'nc_list': nc_list})


@login_required
def get_ucs(request):
    location_id = request.GET.get('location_id')
    if location_id:
        ucs = UC.objects.filter(location_id=location_id).values('id', 'uc_name')
        return JsonResponse(list(ucs), safe=False)
    return JsonResponse([], safe=False)


@login_required
def get_tubewells(request):
    uc_id = request.GET.get('uc_id')
    if uc_id:
        tubewells = TubeWell.objects.filter(uc_id=uc_id).values('id', 'tubewell_name')
        return JsonResponse(list(tubewells), safe=False)
    return JsonResponse([], safe=False)


@login_required
def load_officials(request):
    location_id = request.GET.get('location')
    officials = official.objects.filter(location_id=location_id).order_by('name')
    return JsonResponse(list(officials.values('id', 'name')), safe=False)


# views.py
from django.http import JsonResponse
from .models import UC

def dropuc(request):
    location_id = request.GET.get('location_id')
    ucs = UC.objects.filter(location_id=location_id).values('id', 'uc_name')
    return JsonResponse(list(ucs), safe=False)



from django.shortcuts import render
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import CustomPasswordChangeForm

class PasswordUpdateView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'password_change.html'




def password_change_done(request):
    return render(request, 'password_change_done.html')





# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             next_url = request.GET.get('next', 'splash')  
#             return redirect(next_url)
#         else:
#             messages.error(request, 'Invalid username or password.')

#     return render(request, 'login.html')  




def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            # Only lg@123 user
            if user.username == "lg@123":
                 return redirect("api:dashboard")


            # Other users
            next_url = request.GET.get('next', 'splash')
            return redirect(next_url)

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def splash_screen(request):
    return render(request, 'splash.html')





@login_required
def home_view(request):
    
    # Get the date from the request or use today's date
    date_str = request.GET.get('date')
    if date_str:
        selected_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()

    # Determine locations the user can access
    if request.user.is_superuser:
        locations = Location.objects.all()  # Superuser can access all locations
    else:
        # Filter locations based on LocationPermission for non-superusers
        user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
        location_ids = user_permissions.values_list('locations', flat=True)
        locations = Location.objects.filter(id__in=location_ids)

        

    # Employee statistics
    today_attendance = EmployeeAttendance.objects.filter(attendance_date=selected_date, location__in=locations)

    # Filter only active employees (status_id = 1)
    active_employees = Employee.objects.filter(location__in=locations, status_id=1)
    total_employees = active_employees.count()

    # Filter today's attendance only for active employees
    active_employee_ids = active_employees.values_list('id', flat=True)
    total_present = today_attendance.filter(present=True).count()
    total_absent = today_attendance.filter(absent=True).count()
    total_leave = today_attendance.filter(leave=True).count()


       # Calculate percentages if total_employees > 0
    if total_employees > 0:
        present_percentage = (total_present / total_employees) * 100
        absent_percentage = (total_absent / total_employees) * 100
        leave_percentage = (total_leave / total_employees) * 100
    else:
        present_percentage = absent_percentage = leave_percentage = 0

    # TubeWell statistics
    today_tubewell_attendance = TubeWellAttendance.objects.filter(attendance_date=selected_date, location__in=locations)
    total_tubewells = TubeWell.objects.filter(location__in=locations).count()
    total_functional_tubewells = today_tubewell_attendance.filter(functional=True).count()
    total_non_operational_tubewells = today_tubewell_attendance.filter(non_operational=True).count()
    total_non_functional_tubewells = today_tubewell_attendance.filter(non_functional=True).count()

    # Water supply data
    water_supply_data = WaterSupply.objects.filter(date=selected_date, location__in=locations)
    totals_water_supply = {
        'total_new_connections': water_supply_data.aggregate(Sum('new_water_supply_connection_registered'))['new_water_supply_connection_registered__sum'] or 0,
    }

    # Water quality data and location-based totals
    water_quality_data = Watertest.objects.filter(date=selected_date, location__in=locations)
    location_totals = {}
    for test in water_quality_data:
        location_name = test.tubewell.location.location_name  # Adjust as per your model relationships
        location_totals[location_name] = location_totals.get(location_name, 0) + 1
    total_tests = sum(location_totals.values())

  # Filtration statistics
    locations = Location.objects.filter(id__in=request.user.locationpermission_set.values_list('locations', flat=True))

    total_filters = Filter.objects.filter(location__in=locations).count()
    total_functional_filters = FilterAttendance.objects.filter(attendance_date=selected_date, location__in=locations, functional=True).count()
    total_non_functional_filters = FilterAttendance.objects.filter(attendance_date=selected_date, location__in=locations, non_functional=True).count()

    # Vehicle statistics
    total_vehicles = Vehicle.objects.filter(
        location__in=locations,
        status='Active'
    ).count()

    total_functional = VehicleAttendance.objects.filter(
        attendance_date=selected_date,
        vehicle_name__location__in=locations,
        vehicle_name__status='Active',
        functional=True
    ).count()

    total_non_functional = VehicleAttendance.objects.filter(
        attendance_date=selected_date,
        vehicle_name__location__in=locations,
        vehicle_name__status='Active',
        non_functional=True
    ).count()

    total_parked = VehicleAttendance.objects.filter(
        attendance_date=selected_date,
        vehicle_name__location__in=locations,
        vehicle_name__status='Active',
        parked=True
    ).count()

    total_field_operation = VehicleAttendance.objects.filter(
        attendance_date=selected_date,
        vehicle_name__location__in=locations,
        vehicle_name__status='Active',
        field_operation=True
    ).count()

    total_minor_repair = VehicleAttendance.objects.filter(
        attendance_date=selected_date,
        vehicle_name__location__in=locations,
        vehicle_name__status='Active',
        minor_repair=True
    ).count()

    total_major_repair = VehicleAttendance.objects.filter(
        attendance_date=selected_date,
        vehicle_name__location__in=locations,
        vehicle_name__status='Active',
        major_repair=True
    ).count()


     # 🚨 Here's the new fuel aggregation logic (same as in daily_fuel_report)
    fuel_data = Fuel.objects.filter(date=selected_date, location__in=locations)
    total_lfs_trips = fuel_data.aggregate(Sum('lfs_trips_no'))['lfs_trips_no__sum'] or 0
    total_fuel_top_up = fuel_data.aggregate(Sum('fuel_top_up_liters'))['fuel_top_up_liters__sum'] or 0
    


    # Field visit statistics
    total_visits_today = FieldVisitReport.objects.filter(date=selected_date, location__in=locations).count()
    designation_counts = (
        FieldVisitReport.objects.filter(date=selected_date, location__in=locations)
        .values('name_of_official__designation')
        .annotate(total=Count('name_of_official__designation'))
    )



    # Media statistics (daily post attendance)
    post_attendances = PostAttendance.objects.filter(post_date=selected_date)
    post_types = Post.objects.all()
    post_type_counts = {}

    for post_type in post_types:
        post_type_count = post_attendances.filter(post_type=post_type).annotate(
            no_of_post_as_int=Cast('no_of_post', models.IntegerField())
        ).aggregate(total_posts=Sum('no_of_post_as_int'))
        
        post_type_counts[post_type.name] = post_type_count['total_posts'] or 0


    # Complaint statistics
    complaints_today = Complaint.objects.filter(date=selected_date)
    total_complaints = complaints_today.count()
    total_resolved_complaints = complaints_today.filter(status='resolved').count()
    total_pending_complaints = complaints_today.filter(status='pending').count()


    


    # Sanitation statistics - Filter by locations the user can access
    total_sanitation = Sanitation.objects.filter(date=selected_date, location__in=locations)
    total_primary_waste_collection = total_sanitation.aggregate(Sum('primary_waste_collection_tons'))['primary_waste_collection_tons__sum'] or 0
    total_waste_locally_dumped = total_sanitation.aggregate(Sum('waste_locally_dumped_tons'))['waste_locally_dumped_tons__sum'] or 0
    total_waste_dumped_at_lfs = total_sanitation.aggregate(Sum('waste_dumped_at_lfs_tons'))['waste_dumped_at_lfs_tons__sum'] or 0
    total_lfs_trips = total_sanitation.aggregate(Sum('lfs_trips_no'))['lfs_trips_no__sum'] or 0
    total_local_dumping_trips = total_sanitation.aggregate(Sum('local_dumping_trips_no'))['local_dumping_trips_no__sum'] or 0
    total_door_to_door_collection = total_sanitation.aggregate(Sum('door_to_door_solid_waste_collection_no'))['door_to_door_solid_waste_collection_no__sum'] or 0
    total_replacement_of_manhole_covers = total_sanitation.aggregate(Sum('replacement_of_manhole_covers'))['replacement_of_manhole_covers__sum'] or 0
    total_cleaning_de_siltation_of_manhole = total_sanitation.aggregate(Sum('cleaning_de_siltation_of_manholes'))['cleaning_de_siltation_of_manholes__sum'] or 0
    total_cleaning_de_siltation_of_drain_sewars = total_sanitation.aggregate(Sum('cleaning_de_siltation_of_drain_sewars_km'))['cleaning_de_siltation_of_drain_sewars_km__sum'] or 0
    total_fumigation_sprays = total_sanitation.aggregate(Sum('fumigation_sprays_no'))['fumigation_sprays_no__sum'] or 0
    total_ir_spray = total_sanitation.aggregate(Sum('ir_spray_no'))['ir_spray_no__sum'] or 0

    total_containers = Bin.objects.filter(name='container', location__in=locations).count()
    total_moqas = Bin.objects.filter(name='moqa', location__in=locations).count()

    # Count lifted and unlifted containers and Moqas
    total_lifted_containers = BinAttendance.objects.filter(
        lifted=True,
        attendance_date=selected_date,
        bin_name__name='container',
        location__in=locations
    ).count()

    total_unlifted_containers = BinAttendance.objects.filter(
        unlifted=True,
        attendance_date=selected_date,
        bin_name__name='container',
        location__in=locations
    ).count()

    total_lifted_moqas = BinAttendance.objects.filter(
        lifted=True,
        attendance_date=selected_date,
        bin_name__name='moqa',
        location__in=locations
    ).count()

    total_unlifted_moqas = BinAttendance.objects.filter(
        unlifted=True,
        attendance_date=selected_date,
        bin_name__name='moqa',
        location__in=locations
    ).count()
    
# Calculate total fuel issued and total trips for each location


    location_fuel_and_trips = {}
    for location in locations:
        total_fuel_issued = VehiclePE.objects.filter(
            attendance_date=selected_date, 
            location=location
        ).aggregate(Sum('fuel_issued'))['fuel_issued__sum'] or 0
        
        total_primary_trips = VehiclePE.objects.filter(
            attendance_date=selected_date,
            location=location,
            vehicle_type="Primary"
        ).aggregate(Sum('vehicle_trips'))['vehicle_trips__sum'] or 0

        total_secondary_trips = VehiclePE.objects.filter(
            attendance_date=selected_date,
            location=location,
            vehicle_type="Secondary"
        ).aggregate(Sum('vehicle_trips'))['vehicle_trips__sum'] or 0

        location_fuel_and_trips[location.location_name] = {  # Change 'location.name' to 'location.location_name'
            'total_fuel_issued': total_fuel_issued,
            'total_primary_trips': total_primary_trips,
            'total_secondary_trips': total_secondary_trips
        }





            # Water Supply statistics
    
   
       # Bin statistics
    total_bins = Bin.objects.count()
    total_lifted = BinAttendance.objects.filter(lifted=True, attendance_date=selected_date).count()
    total_unlifted = BinAttendance.objects.filter(unlifted=True, attendance_date=selected_date).count()



    # Retrieve today's CLC activity and total reports
    clc_reports_today = CLC.objects.filter(date=selected_date)
    total_clc_reports = clc_reports_today.count()

    # Assume 'Activity' is a ForeignKey field in CLC, adjust if necessary
    clc_activity_data = clc_reports_today.values('activity__name').annotate(total_reports=Count('activity__name'))


    today = timezone.now().date()

    

    # Fetch water quality data for the selected date
    water_quality_data = Watertest.objects.filter(date=selected_date)
    location_totals = {}

    # Calculate totals by location
    for test in water_quality_data:
        location_name = test.tubewell.location.location_name  # Adjust as per your model relationships
        if location_name not in location_totals:
            location_totals[location_name] = 0
        location_totals[location_name] += 1

    # Calculate total number of tests across all locations
    total_tests = sum(location_totals.values())

        

        # Filtration statistics
    total_filters = Filter.objects.filter(status='Active').count()
 # Count only active filters
    total_functional_filters = FilterAttendance.objects.filter(
        attendance_date=selected_date,
        functional=True,
        filter_name__status='Active'  # Only active filters
    ).count()

    total_non_functional_filters = FilterAttendance.objects.filter(
        attendance_date=selected_date,
        non_functional=True,
        filter_name__status='Active'  # Only active filters
    ).count()

    locations = Location.objects.all() 

    revenue_data = Revenue.objects.filter(date=selected_date, location__in=locations)
    
    revenue_totals = {
        'total_recovery_of_day': revenue_data.aggregate(Sum('recovery_of_day'))['recovery_of_day__sum'] or 0,
        'total_billed_amount': revenue_data.aggregate(Sum('billed_amount_total'))['billed_amount_total__sum'] or 0,
        'total_number_of_bills_paid': revenue_data.aggregate(Sum('number_of_bills_paid'))['number_of_bills_paid__sum'] or 0,
    }

    latest_document = Document.objects.order_by('-id').first()


    # Debug output
  
    # Prepare context for rendering
    context = {
         'total_lfs_trips': total_lfs_trips,
        'total_fuel_top_up': total_fuel_top_up,
                'latest_document': latest_document,  # Add latest document to the context

        'present_percentage': present_percentage,
        'absent_percentage': absent_percentage,
        'leave_percentage': leave_percentage,
                'revenue_totals': revenue_totals,

         'location_totals': location_totals,
        'total_tests': total_tests,
        'total_fuel_issued': total_fuel_issued,
    'total_primary_trips': total_primary_trips,
    'total_secondary_trips': total_secondary_trips,
         'total_containers': total_containers,
        'total_moqas': total_moqas,
        'total_lifted_containers': total_lifted_containers,
        'total_unlifted_containers': total_unlifted_containers,
        'total_lifted_moqas': total_lifted_moqas,
        'total_unlifted_moqas': total_unlifted_moqas,
        'total_filters': total_filters,
        'total_functional_filters': total_functional_filters,
        'total_non_functional_filters': total_non_functional_filters,
        'total_visits_today': total_visits_today,
        'designation_counts': designation_counts,
        'today': today,
        'total_clc_reports': total_clc_reports,  # CLC total reports
        'clc_activity_data': clc_activity_data,  #
        'selected_date': selected_date,
        'total_employees': total_employees,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_leave': total_leave,
        'total_bins': total_bins,
        'total_lifted': total_lifted,
        'total_unlifted': total_unlifted,
        'total_tubewells': total_tubewells,
        'total_functional_tubewells': total_functional_tubewells,
        'total_non_operational_tubewells': total_non_operational_tubewells,
        'total_non_functional_tubewells': total_non_functional_tubewells,     

        'total_vehicles': total_vehicles,
        'total_functional': total_functional,
        'total_non_functional': total_non_functional,

        'total_parked': total_parked,
        'total_field_operation': total_field_operation,
        'total_minor_repair': total_minor_repair,
        'total_major_repair': total_major_repair,

        'selected_date': selected_date,
         'totals_water_supply': totals_water_supply,

        'post_attendances': post_attendances,
        'post_types': post_types,
        'post_type_counts': post_type_counts,
        
        'selected_date': selected_date,
        'total_complaints': total_complaints,
    'total_resolved_complaints': total_resolved_complaints,
    'total_pending_complaints': total_pending_complaints,
      
   
        'selected_date': selected_date,
        'locations': locations, 
        'totals': {
            'primary_waste_collection': total_primary_waste_collection,
            'waste_locally_dumped': total_waste_locally_dumped,
            'waste_dumped_at_lfs': total_waste_dumped_at_lfs,
            'lfs_trips': total_lfs_trips,
            'local_dumping_trips': total_local_dumping_trips,
            'door_to_door_collection': total_door_to_door_collection,
            'replacement_of_manhole_covers': total_replacement_of_manhole_covers,
            'cleaning_de_siltation_of_manhole': total_cleaning_de_siltation_of_manhole,
            'cleaning_de_siltation_of_drain_sewars': total_cleaning_de_siltation_of_drain_sewars,
            'fumigation_sprays': total_fumigation_sprays,
            'ir_spray': total_ir_spray,
            
        },

        
        'locations': locations,  # Optional: If you need this for dropdown or other elements
        'selected_date': selected_date,
        

    }

    return render(request, 'home.html', context)




from .models import EmployeeAttendance, Employee, LocationPermission
from .models import Status


@login_required
@view_permission_required('attendance_report')
def attendance_report(request):
    attendance_data = []

    # 🔹 Get allowed locations
    if request.user.is_superuser:
        locations = Location.objects.all().order_by('location_name')
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
        locations = Location.objects.filter(
            id__in=user_permissions.values_list('locations', flat=True)
        ).order_by('location_name')

    # 🔹 Fetch only UCs linked to allowed locations
    ucs = UC.objects.filter(location__in=locations).order_by('uc_name')

    # 🔹 Departments remain the same
    departments = Employee.objects.values_list('department', flat=True).distinct().order_by('department')

    # 🔹 Get filter parameters
    selected_date_str = request.GET.get('date', str(timezone.now().date()))
    search_query = request.GET.get('search_query', '').strip()
    location_filter = request.GET.get('location', '').strip()
    uc_filter = request.GET.get('uc', '').strip()
    department_filter = request.GET.getlist('department')

    # 🔹 Validate date
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        if selected_date > timezone.now().date():
            raise ValueError("You cannot add attendance for a future date.")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('attendance_report')

    # 🔹 Build filters
    filters = Q()
    if search_query:
        filters &= Q(name__icontains=search_query)

    # 🔹 Location filter
    if location_filter:
        try:
            selected_location = Location.objects.get(location_name=location_filter)
            if selected_location.id in locations.values_list('id', flat=True):
                filters &= Q(location=selected_location)
            else:
                messages.error(request, "You do not have permission to view this location.")
                return redirect('attendance_report')
        except Location.DoesNotExist:
            messages.error(request, f"Location '{location_filter}' not found.")

    # 🔹 UC filter (only if UC is in allowed locations)
    if uc_filter:
        uc_obj = UC.objects.filter(uc_name=uc_filter, location__in=locations).first()
        if uc_obj:
            filters &= Q(uc=uc_obj)
        else:
            messages.error(request, f"UC '{uc_filter}' not found or not in allowed locations.")

    # 🔹 Department filter
    if department_filter:
        filters &= Q(department__in=department_filter)

    # 🔹 Fetch active employees in allowed locations
    active_status = Status.objects.get(id=1)
    employees = Employee.objects.filter(filters & Q(location__in=locations) & Q(status=active_status))

    # 🔹 Get attendance records
    attendance_records = EmployeeAttendance.objects.filter(
        attendance_date=selected_date,
        employee_name__in=employees
    )
    attendance_mapping = {record.employee_name.id: record for record in attendance_records}

    # 🔹 Build attendance data
    for employee in employees:
        attendance = attendance_mapping.get(employee.id)
        attendance_data.append({
            'employee_id': employee.employee_id,
            'name': employee.name,
            'father_name': employee.father_name,
            'location': employee.location,
            'uc': employee.uc,
            'department': employee.department,
            'designation': employee.designation,
            'attendance_date': selected_date,
            'present': attendance.present if attendance else True,
            'absent': attendance.absent if attendance else False,
            'leave': attendance.leave if attendance else False,
            'has_attendance': attendance is not None
        })

    # 🔹 Save attendance
    if request.method == 'POST':
        for employee in employees:
            status = request.POST.get(f'status_{employee.employee_id}')
            if status:
                EmployeeAttendance.objects.update_or_create(
                    employee_name=employee,
                    attendance_date=selected_date,
                    defaults={
                        'present': status == 'present',
                        'absent': status == 'absent',
                        'leave': status == 'leave',
                        'uc': employee.uc,
                        'location': employee.location
                    }
                )
        messages.success(request, "Attendance saved successfully.")
        return redirect('attendance_report')

    # 🔹 Context
    context = {
        'attendance_data': attendance_data,
        'date': selected_date,
        'search_query': search_query,
        'location_filter': location_filter,
        'uc_filter': uc_filter,
        'department_filter': department_filter,
        'ucs': ucs,  # 🔥 Now only UCs from allowed locations
        'locations': locations,
        'departments': departments,
    }
    return render(request, 'attendance_report.html', context)


# views.py

from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Employee, EmployeeAttendance, Location, UC, LocationPermission, Status


@login_required
@view_permission_required('total_attendance_report')
def total_attendance_report(request):
    attendance_data = []

    # Get user's allowed locations based on LocationPermission
    if request.user.is_superuser:
        locations = Location.objects.all()  # Superuser can view all locations
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
        locations = Location.objects.filter(id__in=user_permissions.values_list('locations', flat=True))

    # Fetching UCs
    ucs = UC.objects.all()

    # Get start and end date from GET parameters
    start_date_str = request.GET.get('start_date', str(timezone.now().date()))
    end_date_str = request.GET.get('end_date', str(timezone.now().date()))
    search_query = request.GET.get('search_query', '').strip()
    location_filter = request.GET.get('location', '').strip()
    uc_filter = request.GET.get('uc', '').strip()

    # Process start and end date
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if start_date > timezone.now().date() or end_date > timezone.now().date():
            raise ValueError("Dates cannot be in the future.")
        if start_date > end_date:
            raise ValueError("Start date cannot be later than end date.")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('total_attendance_report')

    # Filter employees based on search query, location, and UC
    filters = Q()
    if search_query:
        filters &= Q(name__icontains=search_query)  # Assuming 'name' is the field in Employee

    if location_filter:
        try:
            location_id = Location.objects.get(location_name=location_filter).id
            if location_id in locations.values_list('id', flat=True):  # Check if location is allowed
                filters &= Q(location__id=location_id)
            else:
                messages.error(request, "You do not have permission to view this location.")
                return redirect('total_attendance_report')
        except Location.DoesNotExist:
            messages.error(request, f"Location '{location_filter}' not found.")

    if uc_filter:
        uc_queryset = UC.objects.filter(uc_name=uc_filter)
        if uc_queryset.exists():
            uc_id = uc_queryset.first().id
            filters &= Q(uc__id=uc_id)
        else:
            messages.error(request, f"UC '{uc_filter}' not found.")

    # Filter employees only in allowed locations and with 'Active' status (status id = 1)
    active_status = Status.objects.get(id=1)  # Active status
    employees = Employee.objects.filter(filters & Q(location__in=locations) & Q(status=active_status))

    # Fetch attendance records for the selected date range
    attendance_records = EmployeeAttendance.objects.filter(
        attendance_date__range=[start_date, end_date], employee_name__in=employees)

    # Create a mapping of attendance for easier access
    attendance_mapping = {}
    for record in attendance_records:
        if record.employee_name.id not in attendance_mapping:
            attendance_mapping[record.employee_name.id] = {
                'present': 0,
                'absent': 0,
                'leave': 0
            }
        if record.present:
            attendance_mapping[record.employee_name.id]['present'] += 1
        if record.absent:
            attendance_mapping[record.employee_name.id]['absent'] += 1
        if record.leave:
            attendance_mapping[record.employee_name.id]['leave'] += 1

    # Generate attendance data for each employee
    for employee in employees:
        attendance = attendance_mapping.get(employee.id, {'present': 0, 'absent': 0, 'leave': 0})
        attendance_data.append({
            'employee_id': employee.employee_id,
            'name': employee.name,
            'father_name': employee.father_name,
            'location': employee.location,
            'uc': employee.uc,
            'department': employee.department,
            'designation': employee.designation,
            'attendance_period': f"{start_date} to {end_date}",
            'present': attendance['present'],
            'absent': attendance['absent'],
            'leave': attendance['leave'],
            'total_days': (end_date - start_date).days + 1,
        })

    # Prepare context for rendering
    context = {
        'attendance_data': attendance_data,
        'start_date': start_date,
        'end_date': end_date,
        'search_query': search_query,
        'location_filter': location_filter,
        'uc_filter': uc_filter,
        'ucs': ucs,
        'locations': locations,
    }
    return render(request, 'total_attendance_report.html', context)





@login_required
@view_permission_required('attendance_report_generator')
def attendance_report_generator(request):
    attendance_data = []

    # Fetch locations, UCs, and departments
    locations = Location.objects.all()
    ucs = UC.objects.all()
    departments = Employee.objects.values_list('department', flat=True).distinct()

    # Get query parameters for date range and filters
    start_date_str = request.GET.get('start_date', str(timezone.now().date()))
    end_date_str = request.GET.get('end_date', str(timezone.now().date()))
    location_filter = request.GET.get('location', '').strip()
    uc_filter = request.GET.get('uc', '').strip()
    department_filter = request.GET.get('department', '').strip()
    employee_id_filter = request.GET.get('employee_id', '').strip()
    attendance_status = request.GET.get('attendance_status', '').strip()

    # Check user permissions for location access
    permitted_locations = Location.objects.all()  # Default to all locations

    if not request.user.is_superuser:
        # Fetch user permissions
        user_permissions = LocationPermission.objects.filter(user=request.user)
        
        # If user has location permissions
        if user_permissions.exists():
            permitted_locations = user_permissions.first().locations.all()

            # Filter locations based on user permissions
            locations = locations.filter(id__in=permitted_locations)

            # Apply location filter if needed
            if location_filter and location_filter not in permitted_locations.values_list('location_name', flat=True):
                messages.error(request, f"You do not have permission to view attendance for location '{location_filter}'.")
                return redirect('attendance_report_generator')

    # Process dates
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if start_date > end_date:
            raise ValueError("Start date cannot be later than end date.")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('attendance_report_generator')

    # Filter employees based on location, UC, department, and Employee ID
    filters = Q()
    
    if location_filter:
        try:
            location_id = Location.objects.get(location_name=location_filter).id
            if location_id not in permitted_locations.values_list('id', flat=True):
                messages.error(request, f"You do not have permission to view attendance for location '{location_filter}'.")
                return redirect('attendance_report_generator')
            filters &= Q(location__id=location_id)
        except Location.DoesNotExist:
            messages.error(request, f"Location '{location_filter}' not found.")
    
    if uc_filter:
        uc_queryset = UC.objects.filter(uc_name=uc_filter)
        if uc_queryset.exists():
            if uc_queryset.count() > 1:
                messages.warning(request, f"Multiple UCs found for '{uc_filter}'. Using the first one.")
            uc_id = uc_queryset.first().id
            filters &= Q(uc__id=uc_id)
        else:
            messages.error(request, f"UC '{uc_filter}' not found.")
    
    if department_filter:
        filters &= Q(department__icontains=department_filter)
    
    if employee_id_filter:
        filters &= Q(employee_id__icontains=employee_id_filter)

    # Apply location permission filtering directly in employee query
    employees = Employee.objects.filter(filters, location__in=permitted_locations)

    # Apply attendance status filter to attendance records
    attendance_filters = Q(attendance_date__range=(start_date, end_date), employee_name__in=employees)
    if attendance_status == 'present':
        attendance_filters &= Q(present=True)
    elif attendance_status == 'absent':
        attendance_filters &= Q(absent=True)
    elif attendance_status == 'leave':
        attendance_filters &= Q(leave=True)

    # Fetch only attendance records matching the status
    attendance_records = EmployeeAttendance.objects.filter(attendance_filters)

    # Create a mapping of attendance for easier access, filtering only those with matching attendance records
    attendance_mapping = {}
    for record in attendance_records:
        attendance_mapping.setdefault(record.employee_name.id, []).append(record)

    # Generate attendance data only for employees with matching status records
    for employee_id, attendance_list in attendance_mapping.items():
        employee = Employee.objects.get(id=employee_id)
        attendance_data.append({
            'employee_id': employee.employee_id,
            'name': employee.name,
            'location': employee.location,
            'uc': employee.uc,
            'department': employee.department,
            'designation': employee.designation,
            'status': employee.status.status if employee.status else 'N/A',  # Fetch employee status

            'attendance_records': attendance_list,
            
        })

    # Prepare context for rendering
    context = {
        'attendance_data': attendance_data,
        'start_date': start_date,
        'end_date': end_date,
        'location_filter': location_filter,
        'uc_filter': uc_filter,
        'department_filter': department_filter,
        'employee_id_filter': employee_id_filter,
        'attendance_status': attendance_status,
        'ucs': ucs,
        'locations': locations,
        'departments': departments,
    }
    return render(request, 'attendance_report_generator.html', context)




@login_required
@view_permission_required('attendance_summary')
def attendance_summary(request):
    # Get the selected date from the GET parameters or default to the current date
    selected_date = request.GET.get('date', timezone.now().date())

    # Process the selected date
    if isinstance(selected_date, str):
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()

    # Ensure the selected date is not in the future
    if selected_date > timezone.now().date():
        messages.error(request, "You cannot view attendance for a future date.")
        return redirect('attendance_summary')

    # Check if the user is a superuser
    if request.user.is_superuser:
        # Superuser can view attendance for all locations, only active employees
        locations_queryset = EmployeeAttendance.objects.filter(
            attendance_date=selected_date,
            employee_name__status_id=1
        )
    else:
        # Get the locations the user has permission to view
        location_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
        allowed_locations = location_permissions.values_list('locations__location_name', flat=True)

        # Filter the attendance data to only include allowed locations and active employees
        locations_queryset = EmployeeAttendance.objects.filter(
            attendance_date=selected_date,
            employee_name__location__location_name__in=allowed_locations,
            employee_name__status_id=1
        )

    # Query the attendance data grouped by location
    locations = locations_queryset.values(
        'employee_name__location__location_name'
    ).annotate(
        total_present=Count('id', filter=Q(present=True)),
        total_absent=Count('id', filter=Q(absent=True)),
        total_leave=Count('id', filter=Q(leave=True))
    ).order_by('employee_name__location__location_name')

    # Initialize location-wise summary
    location_wise_summary = {}

    # Prepare data for the chart
    location_labels = []
    total_employees_data = []
    total_present_data = []
    total_leave_data = []
    total_absent_data = []

    # Loop through each location and get department-wise data
    for loc in locations:
        location_name = loc['employee_name__location__location_name']

        # Get the total number of active employees in this location
        total_employees = Employee.objects.filter(
            location__location_name=location_name,
            status_id=1
        ).count()

        # Department-wise attendance data (only for active employees)
        department_summary = EmployeeAttendance.objects.filter(
            attendance_date=selected_date,
            employee_name__location__location_name=location_name,
            employee_name__status_id=1
        ).values(
            'employee_name__department'
        ).annotate(
            total_present=Count('id', filter=Q(present=True)),
            total_absent=Count('id', filter=Q(absent=True)),
            total_leave=Count('id', filter=Q(leave=True))
        )

        # Totals for the location
        total_present = total_absent = total_leave = 0
        for department in department_summary:
            total_present += department['total_present']
            total_absent += department['total_absent']
            total_leave += department['total_leave']

        # Calculate the overall total for the location
        total_attendance = total_present + total_absent + total_leave

        # Add the summary data to the location_wise_summary
        location_wise_summary[location_name] = {
            'total_employees': total_employees,
            'departments': department_summary,
            'totals': {
                'total_present': total_present,
                'total_absent': total_absent,
                'total_leave': total_leave,
                'total_attendance': total_attendance,
            }
        }

        # Collect data for the chart
        location_labels.append(location_name)
        total_employees_data.append(total_employees)
        total_present_data.append(total_present)
        total_leave_data.append(total_leave)
        total_absent_data.append(total_absent)

    # Get attendance summary for all locations (filtered by permission and active employees)
    all_locations_summary = locations_queryset.values(
        'employee_name__location__location_name'
    ).annotate(
        total_present=Count('id', filter=Q(present=True)),
        total_absent=Count('id', filter=Q(absent=True)),
        total_leave=Count('id', filter=Q(leave=True))
    ).order_by('employee_name__location__location_name')

    department_summary_all_locations = locations_queryset.values(
        'employee_name__department'
    ).annotate(
        total_present=Count('id', filter=Q(present=True)),
        total_absent=Count('id', filter=Q(absent=True)),
        total_leave=Count('id', filter=Q(leave=True))
    ).order_by('employee_name__department')

    # Calculate overall totals across all departments (filtered by permission and active employees)
    overall_totals = locations_queryset.aggregate(
        total_present=Count('id', filter=Q(present=True)),
        total_absent=Count('id', filter=Q(absent=True)),
        total_leave=Count('id', filter=Q(leave=True))
    )
    overall_totals['total_attendance'] = (
        overall_totals['total_present'] + overall_totals['total_absent'] + overall_totals['total_leave']
    )

    # Pass the data to the template
    context = {
        'location_wise_summary': location_wise_summary,
        'selected_date': selected_date,
        'location_labels': location_labels,
        'total_employees_data': total_employees_data,
        'total_present_data': total_present_data,
        'total_leave_data': total_leave_data,
        'total_absent_data': total_absent_data,
        'all_locations_summary': all_locations_summary,
        'department_summary_all_locations': department_summary_all_locations,
        'overall_totals': overall_totals,
    }

    return render(request, 'attendance_summary.html', context)




def get_complaint_summary(report_date, user):
    # This function returns the complaint summary data for a specific date
    complaint_summary = []
    total_complaints = total_resolved = total_pending = 0
    source_summary = {}

    # Get the locations the user has permission to view
    locations = Location.objects.all()

    # Check if the user is not a superuser and filter locations based on user permissions
    if not user.is_superuser:
        user_locations = LocationPermission.objects.filter(
            user=user, can_view=True
        ).values_list('locations', flat=True)
        locations = locations.filter(id__in=user_locations)

    # Iterate over the locations the user has permission to view
    for location in locations:
        complaints = Complaint.objects.filter(date=report_date, location=location)

        total_location_complaints = complaints.count()
        resolved_complaints = complaints.filter(status='resolved').count()
        pending_complaints = complaints.filter(status='pending').count()

        location_source_summary = {}
        for complaint in complaints:
            source = complaint.complaint_source
            if source not in location_source_summary:
                location_source_summary[source] = {'total': 0, 'resolved': 0, 'pending': 0}
            location_source_summary[source]['total'] += 1
            if complaint.status == 'resolved':
                location_source_summary[source]['resolved'] += 1
            else:
                location_source_summary[source]['pending'] += 1

            # Update the global source summary
            if source not in source_summary:
                source_summary[source] = {'total': 0, 'resolved': 0, 'pending': 0}
            source_summary[source]['total'] += 1
            if complaint.status == 'resolved':
                source_summary[source]['resolved'] += 1
            else:
                source_summary[source]['pending'] += 1

        # Update overall totals
        total_complaints += total_location_complaints
        total_resolved += resolved_complaints
        total_pending += pending_complaints

        # Add summary data for this location
        complaint_summary.append({
            'location': location,
            'total_complaints': total_location_complaints,
            'resolved_complaints': resolved_complaints,
            'pending_complaints': pending_complaints,
            'source_summary': location_source_summary,
        })

    return complaint_summary


from django.db.models import Sum

def get_fuel_summary(report_date, user):
    """
    Returns cumulative and per-location fuel data for a specific date and user.
    """
    # Superusers see all locations except Headoffice
    if user.is_superuser:
        locations = Location.objects.exclude(location_name="Headoffice")
    else:
        user_locations = LocationPermission.objects.filter(
            user=user, can_view=True
        ).values_list('locations__id', flat=True)
        locations = Location.objects.filter(id__in=user_locations).exclude(location_name="Headoffice")

    fuel_data_per_location = []
    fuel_totals = {
        'lfs_trips_no': 0,
        'primary_trips': 0,
        'fuel_top_up_liters': 0,
    }

    for location in locations:
        fuel_qs = Fuel.objects.filter(date=report_date, location=location)
        location_totals = {
            'location': location,
            'lfs_trips_no': fuel_qs.aggregate(Sum('lfs_trips_no'))['lfs_trips_no__sum'] or 0,
            'primary_trips': fuel_qs.aggregate(Sum('primary_trips'))['primary_trips__sum'] or 0,
            'fuel_top_up_liters': fuel_qs.aggregate(Sum('fuel_top_up_liters'))['fuel_top_up_liters__sum'] or 0,
        }

        # Add to cumulative totals
        fuel_totals['lfs_trips_no'] += location_totals['lfs_trips_no']
        fuel_totals['primary_trips'] += location_totals['primary_trips']
        fuel_totals['fuel_top_up_liters'] += location_totals['fuel_top_up_liters']

        fuel_data_per_location.append(location_totals)

    return {
        'totals': fuel_totals,
        'by_location': fuel_data_per_location,
    }


@login_required
@view_permission_required('attendance_summary_pdf')
def attendance_summary_pdf(request):
    selected_date = request.GET.get('date', timezone.now().date())

    # Convert selected_date string to date
    if isinstance(selected_date, str):
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()

    # Prevent access to future dates
    if selected_date > timezone.now().date():
        return redirect('home')

    # Retrieve the user's permitted location IDs
    location_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
    permitted_location_ids = list(location_permissions.values_list('locations', flat=True))

    if not permitted_location_ids:
        return redirect('home')

    # Get full Location objects to loop through
    permitted_locations = Location.objects.filter(id__in=permitted_location_ids)

    # Determine display name
    if permitted_locations.count() == 1:
        location_display = permitted_locations.first().location_name
    else:
        location_display = "All WSSP"


    # Filter attendance by permitted locations
    department_summary_all_locations = EmployeeAttendance.objects.filter(
        attendance_date=selected_date,
        location__in=permitted_locations  # Assuming attendance has a location field
    ).values(
        'employee_name__department'
    ).annotate(
        total_present=Count('id', filter=Q(present=True)),
        total_absent=Count('id', filter=Q(absent=True)),
        total_leave=Count('id', filter=Q(leave=True))
    ).order_by('employee_name__department')

    # Calculate totals in the view
    if department_summary_all_locations:
        overall_totals = {
            'total_present': sum(d['total_present'] for d in department_summary_all_locations),
            'total_absent': sum(d['total_absent'] for d in department_summary_all_locations),
            'total_leave': sum(d['total_leave'] for d in department_summary_all_locations),
        }
    else:
        # messages.error(request, "No records found for the selected date.")
        return redirect('home')

    # Your code to generate and return the PDF would go here.

    # Initialize counters for vehicle attendance
    vehicles = Vehicle.objects.all()
    total_vehicles = 0
    total_functional = 0
    total_non_functional = 0
    total_functional_parked = 0
    total_functional_field_operation = 0
    total_non_functional_minor_repair = 0
    total_non_functional_major_repair = 0

    for vehicle in vehicles:
        attendance = VehicleAttendance.objects.filter(
            vehicle_name=vehicle,
            attendance_date=selected_date,
            location__in=permitted_locations
        ).first()
        
        if attendance:
            total_vehicles += 1
            if attendance.functional:
                total_functional += 1
                if attendance.parked:
                    total_functional_parked += 1
                if attendance.field_operation:
                    total_functional_field_operation += 1
            elif attendance.non_functional:
                total_non_functional += 1
                if attendance.minor_repair:
                    total_non_functional_minor_repair += 1
                if attendance.major_repair:
                    total_non_functional_major_repair += 1

    # ✅ Moved outside the loop!
    total_fleet = (
        total_functional_parked +
        total_functional_field_operation +
        total_non_functional_minor_repair +
        total_non_functional_major_repair
    )                         

    fuel_summary = get_fuel_summary(selected_date, request.user)


     # Designation-wise counts for the selected date
    designation_counts = (
        FieldVisitReport.objects.filter(date=selected_date, location__in=permitted_locations)  # Apply location filter
        .values('name_of_official__designation')
        .annotate(total=Count('name_of_official__designation'))
    )

    # Activity-wise summary for the selected date
    activity_summary = (
        CLC.objects.filter(date=selected_date, location__in=permitted_locations)  # Apply location filter
        .values('activity__name')
        .annotate(total_reports=Count('id'))
        .order_by('activity__name')
    )


# Initialize type summary
    type_summary = {}

    # Filter complaints based on the selected date and the permitted locations
    complaints = Complaint.objects.filter(
        date=selected_date, 
        location__in=permitted_locations  # Ensure you're filtering by allowed locations
    )

    for complaint in complaints:
        complaint_type = complaint.complaint_type
        if complaint_type not in type_summary:
            type_summary[complaint_type] = {'total': 0, 'resolved': 0, 'pending': 0}
        
        type_summary[complaint_type]['total'] += 1
        
        # Count the resolved and pending complaints
        if complaint.status == 'resolved':
            type_summary[complaint_type]['resolved'] += 1
        else:
            type_summary[complaint_type]['pending'] += 1


    # Assuming you have a user object available (e.g., request.user)
    user = request.user

    # Get the locations the user has permission to view
    location_permissions = LocationPermission.objects.filter(user=user, can_view=True)

    # Extract the locations the user has access to
    allowed_locations = location_permissions.values_list('locations', flat=True)

    # Add the total KPIs for Tubewells
    total_tubewells = TubeWell.objects.filter(location__in=allowed_locations).count()  # Filter by allowed locations

    total_functional_tubewells = TubeWellAttendance.objects.filter(
        attendance_date=selected_date, 
        functional=True,
        location__in=allowed_locations  # Filter by allowed locations
    ).count()

    total_non_operational_tubewells = TubeWellAttendance.objects.filter(
        attendance_date=selected_date, 
        non_operational=True,
        location__in=allowed_locations  # Filter by allowed locations
    ).count()

    total_non_functional_tubewells = TubeWellAttendance.objects.filter(
        attendance_date=selected_date, 
        non_functional=True,
        location__in=allowed_locations  # Filter by allowed locations
    ).count()

    total_new_connections = WaterSupply.objects.filter(
        date=selected_date,
        location__in=allowed_locations  # Filter by allowed locations
    ).aggregate(Sum('new_water_supply_connection_registered'))['new_water_supply_connection_registered__sum'] or 0

    total_functional_filtration = FilterAttendance.objects.filter(
        attendance_date=selected_date, 
        functional=True,
        location__in=allowed_locations  # Filter by allowed locations
    ).count()

    total_non_functional_filtration = FilterAttendance.objects.filter(
        attendance_date=selected_date, 
        non_functional=True,
        location__in=allowed_locations  # Filter by allowed locations
    ).count()

    total_tests = Watertest.objects.filter(
        date=selected_date,
        location__in=allowed_locations  # Filter by allowed locations
    ).count()

    total_safe_tests = Watertest.objects.filter(
        date=selected_date,
        output='safe',
        location__in=allowed_locations  # Filter by allowed locations
    ).count()

    total_unsafe_tests = Watertest.objects.filter(
        date=selected_date,
        output='unsafe',
        location__in=allowed_locations  # Filter by allowed locations
    ).count()


   
            
    # Media summary data
    post_type_id = request.GET.get('post_type', 'all')
    post_attendances = PostAttendance.objects.filter(post_date=selected_date)
    if post_type_id != "all":
        post_attendances = post_attendances.filter(post_type_id=post_type_id)

    media_summary = (
        post_attendances
        .values(post_type_name=F('post_type__name'), platform_name=F('post_detail__media_channel'))
        .annotate(total_posts=Count('id'))
    )
    
    total_posts = post_attendances.count()

     # Fetch complaint summary data for the selected date
        # Get the locations the user has permission to view
    locations = Location.objects.all()


    complaint_summary = get_complaint_summary(selected_date, request.user)  # Ensure this line is correctly defined

    # Check if the user is not a superuser and filter locations based on user permissions
    if not request.user.is_superuser:
        user_locations = LocationPermission.objects.filter(
            user=request.user, can_view=True
        ).values_list('locations', flat=True)
        locations = locations.filter(id__in=user_locations)

    # Optionally filter by a specific location passed in the request
    location_filter = request.GET.get('location', None)
    filtered_locations = locations.filter(id=location_filter) if location_filter else locations

    # Initialize summary variables
    type_summary = {}
    total_received = 0
    total_resolved = 0
    total_pending = 0

    # Fetch the complaints for the selected date and filtered locations
    complaints = Complaint.objects.filter(date=selected_date, location__in=filtered_locations)

    # Process the complaints
    for complaint in complaints:
        complaint_type = complaint.complaint_type
        if complaint_type not in type_summary:
            type_summary[complaint_type] = {'total': 0, 'resolved': 0, 'pending': 0}
        
        type_summary[complaint_type]['total'] += 1
        if complaint.status == 'resolved':
            type_summary[complaint_type]['resolved'] += 1
        else:
            type_summary[complaint_type]['pending'] += 1
        
        total_received += 1
        if complaint.status == 'resolved':
            total_resolved += 1
        else:
            total_pending += 1


    # Assuming today is the default date if no date is provided in the request
    today = datetime.today().date()

    # Get the selected date from the GET request or default to today
    selected_date_str = request.GET.get('date', None)
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date() if selected_date_str else today

    # Get the current month and year from the selected date
    current_month = selected_date.month
    current_year = selected_date.year

    # Get all locations
    locations = Location.objects.all()

    # Check if the user is not a superuser and filter locations based on user permissions
    if not request.user.is_superuser:
        user_locations = LocationPermission.objects.filter(
            user=request.user, can_view=True
        ).values_list('locations', flat=True)
        locations = locations.filter(id__in=user_locations)

    # Optionally filter by a specific location passed in the request
    location_filter = request.GET.get('location', None)
    filtered_locations = locations.filter(id=location_filter) if location_filter else locations

    # Initialize a list to hold the total revenue summary data
    total_revenue_summary = []

    # Iterate over each filtered location to calculate the revenue data
    for location in filtered_locations:
        # Get revenue data for the current location
        revenue_data = Revenue.objects.filter(location=location)

        # Calculate the total recovery for the selected day
        total_recovery_day_water_supply = revenue_data.filter(date=selected_date).aggregate(
            total=Sum('recovery_day_water_supply')
        )['total'] or 0

        total_recovery_day_solid_waste_management = revenue_data.filter(date=selected_date).aggregate(
            total=Sum('recovery_day_solid_waste_management')
        )['total'] or 0

        total_recovery_of_day = total_recovery_day_water_supply + total_recovery_day_solid_waste_management

        # Calculate the total bill paid for the selected day
        total_bill_paid_day_water_supply = revenue_data.filter(date=selected_date).aggregate(
            total=Sum('bill_paid_day_water_supply')
        )['total'] or 0

        total_bill_paid_day_solid_waste_management = revenue_data.filter(date=selected_date).aggregate(
            total=Sum('bill_paid_day_solid_waste_management')
        )['total'] or 0

        # Calculate the total paid amount for the current month
        total_paid_month_water_supply = revenue_data.filter(
            date__month=current_month, date__year=current_year
        ).aggregate(total=Sum('total_paid_month_water_supply'))['total'] or 0

        total_paid_month_solid_waste_management = revenue_data.filter(
            date__month=current_month, date__year=current_year
        ).aggregate(total=Sum('total_paid_month_solid_waste_management'))['total'] or 0

        # Calculate the total billed amount for the selected day
        total_billed_amount_total = revenue_data.filter(
            date=selected_date
        ).aggregate(total=Sum('billed_amount_total'))['total'] or 0

        # Calculate the total number of bills paid for the selected day
        total_number_of_bills_paid = revenue_data.filter(
            date=selected_date
        ).aggregate(total=Sum('number_of_bills_paid'))['total'] or 0

        # Append the calculated data for the current location
        total_revenue_summary.append({
            'location': location,
            'total_recovery_day_water_supply': total_recovery_day_water_supply,
            'total_recovery_day_solid_waste_management': total_recovery_day_solid_waste_management,
            'total_recovery_of_day': total_recovery_of_day,
            'total_bill_paid_day_water_supply': total_bill_paid_day_water_supply,
            'total_bill_paid_day_solid_waste_management': total_bill_paid_day_solid_waste_management,
            'total_paid_month_water_supply': total_paid_month_water_supply,
            'total_paid_month_solid_waste_management': total_paid_month_solid_waste_management,
            'total_billed_amount_total': total_billed_amount_total,
            'total_number_of_bills_paid': total_number_of_bills_paid,
        })

    # Calculate the totals across all locations
    totals = {
        'total_recovery_day_water_supply': sum(item['total_recovery_day_water_supply'] for item in total_revenue_summary),
        'total_recovery_day_solid_waste_management': sum(item['total_recovery_day_solid_waste_management'] for item in total_revenue_summary),
        'total_recovery_of_day': sum(item['total_recovery_of_day'] for item in total_revenue_summary),
        'total_bill_paid_day_water_supply': sum(item['total_bill_paid_day_water_supply'] for item in total_revenue_summary),
        'total_bill_paid_day_solid_waste_management': sum(item['total_bill_paid_day_solid_waste_management'] for item in total_revenue_summary),
        'total_paid_month_water_supply': sum(item['total_paid_month_water_supply'] for item in total_revenue_summary),
        'total_paid_month_solid_waste_management': sum(item['total_paid_month_solid_waste_management'] for item in total_revenue_summary),
        'total_billed_amount_total': sum(item['total_billed_amount_total'] for item in total_revenue_summary),
        'total_number_of_bills_paid': sum(item['total_number_of_bills_paid'] for item in total_revenue_summary),
    }


    location_data = []
    total_sanitation = {
        'primary_waste_collection': 0,
        'waste_locally_dumped': 0,
        'waste_dumped_at_lfs': 0,
        'lfs_trips': 0,
        'local_dumping_trips': 0,
        'door_to_door_collection': 0,
        'replacement_of_manhole_covers': 0,
        'cleaning_de_siltation_of_manhole': 0,
        'cleaning_de_siltation_of_drain_sewers': 0,
        'fumigation_sprays': 0,
        'ir_spray': 0,
        'total_moqas': 0,
        'lifted_moqas': 0,
        'unlifted_moqas': 0,
        'total_containers': 0,
        'lifted_containers': 0,
        'unlifted_containers': 0
    }

    for location in permitted_locations:
        # Filter sanitation data by permitted locations
        sanitation = Sanitation.objects.filter(location=location, date=selected_date).first()

        total_moqas = Bin.objects.filter(location=location, name='moqa').count()
        total_containers = Bin.objects.filter(location=location, name='container').count()
        
        lifted_moqas = BinAttendance.objects.filter(location=location, attendance_date=selected_date, bin_name__name='moqa', lifted=True).count()
        unlifted_moqas = BinAttendance.objects.filter(location=location, attendance_date=selected_date, bin_name__name='moqa', lifted=False).count()
        
        lifted_containers = BinAttendance.objects.filter(location=location, attendance_date=selected_date, bin_name__name='container', lifted=True).count()
        unlifted_containers = BinAttendance.objects.filter(location=location, attendance_date=selected_date, bin_name__name='container', lifted=False).count()

        # Add the sanitation data for totals aggregation
        total_sanitation['primary_waste_collection'] += sanitation.primary_waste_collection_tons or 0 if sanitation else 0
        total_sanitation['waste_locally_dumped'] += sanitation.waste_locally_dumped_tons or 0 if sanitation else 0
        total_sanitation['waste_dumped_at_lfs'] += sanitation.waste_dumped_at_lfs_tons or 0 if sanitation else 0
        total_sanitation['lfs_trips'] += sanitation.lfs_trips_no or 0 if sanitation else 0
        total_sanitation['local_dumping_trips'] += sanitation.local_dumping_trips_no or 0 if sanitation else 0
        total_sanitation['door_to_door_collection'] += sanitation.door_to_door_solid_waste_collection_no or 0 if sanitation else 0
        total_sanitation['replacement_of_manhole_covers'] += sanitation.replacement_of_manhole_covers or 0 if sanitation else 0
        total_sanitation['cleaning_de_siltation_of_manhole'] += sanitation.cleaning_de_siltation_of_manholes or 0 if sanitation else 0
        total_sanitation['cleaning_de_siltation_of_drain_sewers'] += sanitation.cleaning_de_siltation_of_drain_sewars_km or 0 if sanitation else 0
        total_sanitation['fumigation_sprays'] += sanitation.fumigation_sprays_no or 0 if sanitation else 0
        total_sanitation['ir_spray'] += sanitation.ir_spray_no or 0 if sanitation else 0

        # For bin data
        total_sanitation['total_moqas'] += total_moqas
        total_sanitation['lifted_moqas'] += lifted_moqas
        total_sanitation['unlifted_moqas'] += unlifted_moqas
        total_sanitation['total_containers'] += total_containers
        total_sanitation['lifted_containers'] += lifted_containers
        total_sanitation['unlifted_containers'] += unlifted_containers

        # Add the location-wise data to location_data
        location_data.append({
            'location': location,
            'total_moqas': total_moqas,
            'total_containers': total_containers,
            'lifted_moqas': lifted_moqas,
            'unlifted_moqas': unlifted_moqas,
            'lifted_containers': lifted_containers,
            'unlifted_containers': unlifted_containers,
            'primary_waste_collection': sanitation.primary_waste_collection_tons if sanitation else 0,
            'waste_locally_dumped': sanitation.waste_locally_dumped_tons if sanitation else 0,
            'waste_dumped_at_lfs': sanitation.waste_dumped_at_lfs_tons if sanitation else 0,
            'lfs_trips': sanitation.lfs_trips_no if sanitation else 0,
            'local_dumping_trips': sanitation.local_dumping_trips_no if sanitation else 0,
            'door_to_door_collection': sanitation.door_to_door_solid_waste_collection_no if sanitation else 0,
            'replacement_of_manhole_covers': sanitation.replacement_of_manhole_covers if sanitation else 0,
            'cleaning_de_siltation_of_manhole': sanitation.cleaning_de_siltation_of_manholes if sanitation else 0,
            'cleaning_de_siltation_of_drain_sewers': sanitation.cleaning_de_siltation_of_drain_sewars_km if sanitation else 0,
            'fumigation_sprays': sanitation.fumigation_sprays_no if sanitation else 0,
            'ir_spray': sanitation.ir_spray_no if sanitation else 0,
        })

        # Get trip data for vehicles (Filtered by location and date)
        trip_data = VehiclePE.objects.filter(attendance_date=selected_date, location__in=permitted_locations)

        # Sum the primary trips (where vehicle_type = 'Primary')
        total_primary_trip = trip_data.filter(vehicle_type='Primary').aggregate(Sum('vehicle_trips'))['vehicle_trips__sum'] or 0

        # Sum the secondary trips (where vehicle_type = 'Secondary')
        total_secondary_trip = trip_data.filter(vehicle_type='Secondary').aggregate(Sum('vehicle_trips'))['vehicle_trips__sum'] or 0

        # Total fuel issued
        total_fuel = trip_data.aggregate(Sum('fuel_issued'))['fuel_issued__sum'] or 0

 
    
    
    context = {
        'complaint_summary': complaint_summary,
        
        'total_primary_trip': total_primary_trip,
    'total_secondary_trip': total_secondary_trip,
    'total_fuel': total_fuel,
        'selected_date': selected_date,
        'department_summary_all_locations': department_summary_all_locations,
        'total_vehicles': total_vehicles,
        'total_functional': total_functional,
        'total_non_functional': total_non_functional,
        'total_functional_parked': total_functional_parked,
        'total_functional_field_operation': total_functional_field_operation,
        'total_non_functional_minor_repair': total_non_functional_minor_repair,
        'total_non_functional_major_repair': total_non_functional_major_repair,
        'designation_counts': designation_counts,  # Include designation totals
        'activity_summary': activity_summary,  # Include activity summary
        'type_summary': type_summary,
        'total_tubewells': total_tubewells,
        'total_functional': total_functional_tubewells,
        'total_non_operational': total_non_operational_tubewells,
        'total_non_functional': total_non_functional_tubewells,
        'total_new_connections': total_new_connections,
        'total_functional_filtration': total_functional_filtration,
        'total_non_functional_filtration': total_non_functional_filtration,
        'total_tests': total_tests,
        'total_safe_tests': total_safe_tests,
        'total_unsafe_tests': total_unsafe_tests,
        'media_summary': media_summary,  # Add media summary to context
        'complaint_summary': complaint_summary,  # Add complaint data to the context
            'activity_summary': activity_summary,  # Add activity summary to the context
        'total_revenue_summary': total_revenue_summary,
        'department_summary_all_locations': department_summary_all_locations,
    'overall_totals': overall_totals,
            'type_summary': type_summary,  # Pass complaint type summary to context
            
        'total_received': total_received,
        'total_resolved': total_resolved,
        'total_pending': total_pending,
        'total_primary_waste_collection': total_sanitation['primary_waste_collection'],
    'total_waste_locally_dumped': total_sanitation['waste_locally_dumped'],
    'total_waste_dumped_at_lfs': total_sanitation['waste_dumped_at_lfs'],
    'total_lfs_trips': total_sanitation['lfs_trips'],
    'total_local_dumping_trips': total_sanitation['local_dumping_trips'],
    'total_door_to_door_collection': total_sanitation['door_to_door_collection'],
    'total_replacement_of_manhole_covers': total_sanitation['replacement_of_manhole_covers'],
    'total_cleaning_de_siltation_of_manhole': total_sanitation['cleaning_de_siltation_of_manhole'],
    'total_cleaning_de_siltation_of_drain_sewers': total_sanitation['cleaning_de_siltation_of_drain_sewers'],
    'total_fumigation_sprays': total_sanitation['fumigation_sprays'],
    'total_ir_spray': total_sanitation['ir_spray'],
    'total_moqas': total_sanitation['total_moqas'],
    'total_lifted_moqas': total_sanitation['lifted_moqas'],
    'total_unlifted_moqas': total_sanitation['unlifted_moqas'],
    'total_containers': total_sanitation['total_containers'],
    'total_lifted_containers': total_sanitation['lifted_containers'],
    'total_unlifted_containers': total_sanitation['unlifted_containers'],
     'fuel_totals': fuel_summary['totals'],
    'fuel_data_per_location': fuel_summary['by_location'],
     "total_fleet": total_fleet,
      'location_display': location_display,




    }

    template_path = 'attendance_summary_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="WSSP-DPR-Report-{selected_date}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


import xlsxwriter
from io import BytesIO
from django.http import HttpResponse


import xlsxwriter
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now


@login_required
@view_permission_required('attendance_summary_excel')
def attendance_summary_excel(request):
    selected_date = request.GET.get('date', now().date())
    if isinstance(selected_date, str):
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = now().date()

    if selected_date > now().date():
        messages.error(request, "You cannot view attendance for a future date.")
        return redirect('attendance_summary')

    # Fetch data (similar to your PDF logic)
    department_summary_all_locations = EmployeeAttendance.objects.filter(attendance_date=selected_date).values(
        'employee_name__department'
    ).annotate(
        total_present=Count('id', filter=Q(present=True)),
        total_absent=Count('id', filter=Q(absent=True)),
        total_leave=Count('id', filter=Q(leave=True))
    ).order_by('employee_name__department')

    vehicles = Vehicle.objects.all()
    total_vehicles = 0
    total_functional = 0
    total_non_functional = 0
    total_functional_parked = 0
    total_functional_field_operation = 0
    total_non_functional_minor_repair = 0
    total_non_functional_major_repair = 0

    for vehicle in vehicles:
        attendance = VehicleAttendance.objects.filter(vehicle_name=vehicle, attendance_date=selected_date).first()
        if attendance:
            total_vehicles += 1
            if attendance.functional:
                total_functional += 1
                if attendance.parked:
                    total_functional_parked += 1
                if attendance.field_operation:
                    total_functional_field_operation += 1
            elif attendance.non_functional:
                total_non_functional += 1
                if attendance.minor_repair:
                    total_non_functional_minor_repair += 1
                if attendance.major_repair:
                    total_non_functional_major_repair += 1

    designation_counts = FieldVisitReport.objects.filter(date=selected_date).values('name_of_official__designation').annotate(total=Count('name_of_official__designation'))
    activity_summary = CLC.objects.filter(date=selected_date).values('activity__name').annotate(total_reports=Count('id')).order_by('activity__name')
    type_summary = {}
    complaints = Complaint.objects.filter(date=selected_date)
    for complaint in complaints:
        complaint_type = complaint.complaint_type
        if complaint_type not in type_summary:
            type_summary[complaint_type] = {'total': 0, 'resolved': 0, 'pending': 0}
        type_summary[complaint_type]['total'] += 1
        if complaint.status == 'resolved':
            type_summary[complaint_type]['resolved'] += 1
        else:
            type_summary[complaint_type]['pending'] += 1

    # Calculate the WATER SUPPLY section data
    total_tubewells = TubeWell.objects.count()
    total_functional_tubewells = TubeWellAttendance.objects.filter(attendance_date=selected_date, functional=True).count()
    total_non_operational_tubewells = TubeWellAttendance.objects.filter(attendance_date=selected_date, non_operational=True).count()
    total_non_functional_tubewells = TubeWellAttendance.objects.filter(attendance_date=selected_date, non_functional=True).count()
    total_new_connections = WaterSupply.objects.filter(date=selected_date).aggregate(Sum('new_water_supply_connection_registered'))['new_water_supply_connection_registered__sum'] or 0
    total_functional_filtration = FilterAttendance.objects.filter(attendance_date=selected_date, functional=True).count()
    total_non_functional_filtration = FilterAttendance.objects.filter(attendance_date=selected_date, non_functional=True).count()
    total_tests = Watertest.objects.filter(date=selected_date).count()
    total_safe_tests = Watertest.objects.filter(date=selected_date, output='safe').count()
    total_unsafe_tests = Watertest.objects.filter(date=selected_date, output='unsafe').count()

    # Create Excel file
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Summary')
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'align': 'center'})

    row = 0

    # Add header
    worksheet.merge_range('A1:E1', 'WATER & SANITATION SERVICES PESHAWAR (WSSP)', header_format)
    worksheet.merge_range('A2:E2', f'Daily Progress Report - {selected_date}', header_format)
    row += 3

    # Department-wise attendance summary
    worksheet.write(row, 0, "Attendance Summary", header_format)
    row += 1
    headers = ['Department', 'Total Present', 'Total Absent', 'Total Leave']
    for col_num, header in enumerate(headers):
        worksheet.write(row, col_num, header, header_format)
    row += 1
    for record in department_summary_all_locations:
        worksheet.write(row, 0, record['employee_name__department'])
        worksheet.write(row, 1, record['total_present'])
        worksheet.write(row, 2, record['total_absent'])
        worksheet.write(row, 3, record['total_leave'])
        row += 1

    # Vehicle attendance summary
    worksheet.write(row, 0, "Fleet Summary", header_format)
    row += 1
    headers = [
        'Total Functional', 'Total Non-Functional',
        'Functional Parked', 'Field Operation', 'Minor Repair', 'Major Repair'
    ]
    for col_num, header in enumerate(headers):
        worksheet.write(row, col_num, header, header_format)
    row += 1
    data = [
        total_functional, total_non_functional,
        total_functional_parked, total_functional_field_operation,
        total_non_functional_minor_repair, total_non_functional_major_repair
    ]
    for col_num, value in enumerate(data):
        worksheet.write(row, col_num, value)
    row += 2

    # Designation counts
    worksheet.write(row, 0, "Field Visits Conducted", header_format)
    row += 1
    headers = ['Designation', 'Total']
    for col_num, header in enumerate(headers):
        worksheet.write(row, col_num, header, header_format)
    row += 1
    for record in designation_counts:
        worksheet.write(row, 0, record['name_of_official__designation'])
        worksheet.write(row, 1, record['total'])
        row += 1



    
    # WATER SUPPLY table
    worksheet.write(row, 0, "WATER SUPPLY", header_format)
    row += 1
    headers = ['KPI', 'Detail']
    for col_num, header in enumerate(headers):
        worksheet.write(row, col_num, header, header_format)
    row += 1

    water_supply_data = [
        ("Total Tubewells", total_tubewells),
        ("Operational Tubewells", total_functional_tubewells),
        ("Non-Operational Tubewells", total_non_operational_tubewells),
        ("Non-Functional Tubewells", total_non_functional_tubewells),
        ("Total New Connections", total_new_connections),
        ("Functional Filtration Plants", total_functional_filtration),
        ("Non-Functional Filtration Plants", total_non_functional_filtration),
        ("Total Tests", total_tests),
        ("Safe Tests", total_safe_tests),
        ("Unsafe Tests", total_unsafe_tests),
    ]

    for key, value in water_supply_data:
        worksheet.write(row, 0, key)
        worksheet.write(row, 1, value)
        row += 1

    row += 2    

    # Repeat similar logic for activity summary, complaints, and KPIs, adding titles and data

    # Close workbook
    workbook.close()
    output.seek(0)

    # Create response
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="attendance_summary_{selected_date}.xlsx"'
    return response



@login_required
@view_permission_required('vehicle_attendance_report')
def vehicle_attendance_report(request):
    attendance_data = []
    vehicles = Vehicle.objects.filter(status='Active')
    
    # Fetching locations and vehicle types
    locations = Location.objects.all()
    vehicle_types = Vehicle.objects.values_list('vehicle_type', flat=True).distinct()

    selected_date_str = request.GET.get('date', timezone.now().date())
    location_filter = request.GET.get('location', '').strip()
    vehicle_type_filter = request.GET.get('vehicle_type', '').strip()

    # Check user permissions for location access
    permitted_locations = Location.objects.all()  # Default to all locations

    if not request.user.is_superuser:
        # Fetch user permissions
        user_permissions = LocationPermission.objects.filter(user=request.user)
        
        # If user has location permissions
        if user_permissions.exists():
            permitted_locations = user_permissions.first().locations.all()

            # Filter locations based on user permissions
            locations = locations.filter(id__in=permitted_locations)

            # Apply location filter if needed
            if location_filter and location_filter not in permitted_locations.values_list('location_name', flat=True):
                messages.error(request, f"You do not have permission to view attendance for location '{location_filter}'.")
                return redirect('vehicle_attendance_report')

    # Process date
    if isinstance(selected_date_str, str):
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('vehicle_attendance_report')
    else:
        selected_date = selected_date_str

    # Ensure the selected date is not in the future
    if selected_date > timezone.now().date():
        messages.error(request, "You cannot add attendance for a future date.")
        return redirect('vehicle_attendance_report')

    # Filter vehicles based on location and vehicle type
    if location_filter:
        # Ensure location filter is within permitted locations
        if location_filter not in permitted_locations.values_list('location_name', flat=True):
            messages.error(request, f"You do not have permission to view vehicles for location '{location_filter}'.")
            return redirect('vehicle_attendance_report')

        vehicles = vehicles.filter(location__location_name=location_filter)
    
    if vehicle_type_filter:
        vehicles = vehicles.filter(vehicle_type=vehicle_type_filter)

    # Generate attendance data (only for the permitted vehicles)
    for vehicle in vehicles:
        attendance = VehicleAttendance.objects.filter(
            vehicle_name=vehicle,
            attendance_date=selected_date
        ).first()

        # Ensure that the attendance data is only shown for vehicles from permitted locations
        if vehicle.location in permitted_locations:
            attendance_data.append({
                'vehicle_id': vehicle.vehicle_id,
                'vehicle_name': vehicle.vehicle_name,
                'location': vehicle.location,
                'vehicle_type': vehicle.vehicle_type,
                'attendance_date': selected_date,
                'functional': attendance.functional if attendance else True,  # Default to True
                'non_functional': attendance.non_functional if attendance else False,
                'parked': attendance.parked if attendance else None,
                'field_operation': attendance.field_operation if attendance else None,
                'minor_repair': attendance.minor_repair if attendance else None,
                'major_repair': attendance.major_repair if attendance else None,
            })

    # Handle attendance save
    if request.method == 'POST':
        for vehicle in vehicles:
            status = request.POST.get(f'status_{vehicle.vehicle_id}')
            if status:
                functional = status == 'functional'
                non_functional = status == 'non_functional'
                
                # Handle parked and field_operation if functional
                parked = request.POST.get(f'functional_options_{vehicle.vehicle_id}') == 'parked' if functional else None
                field_operation = request.POST.get(f'functional_options_{vehicle.vehicle_id}') == 'field_operation' if functional else None
                
                # Handle minor_repair and major_repair if non-functional
                minor_repair = request.POST.get(f'repair_options_{vehicle.vehicle_id}') == 'minor_repair' if non_functional else None
                major_repair = request.POST.get(f'repair_options_{vehicle.vehicle_id}') == 'major_repair' if non_functional else None

                attendance, created = VehicleAttendance.objects.update_or_create(
                    vehicle_name=vehicle,
                    attendance_date=selected_date,
                    defaults={
                        'functional': functional,
                        'non_functional': non_functional,
                        'location': vehicle.location,
                        'parked': parked,
                        'field_operation': field_operation,
                        'minor_repair': minor_repair,
                        'major_repair': major_repair,
                    }
                )
        messages.success(request, "Vehicle attendance saved successfully.")
        return redirect('vehicle_attendance_report')

    # Prepare context for rendering
    context = {
        'attendance_data': attendance_data,
        'date': selected_date,
        'location_filter': location_filter,
        'vehicle_type_filter': vehicle_type_filter,
        'locations': locations,
        'vehicle_types': vehicle_types,
    }
    return render(request, 'vehicle_attendance_report.html', context)




import csv

from django.db.models import F, Q
from datetime import datetime
from django.utils import timezone


@login_required
@view_permission_required('report_vehicle')
def report_vehicle(request):
    vehicles = Vehicle.objects.all()
    locations = Location.objects.all()
    vehicle_types = Vehicle.objects.values_list('vehicle_type', flat=True).distinct()

    # Filters
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    location_filter = request.GET.get('location', '').strip()
    vehicle_type_filter = request.GET.get('vehicle_type', '').strip()
    vehicle_id_filter = request.GET.get('vehicle_id', '').strip()

    # Permission filtering
    permitted_locations = Location.objects.all()
    if not request.user.is_superuser:
        user_permissions = LocationPermission.objects.filter(user=request.user)
        if user_permissions.exists():
            permitted_locations = user_permissions.first().locations.all()
            locations = locations.filter(id__in=permitted_locations)
            vehicles = vehicles.filter(location__in=permitted_locations)
            if location_filter and location_filter not in permitted_locations.values_list('location_name', flat=True):
                messages.error(
                    request,
                    f"You do not have permission to view attendance for location '{location_filter}'."
                )
                return redirect('report_vehicle')

    today = timezone.now().date()
    from_date = today if not from_date_str else datetime.strptime(from_date_str, '%Y-%m-%d').date()
    to_date = today if not to_date_str else datetime.strptime(to_date_str, '%Y-%m-%d').date()

    if from_date > to_date:
        messages.error(request, "The 'From' date cannot be later than the 'To' date.")
        return redirect('report_vehicle')
    if to_date > today:
        messages.error(request, "The 'To' date cannot be in the future.")
        return redirect('report_vehicle')

    if location_filter:
        vehicles = vehicles.filter(location__location_name=location_filter)
    if vehicle_type_filter:
        vehicles = vehicles.filter(vehicle_type=vehicle_type_filter)
    if vehicle_id_filter:
        vehicles = vehicles.filter(vehicle_id__icontains=vehicle_id_filter)

    consolidated_data = []
    total_trips = total_fuel = total_km = total_cost = 0
    total_functional = total_non_functional = total_parked = 0
    total_field_operation = total_minor_repair = total_major_repair = 0
    # 🛠 New totals for oils
    total_engine_oil = total_hydraulic_oil = 0

    for vehicle in vehicles:
        attendance_records = VehicleAttendance.objects.filter(
            vehicle_name=vehicle,
            attendance_date__range=[from_date, to_date]
        )

        functional_count = attendance_records.filter(functional=True).count()
        non_functional_count = attendance_records.filter(non_functional=True).count()
        parked_count = attendance_records.filter(parked=True).count()
        field_operation_count = attendance_records.filter(field_operation=True).count()
        minor_repair_count = attendance_records.filter(minor_repair=True).count()
        major_repair_count = attendance_records.filter(major_repair=True).count()

        pe_records = VehiclePE.objects.filter(
            vehicle_name=vehicle,
            attendance_date__range=[from_date, to_date]
        )
        trips = pe_records.aggregate(total=Sum('vehicle_trips'))['total'] or 0
        fuel = pe_records.aggregate(total=Sum('fuel_issued'))['total'] or 0
        km = pe_records.aggregate(total=Sum('running_km'))['total'] or 0
        # 🛠 Aggregate engine and hydraulic oil
        engine_oil = pe_records.aggregate(total=Sum('engine_oil'))['total'] or 0
        hydraulic_oil = pe_records.aggregate(total=Sum('hydraulic_oil'))['total'] or 0

        repair_records = Vehiclerepair.objects.filter(
            Vehicle=vehicle,
            date__range=[from_date, to_date]
        )
        cost = repair_records.aggregate(total=Sum('cost'))['total'] or 0
        repair = 'Yes' if repair_records.exists() else 'No'

        consolidated_data.append({
            'vehicle_id': vehicle.vehicle_id,
            'vehicle_name': vehicle.vehicle_name,
            'location': vehicle.location.location_name,
            'vehicle_type': vehicle.vehicle_type,
            'functional_total': functional_count,
            'non_functional_total': non_functional_count,
            'parked_total': parked_count,
            'field_operation_total': field_operation_count,
            'minor_repair_total': minor_repair_count,
            'major_repair_total': major_repair_count,
            'trips': trips,
            'fuel_issued': fuel,
            'running_km': km,
            'engine_oil': engine_oil,
            'hydraulic_oil': hydraulic_oil,
            'repair': repair,
            'repair_cost': cost,
        })

        total_trips += trips
        total_fuel += fuel
        total_km += km
        total_cost += cost
        total_functional += functional_count
        total_non_functional += non_functional_count
        total_parked += parked_count
        total_field_operation += field_operation_count
        total_minor_repair += minor_repair_count
        total_major_repair += major_repair_count
        total_engine_oil += engine_oil
        total_hydraulic_oil += hydraulic_oil

    # 🛠 Include in CSV export
    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="vehicle_report_consolidated.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Vehicle ID','Vehicle Name','Location','Vehicle Type',
            'Functional','Non-Functional','Parked','Field Operation',
            'Minor Repair','Major Repair','Trips','Fuel Issued','Running KM',
            'Engine Oil','Hydraulic Oil','Repair (Yes/No)','Repair Cost'
        ])
        for data in consolidated_data:
            writer.writerow([
                data['vehicle_id'],data['vehicle_name'],data['location'],data['vehicle_type'],
                data['functional_total'],data['non_functional_total'],data['parked_total'],
                data['field_operation_total'],data['minor_repair_total'],data['major_repair_total'],
                data['trips'],data['fuel_issued'],data['running_km'],
                data['engine_oil'],data['hydraulic_oil'],data['repair'],data['repair_cost']
            ])
        writer.writerow([])
        writer.writerow([
            'Totals','','','',total_functional,total_non_functional,total_parked,
            total_field_operation,total_minor_repair,total_major_repair,total_trips,
            total_fuel,total_km,total_engine_oil,total_hydraulic_oil,'',total_cost
        ])
        return response

    return render(request, 'report_vehicle.html', {
        'attendance_data': consolidated_data,
        'from_date': from_date,
        'to_date': to_date,
        'location_filter': location_filter,
        'vehicle_type_filter': vehicle_type_filter,
        'vehicle_id_filter': vehicle_id_filter,
        'locations': locations,
        'vehicle_types': vehicle_types,
        'total_trips': total_trips,
        'total_fuel_issued': total_fuel,
        'total_km': total_km,
        'total_engine_oil': total_engine_oil,       # 🛠 Pass to template
        'total_hydraulic_oil': total_hydraulic_oil, # 🛠 Pass to template
        'total_repair_cost': total_cost,
        'total_functional': total_functional,
        'total_non_functional': total_non_functional,
        'total_parked': total_parked,
        'total_field_operation': total_field_operation,
        'total_minor_repair': total_minor_repair,
        'total_major_repair': total_major_repair,
    })



@login_required
@view_permission_required('vehicle_attendance_summary')
def vehicle_attendance_summary(request):

    # Fetching locations
    locations = Location.objects.all()
    locations = Location.objects.exclude(location_name="Headoffice").order_by('location_name')


    # Get selected date from query params or use today as default
    selected_date_str = request.GET.get('date', timezone.now().date())
    location_filter = request.GET.get('location', '').strip()

    # Check user permissions for location access
    permitted_locations = Location.objects.all()  # Default to all locations

    if not request.user.is_superuser:
        # Fetch user permissions
        user_permissions = LocationPermission.objects.filter(user=request.user)
        
        # If user has location permissions
        if user_permissions.exists():
            permitted_locations = user_permissions.first().locations.all()

            # Filter locations based on user permissions
            locations = locations.filter(id__in=permitted_locations)

            # Apply location filter if needed
            if location_filter and location_filter not in permitted_locations.values_list('location_name', flat=True):
                messages.error(request, f"You do not have permission to view attendance for location '{location_filter}'.")
                return redirect('vehicle_attendance_summary')

    # Process the selected date
    if isinstance(selected_date_str, str):
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('vehicle_attendance_summary')
    else:
        selected_date = selected_date_str

    # Ensure the selected date is not in the future
    if selected_date > timezone.now().date():
        messages.error(request, "You cannot view attendance for a future date.")
        return redirect('vehicle_attendance_summary')

    # Initialize totals by location
    attendance_summary = []
    total_vehicles = 0  # Initialize vehicle total count
    total_functional = 0
    total_non_functional = 0
    total_functional_parked = 0
    total_functional_field_operation = 0
    total_non_functional_minor_repair = 0
    total_non_functional_major_repair = 0
    tracker_summary = []
    total_functional_tracker = 0
    total_non_functional_tracker = 0

    for location in locations:
        # Filter vehicles by location if a location filter is applied
        if location_filter and location.location_name != location_filter:
            continue

        # Only show vehicles from the permitted locations
        if location not in permitted_locations:
            continue

        vehicles = Vehicle.objects.filter(location=location, status='Active')
        total_vehicles += vehicles.count()  # Count the total vehicles

        # Initialize local totals for this location
        location_functional = 0
        location_non_functional = 0
        location_functional_parked = 0
        location_functional_field_operation = 0
        location_non_functional_minor_repair = 0
        location_non_functional_major_repair = 0

        # Generate attendance summary data for the location
        for vehicle in vehicles:
            attendance = VehicleAttendance.objects.filter(
                vehicle_name=vehicle,
                attendance_date=selected_date
            ).first()

            # Increment totals based on attendance status
            if attendance:
                if attendance.functional:
                    location_functional += 1
                    if attendance.parked:
                        location_functional_parked += 1
                    if attendance.field_operation:
                        location_functional_field_operation += 1
                elif attendance.non_functional:
                    location_non_functional += 1
                    if attendance.minor_repair:
                        location_non_functional_minor_repair += 1
                    if attendance.major_repair:
                        location_non_functional_major_repair += 1

        # Add summary for the location
        attendance_summary.append({
            'location': location,
            'total_functional': location_functional,
            'total_non_functional': location_non_functional,
            'total_functional_parked': location_functional_parked,
            'total_functional_field_operation': location_functional_field_operation,
            'total_non_functional_minor_repair': location_non_functional_minor_repair,
            'total_non_functional_major_repair': location_non_functional_major_repair,
                            'total_vehicles': vehicles.count(),  # Add total vehicles for this location

        })

        # Sum up overall totals
        total_functional += location_functional
        total_non_functional += location_non_functional
        total_functional_parked += location_functional_parked
        total_functional_field_operation += location_functional_field_operation
        total_non_functional_minor_repair += location_non_functional_minor_repair
        total_non_functional_major_repair += location_non_functional_major_repair

        # Tracker summary by location
        trackers = Tracker.objects.filter(location=location)
        tracker_functional = TrackerAttendance.objects.filter(
            vehicle_name__in=trackers, 
            attendance_date=selected_date, 
            functional=True
        ).count()
        tracker_non_functional = TrackerAttendance.objects.filter(
            vehicle_name__in=trackers, 
            attendance_date=selected_date, 
            non_functional=True
        ).count()
        tracker_summary.append({
            'location': location.location_name,
            'total_functional': tracker_functional,
            'total_non_functional': tracker_non_functional,
        })
        
        # Sum up overall tracker totals
        total_functional_tracker += tracker_functional
        total_non_functional_tracker += tracker_non_functional

         # Initialize summary dictionary
    status_summary = {
        'parked': {'primary': 0, 'secondary': 0},
        'field_operation': {'primary': 0, 'secondary': 0},
        'minor_repair': {'primary': 0, 'secondary': 0},
        'major_repair': {'primary': 0, 'secondary': 0},
    }

    for location in locations:
        # Filter vehicles by location if a location filter is applied
        if location_filter and location.location_name != location_filter:
            continue

        # Only show vehicles from the permitted locations
        if location not in permitted_locations:
            continue

        vehicles = Vehicle.objects.filter(
            location=location,
            status='Active',
            vehicle_type__in=['Primary', 'Secondary']
        )

        # Generate attendance summary data for the location
        for vehicle in vehicles:
            attendance = VehicleAttendance.objects.filter(
                vehicle_name=vehicle,
                attendance_date=selected_date
            ).first()

            # Check if attendance exists and increment status counts
            if attendance:
                # Determine if primary or secondary vehicle based on vehicle_type
                vehicle_type = vehicle.vehicle_type  # This will be 'Primary' or 'Secondary'
                status_key = None

                if attendance.parked:
                    status_key = 'parked'
                elif attendance.field_operation:
                    status_key = 'field_operation'
                elif attendance.minor_repair:
                    status_key = 'minor_repair'
                elif attendance.major_repair:
                    status_key = 'major_repair'

                if status_key:
                    if vehicle_type == 'Primary':
                        status_summary[status_key]['primary'] += 1
                    elif vehicle_type == 'Secondary':
                        status_summary[status_key]['secondary'] += 1
     # 🚀 **FETCH FUEL DATA**
    total_data = []
    fuel_totals = {
        'fuel_top_up_liters': 0,
        'lfs_trips_no': 0,
            'primary_trips': 0,

    }

    for location in locations:
        fuel_data = Fuel.objects.filter(date=selected_date, location=location)
        location_fuel_totals = {
            'location': location,
            'fuel_top_up_liters': fuel_data.aggregate(Sum('fuel_top_up_liters'))['fuel_top_up_liters__sum'] or 0,
            'lfs_trips_no': fuel_data.aggregate(Sum('lfs_trips_no'))['lfs_trips_no__sum'] or 0,
                    'primary_trips': fuel_data.aggregate(Sum('primary_trips'))['primary_trips__sum'] or 0,

        }

        for key in fuel_totals:
            fuel_totals[key] += location_fuel_totals[key]

        total_data.append(location_fuel_totals)

    # **Convert fuel data into a dictionary for easy lookup**
    fuel_data_dict = {item['location'].id: item for item in total_data}                     

    # Prepare context for rendering
    context = {
        'date': selected_date,
        'location_filter': location_filter,
        'locations': locations,
        'attendance_summary': attendance_summary,  # Include the summarized data
        'total_vehicles': total_vehicles,  # Pass total vehicle count
        'total_functional': total_functional,  # Pass total functional count
        'total_non_functional': total_non_functional,  # Pass total non-functional count
        'total_functional_parked': total_functional_parked,  # Total parked
        'total_functional_field_operation': total_functional_field_operation,  # Total field operation
        'total_non_functional_minor_repair': total_non_functional_minor_repair,  # Total minor repair
        'total_non_functional_major_repair': total_non_functional_major_repair,  # Total major repair
        'tracker_summary': tracker_summary,
        'total_functional_tracker': total_functional_tracker,
        'total_non_functional_tracker': total_non_functional_tracker,
                'status_summary': status_summary,  # Include the status summary
                'fuel_data_dict': fuel_data_dict,  # **✅ Pass fuel data**
        'fuel_totals': fuel_totals,  # **✅ Pass fuel totals**

    }
    return render(request, 'vehicle_attendance_summary.html', context)




@login_required
@view_permission_required('vehicle_pe_attendance')
def vehicle_pe_attendance(request):
    attendance_data = []

    vehicles = Vehicle.objects.all()
    locations = Location.objects.all()
    STATE_CHOICES = VehiclePE.STATE_CHOICE00

    if request.user.is_authenticated:
        user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
        locations = Location.objects.filter(
            id__in=[location.id for location in user_permissions.first().locations.all()]
        )
    else:
        locations = Location.objects.none()

    selected_date_str = request.GET.get('date', timezone.now().date())
    location_filter = request.GET.get('location', '').strip()
    vehicle_type_filter = request.GET.get('vehicle_type', '').strip()

    try:
        selected_date = (
            datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            if isinstance(selected_date_str, str)
            else selected_date_str
        )
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('vehicle_pe_attendance')

    if selected_date > timezone.now().date():
        messages.error(request, "Attendance for future dates is not allowed.")
        return redirect('vehicle_pe_attendance')

    if location_filter:
        vehicles = vehicles.filter(location__location_name=location_filter)
    if vehicle_type_filter:
        vehicles = vehicles.filter(vehicle_type=vehicle_type_filter)

    vehicles = vehicles.filter(location__in=locations)

    # -------- GET: Build attendance data for the template --------
    for vehicle in vehicles:
        attendance = VehiclePE.objects.filter(
            vehicle_name=vehicle,
            attendance_date=selected_date
        ).first()

        odometer_start = attendance.odometer_start if attendance else None
        odometer_end = attendance.odometer_end if attendance else None
        manual_running_km = attendance.manual_running_km if attendance else None
        running_km = (
            (odometer_end - odometer_start)
            if odometer_start is not None and odometer_end is not None
            else manual_running_km
        )

        attendance_data.append({
            'vehicle_id': vehicle.vehicle_id,
            'vehicle_name': vehicle.vehicle_name,
            'location': vehicle.location.location_name,
            'vehicle_type': vehicle.vehicle_type,
            'attendance_date': selected_date,
            'vehicle_trips': attendance.vehicle_trips if attendance else 0,
            'fuel_issued': attendance.fuel_issued if attendance else 0,
            'odometer_start': odometer_start,
            'odometer_end': odometer_end,
            'manual_running_km': manual_running_km,
            'running_km': running_km,
            # 🛠 Add engine & hydraulic oil values for display
            'engine_oil': attendance.engine_oil if attendance else None,
            'hydraulic_oil': attendance.hydraulic_oil if attendance else None,
        })

    # -------- POST: Save submitted attendance --------
    if request.method == 'POST':
        for vehicle in vehicles:
            odometer_start = request.POST.get(f'odometer_start_{vehicle.vehicle_id}', '')
            odometer_end = request.POST.get(f'odometer_end_{vehicle.vehicle_id}', '')
            manual_running_km = request.POST.get(f'manual_running_km_{vehicle.vehicle_id}', '')

            running_km = (
                int(odometer_end) - int(odometer_start)
                if odometer_start and odometer_end
                else int(manual_running_km or 0)
            )

            # 🛠 Get oil values from form (allow blanks)
            engine_oil = request.POST.get(f'engine_oil_{vehicle.vehicle_id}', '')
            hydraulic_oil = request.POST.get(f'hydraulic_oil_{vehicle.vehicle_id}', '')

            attendance, created = VehiclePE.objects.update_or_create(
                vehicle_name=vehicle,
                attendance_date=selected_date,
                defaults={
                    'vehicle_trips': request.POST.get(f'vehicle_trips_{vehicle.vehicle_id}', 0),
                    'fuel_issued': request.POST.get(f'fuel_issued_{vehicle.vehicle_id}', 0),
                    'odometer_start': int(odometer_start) if odometer_start else None,
                    'odometer_end': int(odometer_end) if odometer_end else None,
                    'manual_running_km': int(manual_running_km) if manual_running_km else None,
                    'running_km': running_km,
                    'engine_oil': engine_oil if engine_oil else None,
                    'hydraulic_oil': hydraulic_oil if hydraulic_oil else None,
                    'location': vehicle.location,
                    'vehicle_type': vehicle.vehicle_type,
                }
            )
        messages.success(request, "Vehicle attendance saved successfully.")
        return redirect('vehicle_pe_attendance')

    context = {
        'attendance_data': attendance_data,
        'date': selected_date,
        'location_filter': location_filter,
        'vehicle_type_filter': vehicle_type_filter,
        'locations': locations,
        'vehicle_types': STATE_CHOICES,
    }
    return render(request, 'vehicle_pe_attendance.html', context)



@login_required
@view_permission_required('tracker_attendance_report')
def tracker_attendance_report(request):
    attendance_data = []
    
    # Fetch locations for filtering, based on user permissions
    locations = Location.objects.all()
    if request.user.is_authenticated:
        user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
        locations = Location.objects.filter(id__in=[location.id for location in user_permissions.first().locations.all()])
    else:
        locations = Location.objects.none()  # No locations if the user isn't authenticated

    selected_date_str = request.GET.get('date', str(timezone.now().date()))  # Defaults to today's date
    location_filter = request.GET.get('location', '').strip()

    # Process date
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        if selected_date > timezone.now().date():
            raise ValueError("You cannot add attendance for a future date.")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('tracker_attendance_report')

    # Apply filters for location
    filters = Q()
    if location_filter:
        try:
            location_id = Location.objects.get(location_name=location_filter).id
            filters &= Q(location__id=location_id)
        except Location.DoesNotExist:
            messages.error(request, f"Location '{location_filter}' not found.")

    filters_queryset = Tracker.objects.filter(filters, location__in=locations)  # Filter trackers based on user permissions

    # Fetch attendance records for the selected date
    attendance_records = TrackerAttendance.objects.filter(attendance_date=selected_date, vehicle_name__in=filters_queryset)
    attendance_mapping = {record.vehicle_name.id: record for record in attendance_records}

    # Build attendance data
    for tracker_obj in filters_queryset:
        attendance = attendance_mapping.get(tracker_obj.id)
        attendance_data.append({
            'vehicle_id': tracker_obj.vehicle_id,
            'name': tracker_obj.vehicle_name,
            'location': tracker_obj.location,
            'attendance_date': selected_date,
            'functional': attendance.functional if attendance else True,
            'non_functional': attendance.non_functional if attendance else False,
            'has_attendance': attendance is not None
        })

    # Handle attendance save
    if request.method == 'POST':
        for tracker_obj in filters_queryset:
            status = request.POST.get(f'status_{tracker_obj.vehicle_id}')
            if status:
                TrackerAttendance.objects.update_or_create(
                    vehicle_name=tracker_obj,
                    attendance_date=selected_date,
                    defaults={
                        'functional': status == 'functional',
                        'non_functional': status == 'non_functional',
                        'location': tracker_obj.location
                    }
                )
        messages.success(request, "Attendance saved successfully.")
        return redirect('tracker_attendance_report')

    # Prepare context for rendering
    context = {
        'attendance_data': attendance_data,
        'date': selected_date,
        'location_filter': location_filter,
        'locations': locations,
    }
    return render(request, 'tracker_attendance_report.html', context)



from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Vehiclerepair, Location, UC, Vehicle, LocationPermission
from .forms import VehiclerepairForm
from datetime import date

@login_required
@view_permission_required('vehicle_repair_view')
def vehicle_repair_view(request):
    # Get the date from the GET request, default to today's date
    report_date = request.GET.get('date', date.today())
    
    # Determine which locations the user has access to
    if request.user.is_superuser:
        locations = Location.objects.all()  # Superuser can view all locations
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = user_permissions.values_list('locations', flat=True)
        locations = Location.objects.filter(id__in=location_ids)

    # Filter repair data based on allowed locations and date
    repair_data = Vehiclerepair.objects.filter(location__in=locations, date=report_date)

    # Handle form submission
    if request.method == 'POST':
        form = VehiclerepairForm(request.POST, request.FILES)
        if form.is_valid():
            selected_location = form.cleaned_data['location']
            if request.user.is_superuser or selected_location in locations:
                repair = form.save()
                return JsonResponse({
                    'success': True,
                    'repair': {
                        'date': repair.date.strftime('%Y-%m-%d'),
                        'Vehicle_repair_description': repair.Vehicle_repair_description,
                                               
                        'cost': repair.cost,
                        'remarks': repair.remarks,
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'You do not have permission to add data for this location.'})
    else:
        form = VehiclerepairForm()

    context = {
        'report_date': report_date,
        'repair_data': repair_data,
        'form': form,
    }
    
    return render(request, 'vehicle_repair.html', context)








@login_required
@view_permission_required('field_visit_report')
def field_visit_report(request):
    report_date = timezone.now().date()

    # Get the report date from GET request if available
    if request.method == 'GET':
        report_date = request.GET.get('date', report_date)

    # --------------------------------------
    # 1️⃣ Get allowed locations for the user
    # --------------------------------------
    if request.user.is_superuser:
        allowed_locations = Location.objects.all()
    else:
        perms = LocationPermission.objects.filter(user=request.user, can_view=True)
        if perms.exists():
            allowed_locations = Location.objects.filter(
                id__in=perms.values_list('locations__id', flat=True)
            ).distinct()
        else:
            allowed_locations = Location.objects.none()

    # --------------------------------------
    # 2️⃣ Initialize form and limit location choices
    # --------------------------------------
    form = FieldVisitReportForm(request.POST or None, request.FILES or None)
    form.fields['location'].queryset = allowed_locations

    # --------------------------------------
    # 3️⃣ Prepare total_data for template
    # --------------------------------------
    total_data = []
    for location in allowed_locations:
        total_visits = FieldVisitReport.objects.filter(date=report_date, location=location)
        total_data.append({
            'location': location,
            'visit_count': total_visits.count(),
            'reports': total_visits
        })

    # --------------------------------------
    # 4️⃣ designation_counts filtered by allowed locations
    # --------------------------------------
    designation_counts = (
        FieldVisitReport.objects.filter(date=report_date, location__in=allowed_locations)
        .values('name_of_official__designation')
        .annotate(total=Count('name_of_official__designation'))
    )

    # --------------------------------------
    # 5️⃣ Handle POST (form submission)
    # --------------------------------------
    if request.method == 'POST' and form.is_valid():
        selected_location = form.cleaned_data.get('location')

        if selected_location not in allowed_locations:
            form.add_error('location', 'You do not have permission to select this location.')
            return render(request, 'field_visit_report.html', {
                'form': form,
                'error': 'You do not have permission to select this location.',
                'total_data': total_data,
                'report_date': report_date,
                'designation_counts': designation_counts
            })

        # Save the report with latitude and longitude
        field_visit_report = form.save(commit=False)
        field_visit_report.latitude = form.cleaned_data.get('latitude')
        field_visit_report.longitude = form.cleaned_data.get('longitude')
        field_visit_report.save()

        return redirect('field_visit_report')

    # --------------------------------------
    # 6️⃣ Context for template
    # --------------------------------------
    context = {
        'total_data': total_data,
        'form': form,
        'report_date': report_date,
        'designation_counts': designation_counts,
    }
    return render(request, 'field_visit_report.html', context)






from django.shortcuts import get_object_or_404, redirect, render
from .models import FieldVisitReport
from .forms import FieldVisitReportForm

def update_field_visit_report(request, report_id):
    field_visit_report = get_object_or_404(FieldVisitReport, id=report_id)

    if request.method == 'POST':
        # Update fields using POST data
        field_visit_report.date = request.POST.get('date', field_visit_report.date)
        field_visit_report.location_id = request.POST.get('location', field_visit_report.location_id)
        field_visit_report.visit_area = request.POST.get('visit_area', field_visit_report.visit_area)
        field_visit_report.brief_report = request.POST.get('brief_report', field_visit_report.brief_report)

        # Handle file upload for the image
        if 'image' in request.FILES:
            field_visit_report.image = request.FILES['image']

        # Save the updated report
        field_visit_report.save()
        return redirect('field_visit_report')

    context = {
        'field_visit_report': field_visit_report,
        'form': FieldVisitReportForm(instance=field_visit_report),
    }
    return render(request, 'update_field_visit_report.html', context)



@login_required
@view_permission_required('field_visit_summary')
def field_visit_summary(request):
    form = FieldVisitReportForm(request.POST or None)
    report_date = timezone.now().date()

    # Get the report date from GET request if available
    if request.method == 'GET':
         report_date = request.GET.get('date', date.today().strftime('%Y-%m-%d'))

    # Retrieve the user's location-based permissions
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # Superusers can see all locations
            locations = Location.objects.all().order_by('location_name')
        else:
            # Non-superusers can see only the locations they have permission for
            user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
            locations = Location.objects.filter(id__in=[location.id for location in user_permissions.first().locations.all()])
    else:
        locations = Location.objects.none()  # No locations if the user isn't authenticated

    total_data = []
    overall_visit_count = 0  # Variable to store total visits for location-wise summary

    # Gather visit report data by location, filtered by the locations the user has permission to view
    for location in locations:
        total_visits = FieldVisitReport.objects.filter(date=report_date, location=location)
        visit_count = total_visits.count()
        overall_visit_count += visit_count  # Update overall visits
        reports = total_visits.values('date', 'name_of_official__name', 'visit_area', 'brief_report')

        total_entry = {
            'location': location,
            'visit_count': visit_count,
            'reports': list(reports),
        }
        total_data.append(total_entry)

    # Designation-wise counts for today's date
    designation_counts = (
        FieldVisitReport.objects.filter(date=report_date)
        .values('name_of_official__designation')
        .annotate(total=Count('name_of_official__designation'))
    )
    
    overall_designation_totals = {d['name_of_official__designation']: d['total'] for d in designation_counts}

    # Location and designation-wise counts, filtered by locations the user can view
    location_designation_counts = []
    for location in locations:
        designation_data = (
            FieldVisitReport.objects.filter(date=report_date, location=location)
            .values('name_of_official__designation')
            .annotate(total=Count('name_of_official__designation'))
        )
        location_entry = {
            'location': location,
            'designation_totals': {item['name_of_official__designation']: item['total'] for item in designation_data}
        }
        location_designation_counts.append(location_entry)

    # Handle form submission
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('field_visit_summary')  # Redirect to avoid resubmission

    # Calculate total visits across all locations
    overall_total_visits = sum(entry['visit_count'] for entry in total_data)  # Calculate total visits

    # Context for template
    context = {
        'total_data': total_data,
        'form': form,
        'report_date': report_date,
        'designation_counts': designation_counts,  # Pass designation totals
        'location_designation_counts': location_designation_counts,  # Pass location and designation totals
        'overall_visit_count': overall_visit_count,  # Pass total visits
        'overall_designation_totals': overall_designation_totals,  # Pass designation totals
        'overall_total_visits': overall_total_visits,  # Total visits for the summary
        'overall_location_visits': overall_total_visits,  # Pass total visits for location table
    }
    return render(request, 'field_visit_summary.html', context)


from django.shortcuts import render
from django.db.models import Q
from .models import FieldVisitReport, official, Location

@login_required
@view_permission_required('generate_field_visit_report')
def generate_field_visit_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location_filter = request.GET.get('location')
    designation_filter = request.GET.get('designation')

    # Get all locations and designations for the dropdown
    locations = Location.objects.all()
    designations = official.objects.values('designation').distinct()

    # Filter the reports based on the provided filters
    field_visit_reports = FieldVisitReport.objects.all()

    if start_date:
        field_visit_reports = field_visit_reports.filter(date__gte=start_date)
    if end_date:
        field_visit_reports = field_visit_reports.filter(date__lte=end_date)
    if location_filter:
        field_visit_reports = field_visit_reports.filter(location__location_name=location_filter)
    if designation_filter:
        field_visit_reports = field_visit_reports.filter(name_of_official__designation=designation_filter)

    # Calculate totals (if needed, depending on your reporting needs)
    totals = {
        'total_reports': field_visit_reports.count(),
        # Add any other totals you need
    }

    return render(request, 'report_FV.html', {  # Updated template name
        'field_visit_reports': field_visit_reports,
        'locations': locations,
        'designations': designations,
        'start_date': start_date,
        'end_date': end_date,
        'location_filter': location_filter,
        'designation_filter': designation_filter,
        'totals': totals
    })

from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from .models import TubeWell, Location, UC, TubeWellAttendance, LocationPermission

from decimal import Decimal, InvalidOperation



def get_filtered_tubewells(request, location_filter, uc_filter, selected_date):
    # Get the logged-in user
    user = request.user
    
    # Check if the user has location-based permissions
    location_permissions = LocationPermission.objects.filter(user=user, can_view=True)
    
    # Get the locations that the user has permission to view
    permitted_locations = location_permissions.values_list('locations', flat=True)

    # Filter tubewells based on location, UC, and user's permission
    tubewells = TubeWell.objects.all()

    # Apply location filter if provided, and ensure the user has permission to view the location
    if location_filter:
        tubewells = tubewells.filter(location__location_name=location_filter, location__id__in=permitted_locations)
    else:
        tubewells = tubewells.filter(location__id__in=permitted_locations)

    # Apply UC filter if provided
    if uc_filter:
        tubewells = tubewells.filter(uc__uc_name=uc_filter)

    return tubewells



def calculate_water_produce(attendance, tubewell):
    # Calculate water produce based on available data (either meter readings or run hour and average discharge)
    if attendance:
        if attendance.meter_reading_start and attendance.meter_reading_end:
            try:
                meter_start = Decimal(attendance.meter_reading_start)
                meter_end = Decimal(attendance.meter_reading_end)
                return meter_end - meter_start
            except Exception as e:
                print(f"Error calculating water produce from meter readings: {e}")
        else:
            try:
                run_hour = Decimal(attendance.run_hour or 0)
                average_discharge = Decimal(tubewell.average_discharge or 0)
                return run_hour * average_discharge
            except Exception as e:
                print(f"Error calculating water produce from run hour and average discharge: {e}")
    return None  # If no attendance data, return None


def save_attendance_data(request, selected_date, tubewells):
    for tubewell in tubewells:
        status = request.POST.get(f'status_{tubewell.tubewell_id}')
        functional = status == 'functional'
        non_functional = status == 'non_functional'
        non_operational = status == 'non_operational'

        # Get meter readings and calculate water produce
        meter_reading_start = request.POST.get(f'meter_reading_start_{tubewell.tubewell_id}')
        meter_reading_end = request.POST.get(f'meter_reading_end_{tubewell.tubewell_id}')
        
        # Validate and convert meter readings
        try:
            if meter_reading_start and meter_reading_end:
                meter_reading_start = Decimal(meter_reading_start)
                meter_reading_end = Decimal(meter_reading_end)
                water_produce = meter_reading_end - meter_reading_start
            else:
                run_hour = Decimal(request.POST.get(f'run_hour_{tubewell.tubewell_id}', 0))
                average_discharge = Decimal(tubewell.average_discharge)
                water_produce = run_hour * average_discharge
        except (ValueError, InvalidOperation) as e:
            # If there's an error converting the meter readings or run_hour, log the error and skip
            print(f"Error processing tubewell {tubewell.tubewell_id}: {e}")
            water_produce = 0  # Default value in case of error

        attendance, created = TubeWellAttendance.objects.update_or_create(
            tubewell=tubewell,
            attendance_date=selected_date,
            defaults={
                'functional': functional,
                'non_functional': non_functional,
                'non_operational': non_operational,
                'run_hour': request.POST.get(f'run_hour_{tubewell.tubewell_id}', '') if functional else '',
                'electricity_consume': request.POST.get(f'electricity_consume_{tubewell.tubewell_id}', '') if functional else '',
                'water_produce': water_produce,
                'remarks': request.POST.get(f'remarks_{tubewell.tubewell_id}', ''),
                'location': tubewell.location,
                'uc': tubewell.uc,
                'meter_reading_start': meter_reading_start if meter_reading_start else '',
                'meter_reading_end': meter_reading_end if meter_reading_end else ''
            }
        )
    messages.success(request, "TubeWell data saved successfully.")



@login_required
@view_permission_required('tubewell_attendance')
def tubewell_attendance(request):
    attendance_data = []
    tubewells = TubeWell.objects.all()
    locations = Location.objects.all()
    ucs = UC.objects.all()

    # Get the selected date and filters
    selected_date_str = request.GET.get('date', timezone.now().date())
    location_filter = request.GET.get('location', '').strip()
    uc_filter = request.GET.get('uc', '').strip()

    # Process the selected date
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if isinstance(selected_date_str, str) else selected_date_str
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('tubewell_attendance_report')

    if selected_date > timezone.now().date():
        messages.error(request, "You cannot add attendance for a future date.")
        return redirect('tubewell_attendance_report')

    # Retrieve tubewells based on permissions and filters
    tubewells = get_filtered_tubewells(request, location_filter, uc_filter, selected_date)

    # Generate attendance data
    for tubewell in tubewells:
        attendance = TubeWellAttendance.objects.filter(tubewell=tubewell, attendance_date=selected_date).first()

        # Calculate water produced
        water_produce = calculate_water_produce(attendance, tubewell)

        attendance_data.append({
            'tubewell_id': tubewell.tubewell_id,
            'tubewell_name': tubewell.tubewell_name,
            'location': tubewell.location,
            'uc': tubewell.uc,
            'scada': tubewell.scada,
            'flow_meter': tubewell.flow_meter,
            'motor_hours_power': tubewell.motor_hours_power,

            'tubewell_no_connection': tubewell.tubewell_no_connection,
            'average_discharge': tubewell.average_discharge,
            'attendance_date': selected_date,
            'functional': attendance.functional if attendance else True,
            'non_functional': attendance.non_functional if attendance else False,
            'non_operational': attendance.non_operational if attendance else False,
            'run_hour': attendance.run_hour if attendance and attendance.functional else '',
            'electricity_consume': attendance.electricity_consume if attendance and attendance.functional else '',
            'water_produce': water_produce if water_produce else '',
            'meter_reading_start': attendance.meter_reading_start if attendance else '',
            'meter_reading_end': attendance.meter_reading_end if attendance else '',
            'remarks': attendance.remarks if attendance else ''
        })

    # Handle attendance saving on POST request
    if request.method == 'POST':
        save_attendance_data(request, selected_date, tubewells)
        return redirect('tubewell_attendance')

    # Context for rendering the template
    context = {
        'attendance_data': attendance_data,
        'date': selected_date,
        'location_filter': location_filter,
        'uc_filter': uc_filter,
        'locations': locations,
        'ucs': ucs,
    }

    return render(request, 'tubewell_attendance.html', context)





from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import TubeWell, TubeWellAttendance, Location, UC, LocationPermission



@login_required
@view_permission_required('report_tubwell_2')
def report_tubwell_2(request):
    attendance_data = []
    tubewells = TubeWell.objects.all()

    # Fetching locations and UCs
    locations = Location.objects.all()
    ucs = UC.objects.all()

    # Get selected date range, location, UC, search filters, and status filters
    from_date_str = request.GET.get('from_date', '')
    to_date_str = request.GET.get('to_date', '')
    location_filter = request.GET.get('location', '').strip()
    uc_filter = request.GET.get('uc', '').strip()
    search_filter = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()

    # Convert string dates to date objects, handle empty from_date and to_date
    try:
        if from_date_str:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        else:
            from_date = None

        if to_date_str:
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        else:
            to_date = None
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('report_tubwell_2')

    # Check if from_date is before to_date
    if from_date and to_date and from_date > to_date:
        messages.error(request, "'From' date cannot be later than 'To' date.")
        return redirect('report_tubwell_2')

    # Fetch locations based on user permissions
    if request.user.is_authenticated:
        if request.user.is_superuser:
            locations = Location.objects.all()
        else:
            user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
            locations = Location.objects.filter(id__in=[loc.id for loc in user_permissions.first().locations.all()])
    else:
        locations = Location.objects.none()

    # Filter tubewells based on location and UC
    if location_filter:
        tubewells = tubewells.filter(location__location_name=location_filter)
    if uc_filter:
        tubewells = tubewells.filter(uc__uc_name=uc_filter)

    # Filter tubewells based on location permission
    if not request.user.is_superuser:
        tubewells = tubewells.filter(location__in=locations)

    # Apply search filter for Tubewell ID or Name
    if search_filter:
        tubewells = tubewells.filter(
            Q(tubewell_id__icontains=search_filter) |
            Q(tubewell_name__icontains=search_filter)
        )

    # Generate aggregated attendance data for each tubewell
    for tubewell in tubewells:
        # Prepare filter conditions for the attendance data
        attendance_filter = {'tubewell': tubewell}

        # Add date range filter if both from_date and to_date are provided
        if from_date and to_date:
            attendance_filter['attendance_date__range'] = [from_date, to_date]

        # Add status filter if provided
        if status_filter == 'functional':
            attendance_filter['functional'] = True
        elif status_filter == 'non_functional':
            attendance_filter['non_functional'] = True
        elif status_filter == 'non_operational':
            attendance_filter['non_operational'] = True

        # Fetch attendance data
        attendance = TubeWellAttendance.objects.filter(**attendance_filter)

        # Initialize counters for each status and totals
        functional_days = 0
        non_functional_days = 0
        non_operational_days = 0
        run_hours_total = 0
        electricity_consume_total = 0
        water_produce_total = 0

        # Process attendance records and calculate counts and totals
        for record in attendance:
            if record.functional:
                functional_days += 1
            elif record.non_functional:
                non_functional_days += 1
            elif record.non_operational:
                non_operational_days += 1

            # Accumulate totals for run hours, electricity, and water produced
            run_hours_total += float(record.run_hour) if record.run_hour else 0
            electricity_consume_total += float(record.electricity_consume) if record.electricity_consume else 0
            water_produce_total += float(record.water_produce) if record.water_produce else 0

        # Add aggregated data for each tubewell
        attendance_data.append({
            'tubewell_id': tubewell.tubewell_id,
            'tubewell_name': tubewell.tubewell_name,
            'location': tubewell.location,
            'uc': tubewell.uc,
            'functional_days': functional_days,
            'non_functional_days': non_functional_days,
            'non_operational_days': non_operational_days,
            'run_hours_total': run_hours_total,
            'electricity_consume_total': electricity_consume_total,
            'water_produce_total': water_produce_total,
            'remarks': '',  # Optional: can be used for additional information
        })

    # Prepare context for rendering
    context = {
        'attendance_data': attendance_data,
        'from_date': from_date,
        'to_date': to_date,
        'location_filter': location_filter,
        'uc_filter': uc_filter,
        'search_filter': search_filter,
        'status_filter': status_filter,
        'locations': locations,
        'ucs': ucs,
    }

    return render(request, 'tubewell_attendance_report_2.html', context)




@login_required
@view_permission_required('tubewell_attendance_summary')
def tubewell_attendance_summary(request):
    # Get selected date from query params or use today as default
    selected_date_str = request.GET.get('date', timezone.now().date())
    location_filter = request.GET.get('location', '').strip()

    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if isinstance(selected_date_str, str) else selected_date_str
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('tubewell_attendance_summary')

    if selected_date > timezone.now().date():
        messages.error(request, "You cannot view attendance for a future date.")
        return redirect('tubewell_attendance_summary')

    # Location permissions logic
    if request.user.is_superuser:
        # Superusers can see all locations
         locations = Location.objects.exclude(location_name="Headoffice").order_by('location_name')
    else:
        # Non-superusers can only see locations they have permission for
        user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
        locations = Location.objects.filter(id__in=[location.id for location in user_permissions.first().locations.all()])

    # Filtering locations by location filter (if any)
    if location_filter:
        locations = locations.filter(location_name=location_filter)

    # Initialize total variables
    total_tubewells = 0
    total_functional = 0
    total_non_functional = 0
    total_non_operational = 0
    total_new_connections = 0
    total_functional_filtration = 0
    total_non_functional_filtration = 0
    total_tests = 0
    total_safe_tests = 0
    total_unsafe_tests = 0

    combined_summary = []

    for location in locations:
        tubewells = TubeWell.objects.filter(location=location)
        total_tubewells += tubewells.count()

        location_functional = 0
        location_non_functional = 0
        location_non_operational = 0

        for tubewell in tubewells:
            attendance = TubeWellAttendance.objects.filter(tubewell=tubewell, attendance_date=selected_date).first()

            if attendance:
                if attendance.functional:
                    location_functional += 1
                if attendance.non_functional:
                    location_non_functional += 1
                if attendance.non_operational:
                    location_non_operational += 1

        # Water Supply Data
        water_supply = WaterSupply.objects.filter(location=location, date=selected_date).first()
        new_connections = water_supply.new_water_supply_connection_registered if water_supply else 0

        # Ensure functional_filtration and non_functional_filtration are integers
        functional_filtration = water_supply.functional_filtration_plants if water_supply else 0
        non_functional_filtration = water_supply.non_functional_filtration_plants if water_supply else 0

        # Filter Attendance Data
        filter_attendance_records = FilterAttendance.objects.filter(location=location, attendance_date=selected_date)
        location_functional_filtration = filter_attendance_records.filter(functional=True).count() or 0
        location_non_functional_filtration = filter_attendance_records.filter(non_functional=True).count() or 0

        # Water Test Data
        water_tests = Watertest.objects.filter(location=location, date=selected_date)
        location_total_tests = water_tests.count()
        location_safe_tests = water_tests.filter(output='safe').count()
        location_unsafe_tests = water_tests.filter(output='unsafe').count()

        # Add to cumulative totals
        total_tests += location_total_tests
        total_safe_tests += location_safe_tests
        total_unsafe_tests += location_unsafe_tests

        # Add location-specific data to combined summary
        combined_summary.append({
            'location': location,
            'total_functional': location_functional,
            'total_non_functional': location_non_functional,
            'total_non_operational': location_non_operational,
            'new_connections': new_connections,
            'functional_filtration': (functional_filtration or 0) + (location_functional_filtration or 0),
            'non_functional_filtration': (non_functional_filtration or 0) + (location_non_functional_filtration or 0),
            'total_tests': location_total_tests,
            'safe_tests': location_safe_tests,
            'unsafe_tests': location_unsafe_tests,
                'total_tubewells': tubewells.count(),  # Add total tubewells for this location

        })

        total_functional += location_functional
        total_non_functional += location_non_functional
        total_non_operational += location_non_operational
        total_new_connections += new_connections

        # Accumulate filtration totals ensuring they're not None
        total_functional_filtration += (functional_filtration or 0) + (location_functional_filtration or 0)
        total_non_functional_filtration += (non_functional_filtration or 0) + (location_non_functional_filtration or 0)

    # Pass totals to the template context
    context = {
        'date': selected_date,
        'location_filter': location_filter,
        'locations': locations,
        'combined_summary': combined_summary,
        'total_tubewells': total_tubewells,
        'total_functional': total_functional,
        'total_non_functional': total_non_functional,
        'total_non_operational': total_non_operational,
        'total_new_connections': total_new_connections,
        'total_functional_filtration': total_functional_filtration,
        'total_non_functional_filtration': total_non_functional_filtration,
        'total_tests': total_tests,
        'total_safe_tests': total_safe_tests,
        'total_unsafe_tests': total_unsafe_tests,
    }

    return render(request, 'tubewell_attendance_summary.html', context)


@login_required
@view_permission_required('water_supply_report')
def water_supply_report(request):
    # Get the date from the GET request, default to today's date
    report_date = request.GET.get('date', date.today())

    # Determine which locations the user has access to
    if request.user.is_superuser:
        locations = Location.objects.all()  # Superuser can view all locations
    else:
        # For non-superusers, filter locations based on the LocationPermission model
        user_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = []
        for perm in user_permissions:
            location_ids.extend(perm.locations.values_list('id', flat=True))
        locations = Location.objects.filter(id__in=location_ids)

    # Filter water supply data by the allowed locations and the report date
    water_supply_data = WaterSupply.objects.filter(location__in=locations, date=report_date)

    # Calculate totals
    totals = {
        'total_new_connections': water_supply_data.aggregate(Sum('new_water_supply_connection_registered'))['new_water_supply_connection_registered__sum'] or 0,
    }

    # Handle form submission for new report creation
    if request.method == 'POST':
        form = WaterSupplyReportForm(request.POST)
        
        # Check if the user has permission to add reports (for non-superusers)
        if request.user.is_superuser or request.user.has_perm('app.add_watersupplyreport'):
            if form.is_valid():
                # Check if a report already exists for the given location and date
                location = form.cleaned_data['location']
                if WaterSupply.objects.filter(location=location, date=report_date).exists():
                    return JsonResponse({'success': False, 'message': 'A report for this location already exists for today.'})
                
                # Save the new report
                report = form.save()

                # Returning newly created report data
                return JsonResponse({
                    'success': True,
                    'report': {
                        'date': report.date.strftime('%Y-%m-%d'),
                        'new_water_supply_connection_registered': report.new_water_supply_connection_registered,
                    }
                })
        else:
            return JsonResponse({'success': False, 'message': 'You do not have permission to add reports.'})
    else:
        form = WaterSupplyReportForm()

    # Filter the locations in the form
    if not request.user.is_superuser:
        form.fields['location'].queryset = locations  # Restrict the locations based on user permissions

    # Prepare context to be passed to the template
    context = {
        'report_date': report_date,
        'water_supply_data': water_supply_data,
        'form': form,
        'totals': totals,
    }
    
    # Render the report template
    return render(request, 'water_supply_report.html', context)


@login_required
@view_permission_required('tubewell_attendance_report')
def tubewell_attendance_report(request):
    attendance_data = []
    total_run_hour = 0
    total_electricity_consume = 0
    total_water_produce = 0
    total_repair_cost = 0

    # Fetching locations and UCs
    locations = Location.objects.all()
    ucs = UC.objects.all()

    selected_date_str = request.GET.get('date', timezone.now().date())
    location_filter = request.GET.get('location', '').strip()
    uc_filter = request.GET.get('uc', '').strip()
    tubewell_id_filter = request.GET.get('tubewell_id', '').strip()
    tubewell_name_filter = request.GET.get('tubewell_name', '').strip()

    # Process from and to date filters
    from_date_str = request.GET.get('from_date', '').strip()
    to_date_str = request.GET.get('to_date', '').strip()

    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if isinstance(selected_date_str, str) else selected_date_str
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('tubewell_attendance_report')

    if selected_date > timezone.now().date():
        messages.error(request, "You cannot add attendance for a future date.")
        return redirect('tubewell_attendance_report')

    # Retrieve the user's location-based permissions
    if request.user.is_authenticated:
        if request.user.is_superuser:
            locations = Location.objects.all()  # Superusers can see all locations
        else:
            user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
            locations = Location.objects.filter(id__in=[location.id for location in user_permissions.first().locations.all()])
    else:
        locations = Location.objects.none()  # No locations if the user isn't authenticated

    # Filter attendance data for saved records
    attendance_records = TubeWellAttendance.objects.filter(attendance_date=selected_date)

    # Apply filters based on user input
    if location_filter:
        attendance_records = attendance_records.filter(location__location_name=location_filter)
    if uc_filter:
        attendance_records = attendance_records.filter(uc__uc_name=uc_filter)
    if tubewell_id_filter:
        attendance_records = attendance_records.filter(tubewell__tubewell_id__icontains=tubewell_id_filter)
    if tubewell_name_filter:
        attendance_records = attendance_records.filter(tubewell__tubewell_name__icontains=tubewell_name_filter)
    if from_date:
        attendance_records = attendance_records.filter(attendance_date__gte=from_date)
    if to_date:
        attendance_records = attendance_records.filter(attendance_date__lte=to_date)

    # Filter attendance data based on location permission
    if not request.user.is_superuser:
        attendance_records = attendance_records.filter(location__in=locations)

    # Generate attendance data based on saved records
    for attendance in attendance_records:
        # Get the corresponding water test data
        water_test = Watertest.objects.filter(tubewell=attendance.tubewell, date=selected_date).first()

        # Determine Water Test (Yes/No)
        water_test_status = "Yes" if water_test else "No"

        # Determine Test Output (Safe/Unsafe)
        test_output = water_test.output if water_test else "-----"

        # Get the corresponding repair data
        repair = Tubewellrepair.objects.filter(tubewell=attendance.tubewell, date=selected_date).first()

        # Determine Tubewell Repair (Yes/No)
        repair_status = "Yes" if repair else "No"

        # Get repair cost
        repair_cost = repair.cost if repair else 0

        attendance_data.append({
            'tubewell_id': attendance.tubewell.tubewell_id,
            'tubewell_name': attendance.tubewell.tubewell_name,
            'location': attendance.location,
            'uc': attendance.uc,
            'attendance_date': attendance.attendance_date,
            'functional': attendance.functional,
            'non_functional': attendance.non_functional,
            'non_operational': attendance.non_operational,
            'run_hour': attendance.run_hour,
            'electricity_consume': attendance.electricity_consume,
            'water_produce': attendance.water_produce,
            'remarks': attendance.remarks,
            'water_test': water_test_status,
            'test_output': test_output,
            'tubewell_repair': repair_status,
            'repair_cost': repair_cost,
        })

        # Calculate totals
        total_run_hour += float(attendance.run_hour) if attendance.run_hour else 0
        total_electricity_consume += float(attendance.electricity_consume) if attendance.electricity_consume else 0
        total_water_produce += float(attendance.water_produce) if attendance.water_produce else 0
        total_repair_cost += repair_cost  # Adding repair cost to total

    # CSV Export logic
    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tubewell_attendance_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Tubewell ID', 'Tubewell Name', 'Location', 'UC', 'Attendance Date', 'Functional',
                         'Non Functional', 'Non Operational', 'Run Hour', 'Electricity Consume', 'Water Produce', 
                         'Remarks', 'Water Test (Yes/No)', 'Test Output (Safe/Unsafe)', 'Tubewell Repair (Yes/No)', 
                         'Repair Cost'])

        for data in attendance_data:
            writer.writerow([data['tubewell_id'], data['tubewell_name'], data['location'].location_name, 
                             data['uc'].uc_name, data['attendance_date'], 
                             data['functional'], data['non_functional'], data['non_operational'], 
                             data['run_hour'], data['electricity_consume'], data['water_produce'], data['remarks'],
                             data['water_test'], data['test_output'], data['tubewell_repair'], data['repair_cost']])

        writer.writerow([])
        writer.writerow(['Totals', '', '', '', '', '', '', '', total_run_hour, total_electricity_consume, total_water_produce, 
                         '', '', total_repair_cost])

        return response

    # Context for the template
    context = {
        'attendance_data': attendance_data,
        'date': selected_date,
        'location_filter': location_filter,
        'uc_filter': uc_filter,
        'locations': locations,
        'ucs': ucs,
        'total_run_hour': total_run_hour,
        'total_electricity_consume': total_electricity_consume,
        'total_water_produce': total_water_produce,
        'total_repair_cost': total_repair_cost,  # Pass total repair cost to template
    }
    return render(request, 'tubewell_attendance_report.html', context)



from django.http import JsonResponse
from .models import UC, TubeWell




@login_required
@view_permission_required('water_quality_report')
def water_quality_report(request):
    # Get from and to dates from GET request
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    today = date.today()
    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else today
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else today
    except ValueError:
        from_date = to_date = today

    # Determine which locations the user has access to
    if request.user.is_superuser:
        locations = Location.objects.all()
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = []
        for perm in user_permissions:
            location_ids.extend(perm.locations.values_list('id', flat=True))
        locations = Location.objects.filter(id__in=location_ids)

    # Filter water quality data by date range and allowed locations
    water_quality_data = Watertest.objects.filter(location__in=locations, date__range=[from_date, to_date])

    # Totals
    totals = {
        'total_temperature': water_quality_data.aggregate(Sum('temperature_c'))['temperature_c__sum'] or 0,
        'total_ph': water_quality_data.aggregate(Sum('ph'))['ph__sum'] or 0,
        'total_dissolved_oxygen': water_quality_data.aggregate(Sum('dissolved_oxygen_mg_l'))['dissolved_oxygen_mg_l__sum'] or 0,
    }

    # Test counts per location
    location_test_counts = water_quality_data.values('location').annotate(total_tests=Count('id'))
    location_totals = {item['location']: item['total_tests'] for item in location_test_counts}

    # Handle new report submission
    if request.method == 'POST':
        form = WatertestForm(request.POST)
        if form.is_valid():
            selected_location = form.cleaned_data['location']
            if request.user.is_superuser or selected_location in locations:
                form.save()
                return redirect('water_quality_report')  # <-- redirect to reload the page (update this name if needed)
    else:
        form = WatertestForm()

    context = {
        'from_date': from_date,
        'to_date': to_date,
        'water_quality_data': water_quality_data,
        'form': form,
        'totals': totals,
        'location_totals': location_totals,
    }

    return render(request, 'water_quality_report.html', context)



from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
import traceback

def parse_decimal(value):
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None


def update_watertest(request):
    if request.method == 'POST':
        try:
            record_id = request.POST.get('id')
            print("🔍 Record ID:", record_id)
            print("🧾 POST DATA:", request.POST)

            record = Watertest.objects.get(id=record_id)

            # Assign values
            record.location_type = request.POST.get('location_type')
            record.temperature_c = parse_decimal(request.POST.get('temperature_c'))
            record.ph = parse_decimal(request.POST.get('ph'))
            record.electrical_conductivity_uc_cm = parse_decimal(request.POST.get('electrical_conductivity_uc_cm'))
            record.dissolved_oxygen_mg_l = parse_decimal(request.POST.get('dissolved_oxygen_mg_l'))
            record.tss_mg_l = parse_decimal(request.POST.get('tss_mg_l'))
            record.turbidity_ntu = parse_decimal(request.POST.get('turbidity_ntu'))
            record.tds_mg_l = parse_decimal(request.POST.get('tds_mg_l'))
            record.resistivity_ojm_cm = parse_decimal(request.POST.get('resistivity_ojm_cm'))
            record.salinity_mg_l = parse_decimal(request.POST.get('salinity_mg_l'))
            record.coliform = parse_decimal(request.POST.get('coliform'))
            record.output = request.POST.get('output')

            # Coordinates
            record.longitude = float(request.POST.get('longitude')) if request.POST.get('longitude') else None
            record.latitude = float(request.POST.get('latitude')) if request.POST.get('latitude') else None

            record.save()
            print("✅ Record saved successfully!")

            return JsonResponse({'status': 'success', 'message': '✅ Record updated successfully.'})

        except Watertest.DoesNotExist:
            print("❌ Record not found!")
            return JsonResponse({'status': 'error', 'message': 'Record not found.'})

        except Exception as e:
            print("❌ ERROR while updating Watertest record!")
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


 # Adjust the import based on your app structure




@login_required
@view_permission_required('filter_attendance_report')
def filter_attendance_report(request):
    attendance_data = []
    
    # Determine which locations the user has access to
    if request.user.is_superuser:
        locations = Location.objects.all()  # Superuser can view all locations
    else:
        # For non-superusers, filter locations based on the LocationPermission model
        user_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = []
        for perm in user_permissions:
            location_ids.extend(perm.locations.values_list('id', flat=True))
        locations = Location.objects.filter(id__in=location_ids)  # Only locations the user can view
    
    selected_date_str = request.GET.get('date', str(timezone.now().date()))  # Defaults to today's date
    location_filter = request.GET.get('location', '').strip()

    # Process date
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        if selected_date > timezone.now().date():
            raise ValueError("You cannot add attendance for a future date.")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('filter_attendance_report')

    # Apply filters for location
    filters = Q()
    if location_filter:
        try:
            location_id = Location.objects.get(location_name=location_filter).id  # Adjust field if necessary
            filters &= Q(location__id=location_id)
        except Location.DoesNotExist:
            messages.error(request, f"Location '{location_filter}' not found.")

    # Only Active filters
    filters_queryset = Filter.objects.filter(filters, location__in=locations, status='Active')

    # Fetch attendance records for the selected date, ensuring to apply location filters
    attendance_records = FilterAttendance.objects.filter(attendance_date=selected_date, filter_name__in=filters_queryset)
    attendance_mapping = {record.filter_name.id: record for record in attendance_records}

    # Build attendance data
    for filter_obj in filters_queryset:
        attendance = attendance_mapping.get(filter_obj.id)

        attendance_data.append({
            'filter_id': filter_obj.filter_id,
            'name': filter_obj.name,
            'location': filter_obj.location,
            'attendance_date': selected_date,
            'functional': attendance.functional if attendance else True,
            'non_functional': attendance.non_functional if attendance else False,
            'has_attendance': attendance is not None
        })

    # Handle attendance save
    if request.method == 'POST':
        for filter_obj in filters_queryset:
            status = request.POST.get(f'status_{filter_obj.filter_id}')
            if status:
                FilterAttendance.objects.update_or_create(
                    filter_name=filter_obj,
                    attendance_date=selected_date,
                    defaults={
                        'functional': status == 'functional',
                        'non_functional': status == 'non_functional',
                        'location': filter_obj.location
                    }
                )
        messages.success(request, "Attendance saved successfully.")
        return redirect('filter_attendance_report')

    # Prepare context for rendering
    context = {
        'attendance_data': attendance_data,
        'date': selected_date,
        'location_filter': location_filter,
        'locations': locations,
    }
    return render(request, 'filter_attendance_report.html', context)






from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Tubewellrepair, Location, UC, TubeWell, LocationPermission
from .forms import TubewellrepairForm
from datetime import date

@login_required
@view_permission_required('tubewell_repair_view')
def tubewell_repair_view(request):
    # Get from and to dates from the GET request
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    # Default to today's date if not provided
    today = date.today()
    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else today
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else today
    except ValueError:
        from_date = to_date = today  # fallback in case of invalid format

    # Get user-permitted locations
    if request.user.is_superuser:
        locations = Location.objects.all()
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = user_permissions.values_list('locations', flat=True)
        locations = Location.objects.filter(id__in=location_ids)

    # Filter repair data within date range and permitted locations
    repair_data = Tubewellrepair.objects.filter(
        location__in=locations,
        date__range=[from_date, to_date]
    )

    # Handle form submission
    if request.method == 'POST':
        form = TubewellrepairForm(request.POST, request.FILES)
        if form.is_valid():
            selected_location = form.cleaned_data['location']
            if request.user.is_superuser or selected_location in locations:
                repair = form.save()
                return JsonResponse({
                    'success': True,
                    'repair': {
                        'date': repair.date.strftime('%Y-%m-%d'),
                        'tubewell_repair_description': repair.tubewell_repair_description,
                        'cost': repair.cost,
                        'remarks': repair.remarks,
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'You do not have permission to add data for this location.'})
    else:
        form = TubewellrepairForm()

    context = {
        'from_date': from_date,
        'to_date': to_date,
        'repair_data': repair_data,
        'form': form,
    }

    return render(request, 'tubewell_repair.html', context)








@login_required
@view_permission_required('daily_sanitation_report')
def daily_sanitation_report(request):
    # Fetch locations the user has access to
    if request.user.is_superuser:
        locations = Location.objects.exclude(location_name="Headoffice")  # Superusers see all except Headoffice
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = user_permissions.values_list('locations__id', flat=True)
        locations = Location.objects.filter(id__in=location_ids).exclude(location_name="Headoffice")

    form = SanitationForm(request.POST or None)
    report_date = timezone.now().date()  # Default to current date

    # Handle date filter from GET parameters
    if request.method == 'GET':
        report_date = request.GET.get('date', report_date)

    total_data = []

    # Initialize totals for calculations
    totals = {
        'container_lifted': 0,
        'moqas_cleared': 0,
        'primary_vehicle_trips': 0,
        'primary_waste_collection': 0,
        'waste_locally_dumped': 0,
        'waste_dumped_at_lfs': 0,
        'lfs_trips': 0,
        'local_dumping_trips': 0,
        'fuel_top_up': 0,
        'door_to_door_collection': 0,
        'replacement_of_manhole_covers': 0,
        'cleaning_de_siltation_of_manhole': 0,
        'cleaning_de_siltation_of_drain_sewars': 0,
        'fumigation_sprays': 0,
        'ir_spray': 0,
        'rate_killing': 0,       # ✅ Added
        'dog_catching': 0,       # ✅ Added
    }

    # Retrieve sanitation data for each location
    for location in locations:
        sanitation_data = Sanitation.objects.filter(date=report_date, location=location)
        location_totals = {
            'location': location,
            'container_lifted': sanitation_data.aggregate(Sum('container_lifted'))['container_lifted__sum'] or 0,
            'moqas_cleared': sanitation_data.aggregate(Sum('moqas_cleared'))['moqas_cleared__sum'] or 0,
            'primary_vehicle_trips': sanitation_data.aggregate(Sum('primary_vehicle_trips'))['primary_vehicle_trips__sum'] or 0,
            'primary_waste_collection': sanitation_data.aggregate(Sum('primary_waste_collection_tons'))['primary_waste_collection_tons__sum'] or 0,
            'waste_locally_dumped': sanitation_data.aggregate(Sum('waste_locally_dumped_tons'))['waste_locally_dumped_tons__sum'] or 0,
            'waste_dumped_at_lfs': sanitation_data.aggregate(Sum('waste_dumped_at_lfs_tons'))['waste_dumped_at_lfs_tons__sum'] or 0,
            'lfs_trips': sanitation_data.aggregate(Sum('lfs_trips_no'))['lfs_trips_no__sum'] or 0,
            'local_dumping_trips': sanitation_data.aggregate(Sum('local_dumping_trips_no'))['local_dumping_trips_no__sum'] or 0,
            'fuel_top_up': sanitation_data.aggregate(Sum('fuel_top_up_liters'))['fuel_top_up_liters__sum'] or 0,
            'door_to_door_collection': sanitation_data.aggregate(Sum('door_to_door_solid_waste_collection_no'))['door_to_door_solid_waste_collection_no__sum'] or 0,
            'replacement_of_manhole_covers': sanitation_data.aggregate(Sum('replacement_of_manhole_covers'))['replacement_of_manhole_covers__sum'] or 0,
            'cleaning_de_siltation_of_manhole': sanitation_data.aggregate(Sum('cleaning_de_siltation_of_manholes'))['cleaning_de_siltation_of_manholes__sum'] or 0,
            'cleaning_de_siltation_of_drain_sewars': sanitation_data.aggregate(Sum('cleaning_de_siltation_of_drain_sewars_km'))['cleaning_de_siltation_of_drain_sewars_km__sum'] or 0,
            'fumigation_sprays': sanitation_data.aggregate(Sum('fumigation_sprays_no'))['fumigation_sprays_no__sum'] or 0,
            'ir_spray': sanitation_data.aggregate(Sum('ir_spray_no'))['ir_spray_no__sum'] or 0,
            'rate_killing': sanitation_data.aggregate(Sum('rate_killing_no'))['rate_killing_no__sum'] or 0,     # ✅ Added
            'dog_catching': sanitation_data.aggregate(Sum('dog_catching_no'))['dog_catching_no__sum'] or 0,     # ✅ Added
        }

        # Add location totals to overall totals
        for key in totals:
            if key != 'location':
                totals[key] += location_totals[key]

        total_data.append(location_totals)

    # Handle form submission (new entry or update existing entry)
    if request.method == 'POST' and form.is_valid():
        location = form.cleaned_data['location']
        sanitation_date = form.cleaned_data['date']

        # Check if the user has permission to add or update data for this location
        if request.user.is_superuser or location in locations:
            # Prevent duplicate entries for the same date and location
            existing_entry = Sanitation.objects.filter(date=sanitation_date, location=location).first()

            if existing_entry:
                # Update existing entry
                for field, value in form.cleaned_data.items():
                    setattr(existing_entry, field, value)
                existing_entry.save()
            else:
                # Create a new entry
                form.save()

            return redirect('daily_sanitation_report')  # Avoid resubmission
        else:
            form.add_error('location', "You do not have permission to add or update data for this location.")

    context = {
        'total_data': total_data,
        'form': form,
        'report_date': report_date,
        'totals': totals,
    }

    return render(request, 'sanitation_report.html', context)




from django.db.models import Sum, Q

@login_required
@view_permission_required('sanitation_summary_view')
def sanitation_summary_view(request):
    user = request.user

    # Fetch locations based on user permissions
    if user.is_superuser:
         locations = Location.objects.exclude(location_name="Headoffice").order_by('location_name')
    else:
        location_permissions = LocationPermission.objects.filter(user=user, can_view=True)
        allowed_locations = location_permissions.values_list('locations', flat=True)
        locations = Location.objects.filter(id__in=allowed_locations).exclude(location_name="Headoffice")

    selected_date_str = request.GET.get('date', str(now().date()))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = now().date()

    location_data = []

    # Prepare data for each location
    for location in locations:
        total_moqas = Bin.objects.filter(location=location, name='moqa').count()
        total_containers = Bin.objects.filter(location=location, name='container').count()

        lifted_moqas = BinAttendance.objects.filter(
            location=location, attendance_date=selected_date, bin_name__name='moqa', lifted=True
        ).count()
        unlifted_moqas = BinAttendance.objects.filter(
            location=location, attendance_date=selected_date, bin_name__name='moqa', lifted=False
        ).count()

        lifted_containers = BinAttendance.objects.filter(
            location=location, attendance_date=selected_date, bin_name__name='container', lifted=True
        ).count()
        unlifted_containers = BinAttendance.objects.filter(
            location=location, attendance_date=selected_date, bin_name__name='container', lifted=False
        ).count()

        # Sanitation data for the location
        sanitation = Sanitation.objects.filter(location=location, date=selected_date).first()  # Assuming only one record per date per location

        location_data.append({
            'location': location,
            'total_moqas': total_moqas,
            'total_containers': total_containers,
            'lifted_moqas': lifted_moqas,
            'unlifted_moqas': unlifted_moqas,
            'lifted_containers': lifted_containers,
            'unlifted_containers': unlifted_containers,
            'primary_waste_collection': sanitation.primary_waste_collection_tons if sanitation else 0,
            'waste_locally_dumped': sanitation.waste_locally_dumped_tons if sanitation else 0,
            'waste_dumped_at_lfs': sanitation.waste_dumped_at_lfs_tons if sanitation else 0,
            'lfs_trips': sanitation.lfs_trips_no if sanitation else 0,
            'local_dumping_trips': sanitation.local_dumping_trips_no if sanitation else 0,
            'door_to_door_collection': sanitation.door_to_door_solid_waste_collection_no if sanitation else 0,
            'replacement_of_manhole_covers': sanitation.replacement_of_manhole_covers if sanitation else 0,
            'cleaning_de_siltation_of_manhole': sanitation.cleaning_de_siltation_of_manholes if sanitation else 0,
            'cleaning_de_siltation_of_drain_sewers': sanitation.cleaning_de_siltation_of_drain_sewars_km if sanitation else 0,
            'fumigation_sprays': sanitation.fumigation_sprays_no if sanitation else 0,
            'ir_spray': sanitation.ir_spray_no if sanitation else 0,
        })

    # Prepare data for the chart
    location_labels = [data['location'].location_name for data in location_data]
    total_moqas_data = [data['total_moqas'] for data in location_data]
    lifted_moqas_data = [data['lifted_moqas'] for data in location_data]
    unlifted_moqas_data = [data['unlifted_moqas'] for data in location_data]
    total_containers_data = [data['total_containers'] for data in location_data]
    lifted_containers_data = [data['lifted_containers'] for data in location_data]
    unlifted_containers_data = [data['unlifted_containers'] for data in location_data]

    # Retrieve sanitation data only for permitted locations
    sanitation_filters = Q(date=selected_date)
    if not user.is_superuser:
        sanitation_filters &= Q(location__in=allowed_locations)

    total_sanitation = Sanitation.objects.filter(sanitation_filters)

    # Aggregate totals
    totals = {
        'container_lifted': total_sanitation.aggregate(Sum('container_lifted'))['container_lifted__sum'] or 0,
        'moqas_cleared': total_sanitation.aggregate(Sum('moqas_cleared'))['moqas_cleared__sum'] or 0,
        'primary_vehicle_trips': total_sanitation.aggregate(Sum('primary_vehicle_trips'))['primary_vehicle_trips__sum'] or 0,
        'primary_waste_collection': total_sanitation.aggregate(Sum('primary_waste_collection_tons'))['primary_waste_collection_tons__sum'] or 0,
        'waste_dumped_at_lfs': total_sanitation.aggregate(Sum('waste_dumped_at_lfs_tons'))['waste_dumped_at_lfs_tons__sum'] or 0,
        'waste_locally_dumped': total_sanitation.aggregate(Sum('waste_locally_dumped_tons'))['waste_locally_dumped_tons__sum'] or 0,
        'lfs_trips': total_sanitation.aggregate(Sum('lfs_trips_no'))['lfs_trips_no__sum'] or 0,
        'local_dumping_trips': total_sanitation.aggregate(Sum('local_dumping_trips_no'))['local_dumping_trips_no__sum'] or 0,
        'door_to_door_collection': total_sanitation.aggregate(Sum('door_to_door_solid_waste_collection_no'))['door_to_door_solid_waste_collection_no__sum'] or 0,
        'replacement_of_manhole_covers': total_sanitation.aggregate(Sum('replacement_of_manhole_covers'))['replacement_of_manhole_covers__sum'] or 0,
        'cleaning_de_siltation_of_manhole': total_sanitation.aggregate(Sum('cleaning_de_siltation_of_manholes'))['cleaning_de_siltation_of_manholes__sum'] or 0,
        'cleaning_de_siltation_of_drain_sewars': total_sanitation.aggregate(Sum('cleaning_de_siltation_of_drain_sewars_km'))['cleaning_de_siltation_of_drain_sewars_km__sum'] or 0,
        'fumigation_sprays': total_sanitation.aggregate(Sum('fumigation_sprays_no'))['fumigation_sprays_no__sum'] or 0,
        'ir_spray': total_sanitation.aggregate(Sum('ir_spray_no'))['ir_spray_no__sum'] or 0,
    }

    # Include context
    context = {
        'location_data': location_data,
        'selected_date': selected_date,
        'location_labels': location_labels,
        'total_moqas_data': total_moqas_data,
        'lifted_moqas_data': lifted_moqas_data,
        'unlifted_moqas_data': unlifted_moqas_data,
        'total_containers_data': total_containers_data,
        'lifted_containers_data': lifted_containers_data,
        'unlifted_containers_data': unlifted_containers_data,
        'totals': totals,
        'report_date': selected_date,
    }

    return render(request, 'sanitation_summary.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from django.utils.timezone import now
from .models import Bin, BinAttendance, Binfoam, Location, UC, LocationPermission


@login_required
@view_permission_required('bin_attendance_report')
def bin_attendance_report(request):
    attendance_data = []
    user = request.user

    # Fetch locations and UCs
    if user.is_superuser:
        locations = Location.objects.all()
    else:
        location_permissions = LocationPermission.objects.filter(user=user, can_view=True)
        allowed_locations = location_permissions.values_list('locations', flat=True)
        locations = Location.objects.filter(id__in=allowed_locations)

    ucs = UC.objects.all()

    # Handle filters
    selected_date_str = request.GET.get('date', str(now().date()))
    search_query = request.GET.get('search_query', '').strip()
    location_filter = request.GET.get('location', '').strip()
    uc_filter = request.GET.get('uc', '').strip()
    type_filter = request.GET.get('type', '').strip()

    # Process the date
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        if selected_date > now().date():
            raise ValueError("You cannot add attendance for a future date.")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('bin_attendance_report')

    # Build filters for bins
    filters = Q()
    if search_query:
        filters &= Q(bin_name__name__icontains=search_query)
    if location_filter:
        filters &= Q(location__location_name__icontains=location_filter)
    if uc_filter:
        filters &= Q(uc__uc_name__icontains=uc_filter)
    if type_filter:
        filters &= Q(name=type_filter)

    if not user.is_superuser:
        filters &= Q(location__in=allowed_locations)

    bins = Bin.objects.filter(filters)

    # Fetch attendance for the selected date in bulk
    attendance_records = BinAttendance.objects.filter(attendance_date=selected_date, bin_name__in=bins)
    attendance_mapping = {record.bin_name.id: record for record in attendance_records}

    # Fetch Binfoam data for bins
    binfoam_records = Binfoam.objects.filter(attendance_date=selected_date, bin_name__in=bins)
    binfoam_mapping = {record.bin_name.id: record for record in binfoam_records}

    # Generate attendance data
    for bin in bins:
        attendance = attendance_mapping.get(bin.id)
        binfoam = binfoam_mapping.get(bin.id)  # Fetch related Binfoam entry

        attendance_data.append({
            'bin_id': bin.bin_id,
            'name': bin.name,
            'name_container': bin.name_container,
            'location': bin.location,
            'uc': bin.uc,
            'lifting_frequency': bin.lifting_frequency,
            'category': bin.category,
            'capacity': bin.capacity,
            'lifting_schedule': bin.lifting_schedule,
            'days': bin.days.all(),
            'latitude': bin.latitude,
            'longitude': bin.longitude,
            'first_lifting_time': bin.first_lifting_time,
            'second_lifting_time': bin.second_lifting_time,
            'third_lifting_time': bin.third_lifting_time,

            
            'attendance_date': selected_date,
            'lifted': attendance.lifted if attendance else True,
            'unlifted': attendance.unlifted if attendance else False,
            'liftingfrequency': binfoam.liftingfrequency if binfoam else '0',  # Default to '0'
            'firstliftingtime': binfoam.firstliftingtime.strftime('%H:%M') if binfoam and binfoam.firstliftingtime else '',
            'secondliftingtime': binfoam.secondliftingtime.strftime('%H:%M') if binfoam and binfoam.secondliftingtime else '',
            'thirdliftingtime': binfoam.thirdliftingtime.strftime('%H:%M') if binfoam and binfoam.thirdliftingtime else '',
            
        })

    # Handle attendance save
    if request.method == 'POST':
        for bin in bins:
            status = request.POST.get(f'status_{bin.bin_id}')
            if status:
                BinAttendance.objects.update_or_create(
                    bin_name=bin,
                    attendance_date=selected_date,
                    defaults={
                        'lifted': status == 'lifted',
                        'unlifted': status == 'unlifted',
                        'uc': bin.uc,
                        'location': bin.location
                    }
                )

            # Save Binfoam data as well
            lifting_frequency = request.POST.get(f'liftingfrequency_{bin.bin_id}', '').strip()
            if not lifting_frequency:  # Prevent NULL values
                lifting_frequency = '0'  

            first_lifting_time = request.POST.get(f'firstliftingtime_{bin.bin_id}')
            second_lifting_time = request.POST.get(f'secondliftingtime_{bin.bin_id}')
            third_lifting_time = request.POST.get(f'thirdliftingtime_{bin.bin_id}')

            # Convert empty values to None for proper DB handling
            first_lifting_time = first_lifting_time if first_lifting_time else None
            second_lifting_time = second_lifting_time if second_lifting_time else None
            third_lifting_time = third_lifting_time if third_lifting_time else None

            Binfoam.objects.update_or_create(
                bin_name=bin,
                attendance_date=selected_date,
                defaults={
                    'liftingfrequency': lifting_frequency,
                    'firstliftingtime': first_lifting_time,
                    'secondliftingtime': second_lifting_time,
                    'thirdliftingtime': third_lifting_time,
                    'location': bin.location,
                    'uc': bin.uc,
                }
            )

        messages.success(request, "Saved successfully.")
        return redirect('bin_attendance_report')

    # Prepare context for rendering
    context = {
        'attendance_data': attendance_data,
        'date': selected_date,
        'search_query': search_query,
        'location_filter': location_filter,
        'uc_filter': uc_filter,
        'type_filter': type_filter,
        'ucs': ucs,
        'locations': locations,
        'type_choices': Bin.TYPE_CHOICES,
    }
    return render(request, 'bin_attendance_report.html', context)




from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Q
from datetime import datetime
from .models import Bin, BinAttendance, Binfoam, Location, UC, LocationPermission




@login_required
@view_permission_required('bin_report_view')
def bin_report_view(request):
    attendance_data = []
    user = request.user

    # Fetch locations and UCs
    if user.is_superuser:
        locations = Location.objects.all()
    else:
        location_permissions = LocationPermission.objects.filter(user=user, can_view=True)
        allowed_locations = location_permissions.values_list('locations', flat=True)
        locations = Location.objects.filter(id__in=allowed_locations)

    ucs = UC.objects.all()

    # Handle filters
    selected_date_str = request.GET.get('date', str(now().date()))
    location_filter = request.GET.get('location', '').strip()
    uc_filter = request.GET.get('uc', '').strip()

    # Process the date
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        if selected_date > now().date():
            raise ValueError("You cannot add attendance for a future date.")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('bin_report_view')

    # Build filters for bins
    filters = Q()
    if location_filter:
        filters &= Q(location__id=location_filter)
    if uc_filter:
        filters &= Q(uc__id=uc_filter)
    if not user.is_superuser:
        filters &= Q(location__in=allowed_locations)

    bins = Bin.objects.filter(filters)

    # Fetch attendance and Binfoam data for the selected date
    attendance_records = BinAttendance.objects.filter(attendance_date=selected_date, bin_name__in=bins)
    attendance_mapping = {record.bin_name.id: record for record in attendance_records}

    binfoam_records = Binfoam.objects.filter(attendance_date=selected_date, bin_name__in=bins)
    binfoam_mapping = {record.bin_name.id: record for record in binfoam_records}

    # Generate attendance data
    # Generate attendance data
    for bin in bins:
        attendance = attendance_mapping.get(bin.id)
        binfoam = binfoam_mapping.get(bin.id)

        attendance_data.append({
            'bin_id': bin.bin_id,
            'location': bin.location.location_name,
            'uc': bin.uc.uc_name if bin.uc else 'N/A',
            'nc': bin.nc.nc_name if bin.nc else 'N/A',  # Added NC
            'street': bin.street.street_name if bin.street else 'N/A',  # Added Street
            'vehicle': bin.vehicle.vehicle_name if bin.vehicle else 'N/A',
            'days': ', '.join([day.name for day in bin.days.all()]),
            'status': 'Lifted' if attendance and attendance.lifted else 'Unlifted',
            'lifting_frequency': binfoam.liftingfrequency if binfoam else '0',
            'first_lifting_time': binfoam.firstliftingtime.strftime('%H:%M') if binfoam and binfoam.firstliftingtime else '',
            'second_lifting_time': binfoam.secondliftingtime.strftime('%H:%M') if binfoam and binfoam.secondliftingtime else '',
            'third_lifting_time': binfoam.thirdliftingtime.strftime('%H:%M') if binfoam and binfoam.thirdliftingtime else '',
            'latitude': bin.latitude,  # Add Latitude
        'longitude': bin.longitude,  # Add Longitude
        })

    # Prepare context for rendering
    context = {
        'attendance_data': attendance_data,
        'date': selected_date,
        'location_filter': location_filter,
        'uc_filter': uc_filter,
        'ucs': ucs,
        'locations': locations,
    }
    return render(request, 'bin_report.html', context)



from django.shortcuts import render
from django.utils.timezone import now
from .models import Bin, Binfoam, DayFrequency

def bin_lifting_report(request):
    # Get today's day of the week (e.g., Monday, Tuesday, etc.)
    today = now().date()
    day_of_week = now().strftime('%A')  # Get day as a string (e.g., 'Monday')

    # Fetch bins scheduled for today based on 'days' (ManyToMany with DayFrequency)
    bins = Bin.objects.filter(days__name=day_of_week)

    # Prepare the attendance report data
    attendance_report = []

    # Iterate through bins and check lifting status for today
    for bin in bins:
        # Find the lifting details from Binfoam for today
        binfoam = Binfoam.objects.filter(bin_name=bin, attendance_date=today).first()

        # If there's no lifting data for today, the bin was not lifted
        lifted_status = 'Lifted' if binfoam else 'Unlifted'

        # Add the bin to the report with its lifting details
        attendance_report.append({
            'bin_id': bin.bin_id,
            'name': bin.name,
            'category': bin.category,
            'capacity': bin.capacity,
            'lifting_frequency': bin.lifting_frequency,
            'firstliftingtime': binfoam.firstliftingtime if binfoam else 'N/A',
            'secondliftingtime': binfoam.secondliftingtime if binfoam else 'N/A',
            'thirdliftingtime': binfoam.thirdliftingtime if binfoam else 'N/A',
            'status': lifted_status,
        })

    # Pass the report data to the template
    context = {
        'attendance_report': attendance_report,
        'today': today,
        'day_of_week': day_of_week,
    }

    return render(request, 'bin_lifting_report.html', context)




@login_required
@view_permission_required('daily_post_attendance')
def daily_post_attendance(request):
    today = timezone.now().date()

    # Default filter to today's date
    attendance_date = request.GET.get('attendance_date', today)  # Get date from GET params or default to today
    post_type_id = request.GET.get('post_type', 'all')  # Default to 'all' if not provided
    post_detail_id = request.GET.get('post_detail', 'all')  # Default to 'all' if not provided

    # Filter post attendances based on the selected date
    post_attendances = PostAttendance.objects.filter(post_date=attendance_date)

    # Filter by post type if selected
    if post_type_id and post_type_id != "all":  # Check for 'all' option
        post_attendances = post_attendances.filter(post_type_id=post_type_id)

    # Further filter by post detail if selected
    if post_detail_id and post_detail_id != "all":  # Check for 'all' option
        post_attendances = post_attendances.filter(post_detail_id=post_detail_id)

    # Handle form submission
    if request.method == "POST":
        form = PostAttendanceForm(request.POST)
        if form.is_valid():
            post_date = form.cleaned_data['post_date']
            if post_date <= today:
                form.save()
                messages.success(request, 'Attendance added successfully.')
                return redirect('daily_post_attendance')  # Redirect after successful submission
            else:
                messages.error(request, 'Attendance date cannot be in the future.')
    else:
        form = PostAttendanceForm()

    # Get all post types for filtering
    post_types = Post.objects.all()

    # Get post details for the selected post type, or all if no post_type_id is selected
    post_details = PostDetail.objects.filter(post_id=post_type_id) if post_type_id != 'all' else PostDetail.objects.all()

    return render(request, 'daily_post_attendance.html', {
        'post_attendances': post_attendances,
        'form': form,
        'today': today,
        'attendance_date': attendance_date, 
        'post_types': post_types,
        'post_type_id': post_type_id,
        'post_details': post_details,
        'post_detail_id': post_detail_id,
    })



@login_required
@view_permission_required('media_summary')
def media_summary(request):
    today = timezone.now().date()
    attendance_date = request.GET.get('attendance_date', today)
    post_type_id = request.GET.get('post_type', 'all')

    # Filter posts based on the selected date and type
    post_attendances = PostAttendance.objects.filter(post_date=attendance_date)
    if post_type_id != "all":
        post_attendances = post_attendances.filter(post_type_id=post_type_id)

    # Aggregate data for media summary report
    media_summary = (
        post_attendances
        .values(post_type_name=F('post_type__name'), platform_name=F('post_detail__media_channel'))
        .annotate(total_posts=Count('id'))
    )
    
    # Calculate total posts count
    total_posts = post_attendances.count()

    # Pass the form and summary data to the template
    post_types = Post.objects.all()

    return render(request, 'media_summary.html', {
        'media_summary': media_summary,
        'total_posts': total_posts,
        'post_types': post_types,
        'attendance_date': attendance_date,
        'post_type_id': post_type_id,
    })













from django.shortcuts import get_object_or_404

from django.shortcuts import render
from .models import Complaint, Location
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Complaint, Location, LocationPermission
from .forms import ComplaintManagementForm
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Complaint, ComplaintActionLog, LocationPermission, Location
from .forms import ComplaintManagementForm

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Complaint, ComplaintActionLog, ComplaintResolution, LocationPermission, Location
from .forms import ComplaintManagementForm, ComplaintResolutionForm


@login_required
@view_permission_required('complaint_management_report')
def complaint_management_report(request):
    report_date = timezone.now().date()
    if request.method == 'GET':
        report_date = request.GET.get('date', report_date)

    # Allowed locations
    user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
    allowed_locations = [loc for perm in user_permissions for loc in perm.locations.all()]
    locations = Location.objects.filter(id__in=[loc.id for loc in allowed_locations])

    # Forms
    form = ComplaintManagementForm(request.POST or None, request.FILES or None)
    resolution_form = ComplaintResolutionForm(request.POST or None, request.FILES or None)

    # Save New Complaint
    if request.method == 'POST' and 'save_complaint' in request.POST:
        if form.is_valid():
            complaint = form.save(commit=False)
            if complaint.location in allowed_locations:
                complaint.status = 'pending'   # ✅ Force status to pending
                complaint.save()
                ComplaintActionLog.objects.create(
                    complaint=complaint,
                    user=request.user,
                    action='created'
                )
                messages.success(
                    request,
                    f"✅ Complaint (ID: {complaint.id}) has been saved successfully with status Pending!"
                )
                return redirect('complaint_management_report')
        else:
            messages.error(request, "❌ Failed to save complaint. Please check the form.")

    # Save Complaint Resolution
    if request.method == 'POST' and 'save_resolution' in request.POST:
        complaint_id = request.POST.get('complaint_id')
        complaint = get_object_or_404(Complaint, id=complaint_id)

        if complaint.location in allowed_locations and resolution_form.is_valid():
            resolution = resolution_form.save(commit=False)
            resolution.complaint = complaint
            resolution.save()
            complaint.status = 'resolved'   # ✅ Only updated here
            complaint.save()
            ComplaintActionLog.objects.create(
                complaint=complaint,
                user=request.user,
                action='resolved'
            )
            messages.success(
                request,
                f"✅ Complaint (ID: {complaint.id}) has been resolved successfully!"
            )
            return redirect('complaint_management_report')
        else:
            messages.error(request, "❌ Failed to resolve complaint. Please check the form.")

    # Prepare complaint data
    complaint_data = []
    total_complaints = total_resolved = total_pending = 0
    for location in locations:
        complaints = Complaint.objects.filter(date=report_date, location=location)
        for complaint in complaints:
            logs = ComplaintActionLog.objects.filter(complaint=complaint).order_by('-timestamp')
            complaint_data.append({
                'id': complaint.id,
                'location': complaint.location,
                'uc': complaint.uc,
                'complaint_source': complaint.complaint_source,
                'Pcp_compalin_no': complaint.Pcp_compalin_no,
                'Eak_compalin_no': complaint.Eak_compalin_no,
                'Ebaldia_compalin_no': complaint.Ebaldia_compalin_no,
                'complaint_type': complaint.complaint_type,
                'SubType': complaint.SubType,
                'title': complaint.title,
                'type': complaint.type,
                'complaint_detail': complaint.complaint_detail,
                'date': complaint.date,
                'status': complaint.status,
                'created_at': complaint.created_at,
                'updated_at': complaint.updated_at,
                'logs': logs,
                'first_name': complaint.first_name,
                'last_name': complaint.last_name,
                'bill_number': complaint.bill_number,
                'area': complaint.area,
                'address': complaint.address,
                'tehsil': complaint.tehsil,
                'cnic': complaint.cnic,
                'cell_number': complaint.cell_number,
                'phone_number': complaint.phone_number,
                'gender': complaint.gender,
                'consumer_type': complaint.consumer_type,
                'before_image': complaint.before_image,
            })

        total_complaints += complaints.count()
        total_resolved += complaints.filter(status='resolved').count()
        total_pending += complaints.filter(status='pending').count()

    context = {
        'complaint_data': complaint_data,
        'form': form,
        'resolution_form': resolution_form,
        'report_date': report_date,
        'locations': locations,
        'totals': {
            'total_complaints': total_complaints,
            'total_resolved': total_resolved,
            'total_pending': total_pending,
        },
    }
    return render(request, 'complaint_management.html', context)



from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Complaint, ComplaintActionLog, LocationPermission, Location
from .forms import ComplaintManagementForm, ComplaintResolutionForm
from .decorators import view_permission_required  



@login_required
@view_permission_required('complaint_management_view')
def complaint_management_view(request):
    # --- Allowed locations for user ---
    user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
    allowed_locations = [loc for perm in user_permissions for loc in perm.locations.all()]
    locations = Location.objects.filter(id__in=[loc.id for loc in allowed_locations])

    # --- Filters from request ---
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    complaint_id = request.GET.get("complaint_id")
    cell_number = request.GET.get("cell_number")
    pcp_no = request.GET.get("pcp_no")
    eak_no = request.GET.get("eak_no")
    status = request.GET.get("status")

    today = timezone.now().date()

    # --- Forms ---
    form = ComplaintManagementForm(request.POST or None, request.FILES or None)
    resolution_form = ComplaintResolutionForm(request.POST or None, request.FILES or None)

    # --- Save New Complaint ---
    if request.method == 'POST' and 'save_complaint' in request.POST:
        if form.is_valid():
            complaint = form.save(commit=False)
            if complaint.location in allowed_locations:
                complaint.save()
                ComplaintActionLog.objects.create(
                    complaint=complaint, user=request.user, action='created'
                )
                messages.success(request, f"✅ Complaint (ID: {complaint.id}) has been saved successfully!")
                return redirect('complaint_management_view')
        else:
            messages.error(request, "❌ Failed to save complaint. Please check the form.")

    # --- Save Complaint Resolution ---
    if request.method == 'POST' and 'save_resolution' in request.POST:
        complaint_id_post = request.POST.get('complaint_id')
        complaint = get_object_or_404(Complaint, id=complaint_id_post)

        if complaint.location in allowed_locations and resolution_form.is_valid():
            resolution = resolution_form.save(commit=False)
            resolution.complaint = complaint
            resolution.save()
            complaint.status = 'resolved'
            complaint.save()
            ComplaintActionLog.objects.create(complaint=complaint, user=request.user, action='resolved')
            messages.success(request, "✅ Complaint has been resolved successfully!")
            return redirect('complaint_management_view')
        else:
            messages.error(request, "❌ Failed to resolve complaint. Please check the form.")

    # --- Build Complaint Query ---
    complaints = Complaint.objects.filter(location__in=locations)

    # ✅ Apply date filter ONLY if user entered it
    if from_date or to_date:
        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date() if from_date else datetime(2000, 1, 1).date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date() if to_date else today
            complaints = complaints.filter(date__range=[from_date, to_date])
        except ValueError:
            pass
    else:
        # ✅ Default → only today's data
        complaints = complaints.filter(date=today)

    # ✅ If user searches by any text filter, show all (ignore date)
    if complaint_id or cell_number or pcp_no or eak_no or status:
        complaints = Complaint.objects.filter(location__in=locations)  # reset (all data)
        if complaint_id:
            complaints = complaints.filter(id=complaint_id)
        if cell_number:
            complaints = complaints.filter(cell_number__icontains=cell_number)
        if pcp_no:
            complaints = complaints.filter(Pcp_compalin_no__icontains=pcp_no)
        if eak_no:
            complaints = complaints.filter(Eak_compalin_no__icontains=eak_no)
        if status:
            complaints = complaints.filter(status=status)

    # --- Build Complaint Data ---
    complaint_data = []
    for complaint in complaints:
        logs = ComplaintActionLog.objects.filter(complaint=complaint).order_by('timestamp')
        created_log = logs.filter(action='created').first()
        resolved_log = logs.filter(action='resolved').last()

        # Time to resolve
        time_to_resolve = None
        if created_log and resolved_log:
            diff = resolved_log.timestamp - created_log.timestamp
            days = diff.days
            hours, rem = divmod(diff.seconds, 3600)
            minutes, _ = divmod(rem, 60)
            parts = []
            if days: parts.append(f"{days} day{'s' if days > 1 else ''}")
            if hours: parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
            if minutes: parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
            time_to_resolve = ", ".join(parts) if parts else "less than a minute"

        resolution = getattr(complaint, "resolution", None)

        complaint_data.append({
            'id': complaint.id,
            'location': complaint.location,
            'uc': complaint.uc,
            'complaint_source': complaint.complaint_source,
            'Pcp_compalin_no': complaint.Pcp_compalin_no,
            'Eak_compalin_no': complaint.Eak_compalin_no,
            'complaint_type': complaint.complaint_type,
            'SubType': complaint.SubType,
            'title': complaint.title,
            'type': complaint.type,
            'complaint_detail': complaint.complaint_detail,
            'date': complaint.date,
            'status': complaint.status,
            'created_at': complaint.created_at,
            'updated_at': complaint.updated_at,
            'logs': logs,
            'first_name': complaint.first_name,
            'last_name': complaint.last_name,
            'bill_number': complaint.bill_number,
            'area': complaint.area,
            'address': complaint.address,
            'tehsil': complaint.tehsil,
            'cnic': complaint.cnic,
            'cell_number': complaint.cell_number,
            'phone_number': complaint.phone_number,
            'gender': complaint.gender,
            'consumer_type': complaint.consumer_type,
            'before_image': complaint.before_image,
            'time_to_resolve': time_to_resolve,
            'resolution_description': resolution.description if resolution else None,
            'resolution_customer_satisfaction': resolution.customer_satisfaction if resolution else None,
            'after_image': resolution.after_image if resolution and resolution.after_image else None,
        })

    total_complaints = complaints.count()
    total_resolved = complaints.filter(status='resolved').count()
    total_pending = complaints.filter(status='pending').count()

    # --- Context ---
    context = {
        'complaint_data': complaint_data,
        'form': form,
        'resolution_form': resolution_form,
        'from_date': from_date,
        'to_date': to_date,
        'locations': locations,
        'totals': {
            'total_complaints': total_complaints,
            'total_resolved': total_resolved,
            'total_pending': total_pending,
        },
    }
    return render(request, 'complaint_management_view.html', context)

from django.db.models import Subquery, OuterRef, Count, Value, CharField, F, Case, When
from django.db.models.functions import Concat
from django.utils import timezone
from django.shortcuts import render

def complaints_by_user_view(request):
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    status_filter = request.GET.get('status')

    complaints = Complaint.objects.all()

    if from_date and to_date:
        complaints = complaints.filter(date__range=[from_date, to_date])
        report_date = f"{from_date} to {to_date}"
    elif from_date:
        complaints = complaints.filter(date__gte=from_date)
        report_date = f"{from_date} to {today}"
    elif to_date:
        complaints = complaints.filter(date__lte=to_date)
        report_date = f"till {to_date}"
    else:
        complaints = complaints.filter(date__range=[first_day_of_month, today])
        report_date = f"{first_day_of_month} to {today}"

    if status_filter in ['pending', 'resolved']:
        complaints = complaints.filter(status=status_filter)

    # --- Subquery: get the first "created" log WITH a user ---
    first_real_user = ComplaintActionLog.objects.filter(
        complaint=OuterRef('pk'),
        action='created',
        user__isnull=False
    ).order_by('id')

    complaints = complaints.annotate(
        creator_id=Subquery(first_real_user.values('user_id')[:1]),
        creator_username=Subquery(first_real_user.values('user__username')[:1]),
        creator_fname=Subquery(first_real_user.values('user__first_name')[:1]),
        creator_lname=Subquery(first_real_user.values('user__last_name')[:1]),
    )

    complaints_by_user = (
        complaints.values('creator_id')
        .annotate(total=Count('id'))
        .annotate(
            username=Case(
                When(creator_id__isnull=True, then=Value("System (Auto)")),
                default=F('creator_username'),
                output_field=CharField(),
            ),
            full_name=Case(
                When(creator_id__isnull=True, then=Value("—")),
                default=Concat(
                    F('creator_fname'),
                    Value(' '),
                    F('creator_lname'),
                    output_field=CharField()
                )
            )
        )
        .order_by('-total')
    )

    # ✅ Convert to list so we can filter & sum
    complaints_by_user = list(complaints_by_user)

    # ✅ Remove "System (Auto)" from display
    complaints_by_user = [row for row in complaints_by_user if row['username'] != "System (Auto)"]

    # ✅ Total complaints (excluding system)
    total_complaints = sum(row['total'] for row in complaints_by_user)

    context = {
        'complaints_by_user': complaints_by_user,
        'total_complaints': total_complaints,
        'report_date': report_date,
        'from_date': from_date or first_day_of_month,
        'to_date': to_date or today,
    }
    return render(request, 'complaints_by_user.html', context)




from django.http import JsonResponse
from .models import ComplaintSubType

def ajax_load_subtypes(request):
    complaint_type_id = request.GET.get('complaint_type')
    subtypes = ComplaintSubType.objects.filter(complaint_type_id=complaint_type_id).values('id', 'type_name')
    return JsonResponse(list(subtypes), safe=False)


from django.shortcuts import render
from .models import Complaint, Location, UC, ComplaintSource, ComplaintType
from django.db.models import Q


from collections import Counter

from datetime import date
from calendar import monthrange


from django.db.models import Avg, F, ExpressionWrapper, DurationField
from datetime import timedelta

@login_required
@view_permission_required('complaint_report_generator')
def complaint_report_generator(request):
    # Extract filters from GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location_filter = request.GET.get('location')
    uc_filter = request.GET.get('uc')
    status_filter = request.GET.get('status')
    source_filter = request.GET.get('complaint_source')
    type_filter = request.GET.get('complaint_type')
    subtype_filter = request.GET.get('complaint_subtype')
    cell_number_search = request.GET.get('cell_number') or ''
    name_search = request.GET.get('name') or ''

    # Base queryset
    complaints = Complaint.objects.select_related(
        'location', 'uc', 'complaint_source', 'complaint_type', 'SubType', 'resolution'
    ).prefetch_related('actions', 'responses')

    # Handle location permissions
    if not request.user.is_superuser:
        user_locations = LocationPermission.objects.filter(
            user=request.user, can_view=True
        ).values_list('locations', flat=True)
        complaints = complaints.filter(location__id__in=user_locations)

    # Date filtering
    if start_date and end_date:
        start_date = date.fromisoformat(start_date)
        end_date = date.fromisoformat(end_date)
        complaints = complaints.filter(date__gte=start_date, date__lte=end_date)
    else:
        # Default to current month if no search is performed
        if not any([cell_number_search, name_search, location_filter, uc_filter, 
                    status_filter, source_filter, type_filter, subtype_filter]):
            today = date.today()
            current_year, current_month = today.year, today.month
            start_date = date(current_year, current_month, 1)
            end_date = date(current_year, current_month, monthrange(current_year, current_month)[1])
            complaints = complaints.filter(date__gte=start_date, date__lte=end_date)
        else:
            start_date, end_date = None, None

    # Apply other filters
    if location_filter:
        complaints = complaints.filter(location__location_name=location_filter)
    if uc_filter:
        complaints = complaints.filter(uc__uc_name=uc_filter)
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if source_filter:
        complaints = complaints.filter(complaint_source__source_name=source_filter)
    if type_filter:
        complaints = complaints.filter(complaint_type__type_name=type_filter)
    if subtype_filter:
        complaints = complaints.filter(SubType__type_name=subtype_filter)
    if cell_number_search:
        complaints = complaints.filter(cell_number__icontains=cell_number_search)
    if name_search:
        complaints = complaints.filter(
            Q(first_name__icontains=name_search) | Q(last_name__icontains=name_search)
        )

    # Calculate resolve time per complaint
    complaints_list = []
    for complaint in complaints:
        created_action = complaint.actions.filter(action='created').first()
        resolved_action = complaint.actions.filter(action='resolved').first()
        
        complaint.resolve_time_formatted = "N/A"
        complaint.resolve_time_hours = None
        complaint.resolve_time_days = None
        
        if created_action and resolved_action:
            resolve_time = resolved_action.timestamp - created_action.timestamp
            resolve_time_seconds = resolve_time.total_seconds()
            
            # Calculate time components
            days = int(resolve_time_seconds // 86400)
            hours = int((resolve_time_seconds % 86400) // 3600)
            minutes = int((resolve_time_seconds % 3600) // 60)
            
            complaint.resolve_time_formatted = f"{days}d {hours}h {minutes}m"
            complaint.resolve_time_hours = round(resolve_time_seconds / 3600, 2)
            complaint.resolve_time_days = round(resolve_time_seconds / 86400, 2)
        
        complaints_list.append(complaint)

    # Dropdown data
    locations = Location.objects.all()
    ucs = UC.objects.all()
    complaint_sources = ComplaintSource.objects.all()
    complaint_types = ComplaintType.objects.all()
    complaint_subtypes = ComplaintSubType.objects.all()

    # Graph data
    location_counter = Counter([c.location.location_name for c in complaints_list if c.location])
    source_counter = Counter([c.complaint_source.source_name for c in complaints_list if c.complaint_source])
    type_counter = Counter([c.complaint_type.type_name for c in complaints_list if c.complaint_type])
    status_counter = Counter([c.get_status_display() for c in complaints_list])

    # Customer Satisfaction Data
    satisfaction_counter = Counter()
    resolved_complaints = [c for c in complaints_list if c.status == 'resolved']
    
    for complaint in resolved_complaints:
        if hasattr(complaint, 'resolution') and complaint.resolution.customer_satisfaction:
            satisfaction_counter[complaint.resolution.get_customer_satisfaction_display()] += 1
    
    # Calculate Average Resolve Time (overall)
    resolve_times = []
    for complaint in resolved_complaints:
        if complaint.resolve_time_hours is not None:
            resolve_times.append(complaint.resolve_time_hours * 3600)
    
    # Calculate average in hours and days
    avg_resolve_time_seconds = sum(resolve_times) / len(resolve_times) if resolve_times else 0
    avg_resolve_time_hours = round(avg_resolve_time_seconds / 3600, 2)
    avg_resolve_time_days = round(avg_resolve_time_seconds / 86400, 2)
    
    # Format for display
    if avg_resolve_time_seconds > 0:
        days = int(avg_resolve_time_seconds // 86400)
        hours = int((avg_resolve_time_seconds % 86400) // 3600)
        minutes = int((avg_resolve_time_seconds % 3600) // 60)
        avg_resolve_time_formatted = f"{days}d {hours}h {minutes}m"
    else:
        avg_resolve_time_formatted = "N/A"

    # Statistics
    total_complaints = len(complaints_list)
    resolved_count = len(resolved_complaints)
    pending_count = total_complaints - resolved_count
    resolution_rate = round((resolved_count / total_complaints * 100), 2) if total_complaints > 0 else 0
    
    # Satisfaction rate (percentage of satisfied customers)
    satisfied_count = satisfaction_counter.get('Yes', 0)
    satisfaction_rate = round((satisfied_count / resolved_count * 100), 2) if resolved_count > 0 else 0

    context = {
        'complaints': complaints_list,
        'locations': locations,
        'ucs': ucs,
        'complaint_sources': complaint_sources,
        'complaint_types': complaint_types,
        'complaint_subtypes': complaint_subtypes,
        'start_date': start_date,
        'end_date': end_date,
        'location_filter': location_filter,
        'uc_filter': uc_filter,
        'status_filter': status_filter,
        'source_filter': source_filter,
        'type_filter': type_filter,
        'subtype_filter': subtype_filter,
        'cell_number_search': cell_number_search,
        'name_search': name_search,
        
        # Graph data
        'location_labels': list(location_counter.keys()),
        'location_counts': list(location_counter.values()),
        'source_labels': list(source_counter.keys()),
        'source_counts': list(source_counter.values()),
        'type_labels': list(type_counter.keys()),
        'type_counts': list(type_counter.values()),
        'status_labels': list(status_counter.keys()),
        'status_counts': list(status_counter.values()),
        
        # Satisfaction data
        'satisfaction_labels': list(satisfaction_counter.keys()),
        'satisfaction_counts': list(satisfaction_counter.values()),
        
        # Statistics
        'total_complaints': total_complaints,
        'resolved_count': resolved_count,
        'pending_count': pending_count,
        'resolution_rate': resolution_rate,
        'satisfaction_rate': satisfaction_rate,
        'satisfied_count': satisfied_count,
        
        # Average resolve time (overall)
        'avg_resolve_time_hours': avg_resolve_time_hours,
        'avg_resolve_time_days': avg_resolve_time_days,
        'avg_resolve_time_formatted': avg_resolve_time_formatted,
    }

    return render(request, 'C_report_generator.html', context)

from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Complaint, Location
from .decorators import view_permission_required

@login_required
@view_permission_required('complaint_summary_view')  # Assuming you have a custom permission decorator
def complaint_summary_view(request):
    # Get the date from the query parameters and validate it
    date_str = request.GET.get('date', None)
    report_date = parse_date(date_str) if date_str else now().date()
    if not report_date:
        report_date = now().date()  # Default to today's date if invalid

    location_filter = request.GET.get('location', None)

    # Retrieve locations and initialize summary variables
    locations = Location.objects.all().order_by('location_name')
    complaint_summary = []
    total_complaints = total_resolved = total_pending = 0
    type_summary = {}
    source_summary = {}

    # Handle location permissions: if user is not a superuser, apply location filter based on permissions
    if not request.user.is_superuser:
        # Get locations the user has permission to view
        user_locations = LocationPermission.objects.filter(user=request.user, can_view=True).values_list('locations', flat=True)
        # Filter locations to only those the user has access to
        locations = locations.filter(id__in=user_locations)
    
    # Filter locations if a location filter is applied
    filtered_locations = locations.filter(id=location_filter) if location_filter else locations

    # Iterate over each location to gather complaint data
    for location in filtered_locations:
        complaints = Complaint.objects.filter(date=report_date, location=location)

        total_location_complaints = complaints.count()
        resolved_complaints = complaints.filter(status='resolved').count()
        pending_complaints = complaints.filter(status='pending').count()

        # Summarize complaints by source for this location
        location_source_summary = {}
        for complaint in complaints:
            source = complaint.complaint_source
            if source not in location_source_summary:
                location_source_summary[source] = {'total': 0, 'resolved': 0, 'pending': 0}
            location_source_summary[source]['total'] += 1
            if complaint.status == 'resolved':
                location_source_summary[source]['resolved'] += 1
            else:
                location_source_summary[source]['pending'] += 1

            # Update the global source summary
            if source not in source_summary:
                source_summary[source] = {'total': 0, 'resolved': 0, 'pending': 0}
            source_summary[source]['total'] += 1
            if complaint.status == 'resolved':
                source_summary[source]['resolved'] += 1
            else:
                source_summary[source]['pending'] += 1

            # Summarize complaints by type
            complaint_type = complaint.complaint_type
            if complaint_type not in type_summary:
                type_summary[complaint_type] = {'total': 0, 'resolved': 0, 'pending': 0}
            type_summary[complaint_type]['total'] += 1
            if complaint.status == 'resolved':
                type_summary[complaint_type]['resolved'] += 1
            else:
                type_summary[complaint_type]['pending'] += 1

        # Update overall totals
        total_complaints += total_location_complaints
        total_resolved += resolved_complaints
        total_pending += pending_complaints

        # Add summary data for this location
        complaint_summary.append({
            'location': location,
            'total_complaints': total_location_complaints,
            'resolved_complaints': resolved_complaints,
            'pending_complaints': pending_complaints,
            'source_summary': location_source_summary,
        })

    context = {
        'complaint_summary': complaint_summary,
        'total_complaints': total_complaints,
        'total_resolved': total_resolved,
        'total_pending': total_pending,
        'type_summary': type_summary,
        'source_summary': source_summary,
        'report_date': report_date,
        'locations': locations,
        'location_filter': location_filter,
    }
    return render(request, 'complaint_summary.html', context)










from django.core.exceptions import ValidationError

@login_required
@view_permission_required('revenue_management_report')
def revenue_management_report(request):
    form = RevenueManagementReportForm(request.POST or None)
    report_date = timezone.now().date()

    # Get the selected date or default to today
    if request.method == 'GET':
        report_date = request.GET.get('date', report_date)
        if isinstance(report_date, str):  # Convert from string to date
            report_date = datetime.strptime(report_date, "%Y-%m-%d").date()

    # Filter revenue data for today
    if request.user.is_superuser:
        revenue_data = Revenue.objects.filter(date=report_date)
        allowed_locations = None  # Superuser has no location restrictions
    else:
        # Get locations the user has permission to view
        allowed_locations = LocationPermission.objects.filter(
            user=request.user, can_view=True
        ).values_list('locations', flat=True)
        revenue_data = Revenue.objects.filter(
            date=report_date, location__id__in=allowed_locations
        )

    # Allow form submission for past dates
    if request.method == 'POST' and form.is_valid():
        new_revenue = form.save(commit=False)
        new_revenue.date = form.cleaned_data['date']  # Allow user to set date

        # Check if user is trying to add data for a location they don't have permission to manage
        if not request.user.is_superuser and new_revenue.location.id not in allowed_locations:
            form.add_error('location', "You don't have permission to add revenue data for this location.")
        # Check if an entry already exists for the same date and location
        elif Revenue.objects.filter(
            date=new_revenue.date,
            location=new_revenue.location
        ).exists():
            form.add_error(None, "An entry already exists for this location on this date.")
        else:
            new_revenue.save()
            return redirect('revenue_management_report')

    context = {
        'form': form,
        'report_date': report_date,
        'revenue_data': revenue_data,
    }
    return render(request, 'revenue_management.html', context)




from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect

def update_revenue(request, revenue_id):
    revenue = get_object_or_404(Revenue, id=revenue_id)
    if request.method == 'POST':
        revenue.recovery_day_water_supply = request.POST.get('recovery_day_water_supply', revenue.recovery_day_water_supply)
        revenue.recovery_day_solid_waste_management = request.POST.get('recovery_day_solid_waste_management', revenue.recovery_day_solid_waste_management)
        revenue.recovery_of_day = request.POST.get('recovery_of_day', revenue.recovery_of_day)

        
        
        revenue.bill_paid_day_water_supply = request.POST.get('bill_paid_day_water_supply', revenue.bill_paid_day_water_supply)
        revenue.bill_paid_day_solid_waste_management = request.POST.get('bill_paid_day_solid_waste_management', revenue.bill_paid_day_solid_waste_management)
        revenue.number_of_bills_paid = request.POST.get('number_of_bills_paid', revenue.number_of_bills_paid)
        revenue.billed_amount_total = request.POST.get('billed_amount_total', revenue.billed_amount_total)


       
        revenue.save()
        return redirect('revenue_management_report')



@login_required
@view_permission_required('revenue_summary_view')  # Custom decorator for permission check
def revenue_summary_view(request):
    # Default to today's date unless a specific date is provided
    today = datetime.today().date()
    selected_date_str = request.GET.get('date', None)
    selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date() if selected_date_str else today

    current_month = selected_date.month
    current_year = selected_date.year

    # Get all locations for filtering, excluding 'Headoffice'
    locations = Location.objects.exclude(location_name="Headoffice").order_by('location_name')

    # Restrict locations if the user is not a superuser
    if not request.user.is_superuser:
        user_locations = LocationPermission.objects.filter(
            user=request.user, can_view=True
        ).values_list('locations', flat=True)
        locations = locations.filter(id__in=user_locations)

    # Apply location filter from GET parameters
    location_filter = request.GET.get('location', None)
    filtered_locations = locations.filter(id=location_filter) if location_filter else locations

    # Initialize total summary list
    total_revenue_summary = []

    for location in filtered_locations:
        revenue_data = Revenue.objects.filter(location=location)

        # Calculate daily totals for the selected date
        total_recovery_day_water_supply = revenue_data.filter(date=selected_date).aggregate(
            total=Sum('recovery_day_water_supply')
        )['total'] or 0

        total_recovery_day_solid_waste_management = revenue_data.filter(date=selected_date).aggregate(
            total=Sum('recovery_day_solid_waste_management')
        )['total'] or 0

        total_recovery_of_day = total_recovery_day_water_supply + total_recovery_day_solid_waste_management

        total_bill_paid_day_water_supply = revenue_data.filter(date=selected_date).aggregate(
            total=Sum('bill_paid_day_water_supply')
        )['total'] or 0

        total_bill_paid_day_solid_waste_management = revenue_data.filter(date=selected_date).aggregate(
            total=Sum('bill_paid_day_solid_waste_management')
        )['total'] or 0

        # Calculate monthly totals for this location
        total_paid_month_water_supply = revenue_data.filter(
            date__month=current_month, date__year=current_year
        ).aggregate(total=Sum('total_paid_month_water_supply'))['total'] or 0

        total_paid_month_solid_waste_management = revenue_data.filter(
            date__month=current_month, date__year=current_year
        ).aggregate(total=Sum('total_paid_month_solid_waste_management'))['total'] or 0

        total_billed_amount_total = revenue_data.filter(
            date=selected_date
        ).aggregate(total=Sum('billed_amount_total'))['total'] or 0

        total_number_of_bills_paid = revenue_data.filter(
            date=selected_date
        ).aggregate(total=Sum('number_of_bills_paid'))['total'] or 0

        total_revenue_summary.append({
            'location': location,
            'total_recovery_day_water_supply': total_recovery_day_water_supply,
            'total_recovery_day_solid_waste_management': total_recovery_day_solid_waste_management,
            'total_recovery_of_day': total_recovery_of_day,  # New field
            'total_bill_paid_day_water_supply': total_bill_paid_day_water_supply,
            'total_bill_paid_day_solid_waste_management': total_bill_paid_day_solid_waste_management,
            'total_paid_month_water_supply': total_paid_month_water_supply,
            'total_paid_month_solid_waste_management': total_paid_month_solid_waste_management,
            'total_billed_amount_total': total_billed_amount_total,
            'total_number_of_bills_paid': total_number_of_bills_paid,
        })

    # Calculate overall totals
    totals = {
        'total_recovery_day_water_supply': sum(item['total_recovery_day_water_supply'] for item in total_revenue_summary),
        'total_recovery_day_solid_waste_management': sum(item['total_recovery_day_solid_waste_management'] for item in total_revenue_summary),
        'total_recovery_of_day': sum(item['total_recovery_of_day'] for item in total_revenue_summary),  # New total
        'total_bill_paid_day_water_supply': sum(item['total_bill_paid_day_water_supply'] for item in total_revenue_summary),
        'total_bill_paid_day_solid_waste_management': sum(item['total_bill_paid_day_solid_waste_management'] for item in total_revenue_summary),
        'total_paid_month_water_supply': sum(item['total_paid_month_water_supply'] for item in total_revenue_summary),
        'total_paid_month_solid_waste_management': sum(item['total_paid_month_solid_waste_management'] for item in total_revenue_summary),
        'total_billed_amount_total': sum(item['total_billed_amount_total'] for item in total_revenue_summary),
        'total_number_of_bills_paid': sum(item['total_number_of_bills_paid'] for item in total_revenue_summary),
    }

    return render(request, 'revenue_summary.html', {
        'totals': totals,
        'total_revenue_summary': total_revenue_summary,
        'report_date': selected_date,
        'locations': locations,
        'location_filter': location_filter,
    })


from django.shortcuts import render
from django.db.models import Sum
from .models import Revenue, Location
from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import render
from .models import Revenue, Location, LocationPermission


@login_required
@view_permission_required('revenue_report_generator')
def revenue_report_generator(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location_filter = request.GET.get('location')
    selected_months = request.GET.getlist('month')  # Get multiple selected months

    # Convert months to integers, handling invalid values
    try:
        selected_months = [int(month) for month in selected_months if month.isdigit()]
    except ValueError:
        selected_months = []

    # Default to the current month if no month is selected
    if not selected_months:
        selected_months = [datetime.now().month]

    # Generate list of months for the dropdown
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]

    # Filter locations based on user permissions
    if request.user.is_superuser:
        locations = Location.objects.all()
    else:
        user_locations = LocationPermission.objects.filter(
            user=request.user, can_view=True
        ).values_list('locations', flat=True)
        locations = Location.objects.filter(id__in=user_locations)

    # Filter revenues based on date range, location, and selected months
    revenues = Revenue.objects.all()

    if start_date:
        revenues = revenues.filter(date__gte=start_date)
    if end_date:
        revenues = revenues.filter(date__lte=end_date)
    if location_filter:
        revenues = revenues.filter(location__location_name=location_filter)

    # Apply filtering for multiple selected months
    if selected_months:
        revenues = revenues.filter(date__month__in=selected_months)

    # Ensure non-superusers cannot access unauthorized location data
    if not request.user.is_superuser:
        revenues = revenues.filter(location__id__in=locations.values_list('id', flat=True))

    # 🔥 ORDER BY DATE ASCENDING (important update)
    revenues = revenues.order_by('date')

    # Aggregate totals
    totals = revenues.aggregate(
        total_recovery_day_water_supply=Sum('recovery_day_water_supply'),
        total_recovery_day_solid_waste_management=Sum('recovery_day_solid_waste_management'),
        total_bill_paid_day_water_supply=Sum('bill_paid_day_water_supply'),
        total_bill_paid_day_solid_waste_management=Sum('bill_paid_day_solid_waste_management'),
        total_billed_amount=Sum('billed_amount_total'),
        total_bills_paid=Sum('number_of_bills_paid'),
    )

    # Prepare context
    context = {
        'revenue_data': revenues,
        'totals': totals,
        'start_date': start_date,
        'end_date': end_date,
        'location_filter': location_filter,
        'locations': locations,
        'months': months,
        'selected_months': selected_months,
    }

    return render(request, 'revenue_report.html', context)




@login_required
@view_permission_required('clc_report')
def clc_report(request):
    form = CLCForm()
    report_date = timezone.now().date()

    # Handle the GET request for filtering by date
    if request.method == 'GET':
        report_date = request.GET.get('date', report_date)

    # Get the locations the user has permission to view
    user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
    allowed_locations = [permission.locations.all() for permission in user_permissions]
    allowed_locations = [location for sublist in allowed_locations for location in sublist]  # Flatten the list

    # Retrieve reports only for locations the user has permission to view
    locations = Location.objects.filter(id__in=[location.id for location in allowed_locations])

    total_data = []
    for location in locations:
        # Retrieve reports for the specific location and date
        total_reports = CLC.objects.filter(date=report_date, location=location)

        total_entry = {
            'location': location,
            'reports': total_reports,  # Pass the queryset to the template
        }
        total_data.append(total_entry)

    # Handle the POST request to save a new CLC report
    if request.method == 'POST':
        form = CLCForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            # Check if the location selected in the form is one the user has permission to save reports for
            selected_location = form.cleaned_data.get('location')
            
            # Only allow saving if the selected location is in the allowed locations
            if selected_location and selected_location in allowed_locations:
                # Save the form if the location is valid
                form.save()
                return redirect('clc_report')
            else:
                # If the user does not have permission for the selected location, show an error message
                form.add_error('location', 'You do not have permission to save reports for this location.')

    # Prepare the context for rendering the template
    context = {
        'total_data': total_data,
        'form': form,
        'report_date': report_date,
    }
    return render(request, 'clc_report.html', context)

from django.shortcuts import get_object_or_404, redirect, render
from .models import CLC
from .forms import CLCForm

def update_clc_report(request, report_id):
    clc_report = get_object_or_404(CLC, id=report_id)

    if request.method == 'POST':
        # Update fields using POST data
        clc_report.date = request.POST.get('date', clc_report.date)
        clc_report.location_id = request.POST.get('location', clc_report.location_id)

        clc_report.brief_report = request.POST.get('brief_report', clc_report.brief_report)
        clc_report.no_of_participants = request.POST.get('no_of_participants', clc_report.no_of_participants)  # Update participants count


        # Handle file upload for the image
        if 'image' in request.FILES:
            clc_report.image = request.FILES['image']

        # Save the updated report
        clc_report.save()
        return redirect('clc_report')

    context = {
        'clc_report': clc_report,
        'form': CLCForm(instance=clc_report),
    }
    return render(request, 'update_clc_report.html', context)









from django.shortcuts import render
from django.db.models import Count
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import CLC, Location
from .decorators import view_permission_required  # Assuming you have a custom decorator

@login_required
@view_permission_required('clc_summary')# Assuming you have a custom view permission decorator
def clc_summary(request):
    # Default to today's date if not provided
    report_date = now().date()
    selected_location = None

    # Handle GET request parameters
    if request.method == 'GET':
        date_str = request.GET.get('date', None)
        selected_location = request.GET.get('location', None)

        # Validate and parse the date parameter
        if date_str:
            report_date = parse_date(date_str)
            if not report_date:
                report_date = now().date()  # Fall back to today's date if invalid

    # Retrieve all locations
    locations = Location.objects.all().order_by('location_name')

    # Check if the user is a superuser or has location permissions
    if not request.user.is_superuser:
        # Get locations the user has permission to view
        user_locations = LocationPermission.objects.filter(user=request.user, can_view=True).values_list('locations', flat=True)
        locations = locations.filter(id__in=user_locations)  # Only show locations the user has permission for

    total_data = []

    # Gather CLC report data for each location
    for location in locations:
        if selected_location and str(location.id) != selected_location:
            continue  # Skip locations not matching the selected location

        # Filter reports by date and location
        total_reports = CLC.objects.filter(date=report_date, location=location)
        report_count = total_reports.count()

        # Prepare reports data for the template
        reports = total_reports.values(
            'date',
            'name_of_official__name',
            'activity__name',  # Assuming 'Activity' has a name field
            'brief_report'
        )

        total_entry = {
            'location': location,
            'report_count': report_count,
            'reports': list(reports),
        }
        total_data.append(total_entry)

    # Activity-wise summary
    activity_summary = (
        CLC.objects.filter(date=report_date)
        .values('activity__name')
        .annotate(total_reports=Count('id'))
        .order_by('activity__name')  # Optional: Order by activity name
    )

    # Prepare the context for the template
    context = {
        'total_data': total_data,
        'report_date': report_date,
        'locations': locations,
        'selected_location': selected_location,
        'activity_summary': activity_summary,
    }

    return render(request, 'clc_summary.html', context)


from django.shortcuts import render
from .models import CLC, Activity, CLCStaff, Location


# @login_required
# @view_permission_required('generate_clc_report') 
# def generate_clc_report(request):
#     start_date = request.GET.get('start_date', '')
#     end_date = request.GET.get('end_date', '')
#     location_filter = request.GET.get('location', '')
#     activity_filter = request.GET.get('activity', '')
#     designation_filter = request.GET.get('designation', '')

#     clc_reports = CLC.objects.all()

#     if not request.user.is_superuser:
#         user_locations = LocationPermission.objects.filter(user=request.user, can_view=True).values_list('locations', flat=True)
#         clc_reports = clc_reports.filter(location__id__in=user_locations)

#     if start_date:
#         clc_reports = clc_reports.filter(date__gte=start_date)
#     if end_date:
#         clc_reports = clc_reports.filter(date__lte=end_date)
#     if location_filter:
#         clc_reports = clc_reports.filter(location__location_name=location_filter)
#     if activity_filter:
#         clc_reports = clc_reports.filter(activity__name=activity_filter)
#     if designation_filter:
#         clc_reports = clc_reports.filter(name_of_official__designation=designation_filter)

#     locations = Location.objects.all()

#     if not request.user.is_superuser:
#         locations = locations.filter(id__in=user_locations)

#     activities = Activity.objects.all()
#     designations = CLCStaff.objects.values('designation').distinct()

#     return render(request, 'clc_report_generate.html', {
#         'clc_reports': clc_reports,
#         'start_date': start_date,
#         'end_date': end_date,
#         'location_filter': location_filter,
#         'activity_filter': activity_filter,
#         'designation_filter': designation_filter,
#         'locations': locations,
#         'activities': activities,
#         'designations': designations
#     })



from datetime import datetime

@login_required
@view_permission_required('generate_clc_report')
def generate_clc_report(request):

    # Get filters
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    location_filter = request.GET.get('location', '')
    activity_filter = request.GET.get('activity', '')
    designation_filter = request.GET.get('designation', '')

    # -----------------------------
    # SAFE DATE HANDLING
    # -----------------------------
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except:
            start_date = None
            end_date = None

    # If no dates provided → use current month safely
    if not start_date or not end_date:
        today = datetime.today()

        # First day of current month
        start_date = date(today.year, today.month, 1)

        # First day of next month (safe)
        if today.month == 12:
            next_month = date(today.year + 1, 1, 1)
        else:
            next_month = date(today.year, today.month + 1, 1)

        # Last day of this month
        end_date = next_month - timedelta(days=1)

    # -----------------------------
    # DATA FILTERING
    # -----------------------------
    clc_reports = CLC.objects.all()

    clc_reports = clc_reports.filter(date__gte=start_date, date__lte=end_date)

    if location_filter:
        clc_reports = clc_reports.filter(location__location_name=location_filter)

    if activity_filter:
        clc_reports = clc_reports.filter(activity__name=activity_filter)

    if designation_filter:
        clc_reports = clc_reports.filter(name_of_official__designation=designation_filter)

    clc_reports = clc_reports.order_by('date')

    # -----------------------------
    # FILTER OPTIONS
    # -----------------------------
    locations = Location.objects.all()
    activities = Activity.objects.all()

    # -----------------------------
    # CHART DATA
    # -----------------------------
    location_activity_data = Counter(r.location.location_name for r in clc_reports)
    uc_activity_data = Counter(r.uc.uc_name for r in clc_reports)
    nc_activity_data = Counter(r.nc.nc_name for r in clc_reports)
    activity_count_data = Counter(r.activity.name for r in clc_reports)

    context = {
        'clc_reports': clc_reports,

        'start_date': start_date,
        'end_date': end_date,

        'location_filter': location_filter,
        'activity_filter': activity_filter,
        'designation_filter': designation_filter,

        'locations': locations,
        'activities': activities,

        'location_activity_data': (list(location_activity_data.keys()), list(location_activity_data.values())),
        'uc_activity_data': (list(uc_activity_data.keys()), list(uc_activity_data.values())),
        'nc_activity_data': (list(nc_activity_data.keys()), list(nc_activity_data.values())),
        'activity_count_data': (list(activity_count_data.keys()), list(activity_count_data.values())),
    }

    return render(request, 'clc_report_generate.html', context)



@login_required
@view_permission_required('bin_summary_view')
def bin_summary_view(request):
    locations = Location.objects.all()  # Fetch all locations
    selected_date = request.GET.get('date', timezone.now().date())  # Get the selected date or use today's date
    location_data = []

    # Filter BinAttendance by selected date
    for location in locations:
        total_moqas = Bin.objects.filter(location=location, name='moqa').count()
        total_containers = Bin.objects.filter(location=location, name='container').count()

        lifted_moqas = BinAttendance.objects.filter(location=location, attendance_date=selected_date, bin_name__name='moqa', lifted=True).count()
        unlifted_moqas = BinAttendance.objects.filter(location=location, attendance_date=selected_date, bin_name__name='moqa', lifted=False).count()
        
        lifted_containers = BinAttendance.objects.filter(location=location, attendance_date=selected_date, bin_name__name='container', lifted=True).count()
        unlifted_containers = BinAttendance.objects.filter(location=location, attendance_date=selected_date, bin_name__name='container', lifted=False).count()

        location_data.append({
            'location': location,
            'total_moqas': total_moqas,
            'total_containers': total_containers,
            'lifted_moqas': lifted_moqas,
            'unlifted_moqas': unlifted_moqas,
            'lifted_containers': lifted_containers,
            'unlifted_containers': unlifted_containers,
        })

    # Prepare data for the chart
    location_labels = [data['location'].location_name for data in location_data]
    total_moqas_data = [data['total_moqas'] for data in location_data]
    lifted_moqas_data = [data['lifted_moqas'] for data in location_data]
    unlifted_moqas_data = [data['unlifted_moqas'] for data in location_data]
    total_containers_data = [data['total_containers'] for data in location_data]
    lifted_containers_data = [data['lifted_containers'] for data in location_data]
    unlifted_containers_data = [data['unlifted_containers'] for data in location_data]

    context = {
        'location_data': location_data,
        'selected_date': selected_date,
        'location_labels': location_labels,
        'total_moqas_data': total_moqas_data,
        'lifted_moqas_data': lifted_moqas_data,
        'unlifted_moqas_data': unlifted_moqas_data,
        'total_containers_data': total_containers_data,
        'lifted_containers_data': lifted_containers_data,
        'unlifted_containers_data': unlifted_containers_data,
    }
    
    return render(request, 'bin_summary.html', context)





# views.py
from django.http import JsonResponse
from .models import official



from django.views.generic import ListView
from django.shortcuts import render
from django.views.generic import ListView
from .models import Bin, Location, UC

from django.contrib.auth.models import User
from django.views.generic import ListView
from .models import Bin, Location, LocationPermission

from django.shortcuts import render
from .models import Bin, Location, LocationPermission

from django.shortcuts import render
from .models import Bin, Location, Category, Capacity, DayFrequency  # Import all required models



@login_required
@view_permission_required('bin_list_view')
def bin_list_view(request):
    user = request.user
    location_filter = request.GET.get('location')
    category_filter = request.GET.get('category')
    capacity_filter = request.GET.get('capacity')
    day_filter = request.GET.getlist('days')
    bin_type_filter = request.GET.get('bin_type')  # New filter for bin type

    queryset = Bin.objects.all()

    if not user.is_superuser:
        location_permissions = LocationPermission.objects.filter(user=user, can_view=True)
        allowed_locations = location_permissions.values_list('locations', flat=True)
        queryset = queryset.filter(location_id__in=allowed_locations)

    if location_filter:
        queryset = queryset.filter(location__location_name=location_filter)
    if category_filter:
        queryset = queryset.filter(category__category=category_filter)
    if capacity_filter:
        queryset = queryset.filter(capacity__capacity=capacity_filter)
    if day_filter:
        queryset = queryset.filter(days__name__in=day_filter).distinct()
    if bin_type_filter:  # Apply the bin type filter
        queryset = queryset.filter(name=bin_type_filter)

    locations = Location.objects.all()
    categories = Category.objects.all()
    capacities = Capacity.objects.all()
    days = DayFrequency.objects.all()
    bin_types = Bin.TYPE_CHOICES  # Get bin type choices from the model

    context = {
        'bins': queryset,
        'locations': locations,
        'categories': categories,
        'capacities': capacities,
        'days': days,
        'bin_types': bin_types,  # Pass bin types to the template
        'location_filter': location_filter,
        'category_filter': category_filter,
        'capacity_filter': capacity_filter,
        'day_filter': day_filter,
        'bin_type_filter': bin_type_filter,  # Pass selected bin type to the template
    }

    return render(request, 'bin_list.html', context)



from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import BinUpdateForm

def update_bin_view(request, pk):
    # Fetch the bin object
    bin_obj = get_object_or_404(Bin, pk=pk)

    if request.method == 'POST':
        # Bind the form to the POST data
        form = BinUpdateForm(request.POST, instance=bin_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bin updated successfully!')
            return redirect(reverse('bin_list'))  # Redirect back to the list view
    else:
        # Load the form with existing bin data
        form = BinUpdateForm(instance=bin_obj)

    return render(request, 'update_bin.html', {'form': form, 'bin': bin_obj})




from django.shortcuts import render
from .models import Bin

from .models import Bin

from django.shortcuts import get_object_or_404

from django.shortcuts import render
from .models import Bin, Location, LocationPermission
from django.contrib.auth.models import User

from django.shortcuts import render
from .models import Bin, Location, LocationPermission





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Binfoam, Location, LocationPermission
from .forms import BinfoamForm
from datetime import date
from .models import UcPermission

@login_required
@view_permission_required('binfoam_view')
def binfoam_view(request):
    # Get the date from the GET request, default to today's date
    report_date = request.GET.get('date', date.today())
    
    # Determine which locations and UCs the user has access to
    if request.user.is_superuser:
        locations = Location.objects.all()  # Superuser can view all locations
        ucs = UC.objects.all()  # Superuser can view all UCs
    else:
        # Get location permissions
        user_location_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = user_location_permissions.values_list('locations', flat=True)
        locations = Location.objects.filter(id__in=location_ids)
        
        # Get UC permissions
        user_uc_permissions = UcPermission.objects.filter(user=request.user)
        uc_ids = user_uc_permissions.values_list('Uc', flat=True)
        ucs = UC.objects.filter(id__in=uc_ids)

    # Filter Binfoam data based on allowed locations, UCs, and date
    binfoam_data = Binfoam.objects.filter(location__in=locations, uc__in=ucs, attendance_date=report_date)

    # Handle form submission
    if request.method == 'POST':
        form = BinfoamForm(request.POST)
        if form.is_valid():
            selected_location = form.cleaned_data['location']
            selected_uc = form.cleaned_data['uc']
            if (
                request.user.is_superuser or
                (selected_location in locations and selected_uc in ucs)
            ):
                binfoam = form.save()
                return JsonResponse({
                    'success': True,
                    'binfoam': {
                        'attendance_date': binfoam.attendance_date.strftime('%Y-%m-%d'),
                        'location': str(binfoam.location),
                        'uc': str(binfoam.uc),
                        'bin_name': str(binfoam.bin_name),
                        'liftingfrequency': binfoam.liftingfrequency,
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'You do not have permission to add data for this location or UC.'})
    else:
        form = BinfoamForm()

    context = {
        'report_date': report_date,
        'binfoam_data': binfoam_data,
        'form': form,
    }
    
    return render(request, 'binfoam.html', context)




@login_required
@view_permission_required('report_post_attendance')
def report_post_attendance(request):
    # === Filters ===
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    post_type_filter = request.GET.get('post_type', 'all')

    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else None
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else None
    except ValueError:
        messages.error(request, "Invalid date format.")
        return redirect('report_post_attendance')

    if from_date and to_date and from_date > to_date:
        messages.error(request, "The 'From' date cannot be later than the 'To' date.")
        return redirect('report_post_attendance')

    if to_date and to_date > timezone.now().date():
        messages.error(request, "The 'To' date cannot be in the future.")
        return redirect('report_post_attendance')

    # === Base Query ===
    post_attendances = PostAttendance.objects.all()
    if from_date:
        post_attendances = post_attendances.filter(post_date__gte=from_date)
    if to_date:
        post_attendances = post_attendances.filter(post_date__lte=to_date)
    if post_type_filter != 'all':
        post_attendances = post_attendances.filter(post_type_id=post_type_filter)

    # === Consolidate by Post Type & Details ===
    summary = {}
    total_posts = 0

    for attendance in post_attendances:
        post_type = attendance.post_type.name if attendance.post_type else "Unknown"
        details = attendance.post_detail.media_channel if attendance.post_detail else "N/A"
        count = int(attendance.no_of_post) if str(attendance.no_of_post).isdigit() else 1

        key = (post_type, details)
        if key not in summary:
            summary[key] = count
        else:
            summary[key] += count

        total_posts += count

    # Convert summary dict to list for template
    attendance_data = [
        {'post_type': k[0], 'details': k[1], 'count': v}
        for k, v in summary.items()
    ]

    # === CSV Export ===
    if 'download_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="post_attendance_summary.csv"'
        writer = csv.writer(response)
        writer.writerow(['Post Type', 'Details', 'Count'])

        for row in attendance_data:
            writer.writerow([row['post_type'], row['details'], row['count']])
        writer.writerow([])
        writer.writerow(['Total Posts', total_posts])
        return response

    post_types = Post.objects.all()

    context = {
        'attendance_data': attendance_data,
        'from_date': from_date,
        'to_date': to_date,
        'post_type_filter': post_type_filter,
        'post_types': post_types,
        'total_posts': total_posts,
    }

    return render(request, 'report_post_attendance.html', context)








from django.utils.timezone import now
from datetime import datetime
from django.db.models import Q

from django.utils.timezone import now
from datetime import datetime
from django.shortcuts import render
from .models import Bin, BinAttendance, Binfoam, UC, Location, LocationPermission

def map_all_bins(request):
    # Get filters from the request
    bin_id = request.GET.get('bin_id', '')
    bin_type = request.GET.get('bin_type', '')
    location_id = request.GET.get('location_id', '')
    uc_id = request.GET.get('uc_id', '')
    bin_status = request.GET.get('bin_status', '')
    selected_date_str = request.GET.get('date', str(now().date()))

    # Process the date
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = now().date()

    user = request.user

    # Filter bins with coordinates
    bins = Bin.objects.filter(latitude__isnull=False, longitude__isnull=False)

    # Restrict by location permissions if not superuser
    if not user.is_superuser:
        location_permissions = LocationPermission.objects.filter(user=user, can_view=True)
        allowed_locations = location_permissions.values_list('locations', flat=True)
        bins = bins.filter(location_id__in=allowed_locations)

    # Apply user filters
    if bin_id:
        bins = bins.filter(bin_id__icontains=bin_id)
    if bin_type:
        bins = bins.filter(name=bin_type)
    if location_id:
        bins = bins.filter(location_id=location_id)
    if uc_id:
        bins = bins.filter(uc_id=uc_id)


    # Attendance and Binfoam for selected date
    attendance_records = BinAttendance.objects.filter(attendance_date=selected_date, bin_name__in=bins)
    attendance_mapping = {record.bin_name.id: record for record in attendance_records}

    binfoam_records = Binfoam.objects.filter(attendance_date=selected_date, bin_name__in=bins)
    binfoam_mapping = {record.bin_name.id: record for record in binfoam_records}

    # Filter bins by lifted/unlifted status if applicable
    if bin_status:
        if bin_status == "Lifted":
            bins = bins.filter(id__in=[record.bin_name.id for record in attendance_records if record.lifted])
        elif bin_status == "Unlifted":
            bins = bins.filter(id__in=[record.bin_name.id for record in attendance_records if not record.lifted])

    # Annotate bins
    bins_with_status = []
    bin_js_data = []

    for bin in bins:
        attendance = attendance_mapping.get(bin.id)
        binfoam = binfoam_mapping.get(bin.id)

        status = 'Lifted' if attendance and attendance.lifted else 'Unlifted'
        lifting_frequency = binfoam.liftingfrequency if binfoam else '0'
        first_lifting_time = binfoam.firstliftingtime.strftime('%H:%M') if binfoam and binfoam.firstliftingtime else ''
        second_lifting_time = binfoam.secondliftingtime.strftime('%H:%M') if binfoam and binfoam.secondliftingtime else ''
        third_lifting_time = binfoam.thirdliftingtime.strftime('%H:%M') if binfoam and binfoam.thirdliftingtime else ''

        bins_with_status.append({
            'bin': bin,
            'status': status,
            'lifting_frequency': lifting_frequency,
            'first_lifting_time': first_lifting_time,
            'second_lifting_time': second_lifting_time,
            'third_lifting_time': third_lifting_time,
        })

        bin_js_data.append({
            "bin_id": bin.bin_id,
            "type": bin.name,
            "name": bin.name_container,
            "location": str(bin.location),
            "latitude": bin.latitude,
            "longitude": bin.longitude,
            "status": status,
            "lifting_frequency": lifting_frequency,
            "first_lifting_time": first_lifting_time,
            "second_lifting_time": second_lifting_time,
            "third_lifting_time": third_lifting_time
        })

    # UCs and locations
    ucs = UC.objects.filter(location_id=location_id) if location_id else UC.objects.all()
    locations = Location.objects.all()

    # Total bins by type
    total_containers = bins.filter(name='container').count()
    total_moqas = bins.filter(name='moqa').count()

    # KMZ handling
    kmz_files = KMZUpload.objects.all().order_by('-uploaded_at')
    for kmz in kmz_files:
        if kmz.file.name.endswith('.kmz') and not kmz.kml_file:
            try:
                with zipfile.ZipFile(kmz.file.path, 'r') as zip_ref:
                    for name in zip_ref.namelist():
                        if name.endswith('.kml'):
                            kml_data = zip_ref.read(name)
                            base_name = os.path.splitext(os.path.basename(kmz.file.name))[0]
                            kml_filename = f"{slugify(base_name)}.kml"
                            kmz.kml_file.save(kml_filename, ContentFile(kml_data), save=True)
                            break
            except Exception as e:
                print(f"Failed to extract KML from {kmz.file.name}: {e}")

    # Pass KMZ files to the context
    context = {
        'bins_with_status': bins_with_status,
        'bin_js_data': bin_js_data,
        'locations': locations,
        'ucs': ucs,
        'kmz_files': KMZUpload.objects.all(),  # Pass KMZ files here
        'TYPE_CHOICES': Bin.TYPE_CHOICES,
        'selected_date': selected_date,
        'today_date': date.today().isoformat(),
        'total_containers': total_containers,
        'total_moqas': total_moqas,
    }

    return render(request, 'map_all_bins.html', context)


from django.shortcuts import render
from django.http import JsonResponse
from .models import locationmap

def location_map_view(request):
    return render(request, 'map.html')

def location_map_geojson(request):
    locations = locationmap.objects.all()
    features = []
    for loc in locations:
        if loc.latitude and loc.longitude:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(loc.longitude), float(loc.latitude)],
                },
                "properties": {
                    "name": loc.name,
                },
            })
    return JsonResponse({"type": "FeatureCollection", "features": features})



import geopandas as gpd
import os
import zipfile
from django.shortcuts import render
from django.conf import settings
from .forms import KMZUploadForm
from django.http import JsonResponse



import geopandas as gpd
import zipfile
import os
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import KMZUpload

def kmz_visualization(request, kmz_id):
    kmz = get_object_or_404(KMZUpload, id=kmz_id)
    kmz_path = kmz.file.path

    # Extract KMZ to get KML
    with zipfile.ZipFile(kmz_path, 'r') as kmz_file:
        kml_file = [name for name in kmz_file.namelist() if name.endswith('.kml')][0]
        kml_path = os.path.join(settings.MEDIA_ROOT, 'temp.kml')
        with open(kml_path, 'wb') as f:
            f.write(kmz_file.read(kml_file))

    # Load GeoJSON
    gdf = gpd.read_file(kml_path)
    geojson = gdf.to_json()

    return render(request, 'kmz_visualization.html', {'geojson': geojson})



from django.shortcuts import render, redirect
from .forms import PerfomaTubeForm

from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import PerfomaTubeForm

from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import PerfomaTubeForm

def add_perfoma_tube(request):
    if request.method == 'POST':
        form = PerfomaTubeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfoma Tube data saved successfully!')
            return redirect('add_perfoma_tube')  # Replace with the URL or view name where you want to redirect
        else:
            messages.error(request, 'There was an error saving the data. Please try again.')
            # Log the form errors to the console for debugging
            print(form.errors)  # This will print the form errors to the terminal
    else:
        form = PerfomaTubeForm()

    return render(request, 'add_perfoma_tube.html', {'form': form})




from django.shortcuts import render
from .models import perfoma_tube  # Assuming you have a model called PerfomaTube

def perfoma_tube_list(request):
    # Fetch all PerfomaTube objects from the database
    tubes = perfoma_tube.objects.all()
    return render(request, 'perfoma_tube_list.html', {'tubes': tubes})




from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Street_cleaning, Location, UC, NC, Street, DayFrequency, LiftingFrequency, Employee, Bin, Vehicle
from .forms import StreetCleaningForm

# List View for Street Cleaning
def street_cleaning_list(request):
    street_cleanings = Street_cleaning.objects.all()
    return render(request, 'street_cleaning/list.html', {'street_cleanings': street_cleanings})

# Create View for Street Cleaning
def street_cleaning_create(request):
    if request.method == 'POST':
        form = StreetCleaningForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('street_cleaning_list')
    else:
        form = StreetCleaningForm()
    return render(request, 'street_cleaning/form.html', {'form': form})

# Update View for Street Cleaning
def street_cleaning_update(request, pk):
    street_cleaning = get_object_or_404(Street_cleaning, pk=pk)
    if request.method == 'POST':
        form = StreetCleaningForm(request.POST, instance=street_cleaning)
        if form.is_valid():
            form.save()
            return redirect('street_cleaning_list')
    else:
        form = StreetCleaningForm(instance=street_cleaning)
    return render(request, 'street_cleaning/form.html', {'form': form})



# Detail View for Street Cleaning
def street_cleaning_detail(request, pk):
    street_cleaning = get_object_or_404(Street_cleaning, pk=pk)
    return render(request, 'street_cleaning/detail.html', {'street_cleaning': street_cleaning})


from django.http import JsonResponse
from .models import UC, NC

# Fetch UCs based on selected Location
def get_ucs(request):
    location_id = request.GET.get('location_id')
    ucs = UC.objects.filter(location_id=location_id).values('id', 'uc_name')
    return JsonResponse(list(ucs), safe=False)

# Fetch NCs based on selected UC
def get_ncs(request):
    uc_id = request.GET.get('uc_id')
    ncs = NC.objects.filter(uc_name_id=uc_id).values('id', 'nc_name')
    return JsonResponse(list(ncs), safe=False)

from django.http import JsonResponse
from .models import Employee, Vehicle, Bin

def get_employees(request):
    location_id = request.GET.get('location_id')
    employees = Employee.objects.filter(location_id=location_id)
    employee_data = [{'id': employee.id, 'name': employee.name} for employee in employees]
    return JsonResponse(employee_data, safe=False)

def get_vehicles(request):
    location_id = request.GET.get('location_id')
    vehicles = Vehicle.objects.filter(location_id=location_id)
    vehicle_data = [{'id': vehicle.id, 'name': vehicle.vehicle_name} for vehicle in vehicles]
    return JsonResponse(vehicle_data, safe=False)

def get_bins(request):
    location_id = request.GET.get('location_id')
    bins = Bin.objects.filter(location_id=location_id)
    bin_data = [{'id': bin.id, 'name': bin.name_container} for bin in bins]
    return JsonResponse(bin_data, safe=False)


from django.http import JsonResponse
from .models import Street

def get_streets(request):
    nc_id = request.GET.get('nc_id')
    streets = Street.objects.filter(nc_name_id=nc_id)  # Filter streets by NC ID
    street_data = [{'id': street.id, 'street_name': street.street_name} for street in streets]
    return JsonResponse(street_data, safe=False)




from django.utils import timezone
from datetime import timedelta


def report_summary(request):
    # Define the zones and head office
    locations = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E', 'Headoffice']

    # Parse the selected date or default to today
    selected_date = request.GET.get('report_date')
    report_date = parse_date(selected_date) if selected_date else now().date()

    # Prepare data dictionaries
    # Initialize keys for all locations
    locations = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E', 'Headoffice']

# Ensure all dictionaries have default values
    total_employee_data = {location: 0 for location in locations}
    present_employee_data = {location: 0 for location in locations}
    leave_employee_data = {location: 0 for location in locations}  # Add this line
    absent_employee_data = {location: 0 for location in locations}
    
    total_vehicle_data = {location: 0 for location in locations}
    functional_vehicle_data = {location: 0 for location in locations}
    non_functional_vehicle_data = {location: 0 for location in locations}
    total_tubewell_data = {location: 0 for location in locations}
    functional_tubewell_data = {location: 0 for location in locations}
    total_filter_data = {location: 0 for location in locations}
    functional_filter_data = {location: 0 for location in locations}
    field_visit_data = {location: '✗' for location in locations}
    water_supply_status = {location: '✗' for location in locations}
    complaints_status = {location: '✗' for location in locations}
    clc_status = {location: '✗' for location in locations}
    stanitation_status = {location: '✗' for location in locations}
    total_container_data = {location: 0 for location in locations}
    present_container_data = {location: 0 for location in locations}
    total_moqas_data = {location: 0 for location in locations}
    present_moqas_data = {location: 0 for location in locations}
    functional_container_data = {location: 0 for location in locations}
    functional_moqas_data = {location: 0 for location in locations}
    primary_waste_status = {location: '✗' for location in locations}
    waste_local_status = {location: '✗' for location in locations}
    waste_dump_lfs_status = {location: '✗' for location in locations}
    door_to_status = {location: '✗' for location in locations}
    local_demping_status = {location: '✗' for location in locations}
    lfts_trips_status = {location: '✗' for location in locations}
    cleaning_siltation_Manhole_status = {location: '✗' for location in locations}
    cleangni_siltation_drain_status = {location: '✗' for location in locations}



   

        # Employee data processing
        # Employee data processing
    for location in locations:
        # Get total employees for the current location
        total_employees = Employee.objects.filter(location__location_name=location).count()

        # Get present employees for the current location on the given date
        present_employees = EmployeeAttendance.objects.filter(
            employee_name__location__location_name=location,
            attendance_date=report_date,
            present=True
        ).count()

        # Get leave employees for the current location on the given date
        leave_employees = EmployeeAttendance.objects.filter(
            employee_name__location__location_name=location,
            attendance_date=report_date,
            leave=True
        ).count()

        # Get absent employees for the current location on the given date
        absent_employees = EmployeeAttendance.objects.filter(
            employee_name__location__location_name=location,
            attendance_date=report_date,
            absent=True
        ).count()

        # Store the data for total employees, present employees, leave, and absent
        total_employee_data[location] = total_employees
        present_employee_data[location] = present_employees
        leave_employee_data[location] = leave_employees
        absent_employee_data[location] = absent_employees


      

    for location in locations:
        has_visits = FieldVisitReport.objects.filter(
            location__location_name=location,
            date=report_date
        ).exists()

        field_visit_data[location] = '✓' if has_visits else '✗'

    # Initialize data with default values for all locations
    for location in locations:
        total_tubewell_data[location] = total_tubewell_data.get(location, 0)
        functional_tubewell_data[location] = functional_tubewell_data.get(location, 0)
        total_filter_data[location] = total_filter_data.get(location, 0)
        functional_filter_data[location] = functional_filter_data.get(location, 0)

#





    # Vehicle data processing
    # Get total vehicles for the current location
    total_vehicles = Vehicle.objects.filter(location__location_name=location).count()

    # Count functional vehicles for the current location and date
    functional_vehicles = VehicleAttendance.objects.filter(
        vehicle_name__location__location_name=location,
        attendance_date=report_date,
        functional=True
    ).count()

    # Count non-functional vehicles for the current location and date
    non_functional_vehicles = VehicleAttendance.objects.filter(
        vehicle_name__location__location_name=location,
        attendance_date=report_date,
        functional=False
    ).count()

    # Store the data for vehicles
    total_vehicle_data[location] = total_vehicles
    functional_vehicle_data[location] = functional_vehicles
    non_functional_vehicle_data[location] = non_functional_vehicles

        # Tubewell Data Aggregation
    # Get total tube wells for the current location
    total_tubewells = TubeWell.objects.filter(location__location_name=location).count()

    # Count operational tube wells (functional) for the current location and date
    operational_tubewells = TubeWellAttendance.objects.filter(
        tubewell__location__location_name=location,  # Accessing location_name through the location ForeignKey in TubeWell
        attendance_date=report_date,
        functional=True
    ).count()

    # Count non-functional tube wells for the current location and date
    non_functional_tubewells = TubeWellAttendance.objects.filter(
        tubewell__location__location_name=location,  # Same for non_functional filter
        attendance_date=report_date,
        non_functional=True
    ).count()

    # Count non-operational tube wells for the current location and date
    non_operational_tubewells = TubeWellAttendance.objects.filter(
        tubewell__location__location_name=location,  # Same for non_operational filter
        attendance_date=report_date,
        non_operational=True
    ).count()

    # Store the data for total tube wells and operational/non-operational tube wells
    total_tubewell_data[location] = total_tubewells
    functional_tubewell_data[location] = operational_tubewells + non_functional_tubewells + non_operational_tubewells

    # Filter Data Aggregation
    # Get total filters for the current location
    total_filters = Filter.objects.filter(location__location_name=location).count()

    # Count functional filters for the current location and date
    functional_filters = FilterAttendance.objects.filter(
        filter_name__location__location_name=location,
        attendance_date=report_date,
        functional=True
    ).count()

    # Count non-functional filters for the current location and date
    non_functional_filters = FilterAttendance.objects.filter(
        filter_name__location__location_name=location,
        attendance_date=report_date,
        non_functional=True
    ).count()

    # Store the data for total filters and functional/non-functional filters
    total_filter_data[location] = total_filters
    functional_filter_data[location] = functional_filters + non_functional_filters

    # Calculate Water Supply Status
    # Calculate Water Supply Status
    for location in locations:
    # If both Total Tubewell and Total Filter are equal to their respective functional counts
        if (total_tubewell_data[location] == functional_tubewell_data[location] and
            total_filter_data[location] == functional_filter_data[location]):
            water_supply_status[location] = '✓'
    else:
        water_supply_status[location] = '✗'

    # Initialize complaints status for zones and head office
    complaints_status = {location: '✗' for location in locations}
    complaints_status['Headoffice'] = '✗'

    # Flag to check if any zone has complaint_source == '1334'
    has_1334_complaint_in_any_zone = False

    for location in locations:
        # Fetch complaints for the zone on the given date using the 'date' field (not 'created_at_date')
        complaints_for_zone = Complaint.objects.filter(location__location_name=location, date=report_date)

        if not complaints_for_zone.exists():
            # No complaints for the zone, keep it as '✗'
            continue

        # Check if any complaint in the zone has source '1334'
        found_1334 = any(
            getattr(complaint.complaint_source, 'source_name', None) == '1334'
            for complaint in complaints_for_zone
        )

        if found_1334:
            complaints_status[location] = '✗'
            has_1334_complaint_in_any_zone = True
        else:
            complaints_status[location] = '✓'

    # Determine the head office status
    complaints_status['Headoffice'] = '✓' if has_1334_complaint_in_any_zone else '✗'

    # Debug output
    print("Final Complaints Status:", complaints_status)



# Check CLC data for each zone
    for location in locations:
    # Fetch today's entries for this location
        has_clc_data = CLC.objects.filter(
            location__isnull=False,
            location__location_name=location,
            date=report_date  # Only entries created on the selected date
        ).exists()
        clc_status[location] = '✓' if has_clc_data else '✗'


    # Calculate Total Containers and Moqas
    # Calculate Total Containers and Moqas
    for location in locations:
        # Containers Data for today
        total_containers = Bin.objects.filter(location__location_name=location, name='container').count()
        lifted_containers = BinAttendance.objects.filter(
            location__location_name=location,  # Use location__location_name
            bin_name__name='container',  # Filter by bin name
            attendance_date=report_date,
            lifted=True
        ).count()
        unlifted_containers = BinAttendance.objects.filter(
            location__location_name=location,  # Use location__location_name
            bin_name__name='container',  # Filter by bin name
            attendance_date=report_date,
            lifted=False
        ).count()

        # Moqas Data for today
        total_moqas = Bin.objects.filter(location__location_name=location, name='moqa').count()
        lifted_moqas = BinAttendance.objects.filter(
            location__location_name=location,  # Use location__location_name
            bin_name__name='moqa',  # Filter by bin name
            attendance_date=report_date,
            lifted=True
        ).count()
        unlifted_moqas = BinAttendance.objects.filter(
            location__location_name=location,  # Use location__location_name
            bin_name__name='moqa',  # Filter by bin name
            attendance_date=report_date,
            lifted=False
        ).count()

        # Update data dictionaries
        total_container_data[location] = f"{lifted_containers + unlifted_containers}/{total_containers}"
        total_moqas_data[location] = f"{lifted_moqas + unlifted_moqas}/{total_moqas}"

        # Determine sanitation status
        if (lifted_containers + unlifted_containers == total_containers) and \
        (lifted_moqas + unlifted_moqas == total_moqas):
            stanitation_status[location] = '✓'
        else:
            stanitation_status[location] = '✗'


    # Primary Waste Collection
    for location in locations:
        # Check if any primary waste collection data exists for the given location and date
        has_primary_waste_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            primary_waste_collection_tons__isnull=False
        ).exists()

        # Update the status based on the existence of data
        primary_waste_status[location] = '✓' if has_primary_waste_data else '✗'


    
    # Waste Locally Dumped
    for location in locations:
        # Check if any wastelocal dump waste collection data exists for the given location and date
        has__waste_local_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            waste_locally_dumped_tons__isnull=False
        ).exists()

        # Update the status based on the existence of data
        waste_local_status[location] = '✓' if has__waste_local_data else '✗'





        # Waste Dumped at LFS	

    for location in locations:
        # Check if any wastelocal dump waste collection data exists for the given location and date
        has__waste_lfs_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            waste_dumped_at_lfs_tons__isnull=False
        ).exists()

        # Update the status based on the existence of data
        waste_dump_lfs_status[location] = '✓' if has__waste_lfs_data else '✗'




        # Door to Door Collection

    for location in locations:
        # Check if any wastelocal dump waste collection data exists for the given location and date
        has__door_to_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            door_to_door_solid_waste_collection_no__isnull=False
        ).exists()

        # Update the status based on the existence of data
        door_to_status[location] = '✓' if has__door_to_data else '✗'


    # Local Dumping Trips

    for location in locations:
        # Check if any wastelocal dump waste collection data exists for the given location and date
        has__local_dump_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            local_dumping_trips_no__isnull=False
        ).exists()

        # Update the status based on the existence of data
        local_demping_status[location] = '✓' if has__local_dump_data else '✗'

    # LFS Trips
    for location in locations:
        # Check if any wastelocal dump waste collection data exists for the given location and date
        has__lfs_trips_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            lfs_trips_no__isnull=False
        ).exists()

        # Update the status based on the existence of data
        lfts_trips_status[location] = '✓' if has__lfs_trips_data else '✗'



    # Cleaning De-siltation of Manhole

    for location in locations:
        # Check if any wastelocal dump waste collection data exists for the given location and date
        has__cleaing_de_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            cleaning_de_siltation_of_manholes__isnull=False
        ).exists()

        # Update the status based on the existence of data
        cleaning_siltation_Manhole_status[location] = '✓' if has__cleaing_de_data else '✗'

    # Cleaning De-siltation of Drain Sewers (Km)
    for location in locations:
        # Check if any wastelocal dump waste collection data exists for the given location and date
        has__cleaning_Desiltation_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            cleaning_de_siltation_of_drain_sewars_km__isnull=False
        ).exists()

        # Update the status based on the existence of data
        cleangni_siltation_drain_status[location] = '✓' if has__cleaning_Desiltation_data else '✗'


        # Replacement of Manhole Covers
    replacement_manhole_status = {}

    for location in locations:
        # Check if data exists for the given location and date
        has_replacement_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            replacement_of_manhole_covers__isnull=False
        ).exists()

        # Update the status
        replacement_manhole_status[location] = '✓' if has_replacement_data else 'Not a Daily Activity'



    
        # Fumigation Sprays
    fumigation_status = {}

    for location in locations:
        # Check if data exists for the given location and date
        has_fumigation_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            fumigation_sprays_no__isnull=False
        ).exists()

        # Update the status
        fumigation_status[location] = '✓' if has_fumigation_data else 'Not a Daily Activity'



        # IR Sprays
    ir_status = {}

    for location in locations:
        # Check if data exists for the given location and date
        has_ir_data = Sanitation.objects.filter(
            location__location_name=location,
            date=report_date,
            ir_spray_no__isnull=False
        ).exists()

        # Update the status
        ir_status[location] = '✓' if has_ir_data else 'Not a Daily Activity'


     
    # Initialize a variable to track the most recent date overall
    latest_date = None

    # Iterate over each location to fetch the latest data entry
    for location in locations:
        # Fetch the most recent entry for each location
        latest_entry = Revenue.objects.filter(location__location_name=location).order_by('-date').first()
        
        # Check if data exists for the location
        if latest_entry and latest_entry.date:
            # Update the overall latest date if this one is newer
            if not latest_date or latest_entry.date > latest_date:
                latest_date = latest_entry.date

    # If no data exists for any location, we can show the last inserted date from any location
    latest_revenue_date_text = latest_date.strftime("%d/%m/%Y") if latest_date else "No Data"


 # Get today's date
    today = timezone.now().date()

    # Count how many entries were created today in PostAttendance
    today_entries_count = PostAttendance.objects.filter(created_at__date=today).count()

    # Prepare the dynamic entry text for Head Office
    head_office_entry_text = f"Head Office Completed {today_entries_count} Entries"




    











# Prepare the data for rendering




    # Prepare the data for rendering
    data = {
        'rows': [
            # Employee Status
            {
                'sr': '0',
                'module_name': 'Employee Status',
                'zone_a': '✓' if present_employee_data['Zone A']+ leave_employee_data['Zone A'] + absent_employee_data['Zone A'] == total_employee_data['Zone A'] else '✗',
                'zone_b': '✓' if present_employee_data['Zone B']+ leave_employee_data['Zone B'] + absent_employee_data['Zone B'] == total_employee_data['Zone B'] else '✗',
                'zone_c': '✓' if present_employee_data['Zone C']+ leave_employee_data['Zone C'] + absent_employee_data['Zone C'] == total_employee_data['Zone C'] else '✗',
                'zone_d': '✓' if present_employee_data['Zone D']+ leave_employee_data['Zone D'] + absent_employee_data['Zone D'] == total_employee_data['Zone D'] else '✗',
                'zone_e': '✓' if present_employee_data['Zone E']+ leave_employee_data['Zone E'] + absent_employee_data['Zone E'] == total_employee_data['Zone E'] else '✗',
                'head_office': '✓' if present_employee_data['Headoffice']+ leave_employee_data['Headoffice'] + absent_employee_data['Headoffice'] == total_employee_data['Headoffice'] else '✗',
            },
            # Total Employee
            {
                'sr': '1',
                'module_name': 'Total Employee',
                    'zone_a': f"{present_employee_data['Zone A'] + leave_employee_data['Zone A'] + absent_employee_data['Zone A']}/{total_employee_data['Zone A']}",
                    'zone_b': f"{present_employee_data['Zone B'] + leave_employee_data['Zone B'] + absent_employee_data['Zone B']}/{total_employee_data['Zone B']}",
                    'zone_c': f"{present_employee_data['Zone C'] + leave_employee_data['Zone C'] + absent_employee_data['Zone C']}/{total_employee_data['Zone C']}",
                    'zone_d': f"{present_employee_data['Zone D'] + leave_employee_data['Zone D'] + absent_employee_data['Zone D']}/{total_employee_data['Zone D']}",
                    'zone_e': f"{present_employee_data['Zone E'] + leave_employee_data['Zone E'] + absent_employee_data['Zone E']}/{total_employee_data['Zone E']}",
                    'head_office': f"{present_employee_data['Headoffice'] + leave_employee_data['Headoffice'] + absent_employee_data['Headoffice']}/{total_employee_data['Headoffice']}",
            },
            # Vehicle Status
            {
                'sr': '2',
                'module_name': 'Vehicle Status',
                'zone_a': '✓' if functional_vehicle_data['Zone A']+ non_functional_vehicle_data['Zone A'] == total_vehicle_data['Zone A'] else '✗',
                'zone_b': '✓' if functional_vehicle_data['Zone B']+ non_functional_vehicle_data['Zone B'] == total_vehicle_data['Zone B'] else '✗',
                'zone_c': '✓' if functional_vehicle_data['Zone C']+ non_functional_vehicle_data['Zone C'] == total_vehicle_data['Zone C'] else '✗',
                'zone_d': '✓' if functional_vehicle_data['Zone D']+ non_functional_vehicle_data['Zone D'] == total_vehicle_data['Zone D'] else '✗',
                'zone_e': '✓' if functional_vehicle_data['Zone E']+ non_functional_vehicle_data['Zone E'] == total_vehicle_data['Zone E'] else '✗',
                'head_office': '✓' if functional_vehicle_data['Headoffice']+ non_functional_vehicle_data['Headoffice'] == total_vehicle_data['Headoffice'] else '✗',
            },
            # Total Vehicle
            {
                'sr': '3',
                'module_name': 'Total Vehicle',
                 'zone_a': f"{functional_vehicle_data['Zone A'] + non_functional_vehicle_data['Zone A']}/{total_vehicle_data['Zone A']}",
                    'zone_b': f"{functional_vehicle_data['Zone B'] + non_functional_vehicle_data['Zone B']}/{total_vehicle_data['Zone B']}",
                    'zone_c': f"{functional_vehicle_data['Zone C'] + non_functional_vehicle_data['Zone C']}/{total_vehicle_data['Zone C']}",
                    'zone_d': f"{functional_vehicle_data['Zone D'] + non_functional_vehicle_data['Zone D']}/{total_vehicle_data['Zone D']}",
                    'zone_e': f"{functional_vehicle_data['Zone E'] + non_functional_vehicle_data['Zone E']}/{total_vehicle_data['Zone E']}",
                    'head_office': f"{functional_vehicle_data['Headoffice'] + non_functional_vehicle_data['Headoffice']}/{total_vehicle_data['Headoffice']}",
            },
             {
                'sr': '4',
                'module_name': 'Field Visit Status',
                'zone_a': field_visit_data['Zone A'],
                'zone_b': field_visit_data['Zone B'],
                'zone_c': field_visit_data['Zone C'],
                'zone_d': field_visit_data['Zone D'],
                'zone_e': field_visit_data['Zone E'],
                'head_office': field_visit_data['Headoffice'],
            },
            # Tubewell Status
            {
                'sr': '5',
                'module_name': 'Total Tubewell',
                'zone_a': f"{functional_tubewell_data['Zone A']}/{total_tubewell_data['Zone A']}",
                'zone_b': f"{functional_tubewell_data['Zone B']}/{total_tubewell_data['Zone B']}",
                'zone_c': f"{functional_tubewell_data['Zone C']}/{total_tubewell_data['Zone C']}",
                'zone_d': f"{functional_tubewell_data['Zone D']}/{total_tubewell_data['Zone D']}",
                'zone_e': f"{functional_tubewell_data['Zone E']}/{total_tubewell_data['Zone E']}",
                'head_office': f"{functional_tubewell_data['Headoffice']}/{total_tubewell_data['Headoffice']}",
            },
            # Filter Status
            {
                'sr': '6',
                'module_name': 'Total Filter',
                'zone_a': f"{functional_filter_data['Zone A']}/{total_filter_data['Zone A']}",
                'zone_b': f"{functional_filter_data['Zone B']}/{total_filter_data['Zone B']}",
                'zone_c': f"{functional_filter_data['Zone C']}/{total_filter_data['Zone C']}",
                'zone_d': f"{functional_filter_data['Zone D']}/{total_filter_data['Zone D']}",
                'zone_e': f"{functional_filter_data['Zone E']}/{total_filter_data['Zone E']}",
                'head_office': f"{functional_filter_data['Headoffice']}/{total_filter_data['Headoffice']}",
            },
            {
                'sr': '7',
                'module_name': 'Water Supply Status',
                'zone_a': water_supply_status['Zone A'],
                'zone_b': water_supply_status['Zone B'],
                'zone_c': water_supply_status['Zone C'],
                'zone_d': water_supply_status['Zone D'],
                'zone_e': water_supply_status['Zone E'],
                'head_office': water_supply_status['Headoffice'],
            },
            {
                 'sr': '8',
            'module_name': 'Complaints Status',
            'zone_a': complaints_status['Zone A'],
            'zone_b': complaints_status['Zone B'],
            'zone_c': complaints_status['Zone C'],
            'zone_d': complaints_status['Zone D'],
            'zone_e': complaints_status['Zone E'],
            'head_office': complaints_status['Headoffice'],
            },
            {
                 'sr': '9',
            'module_name': 'CLC Status',
            'zone_a': clc_status['Zone A'],
            'zone_b': clc_status['Zone B'],
            'zone_c': clc_status['Zone C'],
            'zone_d': clc_status['Zone D'],
            'zone_e': clc_status['Zone E'],
            'head_office': clc_status['Headoffice'],
            },
             # Container Status
        {
            'sr': '10',
            'module_name': 'Container Status',
            'zone_a': f"{total_container_data['Zone A']}",
            'zone_b': f"{total_container_data['Zone B']}",
            'zone_c': f"{total_container_data['Zone C']}",
            'zone_d': f"{total_container_data['Zone D']}",
            'zone_e': f"{total_container_data['Zone E']}",
            'head_office': f"{total_container_data['Headoffice']}",
        },
        # Moqa Status
        {
            'sr': '11',
            'module_name': 'Moqa Status',
            'zone_a': f"{total_moqas_data['Zone A']}",
            'zone_b': f"{total_moqas_data['Zone B']}",
            'zone_c': f"{total_moqas_data['Zone C']}",
            'zone_d': f"{total_moqas_data['Zone D']}",
            'zone_e': f"{total_moqas_data['Zone E']}",
            'head_office': f"{total_moqas_data['Headoffice']}",
        },
          {
            'sr': '12',
            'module_name': 'Sanitation Status',
            'zone_a': stanitation_status['Zone A'],
            'zone_b': stanitation_status['Zone B'],
            'zone_c': stanitation_status['Zone C'],
            'zone_d': stanitation_status['Zone D'],
            'zone_e': stanitation_status['Zone E'],
            'head_office': stanitation_status['Headoffice'],
        },
        {
            'sr': '13',
            'module_name': 'Prime  Status',
            'zone_a': primary_waste_status['Zone A'],
            'zone_b': primary_waste_status['Zone B'],
            'zone_c': primary_waste_status['Zone C'],
            'zone_d': primary_waste_status['Zone D'],
            'zone_e': primary_waste_status['Zone E'],
            'head_office': primary_waste_status['Headoffice'],
        },
         {
            'sr': '14',
            'module_name': 'Waste Local Status ',
            'zone_a': waste_local_status['Zone A'],
            'zone_b': waste_local_status['Zone B'],
            'zone_c': waste_local_status['Zone C'],
            'zone_d': waste_local_status['Zone D'],
            'zone_e': waste_local_status['Zone E'],
            'head_office': waste_local_status['Headoffice'],
        },
         {
            'sr': '15',
            'module_name': 'Waste Locally Dumped lfs',
            'zone_a': waste_dump_lfs_status['Zone A'],
            'zone_b': waste_dump_lfs_status['Zone B'],
            'zone_c': waste_dump_lfs_status['Zone C'],
            'zone_d': waste_dump_lfs_status['Zone D'],
            'zone_e': waste_dump_lfs_status['Zone E'],
            'head_office': waste_dump_lfs_status['Headoffice'],
        },
        
         {
            'sr': '16',
            'module_name': 'Door to Door Collection',
            'zone_a': door_to_status['Zone A'],
            'zone_b': door_to_status['Zone B'],
            'zone_c': door_to_status['Zone C'],
            'zone_d': door_to_status['Zone D'],
            'zone_e': door_to_status['Zone E'],
            'head_office': door_to_status['Headoffice'],
        },
         {
            'sr': '17',
            'module_name': 'Local Dumping Trips',
            'zone_a': local_demping_status['Zone A'],
            'zone_b': local_demping_status['Zone B'],
            'zone_c': local_demping_status['Zone C'],
            'zone_d': local_demping_status['Zone D'],
            'zone_e': local_demping_status['Zone E'],
            'head_office': local_demping_status['Headoffice'],
        },
         {
            'sr': '18',
            'module_name': 'LFS Trips',
            'zone_a': lfts_trips_status['Zone A'],
            'zone_b': lfts_trips_status['Zone B'],
            'zone_c': lfts_trips_status['Zone C'],
            'zone_d': lfts_trips_status['Zone D'],
            'zone_e': lfts_trips_status['Zone E'],
            'head_office': lfts_trips_status['Headoffice'],
        },
         {
            'sr': '19',
            'module_name': 'Cleaning De-siltation of Manhole',
            'zone_a': cleaning_siltation_Manhole_status['Zone A'],
            'zone_b': cleaning_siltation_Manhole_status['Zone B'],
            'zone_c': cleaning_siltation_Manhole_status['Zone C'],
            'zone_d': cleaning_siltation_Manhole_status['Zone D'],
            'zone_e': cleaning_siltation_Manhole_status['Zone E'],
            'head_office': cleaning_siltation_Manhole_status['Headoffice'],
        },
         {
            'sr': '20',
            'module_name': 'Cleaning De-siltation of Drain Sewers (Km)',
            'zone_a': cleangni_siltation_drain_status['Zone A'],
            'zone_b': cleangni_siltation_drain_status['Zone B'],
            'zone_c': cleangni_siltation_drain_status['Zone C'],
            'zone_d': cleangni_siltation_drain_status['Zone D'],
            'zone_e': cleangni_siltation_drain_status['Zone E'],
            'head_office': cleangni_siltation_drain_status['Headoffice'],
        },
         {
            'sr': '21',
            'module_name': 'Replacement of Manhole Covers',
            'zone_a': replacement_manhole_status.get('Zone A', 'Not a Daily Activity'),
            'zone_b': replacement_manhole_status.get('Zone B', 'Not a Daily Activity'),
            'zone_c': replacement_manhole_status.get('Zone C', 'Not a Daily Activity'),
            'zone_d': replacement_manhole_status.get('Zone D', 'Not a Daily Activity'),
            'zone_e': replacement_manhole_status.get('Zone E', 'Not a Daily Activity'),
            'head_office': replacement_manhole_status.get('Headoffice', 'Not a Daily Activity'),
        },
        {
            'sr': '22',
            'module_name': 'Fumigation Sprays',
           'zone_a': fumigation_status.get('Zone A', 'Not a Daily Activity'),
            'zone_b': fumigation_status.get('Zone B', 'Not a Daily Activity'),
            'zone_c': fumigation_status.get('Zone C', 'Not a Daily Activity'),
            'zone_d': fumigation_status.get('Zone D', 'Not a Daily Activity'),
            'zone_e': fumigation_status.get('Zone E', 'Not a Daily Activity'),
            'head_office': fumigation_status.get('Headoffice', 'Not a Daily Activity'),
        },
         {
            'sr': '23',
            'module_name': 'IR Sprays',
            'zone_a': ir_status.get('Zone A', 'Not a Daily Activity'),
            'zone_b': ir_status.get('Zone B', 'Not a Daily Activity'),
            'zone_c': ir_status.get('Zone C', 'Not a Daily Activity'),
            'zone_d': ir_status.get('Zone D', 'Not a Daily Activity'),
            'zone_e': ir_status.get('Zone E', 'Not a Daily Activity'),
            'head_office': ir_status.get('Headoffice', 'Not a Daily Activity'),
        },
        {

            'sr': '24',
            'module_name': 'Revenue Status',
            'headoffice': f"Data Enter Till {latest_revenue_date_text}",
        },
        {
             'sr': '25',
        'module_name': 'Media ',
        'head_office_entry_text': head_office_entry_text,
        },
           
        ],
        'report_date': report_date,
    }
    print(f"Head Office Entry Text: {head_office_entry_text}")

    return render(request, 'zreport.html', data)    




    from django.shortcuts import render
from django.db.models import Sum
from .models import Sanitation, Location
from datetime import datetime





@login_required
@view_permission_required('sanitation_data')
def sanitation_data(request):
    user = request.user

    # --- Date filters ---
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    location_id = request.GET.get('location')

    today = date.today()
    if not from_date_str:
        from_date = today.replace(day=1)
        from_date_str = from_date.strftime('%Y-%m-%d')
    else:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()

    if not to_date_str:
        to_date = today
        to_date_str = to_date.strftime('%Y-%m-%d')
    else:
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()

    # --- Queryset ---
    queryset = Sanitation.objects.filter(date__gte=from_date, date__lte=to_date)

    if not user.is_superuser:
        permitted_locations = LocationPermission.objects.filter(user=user).values_list('locations', flat=True)
        queryset = queryset.filter(location__id__in=permitted_locations)

    if location_id:
        queryset = queryset.filter(location__id=location_id)

    # --- Zone-wise aggregation (ordered by location name) ---
    zone_data = queryset.values('location__location_name').annotate(
        total_waste_locally_dumped_tons=Sum('waste_locally_dumped_tons'),
        total_waste_dumped_at_lfs_tons=Sum('waste_dumped_at_lfs_tons'),
        total_primary_waste_collection_tons=Sum('primary_waste_collection_tons'),
        total_primary_vehicle_trips=Sum('primary_vehicle_trips'),
        total_rate_killing_no=Sum('rate_killing_no'),
        total_dog_catching_no=Sum('dog_catching_no'),
        total_lfs_trips_no=Sum('lfs_trips_no'),
        total_local_dumping_trips_no=Sum('local_dumping_trips_no'),
        total_door_to_door_solid_waste_collection_no=Sum('door_to_door_solid_waste_collection_no'),
        total_replacement_of_manhole_covers=Sum('replacement_of_manhole_covers'),
        total_cleaning_de_siltation_of_manholes=Sum('cleaning_de_siltation_of_manholes'),
        total_cleaning_de_siltation_of_drain_sewars_km=Sum('cleaning_de_siltation_of_drain_sewars_km'),
        total_fumigation_sprays_no=Sum('fumigation_sprays_no'),
        total_ir_spray_no=Sum('ir_spray_no'),
    ).order_by('location__location_name')  # ✅ Add ordering here

    # --- Grand total across all zones ---
    grand_total = queryset.aggregate(
        total_waste_locally_dumped_tons=Sum('waste_locally_dumped_tons'),
        total_waste_dumped_at_lfs_tons=Sum('waste_dumped_at_lfs_tons'),
        total_primary_waste_collection_tons=Sum('primary_waste_collection_tons'),
        total_primary_vehicle_trips=Sum('primary_vehicle_trips'),
        total_rate_killing_no=Sum('rate_killing_no'),
        total_dog_catching_no=Sum('dog_catching_no'),
        total_lfs_trips_no=Sum('lfs_trips_no'),
        total_local_dumping_trips_no=Sum('local_dumping_trips_no'),
        total_door_to_door_solid_waste_collection_no=Sum('door_to_door_solid_waste_collection_no'),
        total_replacement_of_manhole_covers=Sum('replacement_of_manhole_covers'),
        total_cleaning_de_siltation_of_manholes=Sum('cleaning_de_siltation_of_manholes'),
        total_cleaning_de_siltation_of_drain_sewars_km=Sum('cleaning_de_siltation_of_drain_sewars_km'),
        total_fumigation_sprays_no=Sum('fumigation_sprays_no'),
        total_ir_spray_no=Sum('ir_spray_no'),
    )

    locations = Location.objects.all()
    selected_location = Location.objects.filter(id=location_id).first() if location_id else None

    return render(request, 'sanitation_data.html', {
        'zone_data': zone_data,
        'grand_total': grand_total,
        'from_date': from_date_str,
        'to_date': to_date_str,
        'locations': locations,
        'selected_location': selected_location,
    })



from django.shortcuts import render
from .models import Document, ADP  # Assuming you have a Document model

@login_required
@view_permission_required('document_list')
def document_list(request):
    # Query all documents from the database
    documents = Document.objects.all()
    
    # Render the template and pass the documents to the context
    return render(request, 'document_list.html', {'documents': documents})

@login_required
@view_permission_required('adp_list')
def adp_list(request):
    # Query all documents from the database
    documents = ADP.objects.all()
    
    # Render the template and pass the documents to the context
    return render(request, 'adp_list.html', {'documents': documents})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum
from .models import Fuel, Location, LocationPermission
from .forms import FuelForm
from .decorators import view_permission_required

@login_required
@view_permission_required('daily_fuel_report')
def daily_fuel_report(request):
    # 🔹 Fetch locations the user has access to
    if request.user.is_superuser:
        locations = Location.objects.exclude(location_name="Headoffice")
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = user_permissions.values_list('locations__id', flat=True)
        locations = Location.objects.filter(id__in=location_ids).exclude(location_name="Headoffice")

    # 🔹 Sort locations alphabetically
    locations = locations.order_by('location_name')

    # 🔹 Initialize form and limit location field choices
    form = FuelForm(request.POST or None)
    form.fields['location'].queryset = locations  # Apply location permission to form

    # 🔹 Handle date filtering
    report_date = request.GET.get('date', timezone.now().date())

    total_data = []
    totals = {
        'lfs_trips_no': 0,
        'primary_trips': 0,
        'fuel_top_up_liters': 0,
    }

    # 🔹 Retrieve fuel data for each location
    for location in locations:
        fuel_data = Fuel.objects.filter(date=report_date, location=location)
        location_totals = {
            'location': location,
            'lfs_trips_no': fuel_data.aggregate(Sum('lfs_trips_no'))['lfs_trips_no__sum'] or 0,
            'primary_trips': fuel_data.aggregate(Sum('primary_trips'))['primary_trips__sum'] or 0,
            'fuel_top_up_liters': fuel_data.aggregate(Sum('fuel_top_up_liters'))['fuel_top_up_liters__sum'] or 0,
        }

        # Add to totals
        for key in totals:
            totals[key] += location_totals[key]

        total_data.append(location_totals)

    # 🔹 Handle form submission (Add/Update Fuel Data)
    if request.method == 'POST' and form.is_valid():
        location = form.cleaned_data['location']
        fuel_date = form.cleaned_data['date']

        # Check location permission
        if request.user.is_superuser or location in locations:
            existing_entry = Fuel.objects.filter(date=fuel_date, location=location).first()

            if existing_entry:
                # Update existing entry
                for field, value in form.cleaned_data.items():
                    setattr(existing_entry, field, value)
                existing_entry.save()
            else:
                # Create new entry
                form.save()

            return redirect('daily_fuel_report')
        else:
            form.add_error('location', "You do not have permission to add or update data for this location.")

    context = {
        'total_data': total_data,
        'form': form,
        'report_date': report_date,
        'totals': totals,
    }
    return render(request, 'fuel_report.html', context)
    

@login_required
@view_permission_required('department_attendance_report')
def department_attendance_report(request):
    # Get user's allowed locations
    if request.user.is_superuser:
        locations = Location.objects.all()
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user, can_view=True)
        locations = Location.objects.filter(id__in=user_permissions.values_list('locations', flat=True))
    
    ucs = UC.objects.all()
    departments = Employee.objects.values_list('department', flat=True).distinct()
    
    # Get date range
    from_date_str = request.GET.get('from_date', str(datetime.today().date()))
    to_date_str = request.GET.get('to_date', str(datetime.today().date()))
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    
    # Get department-wise attendance summary
    department_summary = EmployeeAttendance.objects.filter(
        attendance_date__range=[from_date, to_date]
    ).values('employee_name__department').annotate(
        total_present=Count('id', filter=Q(present=True)),
        total_absent=Count('id', filter=Q(absent=True)),
        total_leave=Count('id', filter=Q(leave=True))
    )
    
    # Calculate overall totals
    total_present = sum(record['total_present'] for record in department_summary)
    total_absent = sum(record['total_absent'] for record in department_summary)
    total_leave = sum(record['total_leave'] for record in department_summary)
    
    context = {
        'department_summary': department_summary,
        'from_date': from_date,
        'to_date': to_date,
        'departments': departments,
        'locations': locations,
        'ucs': ucs,
        'total_present': total_present,
        'total_absent': total_absent,
        'total_leave': total_leave,
    }
    return render(request, 'department_attendance_report.html', context)




from django.shortcuts import render
from .models import VehiclePE, Location
from django.db.models import Sum
from datetime import datetime

@login_required
def distance_and_fuel_report(request):
    # Get the filter parameters from the GET request
    location_filter = request.GET.get('location', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Build the query for vehicle performance data
    query = VehiclePE.objects.values(
        'vehicle_name__vehicle_id', 
        'vehicle_name__vehicle_name', 
        'location__location_name'  # Assuming the Location model has a field 'location_name'
    ) \
    .annotate(
        total_km=Sum('running_km'),
        total_fuel=Sum('fuel_issued')
    )

    # Apply the location filter if specified
    if location_filter:
        query = query.filter(location__location_name=location_filter)

    # Apply the date filters if specified
    if from_date:
        query = query.filter(attendance_date__gte=datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        query = query.filter(attendance_date__lte=datetime.strptime(to_date, '%Y-%m-%d'))

    # Order by vehicle ID
    query = query.order_by('vehicle_name__vehicle_id')

    # Fetch the filtered data
    report_data = query

    # Calculate the total kilometers and fuel issued for all data
    total_km = report_data.aggregate(Sum('total_km'))['total_km__sum'] or 0
    total_fuel = report_data.aggregate(Sum('total_fuel'))['total_fuel__sum'] or 0

    # Calculate category-wise totals by zone with date filters applied
    zone_totals = VehiclePE.objects.values('location__location_name') \
        .annotate(
            total_zone_km=Sum('running_km'),
            total_zone_fuel=Sum('fuel_issued')
        )

    # Apply the location filter for zone totals
    if location_filter:
        zone_totals = zone_totals.filter(location__location_name=location_filter)

    # Apply the date filters for zone totals
    if from_date:
        zone_totals = zone_totals.filter(attendance_date__gte=datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        zone_totals = zone_totals.filter(attendance_date__lte=datetime.strptime(to_date, '%Y-%m-%d'))

    # Order the zone totals by location (zone)
    zone_totals = zone_totals.order_by('location__location_name')

    # Get the list of available locations for the filter dropdown
    locations = Location.objects.all()

    return render(request, 'distance_and_fuel_report.html', {
        'report_data': report_data,
        'locations': locations,
        'selected_location': location_filter,
        'selected_from_date': from_date,
        'selected_to_date': to_date,
        'total_km': total_km,
        'total_fuel': total_fuel,
        'zone_totals': zone_totals,
    })




from django.shortcuts import render
from .models import TubeWell, Location, UC
from datetime import date

from django.shortcuts import render
from .models import TubeWell, Location, UC

from django.db.models import OuterRef, Subquery

from django.utils.timezone import now
from django.db.models import OuterRef, Subquery
from datetime import datetime

from datetime import datetime
from django.utils.timezone import now
from django.db.models import OuterRef, Subquery

from django.utils.timezone import now
from datetime import datetime
from django.db.models import Subquery, OuterRef

import os
import zipfile
from django.core.files.base import ContentFile
from django.utils.text import slugify

@login_required
def map_all_tubewells(request):
    location_id = request.GET.get('location_id')
    uc_id = request.GET.get('uc_id')
    tubewell_id = request.GET.get('tubewell_id')
    scada = request.GET.get('scada')
    flow_meter = request.GET.get('flow_meter')
    attendance_date = request.GET.get('attendance_date')

    tubewells = TubeWell.objects.all()

    # Only include specific tubewell IDs
    # allowed_tubewell_ids = [
    #     'E-23-201', 'E-23-225', 'E-23-236', 'E-23-234', 'E-23-245',
    #     'E-23-247', 'E-23-252', 'E-23-255', 'E-24-266', 'E-25-279',
    #     'E-26-284', 'E-26-286', 'E-26-290', 'E-26-291', 'E-27-355',
    #     'D-38-6', 'A-1-7', 'B-15-149'
    # ]
    # tubewells = TubeWell.objects.filter(tubewell_id__in=allowed_tubewell_ids)

    total_tubewells_all = tubewells.count()

    # === Filters ===
    if location_id:
        tubewells = tubewells.filter(location_id=location_id)
    if uc_id:
        tubewells = tubewells.filter(uc_id=uc_id)
    if tubewell_id:
        tubewells = tubewells.filter(tubewell_id__icontains=tubewell_id)
    if scada in ['Yes', 'No']:
        tubewells = tubewells.filter(scada=scada)
    if flow_meter in ['Yes', 'No']:
        tubewells = tubewells.filter(flow_meter=flow_meter)

    # === Attendance Date ===
    if attendance_date:
        try:
            selected_date = datetime.strptime(attendance_date, "%Y-%m-%d").date()
        except ValueError:
            selected_date = now().date()
    else:
        selected_date = now().date()

    # === Attendance Subquery ===
    attendance_qs = TubeWellAttendance.objects.filter(
        tubewell=OuterRef('pk'),
        attendance_date=selected_date
    )

    # === Annotate TubeWell queryset ===
    tubewells = tubewells.annotate(
        latest_run_hour=Subquery(attendance_qs.values('run_hour')[:1]),
        latest_electricity=Subquery(attendance_qs.values('electricity_consume')[:1]),
        latest_water=Subquery(attendance_qs.values('water_produce')[:1]),
        latest_remarks=Subquery(attendance_qs.values('remarks')[:1]),
        latest_date=Subquery(attendance_qs.values('attendance_date')[:1]),
        latest_functional=Subquery(attendance_qs.values('functional')[:1]),
        latest_non_functional=Subquery(attendance_qs.values('non_functional')[:1]),
        latest_non_operational=Subquery(attendance_qs.values('non_operational')[:1]),
    )

    # === Attach full water depth history ===
    depth_map = defaultdict(list)
    depth_entries = TubeWellwaterdepth.objects.select_related('tubewell').order_by('tubewell_id', '-water_table_measurment_date')

    for depth in depth_entries:
        depth_map[depth.tubewell_id].append({
            'depth': depth.water_table_depth,
            'date': depth.water_table_measurment_date
        })

    for t in tubewells:
        t.depth_history = depth_map.get(t.id, [])

    total_tubewells = tubewells.count()

    # === KMZ to KML Conversion ===
    kmz_files = KMZUpload.objects.all().order_by('-uploaded_at')
    for kmz in kmz_files:
        if kmz.file.name.endswith('.kmz') and not kmz.kml_file:
            try:
                with zipfile.ZipFile(kmz.file.path, 'r') as zip_ref:
                    for name in zip_ref.namelist():
                        if name.endswith('.kml'):
                            kml_data = zip_ref.read(name)
                            base_name = os.path.splitext(os.path.basename(kmz.file.name))[0]
                            kml_filename = f"{slugify(base_name)}.kml"
                            kmz.kml_file.save(kml_filename, ContentFile(kml_data), save=True)
                            break
            except Exception as e:
                print(f"Failed to extract KML from {kmz.file.name}: {e}")

    # === Context ===
    context = {
        'tubewells': tubewells,
        'total_tubewells': total_tubewells,
        'total_tubewells_all': total_tubewells_all,
        'locations': Location.objects.all(),
        'ucs': UC.objects.all(),
        'kmz_files': kmz_files,
        'request': request,
    }

    return render(request, 'map_all_tubewells.html', context)


# API CODE

from rest_framework import viewsets
from .models import Employee, EmployeeAttendance
from .serializers import EmployeeSerializer, EmployeeAttendanceSerializer

class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class EmployeeAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmployeeAttendance.objects.all()
    serializer_class = EmployeeAttendanceSerializer



from datetime import date
from django.db.models.functions import TruncMonth

from django.db.models.functions import TruncMonth  # if not already imported

from datetime import date
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from .models import Complaint  # adjust import if needed
from django.db.models import Min, Max, F, ExpressionWrapper, DurationField

from django.db.models import Count, Q, F, FloatField, ExpressionWrapper, Avg, DurationField
from django.db.models.functions import Coalesce
from django.utils.timezone import now

from datetime import date
from django.db.models import Count, Q, F, FloatField, DurationField, ExpressionWrapper, Avg, Min
from django.db.models.functions import Coalesce, TruncMonth
from django.db.models import OuterRef, Subquery, DateTimeField
from django.utils.timezone import now

from datetime import date
from django.db.models import (
    Count, Q, F, Avg, DurationField, ExpressionWrapper,
    FloatField, DateTimeField, OuterRef, Subquery
)
from django.db.models.functions import TruncMonth, Coalesce
from django.shortcuts import render
from django.utils.timezone import now

from datetime import date
from django.db.models import (
    Count, Q, F, FloatField, DateTimeField, DurationField, Avg,
    ExpressionWrapper, OuterRef, Subquery
)
from django.db.models.functions import TruncMonth, Coalesce


from datetime import date
from django.db.models import Count, Q, Avg, F, ExpressionWrapper, DurationField, DateTimeField, FloatField
from django.db.models.functions import TruncMonth, Coalesce
from django.db.models import OuterRef, Subquery


@login_required
def complaint_dashboard(request):
    today = date.today()

    # === Get Filters ===
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    location_id = request.GET.get('location')

    from_date = from_date if from_date and from_date.lower() != "none" else None
    to_date = to_date if to_date and to_date.lower() != "none" else None
    location_id = location_id if location_id and location_id.lower() != "none" else None

    # === Base QuerySet ===
    complaints = Complaint.objects.exclude(location__location_name__iexact='Headoffice')
    if from_date:
        complaints = complaints.filter(date__gte=from_date)
    if to_date:
        complaints = complaints.filter(date__lte=to_date)
    if location_id:
        complaints = complaints.filter(location_id=location_id)

    total = complaints.count()
    resolved = complaints.filter(status='resolved').count()
    pending = complaints.filter(status='pending').count()
    current_month_total = complaints.filter(date__year=today.year, date__month=today.month).count()

    # ========================= Top Zone / UC / SubType =========================
    current_month_complaints = complaints.filter(date__year=today.year, date__month=today.month)

    # Top Zone
    top_zone = (
        current_month_complaints.values('location__location_name')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )
    top_zone_name = top_zone['location__location_name'] if top_zone else "N/A"
    top_zone_total = top_zone['total'] if top_zone else 0

    # Top UC
    top_uc = (
        current_month_complaints.values('uc__uc_name')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )
    top_uc_name = top_uc['uc__uc_name'] if top_uc else "N/A"
    top_uc_total = top_uc['total'] if top_uc else 0

    # Top SubType
    top_subtype = (
        current_month_complaints.values('SubType__type_name')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )
    top_subtype_name = top_subtype['SubType__type_name'] if top_subtype else "N/A"
    top_subtype_total = top_subtype['total'] if top_subtype else 0
    # =========================================================================

    # === Subquery to get first resolved timestamp ===
    resolved_time_subquery = ComplaintActionLog.objects.filter(
        complaint=OuterRef('pk'),
        action='resolved'
    ).order_by('timestamp').values('timestamp')[:1]

    # Annotate complaints with duration
    complaints_with_duration = complaints.annotate(
        first_resolved=Subquery(resolved_time_subquery, output_field=DateTimeField()),
        duration=ExpressionWrapper(F('first_resolved') - F('created_at'), output_field=DurationField())
    )

    # === Complaint Type Summary (with Resolve Rate & Avg Hours) ===
    type_summary_qs = complaints.values('complaint_type__type_name').annotate(
        total=Count('id'),
        resolved=Count('id', filter=Q(status='resolved')),
        pending=Count('id', filter=Q(status='pending'))
    )

    # Resolve Rate %
    for row in type_summary_qs:
        total_ct = row['total']
        resolved_ct = row['resolved']
        row['resolve_rate'] = round((resolved_ct / total_ct) * 100, 2) if total_ct > 0 else 0

    # Avg Resolution Time per Type
    avg_resolution_by_type = complaints_with_duration.values(
        'complaint_type__type_name'
    ).annotate(
        avg_duration=Avg('duration')
    )
    avg_map = {r['complaint_type__type_name']: r['avg_duration'] for r in avg_resolution_by_type}

    for row in type_summary_qs:
        duration = avg_map.get(row['complaint_type__type_name'])
        row['avg_hours'] = round(duration.total_seconds() / 3600, 2) if duration else None

    type_summary = type_summary_qs

    # === Complaint Source Summary (basic, same as before) ===
    source_summary = complaints.values('complaint_source__source_name').annotate(
        total=Count('id'),
        resolved=Count('id', filter=Q(status='resolved')),
        pending=Count('id', filter=Q(status='pending'))
    )
    source_labels = [item['complaint_source__source_name'] or 'Unknown' for item in source_summary]
    source_totals = [item['total'] for item in source_summary]

    # === Monthly Complaint Trend ===
    current_year = date.today().year
    monthly_data = complaints.filter(date__year=current_year).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(count=Count('id')).order_by('month')

    # === Location-Wise Summary (with Resolve Rate) ===
    location_summary = complaints.values('location__location_name').annotate(
        total=Count('id'),
        resolved=Count('id', filter=Q(status='resolved')),
        pending=Count('id', filter=Q(status='pending')),
    ).annotate(
        resolve_rate=ExpressionWrapper(
            Coalesce(F('resolved') * 100.0 / F('total'), 0.0),
            output_field=FloatField()
        )
    ).order_by('location__location_name')

    # === Average Resolution Time Per Location in HOURS ===
    avg_resolution_by_location = []
    avg_data = complaints_with_duration.values('location__location_name').annotate(
        avg_duration=Avg('duration')
    )
    for row in avg_data:
        location = row['location__location_name']
        duration = row['avg_duration']
        avg_hours = round(duration.total_seconds() / 3600, 2) if duration else None
        avg_resolution_by_location.append({
            'location': location,
            'avg_hours': avg_hours
        })

    # === Overall Avg Resolution Time ===
    durations = [r['duration'] for r in complaints_with_duration.values('duration') if r['duration']]
    avg_resolution_hours = round(
        sum([d.total_seconds() for d in durations]) / 3600 / len(durations),
        2
    ) if durations else 0

    # === Overall Resolve Rate ===
    overall_resolve_rate = round((resolved / total) * 100, 2) if total > 0 else 0

    # === Locations for Dropdown ===
    locations = Location.objects.exclude(location_name__iexact='Headoffice')

    return render(request, 'complaint_dashboard.html', {
        'total': total,
        'resolved': resolved,
        'pending': pending,
        'current_month_total': current_month_total,
        'type_summary': type_summary,
        'source_summary': source_summary,
        'source_labels': source_labels,
        'source_totals': source_totals,
        'monthly_data': monthly_data,
        'location_summary': location_summary,
        'avg_resolution_by_location': avg_resolution_by_location,
        'overall_resolve_rate': overall_resolve_rate,
        'avg_resolution_hours': avg_resolution_hours,
        'locations': locations,
        'selected_location': location_id,
        'from_date': from_date,
        'to_date': to_date,
        # Top Zone / UC / SubType
        'top_zone_name': top_zone_name,
        'top_zone_total': top_zone_total,
        'top_uc_name': top_uc_name,
        'top_uc_total': top_uc_total,
        'top_subtype_name': top_subtype_name,
        'top_subtype_total': top_subtype_total,
    })

from django.shortcuts import render
from .models import Complaint


@login_required
def pending_complaints_list(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    location_id = request.GET.get('location')

    complaints = Complaint.objects.filter(status='pending').exclude(location__location_name__iexact='Headoffice')

    if from_date:
        complaints = complaints.filter(date__gte=from_date)
    if to_date:
        complaints = complaints.filter(date__lte=to_date)
    if location_id and location_id != "":
        complaints = complaints.filter(location_id=location_id)

    locations = Location.objects.exclude(location_name__iexact='Headoffice')

    return render(request, 'pending_complaints_list.html', {
        'complaints': complaints,
        'locations': locations,
        'from_date': from_date,
        'to_date': to_date,
        'selected_location': location_id,
    })

from django.shortcuts import render
from .models import TubeWellwaterdepth

from django.shortcuts import render, get_object_or_404
from .models import TubeWell, TubeWellwaterdepth



@login_required
def water_depth_list(request):
    tubewell_id = request.GET.get('tubewell_id')
    search = request.GET.get('search')

    latest_depth = TubeWellwaterdepth.objects.filter(
        tubewell=OuterRef('pk')
    ).order_by('-water_table_measurment_date')

    tubewells = TubeWell.objects.all().annotate(
        latest_depth_value=Subquery(latest_depth.values('water_table_depth')[:1]),
        latest_depth_date=Subquery(latest_depth.values('water_table_measurment_date')[:1]),
    )

    # 🔎 SEARCH FILTER
    if search:
        tubewells = tubewells.filter(
            Q(tubewell_name__icontains=search) |
            Q(tubewell_id__icontains=search)
        )

    selected_tubewell = None
    history = None
    chart_data = None

    if tubewell_id:
        try:
            selected_tubewell = TubeWell.objects.get(id=tubewell_id)

            history_qs = TubeWellwaterdepth.objects.filter(
                tubewell_id=tubewell_id
            ).order_by('water_table_measurment_date')

            labels = []
            values = []

            for h in history_qs:
                labels.append(str(h.water_table_measurment_date))
                try:
                    values.append(float(h.water_table_depth))
                except:
                    values.append(None)

            chart_data = {
                "labels": labels,
                "values": values
            }

            history = history_qs

        except TubeWell.DoesNotExist:
            selected_tubewell = None

    context = {
        "tubewells": tubewells,
        "all_tubewells": TubeWell.objects.all(),
        "selected_tubewell": selected_tubewell,
        "history": history,
        "chart_data": chart_data,
        "request": request,
    }

    return render(request, "water_depth_list.html", context)


from collections import defaultdict

from django.db.models import Sum, F, FloatField, ExpressionWrapper, Q
from datetime import datetime, timedelta

from django.utils.dateformat import DateFormat
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.utils.dateformat import DateFormat
from django.contrib import messages
from django.shortcuts import render

from django.db.models import Sum
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import render
from .models import Vehicle, VehiclePE, Location, LocationPermission

import json



from .models import Vehicle, VehiclePE, Location, LocationPermission

from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils.dateformat import DateFormat
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Q

from .models import Vehicle, VehiclePE, Location, LocationPermission



@login_required
@view_permission_required('vehicle_pe_monthly_report')
def vehicle_pe_monthly_report(request):
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    end_of_month = today

    vehicles = Vehicle.objects.all()
    STATE_CHOICES = VehiclePE.STATE_CHOICE00

    # === Available months for dropdown ===
    available_months = (
        VehiclePE.objects
        .annotate(month=TruncMonth('attendance_date'))
        .values('month')
        .distinct()
        .order_by('-month')
    )

    month_choices = []
    for item in available_months:
        month_date = item['month']
        if month_date:
            label = DateFormat(month_date).format('F Y')
            value = month_date.strftime('%Y-%m')
            month_choices.append({'label': label, 'value': value})

    # === Apply location permissions ===
    if request.user.is_authenticated:
        permission = LocationPermission.objects.filter(user=request.user, can_view=True).first()
        if permission:
            allowed_locations = permission.locations.all()
            vehicles = vehicles.filter(location__in=allowed_locations)
        else:
            vehicles = Vehicle.objects.none()

    # === Filters ===
    location_filter = request.GET.get('location', '').strip()
    vehicle_type_filter = request.GET.get('vehicle_type', '').strip()
    category_filter = request.GET.get('category', '').strip()
    month = request.GET.get('month')

    if month:
        try:
            month_date = datetime.strptime(month, '%Y-%m')
            start_of_month = month_date.replace(day=1).date()
            if month_date.month == 12:
                end_of_month = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_of_month = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
        except ValueError:
            messages.error(request, "Invalid month format.")

    if location_filter:
        vehicles = vehicles.filter(location__location_name=location_filter)

    if vehicle_type_filter:
        vehicles = vehicles.filter(vehicle_type=vehicle_type_filter)

    if category_filter:
        vehicles = vehicles.filter(category__iexact=category_filter)

    vehicles = vehicles.order_by('location__location_name', 'vehicle_name')
        

    # === Report data ===
    report_data = []
    location_total_trips = {}
    location_total_fuel = {}
    location_total_km = {}
    location_km_per_liter = {}

    for vehicle in vehicles:
        attendances = VehiclePE.objects.filter(
            vehicle_name=vehicle,
            attendance_date__range=(start_of_month, end_of_month)
        )

        total_trips = attendances.aggregate(Sum('vehicle_trips'))['vehicle_trips__sum'] or 0
        total_fuel = attendances.aggregate(Sum('fuel_issued'))['fuel_issued__sum'] or 0

        total_km = 0
        for att in attendances:
            if att.odometer_start is not None and att.odometer_end is not None:
                total_km += att.odometer_end - att.odometer_start
            elif att.manual_running_km:
                total_km += att.manual_running_km

        km_per_liter = round(total_km / total_fuel, 2) if total_fuel > 0 else None
        loc_name = vehicle.location.location_name if vehicle.location else "Unknown"

        location_total_trips[loc_name] = location_total_trips.get(loc_name, 0) + total_trips
        location_total_fuel[loc_name] = location_total_fuel.get(loc_name, 0) + total_fuel
        location_total_km[loc_name] = location_total_km.get(loc_name, 0) + total_km

        report_data.append({
            'vehicle_id': vehicle.vehicle_id,
            'vehicle_name': vehicle.vehicle_name,
            'location': loc_name,
            'vehicle_type': vehicle.vehicle_type,
            'category': vehicle.category or "Uncategorized",
            'total_trips': total_trips,
            'total_fuel': total_fuel,
            'total_km': total_km,
            'km_per_liter': km_per_liter,
        })

    for loc in location_total_km:
        fuel = location_total_fuel.get(loc, 0)
        km = location_total_km.get(loc, 0)
        location_km_per_liter[loc] = round(km / fuel, 2) if fuel > 0 else None

    all_locations = list(
    Location.objects.exclude(location_name="Headoffice")
    .order_by('location_name')
    .values_list('location_name', flat=True)
)
    chart_labels = [loc for loc in all_locations]
    chart_trips = [float(location_total_trips.get(loc, 0)) for loc in chart_labels]
    chart_fuel = [float(location_total_fuel.get(loc, 0)) for loc in chart_labels]
    chart_km = [float(location_total_km.get(loc, 0)) for loc in chart_labels]

    category_summary = defaultdict(lambda: {
        'vehicle_count': 0,
        'location_data': defaultdict(lambda: {'fuel': 0, 'km': 0}),
        'total_fuel': 0,
        'total_km': 0,
    })

    for vehicle in vehicles:
        category = vehicle.category or "Uncategorized"
        location_name = vehicle.location.location_name if vehicle.location else "Unknown"

        attendances = VehiclePE.objects.filter(
            vehicle_name=vehicle,
            attendance_date__range=(start_of_month, end_of_month)
        )

        total_fuel = attendances.aggregate(Sum('fuel_issued'))['fuel_issued__sum'] or 0
        total_km = 0
        for att in attendances:
            if att.odometer_start is not None and att.odometer_end is not None:
                total_km += att.odometer_end - att.odometer_start
            elif att.manual_running_km:
                total_km += att.manual_running_km

        if total_km or total_fuel:
            category_summary[category]['vehicle_count'] += 1
            category_summary[category]['total_fuel'] += total_fuel
            category_summary[category]['total_km'] += total_km
            category_summary[category]['location_data'][location_name]['fuel'] += total_fuel
            category_summary[category]['location_data'][location_name]['km'] += total_km

    category_table = []
    for category, data in category_summary.items():
        row = {
            'category': category,
            'vehicle_count': data['vehicle_count'],
            'overall_km_per_liter': round(data['total_km'] / data['total_fuel'], 2) if data['total_fuel'] > 0 else 'N/A',
            'locations': []
        }

        for loc in all_locations:
            loc_data = data['location_data'].get(loc)
            if loc_data and loc_data['fuel'] > 0:
                km_per_liter = round(loc_data['km'] / loc_data['fuel'], 2)
            else:
                km_per_liter = 'N/A'
            row['locations'].append(km_per_liter)

        category_table.append(row)

    # Get unique categories for the dropdown
    categories = Vehicle.objects.exclude(category__isnull=True).exclude(category__exact="") \
        .values_list('category', flat=True).distinct()

    context = {
        'report_data': report_data,
        'start_date': start_of_month,
        'end_date': end_of_month,
        'locations': Location.objects.exclude(location_name="Headoffice").order_by('location_name'),

        'vehicle_types': STATE_CHOICES,
        'month_choices': month_choices,
        'categories': categories,
        'selected_month': month or today.strftime('%Y-%m'),
        'selected_location': location_filter,
        'selected_vehicle_type': vehicle_type_filter,
        'selected_category': category_filter,
        'location_total_trips': location_total_trips,
        'location_total_fuel': location_total_fuel,
        'location_total_km': location_total_km,
        'location_km_per_liter': location_km_per_liter,
        'chart_labels': json.dumps(chart_labels),
        'chart_trips': json.dumps(chart_trips),
        'chart_fuel': json.dumps(chart_fuel),
        'chart_km': json.dumps(chart_km),
        'category_table': category_table,
    }

    return render(request, 'vehicle_pe_monthly_report.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from .models import TubeWellWaterProduce, TubeWell
from .forms import TubeWellWaterProduceForm
from datetime import date

from django.utils.timezone import now
from .models import TubeWellWaterProduce  

from django.utils.dateformat import DateFormat
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta




@login_required
@view_permission_required('add_water_produce')
def add_water_produce(request):
    user = request.user

    # 🔐 Step 1: Get permitted locations
    if user.is_superuser:
        permitted_locations = Location.objects.all()
    else:
        permitted_locations = Location.objects.filter(
            locationpermission__user=user,
            locationpermission__can_view=True
        ).distinct()

    # 🔐 Step 2: Get permitted tubewells
    permitted_tubewells = TubeWell.objects.filter(location__in=permitted_locations)

    if request.method == 'POST':
        form = TubeWellWaterProduceForm(request.POST)
        form.fields['tubewell'].queryset = permitted_tubewells  

        if form.is_valid():
            tubewell = form.cleaned_data['tubewell']

            # ⛔ Security check
            if not user.is_superuser and tubewell not in permitted_tubewells:
                messages.error(request, "You do not have permission to add data for this tubewell.")
                return redirect('add_water_produce')

            run_hour = float(form.cleaned_data['run_hour'])
            meter_start = float(form.cleaned_data['water_meter_reading_start'])
            meter_end = float(form.cleaned_data['water_meter_reading_end'])
            remarks = form.cleaned_data['remarks']
            produce_date = form.cleaned_data['water_produce_date']

            # ❌ One entry per month per tubewell
            existing_entry = TubeWellWaterProduce.objects.filter(
                tubewell=tubewell,
                water_produce_date__year=produce_date.year,
                water_produce_date__month=produce_date.month,
            ).first()

            if existing_entry:
                messages.error(request, f"An entry already exists for {tubewell} for {produce_date.strftime('%B %Y')}.")
                return redirect('add_water_produce')

          
           # ⭐ Use updated discharge ONLY if discharge date <= production date
            latest_discharge = TubeWelldischarge.objects.filter(
                tubewell=tubewell,
                updated_average_discharge_date__lte=produce_date  # discharge applicable up to this date
            ).order_by('-updated_average_discharge_date').first()

            if latest_discharge and latest_discharge.updated_average_discharge:
                average_discharge = float(latest_discharge.updated_average_discharge)
            else:
                average_discharge = float(tubewell.average_discharge)


            # 🧮 Auto-calculate water produce
            if meter_start == 0 and meter_end == 0:
                water_produce = average_discharge * run_hour
            else:
                water_produce = meter_end - meter_start

            # ✅ Save
            TubeWellWaterProduce.objects.create(
                tubewell=tubewell,
                run_hour=str(run_hour),
                water_produce=str(water_produce),
                remarks=remarks,
                water_meter_reading_start=str(meter_start),
                water_meter_reading_end=str(meter_end),
                water_produce_date=produce_date,
            )

            messages.success(request, "Water production data saved successfully!")
            return redirect('add_water_produce')
    else:
        form = TubeWellWaterProduceForm()
        form.fields['tubewell'].queryset = permitted_tubewells  # ⬅️ Filter dropdown options

    # === Available months for dropdown ===
    available_months = (
        TubeWellWaterProduce.objects
        .annotate(month=TruncMonth('water_produce_date'))
        .values('month')
        .distinct()
        .order_by('-month')
    )

    month_choices = []
    for item in available_months:
        month_date = item['month']
        if month_date:
            label = DateFormat(month_date).format('F Y')
            value = month_date.strftime('%Y-%m')
            month_choices.append({'label': label, 'value': value})

    # 🗓️ Month filtering logic
    selected_month = request.GET.get('month')
    today = now().date()
    if selected_month:
        try:
            selected_date = datetime.strptime(selected_month, '%Y-%m')
            start_of_month = selected_date.replace(day=1)
            next_month = start_of_month + relativedelta(months=1)
            end_of_month = next_month - timedelta(days=1)
        except ValueError:
            start_of_month = today.replace(day=1)
            end_of_month = today
    else:
        start_of_month = today.replace(day=1)
        end_of_month = today

    # 🔎 Filter data by permitted tubewells
    current_month_data = TubeWellWaterProduce.objects.filter(
        water_produce_date__range=(start_of_month, end_of_month),
        tubewell__in=permitted_tubewells
    ).order_by('-water_produce_date')

    return render(request, 'water_produce_form.html', {
        'form': form,
        'current_month_data': current_month_data,
        'month_choices': month_choices,
        'selected_month': selected_month,
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def update_water_produce(request, produce_id):
    user = request.user
    water_produce = get_object_or_404(TubeWellWaterProduce, id=produce_id)
    tubewell = water_produce.tubewell

    # Permissions: Check user can edit this tubewell
    if not user.is_superuser:
        allowed_locations = Location.objects.filter(
            locationpermission__user=user,
            locationpermission__can_view=True
        ).distinct()
        allowed_tubewells = TubeWell.objects.filter(location__in=allowed_locations)
        if tubewell not in allowed_tubewells:
            messages.error(request, "You don't have permission to update this record.")
            return redirect('add_water_produce')

    if request.method == "POST":
        run_hour = float(request.POST.get('run_hour', water_produce.run_hour))
        meter_start = float(request.POST.get('water_meter_reading_start', water_produce.water_meter_reading_start))
        meter_end = float(request.POST.get('water_meter_reading_end', water_produce.water_meter_reading_end))
        remarks = request.POST.get('remarks', water_produce.remarks)
        produce_date_str = request.POST.get('water_produce_date')
        try:
            produce_date = datetime.strptime(produce_date_str, '%Y-%m-%d').date()
        except Exception:
            produce_date = water_produce.water_produce_date

        average_discharge = float(tubewell.average_discharge)

        # Recalculate water produced
        if meter_start == 0 and meter_end == 0:
            water_produce_value = average_discharge * run_hour
        else:
            water_produce_value = meter_end - meter_start

        # Prevent duplicate month entries except this record itself
        existing = TubeWellWaterProduce.objects.filter(
            tubewell=tubewell,
            water_produce_date__year=produce_date.year,
            water_produce_date__month=produce_date.month,
        ).exclude(id=produce_id).first()

        if existing:
            messages.error(request, f"An entry already exists for {tubewell} for {produce_date.strftime('%B %Y')}.")
            return redirect('add_water_produce')

        # Save updates
        water_produce.run_hour = run_hour
        water_produce.water_meter_reading_start = meter_start
        water_produce.water_meter_reading_end = meter_end
        water_produce.water_produce = water_produce_value
        water_produce.remarks = remarks
        water_produce.water_produce_date = produce_date
        water_produce.save()

        messages.success(request, "Water production record updated successfully!")
        return redirect('add_water_produce')

    return redirect('add_water_produce')

    

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from django.utils.dateformat import DateFormat
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .models import TubeWellElectricityUsage
from .forms import TubeWellElectricityUsageForm  
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.utils.dateformat import DateFormat
from django.db.models.functions import TruncMonth
from django.db.models import FloatField
from django.db.models.functions import Cast
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from .models import TubeWell, TubeWellElectricityUsage, Location, LocationPermission
from .forms import TubeWellElectricityUsageForm



@login_required
@view_permission_required('add_electricity_usage')
def add_electricity_usage(request):
    user = request.user

    # 🔐 Get permitted locations
    if user.is_superuser:
        permitted_locations = Location.objects.all()
    else:
        permitted_locations = Location.objects.filter(
            locationpermission__user=user,
            locationpermission__can_view=True
        ).distinct()

    # 🔐 Get permitted tubewells
    permitted_tubewells = TubeWell.objects.filter(location__in=permitted_locations)

    if request.method == 'POST':
        form = TubeWellElectricityUsageForm(request.POST)
        form.fields['tubewell'].queryset = permitted_tubewells  # ⬅️ Filter dropdown options

        if form.is_valid():
            tubewell = form.cleaned_data['tubewell']

            # ⛔ Ensure user can access this tubewell
            if not user.is_superuser and tubewell not in permitted_tubewells:
                messages.error(request, "You do not have permission to add data for this tubewell.")
                return redirect('add_electricity_usage')

            usage_date = form.cleaned_data['usage_date']
            meter_start = form.cleaned_data.get('meter_reading_start') or 0
            meter_end = form.cleaned_data.get('meter_reading_end') or 0
            electricity_manual = form.cleaned_data.get('electricity_consumed') or 0
            remarks = form.cleaned_data.get('remarks', '')

            # 🚫 Prevent future date entries
            today = now().date()
            if usage_date > today:
                messages.error(request, "You cannot enter data for a future date.")
                return redirect('add_electricity_usage')

            # ❌ One entry per tubewell per month
            existing_entry = TubeWellElectricityUsage.objects.filter(
                tubewell=tubewell,
                usage_date__year=usage_date.year,
                usage_date__month=usage_date.month,
            ).first()
            if existing_entry:
                messages.error(request, f"An entry already exists for {tubewell} for {usage_date.strftime('%B %Y')}.")
                return redirect('add_electricity_usage')

            # ⚡ Auto-calculate consumption
            if meter_start > 0 and meter_end > 0 and meter_end >= meter_start:
                electricity_consumed = meter_end - meter_start
            else:
                electricity_consumed = electricity_manual

            # ✅ Save entry
            TubeWellElectricityUsage.objects.create(
                tubewell=tubewell,
                meter_reading_start=meter_start,
                meter_reading_end=meter_end,
                electricity_consumed=electricity_consumed,
                remarks=remarks,
                usage_date=usage_date,
            )

            messages.success(request, "Electricity usage data saved successfully!")
            return redirect('add_electricity_usage')

    else:
        form = TubeWellElectricityUsageForm()
        form.fields['tubewell'].queryset = permitted_tubewells  # ⬅️ Filter dropdown options

        # ✅ Autofill meter start from previous month
        tubewell_id = request.GET.get('tubewell')
        selected_date_str = request.GET.get('date')

        if tubewell_id and selected_date_str:
            try:
                usage_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
                previous_month = usage_date - relativedelta(months=1)

                previous_entry = TubeWellElectricityUsage.objects.filter(
                    tubewell__id=tubewell_id,
                    usage_date__year=previous_month.year,
                    usage_date__month=previous_month.month
                ).first()

                if previous_entry:
                    form.initial['meter_reading_start'] = previous_entry.meter_reading_end
                    form.initial['usage_date'] = usage_date

            except ValueError:
                pass

    # 📅 Month filter dropdown
    available_months = (
        TubeWellElectricityUsage.objects
        .annotate(month=TruncMonth('usage_date'))
        .values('month')
        .distinct()
        .order_by('-month')
    )

    month_choices = []
    for item in available_months:
        month_date = item['month']
        if month_date:
            label = DateFormat(month_date).format('F Y')
            value = month_date.strftime('%Y-%m')
            month_choices.append({'label': label, 'value': value})

    # 🗓️ Filter by selected month
    selected_month = request.GET.get('month')
    today = now().date()
    if selected_month:
        try:
            selected_date = datetime.strptime(selected_month, '%Y-%m')
            start_of_month = selected_date.replace(day=1)
            end_of_month = (start_of_month + relativedelta(months=1)) - timedelta(days=1)
        except ValueError:
            start_of_month = today.replace(day=1)
            end_of_month = today
    else:
        start_of_month = today.replace(day=1)
        end_of_month = today

    # 📊 Limit displayed records to permitted tubewells
    current_month_data = TubeWellElectricityUsage.objects.filter(
        usage_date__range=(start_of_month, end_of_month),
        tubewell__in=permitted_tubewells
    ).order_by('-usage_date')

    return render(request, 'electricity_usage_form.html', {
        'form': form,
        'current_month_data': current_month_data,
        'month_choices': month_choices,
        'selected_month': selected_month,
    })

# API Reading Get Previous
from django.http import JsonResponse
from .models import TubeWellElectricityUsage
from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_previous_reading(request):
    tubewell_id = request.GET.get("tubewell_id")
    usage_date_str = request.GET.get("usage_date")

    if not tubewell_id or not usage_date_str:
        return JsonResponse({"error": "Missing parameters"}, status=400)

    try:
        usage_date = datetime.strptime(usage_date_str, "%Y-%m-%d").date()
        previous_month = usage_date - relativedelta(months=1)

        previous_entry = TubeWellElectricityUsage.objects.filter(
            tubewell_id=tubewell_id,
            usage_date__year=previous_month.year,
            usage_date__month=previous_month.month
        ).order_by('-usage_date').first()

        if previous_entry:
            return JsonResponse({
                "previous_meter_end": float(previous_entry.meter_reading_end),
                "message": "Auto-filled from last month's data"
            })
        else:
            return JsonResponse({"previous_meter_end": None})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# API End Reading Get Previous

from django.shortcuts import render
from django.db.models import Sum
from django.utils.timezone import now
from django.utils.dateformat import DateFormat
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from .models import TubeWell, TubeWellElectricityUsage, TubeWellWaterProduce

from django.shortcuts import render
from django.utils.timezone import now
from django.utils.dateformat import DateFormat
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, FloatField
from django.db.models.functions import TruncMonth, Cast

from .models import TubeWell, TubeWellWaterProduce, TubeWellElectricityUsage


from django.db.models import Sum
from django.db.models.functions import TruncMonth, Cast
from django.db.models import FloatField
from django.utils.timezone import now
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils.dateformat import DateFormat
from django.shortcuts import render



from datetime import datetime, timedelta
from django.utils.timezone import now
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast, TruncMonth
from django.utils.dateformat import DateFormat
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required

@login_required
@view_permission_required('tubewell_monthly_summary')
def tubewell_monthly_summary(request):
    today = now().date()
    selected_month = request.GET.get('month')
    location_id = request.GET.get('location')

    # ---------- Month Range ----------
    if selected_month:
        try:
            selected_date = datetime.strptime(selected_month, '%Y-%m')
            start_of_month = selected_date.replace(day=1)
            end_of_month = (start_of_month + relativedelta(months=1)) - timedelta(days=1)
        except ValueError:
            start_of_month = today.replace(day=1)
            end_of_month = today
    else:
        start_of_month = today.replace(day=1)
        end_of_month = today

    user = request.user

    # ---------- Permitted Locations ----------
    if user.is_superuser:
        permitted_locations = Location.objects.all()
    else:
        permitted_locations = Location.objects.filter(
            locationpermission__user=user,
            locationpermission__can_view=True
        ).distinct()

    # ---------- Tubewells ----------
    tubewells = TubeWell.objects.filter(location__in=permitted_locations)

    if location_id:
        tubewells = tubewells.filter(location_id=location_id)

    report_data = []

    # ---------- Counters for badges ----------
    low_count = 0        # 0 - 0.15
    medium_count = 0     # 0.15 - 0.30
    high_count = 0       # > 0.30
    na_count = 0         # None / N/A

    for tubewell in tubewells:
        electricity_data = TubeWellElectricityUsage.objects.filter(
            tubewell=tubewell,
            usage_date__range=(start_of_month, end_of_month)
        ).aggregate(total_kwh=Sum('electricity_consumed'))

        water_data = TubeWellWaterProduce.objects.filter(
            tubewell=tubewell,
            water_produce_date__range=(start_of_month, end_of_month)
        ).aggregate(total_cum=Sum(Cast('water_produce', FloatField())))

        total_kwh = electricity_data['total_kwh'] or 0
        total_cum = water_data['total_cum'] or 0

        try:
            ratio = round(float(total_kwh) / float(total_cum), 2) if total_kwh and total_cum else None
        except (ZeroDivisionError, TypeError, ValueError):
            ratio = None

        # ---------- Count classification ----------
        if ratio is None:
            na_count += 1
        elif ratio <= 0.15:
            low_count += 1
        elif ratio <= 0.30:
            medium_count += 1
        else:
            high_count += 1

        report_data.append({
            'tubewell_name': tubewell.tubewell_name,
            'tubewell_id': tubewell.tubewell_id,
            'total_kwh': total_kwh,
            'total_cum': total_cum,
            'electricity_per_cum': ratio,
        })

    # ---------- Month Dropdown ----------
    available_months = TubeWellWaterProduce.objects.annotate(
        month=TruncMonth('water_produce_date')
    ).values('month').distinct().order_by('-month')

    month_choices = []
    for item in available_months:
        if item['month']:
            month_choices.append({
                'label': DateFormat(item['month']).format('F Y'),
                'value': item['month'].strftime('%Y-%m')
            })

    return render(request, 'tubewell_monthly_summary.html', {
        'report_data': report_data,
        'month_choices': month_choices,
        'selected_month': selected_month or today.strftime('%Y-%m'),
        'locations': permitted_locations,
        'selected_location': int(location_id) if location_id else None,

        # 🔹 Badge Counts
        'low_count': low_count,
        'medium_count': medium_count,
        'high_count': high_count,
        'na_count': na_count,
    })


from django.shortcuts import render, get_object_or_404, redirect
from .models import Hotspot, HotspotEvent
from .forms import HotspotEventForm


# 🔸 1) Hotspot List View

@login_required
@view_permission_required('hotspot_list')
def hotspot_list(request):
    user = request.user

    # Get locations this user has permission to view
    allowed_locations = LocationPermission.objects.filter(
        user=user, can_view=True
    ).values_list('locations', flat=True)

    # Filter hotspots by allowed locations
    hotspots = Hotspot.objects.filter(location__id__in=allowed_locations).order_by('name')

    # Prepare event data
    events_by_hotspot = {
        hotspot.id: list(
            HotspotEvent.objects.filter(hotspot=hotspot).order_by('-created_at')[:5]
        )
        for hotspot in hotspots
    }

    return render(request, 'hotspot_list.html', {
        'hotspots': hotspots,
        'events_by_hotspot': events_by_hotspot
    })


@login_required
def hotspot_list_map(request):
    user = request.user

    # 🔹 Filter locations: exclude "Headoffice"
    locations = Location.objects.exclude(location_name__iexact="Headoffice").order_by('location_name')

    # 🔹 Handle filter selection from GET parameter
    selected_location = request.GET.get('location')

    # 🔹 Locations allowed for this user
    allowed_locations = LocationPermission.objects.filter(
        user=user, can_view=True
    ).values_list('locations', flat=True)

    # 🔹 Build base queryset
    if user.is_superuser:
        hotspots_qs = Hotspot.objects.all()
    else:
        hotspots_qs = Hotspot.objects.filter(location__id__in=allowed_locations)

    # 🔹 Apply location filter if selected
    if selected_location and selected_location.isdigit():
        hotspots_qs = hotspots_qs.filter(location__id=selected_location)

    hotspots_qs = hotspots_qs.select_related('location', 'uc').order_by('name')

    # 🔹 Prepare hotspot data & history
    hotspot_data = []
    events_by_hotspot = {}

    for hotspot in hotspots_qs:
        events = HotspotEvent.objects.filter(hotspot=hotspot).order_by('-created_at')[:5]
        events_by_hotspot[hotspot.id] = list(events)

        last_event = events.first() if events else None
        last_intensity = last_event.rainfall_intensity if last_event else None
        has_urban = bool(last_event and last_event.urban_start_time and last_event.urban_end_time)

        hotspot_data.append({
            'id': hotspot.id,
            'name': hotspot.name,
            'zone': hotspot.location.location_name,
            'uc': hotspot.uc.uc_name if hotspot.uc else "—",
            'lat': hotspot.latitude,
            'lon': hotspot.longitude,
            'supervisor': hotspot.supervisor_name,
            'supervisor_phone': hotspot.supervisor_phone_number,
            'officer': hotspot.officer_name,
            'officer_phone': hotspot.officer_phone_number,
            'last_intensity': last_intensity,
            'has_urban': has_urban,
        })

    return render(request, 'hotspot_map_list.html', {
        'hotspots': hotspot_data,
        'events_by_hotspot': events_by_hotspot,
        'locations': locations,
        'selected_location': int(selected_location) if selected_location and selected_location.isdigit() else None,
    })

# 🔸 2) Hotspot Event View (Add + List for a specific hotspot)


@login_required
@view_permission_required('hotspot_event_view')
def hotspot_event_view(request):
    user = request.user

    # Get allowed locations for the logged-in user
    allowed_locations = LocationPermission.objects.filter(
        user=user, can_view=True
    ).values_list('locations', flat=True)

    # If superuser, show all events
    if user.is_superuser:
        events = HotspotEvent.objects.all().order_by('-created_at')
        allowed_hotspots = Hotspot.objects.all()
    else:
        allowed_hotspots = Hotspot.objects.filter(location__id__in=allowed_locations)
        events = HotspotEvent.objects.filter(hotspot__in=allowed_hotspots).order_by('-created_at')

    # Limit form hotspot choices to allowed hotspots
    class LimitedHotspotEventForm(HotspotEventForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['hotspot'].queryset = allowed_hotspots

    # Add Event
    if request.method == 'POST' and 'add_event' in request.POST:
        form = LimitedHotspotEventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('hotspot_event_view')
    else:
        form = LimitedHotspotEventForm()

    # Update Event
    if request.method == 'POST' and 'update_event' in request.POST:
        event_id = request.POST.get('event_id')
        event = get_object_or_404(HotspotEvent, id=event_id)
        update_form = LimitedHotspotEventForm(request.POST, request.FILES, instance=event)
        if update_form.is_valid():
            update_form.save()
            return redirect('hotspot_event_view')

    # Delete Event
    if request.method == 'POST' and 'delete_event' in request.POST:
        event_id = request.POST.get('event_id')
        event = get_object_or_404(HotspotEvent, id=event_id)
        event.delete()
        return redirect('hotspot_event_view')

    # Build edit forms for each event
    edit_forms = {event.id: LimitedHotspotEventForm(instance=event) for event in events}

    return render(request, 'hotspot_event_view.html', {
        'events': events,
        'form': form,
        'edit_forms': edit_forms
    })


# 🔸 3) Hotspot History View (Optional)
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.shortcuts import get_object_or_404, render
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import datetime

from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import ExtractMonth, ExtractYear

from django.db.models import Avg, Count, F, DurationField, ExpressionWrapper
from django.db.models.functions import ExtractMonth, ExtractYear
from django.shortcuts import get_object_or_404, render
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils.timezone import timedelta


def format_timedelta(td):
    """Convert timedelta to Hh Mm Ss format."""
    if not td:
        return None
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


@view_permission_required('hotspot_history')
def hotspot_history(request, hotspot_id):
    hotspot = get_object_or_404(Hotspot, id=hotspot_id)

    # Date filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    events = HotspotEvent.objects.filter(hotspot=hotspot).order_by('-created_at')

    if start_date:
        events = events.filter(created_at__date__gte=start_date)
    if end_date:
        events = events.filter(created_at__date__lte=end_date)

    # Counts only complete events (both start & end)
    total_rain_events = events.filter(
        rain_start_time__isnull=False,
        rain_end_time__isnull=False
    ).count()

    total_urban_events = events.filter(
        urban_start_time__isnull=False,
        urban_end_time__isnull=False
    ).count()

    # High Rainfall count
    total_high_rain = events.filter(rainfall_intensity='high').count()

    # Average Rain Duration
    rain_durations = events.filter(
        rain_start_time__isnull=False,
        rain_end_time__isnull=False
    ).annotate(
        duration=ExpressionWrapper(
            F('rain_end_time') - F('rain_start_time'),
            output_field=DurationField()
        )
    )
    avg_rain_duration = rain_durations.aggregate(Avg('duration'))['duration__avg']
    avg_rain_duration = format_timedelta(avg_rain_duration)

    # Average Flood Duration
    flood_durations = events.filter(
        urban_start_time__isnull=False,
        urban_end_time__isnull=False
    ).annotate(
        duration=ExpressionWrapper(
            F('urban_end_time') - F('urban_start_time'),
            output_field=DurationField()
        )
    )
    avg_flood_duration = flood_durations.aggregate(Avg('duration'))['duration__avg']
    avg_flood_duration = format_timedelta(avg_flood_duration)

    # Trend Data
    trend_data = events.annotate(
        month=ExtractMonth('created_at'),
        year=ExtractYear('created_at')
    ).values('year', 'month', 'rainfall_intensity').annotate(
        event_count=Count('id')
    ).order_by('year', 'month')

    labels = sorted(
        list({f"{d['month']}/{d['year']}" for d in trend_data}),
        key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0]))
    )

    low_counts, med_counts, high_counts = [], [], []
    for label in labels:
        month, year = map(int, label.split('/'))
        low = next((d['event_count'] for d in trend_data
                    if d['month'] == month and d['year'] == year and d['rainfall_intensity'] == 'low'), 0)
        med = next((d['event_count'] for d in trend_data
                    if d['month'] == month and d['year'] == year and d['rainfall_intensity'] == 'medium'), 0)
        high = next((d['event_count'] for d in trend_data
                     if d['month'] == month and d['year'] == year and d['rainfall_intensity'] == 'high'), 0)
        low_counts.append(low)
        med_counts.append(med)
        high_counts.append(high)

    # Flood Duration Chart
    flood_duration_data = flood_durations.annotate(
        month=ExtractMonth('created_at'),
        year=ExtractYear('created_at')
    ).values('year', 'month').annotate(
        avg_flood=Avg('duration')
    ).order_by('year', 'month')

    flood_labels = []
    flood_values = []
    for d in flood_duration_data:
        label = f"{d['month']}/{d['year']}"
        minutes = d['avg_flood'].total_seconds() / 60 if d['avg_flood'] else 0
        flood_labels.append(label)
        flood_values.append(round(minutes, 2))

    return render(request, 'hotspot_history.html', {
        'hotspot': hotspot,
        'events': events,
        'total_high_rain': total_high_rain,
        'total_rain_events': total_rain_events,
        'total_urban_events': total_urban_events,
        'avg_rain_duration': avg_rain_duration,
        'avg_flood_duration': avg_flood_duration,
        'trend_labels': labels,
        'low_counts': low_counts,
        'med_counts': med_counts,
        'high_counts': high_counts,
        'flood_labels': flood_labels,
        'flood_values': flood_values,
    })


# views.py
from django.shortcuts import render
from django.db.models import Q
from django.utils.dateparse import parse_date
from .models import Hotspot, HotspotEvent, UC, Location

from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.shortcuts import render
from .models import Hotspot, HotspotEvent, UC, Location, LocationPermission
from django.utils.dateparse import parse_date
from django.db.models import Q, F


@login_required
@view_permission_required('flood_report')
def flood_report(request):
    user = request.user

    # Get allowed locations for this user
    allowed_locations = LocationPermission.objects.filter(
        user=user, can_view=True
    ).values_list('locations', flat=True)

    # Start with all events
    events = HotspotEvent.objects.select_related(
        "hotspot", "hotspot__uc", "hotspot__location"
    )

    if not user.is_superuser:
        events = events.filter(hotspot__location_id__in=allowed_locations)

    # Apply filters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    hotspot_id = request.GET.get("hotspot")
    uc_id = request.GET.get("uc")
    location_id = request.GET.get("location")
    intensity = request.GET.get("intensity")
    urban_flooding = request.GET.get("urban_flooding")  # 👈 NEW filter

    if start_date:
        events = events.filter(created_at__date__gte=parse_date(start_date))
    if end_date:
        events = events.filter(created_at__date__lte=parse_date(end_date))
    if hotspot_id:
        events = events.filter(hotspot_id=hotspot_id)
    if uc_id:
        events = events.filter(hotspot__uc_id=uc_id)
    if location_id:
        events = events.filter(hotspot__location_id=location_id)
    if intensity:
        events = events.filter(rainfall_intensity=intensity)

    # 🔹 Urban Flooding filter
    if urban_flooding == "yes":
        events = events.filter(
            urban_start_time__isnull=False,
            urban_end_time__isnull=False
        )
    elif urban_flooding == "no":
        events = events.exclude(
            urban_start_time__isnull=False,
            urban_end_time__isnull=False
        )

    # Limit dropdowns to allowed data
    if user.is_superuser:
        hotspots = Hotspot.objects.all()
        ucs = UC.objects.all()
        locations = Location.objects.all()
    else:
        hotspots = Hotspot.objects.filter(location_id__in=allowed_locations)
        ucs = UC.objects.filter(hotspot__location_id__in=allowed_locations).distinct()
        locations = Location.objects.filter(id__in=allowed_locations)

    context = {
        "events": events,
        "hotspots": hotspots,
        "ucs": ucs,
        "locations": locations,
        "selected": {
            "start_date": start_date,
            "end_date": end_date,
            "hotspot": hotspot_id,
            "uc": uc_id,
            "location": location_id,
            "intensity": intensity,
            "urban_flooding": urban_flooding,  # 👈 Pass selection to template
        }
    }
    return render(request, "flood_report.html", context)


from django.shortcuts import render, get_object_or_404
from .models import AdpScheme

# View 1: List of ADP Schemes (Name, Code, Start Date, End Date)
from django.shortcuts import render
from .models import AdpScheme
from django.db.models import Q

from django.db.models.functions import ExtractYear


@login_required
@view_permission_required('adp_scheme_list')
def adp_scheme_list(request):
    # Get selected year filter from query parameters
    year_filter = request.GET.get('year')

    # Get all distinct years from start_date for dynamic filter options
    available_years = (
        AdpScheme.objects
        .exclude(start_date__isnull=True)  # ignore records with no date
        .annotate(year=ExtractYear('start_date'))
        .values_list('year', flat=True)
        .distinct()
        .order_by('-year')  # descending order
    )

    # Filter schemes based on selected year (if provided)
    schemes = AdpScheme.objects.all()
    if year_filter:
        schemes = schemes.filter(start_date__year=year_filter)

    return render(
        request,
        'adp_scheme_list.html',
        {
            'schemes': schemes,
            'available_years': available_years,
            'year_filter': year_filter
        }
    )

# View 2: Detail View for a Specific ADP Scheme
@login_required
@view_permission_required('adp_scheme_detail')
def adp_scheme_detail(request, pk):
    scheme = get_object_or_404(AdpScheme, pk=pk)
    return render(request, 'adp_scheme_detail.html', {'scheme': scheme})


from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib import messages
from .models import ComplaintFeedback
from .forms import ComplaintFeedbackForm

# 📋 List all Complaint Feedback
from django.views.generic import ListView
from django.utils import timezone
from .models import ComplaintFeedback

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

@method_decorator(
    [login_required, view_permission_required('ComplaintFeedbackListView')],
    name='dispatch'
)
class ComplaintFeedbackListView(ListView):
    model = ComplaintFeedback
    template_name = 'feedback_list.html'
    context_object_name = 'feedback_list'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        if from_date:
            queryset = queryset.filter(created_at__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__date__lte=to_date)
        return queryset


# ➕ Create Complaint Feedback
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import ComplaintFeedback, Complaint
from .forms import ComplaintFeedbackForm
from django.contrib import messages


@method_decorator(
    [login_required, view_permission_required('ComplaintFeedbackCreateView')],
    name='dispatch'
)
class ComplaintFeedbackCreateView(CreateView):
    model = ComplaintFeedback
    form_class = ComplaintFeedbackForm
    template_name = 'feedback_form.html'
    success_url = reverse_lazy('feedback_list')

    def form_valid(self, form):
        # Get complaint ID from hidden input
        complaint_id = self.request.POST.get('complaint')
        if not complaint_id:
            form.add_error(None, "Please select a complaint first.")
            return self.form_invalid(form)

        # Ensure the complaint exists
        try:
            complaint = Complaint.objects.get(id=complaint_id)
        except Complaint.DoesNotExist:
            form.add_error(None, "Selected complaint does not exist.")
            return self.form_invalid(form)

        # Assign the complaint to the feedback (allow multiple feedbacks)
        form.instance.complaint = complaint

        # Optional: show a message on successful save
        messages.success(
            self.request,
            f"✅ Feedback for Complaint #{complaint.id} has been saved."
        )

        return super().form_valid(form)

# views.py
from django.http import JsonResponse
from .models import Complaint

def complaint_check_api(request):
    complaint_id = request.GET.get('id')
    exists = Complaint.objects.filter(id=complaint_id).exists()
    return JsonResponse({'exists': exists})

# ✏️ Update Complaint Feedback
class ComplaintFeedbackUpdateView(UpdateView):
    model = ComplaintFeedback
    form_class = ComplaintFeedbackForm
    template_name = 'feedback_form.html'
    success_url = reverse_lazy('feedback_list')




from django.shortcuts import render
from django.db.models import Q, OuterRef, Subquery
from django.utils.dateparse import parse_date
from .models import Complaint, ComplaintActionLog

from django.shortcuts import render
from django.db.models import OuterRef, Subquery
from django.utils import timezone
from datetime import date
from calendar import monthrange
from .models import Complaint, ComplaintActionLog


from django.db.models import OuterRef, Subquery
from calendar import monthrange
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Complaint, ComplaintActionLog, ComplaintResolution


@login_required
def complaint_report(request):
    # Get today's date
    today = date.today()

    # Current month boundaries
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])

    # Get filters
    start_date = request.GET.get('from_date')
    end_date = request.GET.get('to_date')

    # Convert string to date if provided
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    # Default filter = current month
    if not start_date and not end_date:
        start_date = first_day
        end_date = last_day

    # Base queryset
    complaints = Complaint.objects.select_related('location', 'uc', 'complaint_type')

    # ✅ Use 'date' field for filtering instead of 'created_at'
    if start_date and end_date:
        complaints = complaints.filter(date__range=[start_date, end_date])
    elif start_date:
        complaints = complaints.filter(date__gte=start_date)
    elif end_date:
        complaints = complaints.filter(date__lte=end_date)

    # Annotate resolved date from logs
    resolved_log = ComplaintActionLog.objects.filter(
        complaint=OuterRef('pk'),
        action='resolved'
    ).order_by('timestamp')

    complaints = complaints.annotate(
        resolved_date=Subquery(resolved_log.values('timestamp')[:1])
    )

    # Annotate customer satisfaction from ComplaintResolution
    satisfaction_subquery = ComplaintResolution.objects.filter(
        complaint=OuterRef('pk')
    ).values('customer_satisfaction')[:1]

    complaints = complaints.annotate(
        customer_satisfaction=Subquery(satisfaction_subquery)
    )

    context = {
        'complaints': complaints,
        'from_date': start_date,
        'to_date': end_date,
    }
    return render(request, 'complaint_report.html', context)





# street///

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Street, Location, LocationPermission
from .forms import StreetForm


# ---------- Helper ----------
def get_user_permitted_locations(user):
    """Return queryset of Locations the user can view."""
    if user.is_superuser:
        return Location.objects.all()  # Superuser sees all

    return Location.objects.filter(
        id__in=LocationPermission.objects.filter(
            user=user, can_view=True
        ).values_list('locations__id', flat=True)
    ).distinct()


# ---------- Street List View ----------
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from .models import Street, Location


class StreetListView(LoginRequiredMixin, ListView):
    model = Street
    template_name = 'street_list.html'
    context_object_name = 'streets'
    paginate_by = 10  # default pagination

    def get_queryset(self):
        user = self.request.user
        location_id = self.request.GET.get('location')

        # Base queryset with permissions
        if user.is_superuser:
            qs = Street.objects.select_related('location', 'uc_name', 'nc_name')
        else:
            permitted_locations = get_user_permitted_locations(user)
            qs = Street.objects.select_related('location', 'uc_name', 'nc_name')\
                               .filter(location__in=permitted_locations)

        # ✅ Location filter
        if location_id:
            qs = qs.filter(location_id=location_id)

        return qs

    def get_paginate_by(self, queryset):
        """
        Get paginate_by from GET parameter. 'all' disables pagination.
        """
        page_size = self.request.GET.get('page_size', str(self.paginate_by))
        if page_size.lower() == 'all':
            return None  # show all records
        try:
            return int(page_size)
        except ValueError:
            return self.paginate_by  # fallback to default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()

        # ✅ Totals
        totals = queryset.aggregate(
            total_houses=Sum('no_of_houses'),
            total_shops=Sum('no_of_shops'),
            total_length_km=Sum('total_length_km'),  # 👈 NEW
        )

        context['total_houses'] = totals['total_houses'] or 0
        context['total_shops'] = totals['total_shops'] or 0
        context['total_length_km'] = totals['total_length_km'] or 0  # 👈 NEW

        # ✅ Locations for filter dropdown
        context['locations'] = Location.objects.all()
        context['selected_location'] = self.request.GET.get('location', '')

        # ✅ Pass page_size to template
        context['page_size'] = self.request.GET.get('page_size', str(self.paginate_by))

        return context


# ---------- Street Create View ----------
class StreetCreateView(LoginRequiredMixin, CreateView):
    model = Street
    form_class = StreetForm
    template_name = 'street_form.html'
    success_url = reverse_lazy('street_list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        user = self.request.user

        if not user.is_superuser:
            permitted_locations = get_user_permitted_locations(user)

            # ✅ Filter Locations
            form.fields['location'].queryset = form.fields['location'].queryset.filter(
                id__in=permitted_locations
            )

            # ✅ Filter UCs within permitted locations
            form.fields['uc_name'].queryset = form.fields['uc_name'].queryset.filter(
                location__in=permitted_locations
            )

            # ✅ Filter NCs within permitted UCs
            form.fields['nc_name'].queryset = form.fields['nc_name'].queryset.filter(
                uc_name__location__in=permitted_locations
            )

            # ✅ Filter Employees by permitted locations
            if 'assign_employee' in form.fields:
                form.fields['assign_employee'].queryset = form.fields['assign_employee'].queryset.filter(
                    location__in=permitted_locations
                )

            # ✅ Filter Vehicles by permitted locations
            if 'assign_vehicle' in form.fields:
                form.fields['assign_vehicle'].queryset = form.fields['assign_vehicle'].queryset.filter(
                    location__in=permitted_locations
                )

        return form


# ---------- Street Update View ----------
class StreetUpdateView(LoginRequiredMixin, UpdateView):
    model = Street
    form_class = StreetForm
    template_name = 'street_form.html'
    success_url = reverse_lazy('street_list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        user = self.request.user

        if not user.is_superuser:
            permitted_locations = get_user_permitted_locations(user)

            # ✅ Filter Locations
            form.fields['location'].queryset = form.fields['location'].queryset.filter(
                id__in=permitted_locations
            )

            # ✅ Filter UCs
            form.fields['uc_name'].queryset = form.fields['uc_name'].queryset.filter(
                location__in=permitted_locations
            )

            # ✅ Filter NCs
            form.fields['nc_name'].queryset = form.fields['nc_name'].queryset.filter(
                uc_name__location__in=permitted_locations
            )

            # ✅ Filter Employees
            if 'assign_employee' in form.fields:
                form.fields['assign_employee'].queryset = form.fields['assign_employee'].queryset.filter(
                    location__in=permitted_locations
                )

            # ✅ Filter Vehicles
            if 'assign_vehicle' in form.fields:
                form.fields['assign_vehicle'].queryset = form.fields['assign_vehicle'].queryset.filter(
                    location__in=permitted_locations
                )

        return form


# ---------- Street Delete View ----------
class StreetDeleteView(LoginRequiredMixin, DeleteView):
    model = Street
    template_name = 'street_confirm_delete.html'
    success_url = reverse_lazy('street_list')

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Street.objects.all()
        permitted_locations = get_user_permitted_locations(user)
        return Street.objects.filter(location__in=permitted_locations)



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from .models import Street, DailyStreetCollection, Location, LocationPermission


@login_required
@view_permission_required('daily_collection_entry')
def daily_collection_entry(request):
    # --- Get selected date or default to today ---
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    # --- Prevent future dates ---
    today = timezone.now().date()
    if selected_date > today:
        messages.warning(request, "You cannot enter data for a future date.")
        selected_date = today

    # --- Get user's permitted locations ---
    permitted_locations = get_user_permitted_locations(request.user)

    # --- Filter streets by permission ---
    if request.user.is_superuser:
        streets = Street.objects.select_related('location', 'uc_name', 'nc_name').all()
    else:
        streets = Street.objects.select_related('location', 'uc_name', 'nc_name').filter(
            location__in=permitted_locations
        )

    # --- Handle POST submission ---
    if request.method == 'POST':
        for street in streets:
            houses = request.POST.get(f"houses_{street.id}")
            shops = request.POST.get(f"shops_{street.id}")
            remarks = request.POST.get(f"remarks_{street.id}")

            if houses or shops or remarks:
                DailyStreetCollection.objects.update_or_create(
                    street=street,
                    collection_date=selected_date,
                    defaults={
                        'collected_houses': houses or 0,
                        'collected_shops': shops or 0,
                        'remarks': remarks or ''
                    }
                )

        messages.success(request, f"Data saved successfully for {selected_date}.")
        return redirect(f"{reverse('daily_collection_entry')}?date={selected_date}")

    # --- Load existing records for selected date ---
    existing_records = DailyStreetCollection.objects.filter(collection_date=selected_date)
    records_dict = {rec.street_id: rec for rec in existing_records}

    return render(request, 'daily_collection_entry.html', {
        'streets': streets,
        'selected_date': selected_date,
        'records_dict': records_dict,
    })


from django.shortcuts import render, get_object_or_404
from .models import Street



@login_required
@view_permission_required('street_detail_view')
def street_detail_view(request, pk):
    street = get_object_or_404(Street, pk=pk)

    # Prepare coordinates for the map
    coordinates = []
    if street.start_latitude and street.start_longitude:
        coordinates.append([float(street.start_longitude), float(street.start_latitude)])
    if street.mid_latitude and street.mid_longitude:
        coordinates.append([float(street.mid_longitude), float(street.mid_latitude)])
    if street.end_latitude and street.end_longitude:
        coordinates.append([float(street.end_longitude), float(street.end_latitude)])

    # Get UC and Location from NC
    uc = street.nc_name.uc_name if street.nc_name and street.nc_name.uc_name else None
    location = uc.location if uc else None

    context = {
        'street': street,
        'coordinates': coordinates,
        'uc': uc,
        'location': location,
    }
    return render(request, 'street_detail.html', context)


# street



from django.shortcuts import render
from django.db.models import Sum
from datetime import date
from .models import Location, Street, DailyStreetCollection

from django.shortcuts import render
from django.db.models import Sum
from datetime import date
from .models import Location, Street, DailyStreetCollection

from datetime import date
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date
from django.utils import timezone

@login_required
@view_permission_required('street_collection_dashboard')
def street_collection_dashboard(request):
    # --- Get selected date or default to today ---
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = date.fromisoformat(selected_date)
    else:
        selected_date = timezone.now().date()  # default to today

    # --- Get user's permitted locations ---
    user = request.user
    if user.is_superuser:
        locations = Location.objects.exclude(location_name__iexact="HeadOffice").order_by('location_name')
    else:
        permitted_locations = get_user_permitted_locations(user)
        locations = permitted_locations.exclude(location_name__iexact="HeadOffice").order_by('location_name')

    # --- Fixed Actual Values per Location ---
    ACTUAL_VALUES = {
        "Zone A": 58847,
        "Zone B": 45873,
        "Zone C": 37121,
        "Zone D": 44769,
        "Zone E": 40757,
    }

    # --- Initialize counters ---
    location_data = []
    total_houses_all = total_shops_all = collected_houses_all = collected_shops_all = 0

    # --- Loop through each permitted location ---
    for location in locations:
        streets = Street.objects.filter(location=location)

        total_houses = streets.aggregate(total=Sum('no_of_houses'))['total'] or 0
        total_shops = streets.aggregate(total=Sum('no_of_shops'))['total'] or 0

        # Dynamic target = houses + shops
        target_total = total_houses + total_shops

        # Load collections for selected date
        collections = DailyStreetCollection.objects.filter(
            street__in=streets,
            collection_date=selected_date
        )

        collected_houses = collections.aggregate(total=Sum('collected_houses'))['total'] or 0
        collected_shops = collections.aggregate(total=Sum('collected_shops'))['total'] or 0

        not_collected_houses = max(total_houses - collected_houses, 0)
        not_collected_shops = max(total_shops - collected_shops, 0)

        house_percentage = (collected_houses / total_houses * 100) if total_houses > 0 else 0
        shop_percentage = (collected_shops / total_shops * 100) if total_shops > 0 else 0

        # Update overall totals
        total_houses_all += total_houses
        total_shops_all += total_shops
        collected_houses_all += collected_houses
        collected_shops_all += collected_shops

        # Fixed actual value from dictionary
        actual_total = ACTUAL_VALUES.get(location.location_name, 0)

        # Append data for this location
        location_data.append({
            'location_name': location.location_name,

            # NEW chart values
            'target_total': target_total,
            'actual_total': actual_total,

            'total_houses': total_houses,
            'collected_houses': collected_houses,
            'not_collected_houses': not_collected_houses,
            'house_percentage': round(house_percentage, 1),

            'total_shops': total_shops,
            'collected_shops': collected_shops,
            'not_collected_shops': not_collected_shops,
            'shop_percentage': round(shop_percentage, 1),
        })

    # --- Overall summary ---
    overall_data = {
        'total_houses': total_houses_all,
        'collected_houses': collected_houses_all,
        'not_collected_houses': max(total_houses_all - collected_houses_all, 0),
        'house_percentage': round((collected_houses_all / total_houses_all * 100), 1) if total_houses_all > 0 else 0,

        'total_shops': total_shops_all,
        'collected_shops': collected_shops_all,
        'not_collected_shops': max(total_shops_all - collected_shops_all, 0),
        'shop_percentage': round((collected_shops_all / total_shops_all * 100), 1) if total_shops_all > 0 else 0,
    }

    # --- Chart Data ---
    chart_labels = [loc['location_name'] for loc in location_data]
    chart_targets = [loc['target_total'] for loc in location_data]
    chart_actuals = [loc['actual_total'] for loc in location_data]

    # --- Render ---
    return render(request, 'street_collection_dashboard.html', {
        'selected_date': selected_date,
        'location_data': location_data,
        'overall_data': overall_data,

        # NEW chart arrays
        'chart_labels': chart_labels,
        'chart_targets': chart_targets,
        'chart_actuals': chart_actuals,
    })




from django.utils import timezone
from datetime import datetime, date
import calendar
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from .models import DailyStreetCollection, Street, Location

@login_required
@view_permission_required('accumulative_street_report')
def accumulative_street_report(request):
    user = request.user

    # --------------------
    # Get permitted locations and exclude HeadOffice
    # --------------------
    if user.is_superuser:
        locations = Location.objects.exclude(location_name__iexact="HeadOffice").order_by('location_name')
    else:
        permitted_locations = get_user_permitted_locations(user)
        locations = permitted_locations.exclude(location_name__iexact="HeadOffice").order_by('location_name')

    # --------------------
    # Default date range = current month
    # --------------------
    today = timezone.now().date()
    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    # --------------------
    # Filters from GET parameters
    # --------------------
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    selected_location = request.GET.get('location')

    # Parse dates (ensure proper date objects for template)
    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else first_day
    except (ValueError, TypeError):
        from_date = first_day

    try:
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else last_day
    except (ValueError, TypeError):
        to_date = last_day

    # --------------------
    # Base queryset
    # --------------------
    collections = DailyStreetCollection.objects.select_related('street', 'street__location')
    collections = collections.filter(collection_date__range=[from_date, to_date])
    collections = collections.filter(street__location__in=locations)

    if selected_location:
        collections = collections.filter(street__location_id=selected_location)

    # --------------------
    # Group by Street
    # --------------------
    report = (
        collections.values('street__id', 'street__street_name', 'street__location__location_name')
        .annotate(
            total_houses=Sum('collected_houses'),
            total_shops=Sum('collected_shops'),
            days_count=Count('collection_date', distinct=True),
        )
        .annotate(
            avg_houses_per_day=Avg('collected_houses'),
            avg_shops_per_day=Avg('collected_shops')
        )
        .order_by('street__street_name')
    )

    # --------------------
    # Pass context to template
    # --------------------
    context = {
        'report': report,
        'locations': locations,
        'selected_location': selected_location,
        'from_date': from_date,  # ✅ always a date object
        'to_date': to_date,      # ✅ always a date object
    }

    return render(request, 'accumulative_street_report.html', context)




from datetime import date, datetime
from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Watertest, Location, LocationPermission
from .forms import WatertestForm


from datetime import date, datetime, timedelta
from calendar import monthrange
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Watertest, Location, LocationPermission

@login_required
@view_permission_required('water_test_report')
def water_test_report(request):
    # -------------------------------
    # GET FILTER PARAMETERS
    # -------------------------------
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    output_filter = request.GET.get('output')
    location_type_filter = request.GET.get('location_type')
    location_filter = request.GET.get('location')

    today = date.today()

    # Get first and last day of current month
    first_day_of_month = today.replace(day=1)
    last_day_of_month = today.replace(day=monthrange(today.year, today.month)[1])

    # Convert string dates safely (default to current month)
    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else first_day_of_month
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else last_day_of_month
    except ValueError:
        from_date = first_day_of_month
        to_date = last_day_of_month

    # -------------------------------
    # USER ACCESS CONTROL
    # -------------------------------
    if request.user.is_superuser:
        locations = Location.objects.all()
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = []
        for perm in user_permissions:
            location_ids.extend(perm.locations.values_list('id', flat=True))
        locations = Location.objects.filter(id__in=location_ids)

    # -------------------------------
    # MAIN QUERYSET FILTERING (exclude Headoffice)
    # -------------------------------
    water_tests = Watertest.objects.filter(
        location__in=locations,
        date__range=[from_date, to_date]
    ).exclude(location__location_name__icontains='Headoffice')  # ✅ exclude Headoffice

    # Apply extra filters
    if output_filter and output_filter != '-----':
        water_tests = water_tests.filter(output=output_filter)

    if location_type_filter and location_type_filter != '-----':
        water_tests = water_tests.filter(location_type=location_type_filter)

    if location_filter and location_filter != '-----':
        water_tests = water_tests.filter(location_id=location_filter)

    # -------------------------------
    # AGGREGATE TOTALS
    # -------------------------------
    totals = {
        'total_tests': water_tests.count(),
        'avg_ph': round(water_tests.aggregate(Sum('ph'))['ph__sum'] or 0, 2),
        'avg_temperature': round(water_tests.aggregate(Sum('temperature_c'))['temperature_c__sum'] or 0, 2),
        'avg_dissolved_oxygen': round(water_tests.aggregate(Sum('dissolved_oxygen_mg_l'))['dissolved_oxygen_mg_l__sum'] or 0, 2),
    }

    # -------------------------------
    # TEST COUNTS BY LOCATION
    # -------------------------------
    location_test_counts = water_tests.values('location__location_name').annotate(total_tests=Count('id'))
    location_totals = {item['location__location_name']: item['total_tests'] for item in location_test_counts}

    # -------------------------------
    # CONTEXT FOR TEMPLATE
    # -------------------------------
    context = {
        'from_date': from_date,
        'to_date': to_date,
        'water_tests': water_tests,
        'totals': totals,
        'location_totals': location_totals,
        'locations': locations.exclude(location_name__icontains='Headoffice'),  # ✅ exclude from dropdown too
        'selected_output': output_filter or '-----',
        'selected_location_type': location_type_filter or '-----',
        'selected_location': location_filter or '-----',
        'output_choices': [
            ('-----', '-----'),
            ('safe', 'safe'),
            ('unsafe', 'unsafe'),
        ],
        'location_type_choices': [
            ('-----', '-----'),
            ('At source', 'At source'),
            ('Consumer Tap', 'Consumer Tap'),
        ],
    }

    return render(request, 'water_test_report.html', context)





from django.db.models import Count, Q
from calendar import month_name


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Count, Min
from django.db.models.functions import ExtractMonth
from calendar import month_name
from .models import Watertest, Location, LocationPermission


from datetime import date, datetime
from calendar import month_name
from django.db.models import Count, Min
from django.db.models.functions import ExtractMonth
from django.shortcuts import render
from .models import Watertest, Location, LocationPermission

@login_required
@view_permission_required('water_quality_dashboard')
def water_quality_dashboard(request):
    # Get filters
    year = int(request.GET.get('year', date.today().year))
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')

    # Determine date range
    today = date.today()
    if from_date_str and to_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            from_date, to_date = today.replace(month=1, day=1), today
    else:
        # Default: full current year
        from_date = date(year, 1, 1)
        to_date = date(year, 12, 31)

    # Determine accessible locations (exclude Head Office)
    if request.user.is_superuser:
        locations = Location.objects.exclude(location_name__iexact="HeadOffice").order_by('location_name')
    else:
        user_permissions = LocationPermission.objects.filter(user=request.user)
        location_ids = []
        for perm in user_permissions:
            location_ids.extend(perm.locations.values_list('id', flat=True))
        locations = (
            Location.objects
            .filter(id__in=location_ids)
            .exclude(location_name__iexact="HeadOffice")
            .order_by('location_name')
        )

    # Filter water quality data by date range and locations
    water_quality_data = Watertest.objects.filter(
        location__in=locations,
        date__range=(from_date, to_date)
    )

    # Month-wise aggregation per location
    monthly_data = (
        water_quality_data
        .annotate(month=ExtractMonth('date'))
        .values('month', 'location__location_name')
        .annotate(test_count=Count('id'))
        .order_by('month')
    )

    # Chart.js data
    months = [month_name[i] for i in range(1, 13)]
    locations_list = [loc.location_name for loc in locations]

    colors = [
        'rgba(255, 99, 132, 0.7)',
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
    ]

    chart_datasets = []
    for i, loc in enumerate(locations_list):
        monthly_counts = [0] * 12
        for item in monthly_data:
            if item['location__location_name'] == loc:
                month_index = item['month'] - 1
                monthly_counts[month_index] = item['test_count']
        chart_datasets.append({
            'label': loc,
            'data': monthly_counts,
            'backgroundColor': colors[i % len(colors)]
        })

    # Available years for dropdown
    earliest_year = Watertest.objects.aggregate(min_year=Min('date'))['min_year']
    if earliest_year:
        years = list(range(earliest_year.year, today.year + 1))
    else:
        years = [today.year]

    # Total tests
    total_tests = water_quality_data.count()
    current_month_total_tests = water_quality_data.filter(date__month=today.month).count()

    # Location-wise stats
    location_stats = []
    for loc in locations:
        loc_tests = water_quality_data.filter(location=loc)
        loc_total = loc_tests.count()
        loc_safe = loc_tests.filter(output='safe').count()
        loc_unsafe = loc_tests.filter(output='unsafe').count()
        location_stats.append({
            'location': loc.location_name,
            'total': loc_total,
            'safe': loc_safe,
            'unsafe': loc_unsafe
        })

    context = {
        'year': year,
        'years': years,
        'months': months,
        'chart_datasets': chart_datasets,
        'total_tests': total_tests,
        'current_month_total_tests': current_month_total_tests,
        'location_stats': location_stats,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, 'water_quality_dashboard.html', context)

 # Adjust the import based on your app structure


from django.http import JsonResponse

from django.http import JsonResponse
from .models import Watertest

def get_unsafe_tests(request):
    location_name = request.GET.get('location')
    tests = (
        Watertest.objects.filter(
            location__location_name=location_name,
            output='unsafe'
        )
        .select_related('uc', 'tubewell', 'location')
        .order_by('-date')
    )

    test_list = [
        {
            'date': test.date.strftime("%Y-%m-%d") if test.date else '',
            'location': test.location.location_name if test.location else '',
            'uc': test.uc.uc_name if test.uc else '',
            'tubewell': test.tubewell.tubewell_name if test.tubewell else '',
            'location_type': test.location_type or '',
            'output': test.output or '',
            'temperature_c': str(test.temperature_c) if test.temperature_c else '',
            'ph': str(test.ph) if test.ph else '',
            'electrical_conductivity_uc_cm': str(test.electrical_conductivity_uc_cm) if test.electrical_conductivity_uc_cm else '',
            'dissolved_oxygen_mg_l': str(test.dissolved_oxygen_mg_l) if test.dissolved_oxygen_mg_l else '',
            'tss_mg_l': str(test.tss_mg_l) if test.tss_mg_l else '',
            'turbidity_ntu': str(test.turbidity_ntu) if test.turbidity_ntu else '',
            'tds_mg_l': str(test.tds_mg_l) if test.tds_mg_l else '',
            'resistivity_ojm_cm': str(test.resistivity_ojm_cm) if test.resistivity_ojm_cm else '',
            'salinity_mg_l': str(test.salinity_mg_l) if test.salinity_mg_l else '',
            'coliform': str(test.coliform) if test.coliform else '',
            'latitude': str(test.latitude) if test.latitude else '',
            'longitude': str(test.longitude) if test.longitude else '',
        }
        for test in tests
    ]

    return JsonResponse({'tests': test_list})







# District Service Delivery forms


# DSD 


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date, datetime
from .models import (
    MajorRoad,
    TrunkSewerInspection,
    StormDrainInspection,
    PondingPointsInspection,
    Location,
    LocationPermission
)
from .forms import (
    MajorRoadForm,
    TrunkSewerInspectionForm,
    StormDrainInspectionForm,
    PondingPointsInspectionForm
)

# ---------------- Helper Functions ----------------
def get_user_locations(user):
    """
    Return queryset of locations the user has permission for (can_view=True)
    """
    perms = LocationPermission.objects.filter(user=user, can_view=True)
    location_ids = [loc.id for perm in perms for loc in perm.locations.all()]
    return Location.objects.filter(id__in=location_ids)

def get_current_month_range():
    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = date(today.year, today.month + 1, 1) if today.month < 12 else date(today.year + 1, 1, 1)
    return start_date, end_date

def generate_summary(queryset, indicators):
    data = []
    for label, field in indicators:
        yes = queryset.filter(**{field: 'Yes'}).count()
        no = queryset.filter(**{field: 'No'}).count()
        percent = round((yes / (yes + no)) * 100, 1) if (yes + no) > 0 else 0
        data.append({"indicator": label, "yes": yes, "no": no, "percent": percent})
    return data

# ------------------- Major Road -------------------
@login_required
@view_permission_required('major_road_list')
def major_road_list(request):
    locations = get_user_locations(request.user)
    roads = MajorRoad.objects.filter(location__in=locations)
    return render(request, 'inspections/major_road_list.html', {'roads': roads})

@login_required
@view_permission_required('major_road_create')
def major_road_create(request):
    locations = get_user_locations(request.user)
    if request.method == 'POST':
        form = MajorRoadForm(request.POST, request.FILES)
        form.fields['location'].queryset = locations
        if form.is_valid():
            form.save()
            messages.success(request, "Major Road inspection added successfully.")
            return redirect('major_road_list')
    else:
        form = MajorRoadForm()
        form.fields['location'].queryset = locations
    return render(request, 'inspections/major_road_form.html', {'form': form})

@login_required
@view_permission_required('major_road_update')
def major_road_update(request, pk):
    road = get_object_or_404(MajorRoad, pk=pk)
    locations = get_user_locations(request.user)
    if request.method == 'POST':
        form = MajorRoadForm(request.POST, request.FILES, instance=road)
        form.fields['location'].queryset = locations
        if form.is_valid():
            form.save()
            messages.success(request, "Major Road inspection updated successfully.")
            return redirect('major_road_list')
    else:
        form = MajorRoadForm(instance=road)
        form.fields['location'].queryset = locations
    return render(request, 'inspections/major_road_form.html', {'form': form})

@login_required
@view_permission_required('major_road_delete')
def major_road_delete(request, pk):
    road = get_object_or_404(MajorRoad, pk=pk)
    if request.method == 'POST':
        road.delete()
        messages.success(request, "Major Road inspection deleted successfully.")
        return redirect('major_road_list')
    return render(request, 'inspections/confirm_delete.html', {'object': road})

# ------------------- Trunk Sewer -------------------
@login_required
@view_permission_required('trunk_sewer_list')
def trunk_sewer_list(request):
    locations = get_user_locations(request.user)
    inspections = TrunkSewerInspection.objects.filter(location__in=locations)
    return render(request, 'inspections/trunk_sewer_list.html', {'inspections': inspections})

@login_required
@view_permission_required('trunk_sewer_create')
def trunk_sewer_create(request):
    locations = get_user_locations(request.user)
    if request.method == 'POST':
        form = TrunkSewerInspectionForm(request.POST, request.FILES)
        form.fields['location'].queryset = locations
        if form.is_valid():
            form.save()
            messages.success(request, "Trunk Sewer inspection added successfully.")
            return redirect('trunk_sewer_list')
    else:
        form = TrunkSewerInspectionForm()
        form.fields['location'].queryset = locations
    return render(request, 'inspections/trunk_sewer_form.html', {'form': form})

@login_required
@view_permission_required('trunk_sewer_update')
def trunk_sewer_update(request, pk):
    inspection = get_object_or_404(TrunkSewerInspection, pk=pk)
    locations = get_user_locations(request.user)
    if request.method == 'POST':
        form = TrunkSewerInspectionForm(request.POST, request.FILES, instance=inspection)
        form.fields['location'].queryset = locations
        if form.is_valid():
            form.save()
            messages.success(request, "Trunk Sewer inspection updated successfully.")
            return redirect('trunk_sewer_list')
    else:
        form = TrunkSewerInspectionForm(instance=inspection)
        form.fields['location'].queryset = locations
    return render(request, 'inspections/trunk_sewer_form.html', {'form': form})

@login_required
@view_permission_required('trunk_sewer_delete')
def trunk_sewer_delete(request, pk):
    inspection = get_object_or_404(TrunkSewerInspection, pk=pk)
    if request.method == 'POST':
        inspection.delete()
        messages.success(request, "Trunk Sewer inspection deleted successfully.")
        return redirect('trunk_sewer_list')
    return render(request, 'inspections/confirm_delete.html', {'object': inspection})

# ------------------- Storm Drain -------------------
@login_required
@view_permission_required('storm_drain_list')
def storm_drain_list(request):
    locations = get_user_locations(request.user)
    drains = StormDrainInspection.objects.filter(location__in=locations)
    return render(request, 'inspections/storm_drain_list.html', {'drains': drains})

@login_required
@view_permission_required('storm_drain_create')
def storm_drain_create(request):
    locations = get_user_locations(request.user)
    if request.method == 'POST':
        form = StormDrainInspectionForm(request.POST, request.FILES)
        form.fields['location'].queryset = locations
        if form.is_valid():
            form.save()
            messages.success(request, "Storm Drain inspection added successfully.")
            return redirect('storm_drain_list')
    else:
        form = StormDrainInspectionForm()
        form.fields['location'].queryset = locations
    return render(request, 'inspections/storm_drain_form.html', {'form': form})

@login_required
@view_permission_required('storm_drain_update')
def storm_drain_update(request, pk):
    drain = get_object_or_404(StormDrainInspection, pk=pk)
    locations = get_user_locations(request.user)
    if request.method == 'POST':
        form = StormDrainInspectionForm(request.POST, request.FILES, instance=drain)
        form.fields['location'].queryset = locations
        if form.is_valid():
            form.save()
            messages.success(request, "Storm Drain inspection updated successfully.")
            return redirect('storm_drain_list')
    else:
        form = StormDrainInspectionForm(instance=drain)
        form.fields['location'].queryset = locations
    return render(request, 'inspections/storm_drain_form.html', {'form': form})

@login_required
@view_permission_required('storm_drain_delete')
def storm_drain_delete(request, pk):
    drain = get_object_or_404(StormDrainInspection, pk=pk)
    if request.method == 'POST':
        drain.delete()
        messages.success(request, "Storm Drain inspection deleted successfully.")
        return redirect('storm_drain_list')
    return render(request, 'inspections/confirm_delete.html', {'object': drain})

# ------------------- Ponding Points -------------------
@login_required
@view_permission_required('ponding_points_list')
def ponding_points_list(request):
    locations = get_user_locations(request.user)
    points = PondingPointsInspection.objects.filter(location__in=locations)
    return render(request, 'inspections/ponding_points_list.html', {'points': points})

@login_required
@view_permission_required('ponding_points_create')
def ponding_points_create(request):
    locations = get_user_locations(request.user)
    if request.method == 'POST':
        form = PondingPointsInspectionForm(request.POST, request.FILES)
        form.fields['location'].queryset = locations
        if form.is_valid():
            form.save()
            messages.success(request, "Ponding Points inspection added successfully.")
            return redirect('ponding_points_list')
    else:
        form = PondingPointsInspectionForm()
        form.fields['location'].queryset = locations
    return render(request, 'inspections/ponding_points_form.html', {'form': form})

@login_required
@view_permission_required('ponding_points_update')
def ponding_points_update(request, pk):
    point = get_object_or_404(PondingPointsInspection, pk=pk)
    locations = get_user_locations(request.user)
    if request.method == 'POST':
        form = PondingPointsInspectionForm(request.POST, request.FILES, instance=point)
        form.fields['location'].queryset = locations
        if form.is_valid():
            form.save()
            messages.success(request, "Ponding Points inspection updated successfully.")
            return redirect('ponding_points_list')
    else:
        form = PondingPointsInspectionForm(instance=point)
        form.fields['location'].queryset = locations
    return render(request, 'inspections/ponding_points_form.html', {'form': form})

@login_required
@view_permission_required('ponding_points_delete')
def ponding_points_delete(request, pk):
    point = get_object_or_404(PondingPointsInspection, pk=pk)
    if request.method == 'POST':
        point.delete()
        messages.success(request, "Ponding Points inspection deleted successfully.")
        return redirect('ponding_points_list')
    return render(request, 'inspections/confirm_delete.html', {'object': point})

# ------------------- Reports with Location Permissions -------------------
@login_required
@view_permission_required('major_road_report')
def major_road_report(request):
    locations = get_user_locations(request.user)
    selected_location = request.GET.get("location")
    start_date, end_date = get_current_month_range()

    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date() if from_date_str else start_date
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date() if to_date_str else end_date

    queryset = MajorRoad.objects.filter(location__in=locations, inspection_date__range=[from_date, to_date])
    if selected_location:
        queryset = queryset.filter(location__id=selected_location)

    indicators = [
        ("Free from garbage / rubble", "free_from_garbage_rubble"),
        ("Dry & clean", "dry_and_clean"),
    ]
    context = {
        "title": "Major Road Inspection Compliance Report",
        "data": generate_summary(queryset, indicators),
        "locations": locations,
        "selected_location": selected_location,
        "from_date": from_date,
        "to_date": to_date,
    }
    return render(request, "inspections/compliance_report.html", context)

# Repeat the same location permission logic for the other reports:
@login_required
@view_permission_required('trunk_sewer_report')
def trunk_sewer_report(request):
    locations = get_user_locations(request.user)
    selected_location = request.GET.get("location")
    start_date, end_date = get_current_month_range()
    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date() if from_date_str else start_date
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date() if to_date_str else end_date

    queryset = TrunkSewerInspection.objects.filter(location__in=locations, inspection_date__range=[from_date, to_date])
    if selected_location:
        queryset = queryset.filter(location__id=selected_location)

    indicators = [
        ("Manhole covered", "manhole_covered"),
        ("Manhole free from damage", "manhole_free_from_damage"),
        ("No sediment around manhole", "no_sediment_around_manhole"),
        ("No outflow of sewage", "no_outflow_of_sewage_from_manhole"),
        ("No bad odour around manhole", "no_bad_odour_around_manhole"),
        ("No blockage at outflow of drain", "no_blockage_at_outflow_of_drain"),
        ("Fast flow of water at outflow of drain", "fastflow_of_water_at_outflow_of_drain"),
    ]
    context = {
        "title": "Trunk Sewer Inspection Compliance Report",
        "data": generate_summary(queryset, indicators),
        "locations": locations,
        "selected_location": selected_location,
        "from_date": from_date,
        "to_date": to_date,
    }
    return render(request, "inspections/compliance_report.html", context)

@login_required
@view_permission_required('storm_drain_report')
def storm_drain_report(request):
    locations = get_user_locations(request.user)
    selected_location = request.GET.get("location")
    start_date, end_date = get_current_month_range()
    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date() if from_date_str else start_date
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date() if to_date_str else end_date

    queryset = StormDrainInspection.objects.filter(location__in=locations, inspection_date__range=[from_date, to_date])
    if selected_location:
        queryset = queryset.filter(location__id=selected_location)

    indicators = [
        ("Entry clear", "entry_clear"),
        ("Exit clear", "exit_clear"),
    ]
    context = {
        "title": "Storm Drain Inspection Compliance Report",
        "data": generate_summary(queryset, indicators),
        "locations": locations,
        "selected_location": selected_location,
        "from_date": from_date,
        "to_date": to_date,
    }
    return render(request, "inspections/compliance_report.html", context)

@login_required
@view_permission_required('ponding_points_report')
def ponding_points_report(request):
    locations = get_user_locations(request.user)
    selected_location = request.GET.get("location")
    start_date, end_date = get_current_month_range()
    from_date_str = request.GET.get("from_date")
    to_date_str = request.GET.get("to_date")
    from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date() if from_date_str else start_date
    to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date() if to_date_str else end_date

    queryset = PondingPointsInspection.objects.filter(location__in=locations, inspection_date__range=[from_date, to_date])
    if selected_location:
        queryset = queryset.filter(location__id=selected_location)

    indicators = [
        ("Any attempt by government", "any_attempt_by_government"),
    ]
    context = {
        "title": "Ponding Points Inspection Compliance Report",
        "data": generate_summary(queryset, indicators),
        "locations": locations,
        "selected_location": selected_location,
        "from_date": from_date,
        "to_date": to_date,
    }
    return render(request, "inspections/compliance_report.html", context)


# DSD
# District Service Delivery forms



# water Discharge


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import TubeWelldischarge
from .forms import TubeWellDischargeForm

# LIST
from django.db.models import OuterRef, Subquery

@login_required
def tubewell_discharge_list(request):
    locations = get_user_locations(request.user)
    query = request.GET.get('q', '')

    # Latest discharge subquery
    latest_discharge = TubeWelldischarge.objects.filter(
        tubewell=OuterRef('pk')
    ).order_by('-created_at')

    tubewells = TubeWell.objects.select_related(
        'location', 'uc'
    ).filter(
        location__in=locations
    )

    # 🔍 Search
    if query:
        tubewells = tubewells.filter(
            Q(tubewell_name__icontains=query) |
            Q(tubewell_id__icontains=query)
        )

    # Annotate latest discharge
    tubewells = tubewells.annotate(
        latest_discharge=Subquery(
            latest_discharge.values('updated_average_discharge')[:1]
        ),
        latest_date=Subquery(
            latest_discharge.values('updated_average_discharge_date')[:1]
        )
    ).order_by('-id')

    return render(request, 'tubewell_discharge/list.html', {
        'tubewells': tubewells,
        'query': query
    })


# CREATE
@login_required
def tubewell_discharge_create(request):
    locations = get_user_locations(request.user)

    if request.method == 'POST':
        form = TubeWellDischargeForm(request.POST)
        form.fields['tubewell'].queryset = TubeWell.objects.filter(
            location__in=locations
        ).order_by('tubewell_name')

        if form.is_valid():
            form.save()
            messages.success(request, 'Discharge record added successfully ✅')
            return redirect('tubewell_discharge_list')
    else:
        form = TubeWellDischargeForm()
        form.fields['tubewell'].queryset = TubeWell.objects.filter(
            location__in=locations
        ).order_by('tubewell_name')

    return render(
        request,
        'tubewell_discharge/form.html',
        {'form': form}
    )


# UPDATE
@login_required
def tubewell_discharge_update(request, pk):
    discharge = get_object_or_404(TubeWelldischarge, pk=pk)
    locations = get_user_locations(request.user)

    if request.method == 'POST':
        form = TubeWellDischargeForm(request.POST, instance=discharge)
        form.fields['tubewell'].queryset = TubeWell.objects.filter(
            location__in=locations
        )

        if form.is_valid():
            form.save()
            messages.success(request, 'Discharge record updated successfully ✏️')
            return redirect('tubewell_discharge_list')
    else:
        form = TubeWellDischargeForm(instance=discharge)
        form.fields['tubewell'].queryset = TubeWell.objects.filter(
            location__in=locations
        )

    return render(
        request,
        'tubewell_discharge/form.html',
        {'form': form}
    )

# DELETE
def tubewell_discharge_delete(request, pk):
    discharge = get_object_or_404(TubeWelldischarge, pk=pk)

    if request.method == 'POST':
        discharge.delete()
        messages.success(request, 'Discharge record deleted successfully 🗑️')
        return redirect('tubewell_discharge_list')

    return render(request, 'tubewell_discharge/confirm_delete.html', {'discharge': discharge})


# Average Discharge






# new DSD


from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    MajorRoad_inspection,
    TrunkSewer_inspection,
    StormDrain_inspection,
    PondingPoints_inspection
)
from .forms import (
    MajorRoadInspectionFormDSD,
    TrunkSewerInspectionFormDSD,
    StormDrainInspectionFormDSD,
    PondingPointsInspectionFormDSD
)


def dsd1_majorroad_list(request):
    data = MajorRoad_inspection.objects.all().order_by('-inspection_date')
    return render(request, 'inspection/list.html', {
        'data': data,
        'title': 'Major Roads Inspection',
        'add_url': 'dsd1_majorroad_add',
        'edit_url': 'dsd1_majorroad_update',
        'delete_url': 'dsd1_majorroad_delete',
    })


def dsd1_majorroad_add(request):
    form = MajorRoadInspectionFormDSD(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('dsd1_majorroad_list')
    return render(request, 'inspection/form.html', {'form': form, 'title': 'Add Major Road Inspection'})


def dsd1_majorroad_update(request, pk):
    obj = get_object_or_404(MajorRoad_inspection, pk=pk)
    form = MajorRoadInspectionFormDSD(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('dsd1_majorroad_list')
    return render(request, 'inspection/form.html', {'form': form, 'title': 'Edit Major Road Inspection'})


def dsd1_majorroad_delete(request, pk):
    get_object_or_404(MajorRoad_inspection, pk=pk).delete()
    return redirect('dsd1_majorroad_list')




def dsd2_trunk_list(request):
    data = TrunkSewer_inspection.objects.all().order_by('-inspection_date')
    return render(request, 'inspection/list.html', {
        'data': data,
        'title': 'Trunk Sewer Inspection',
        'add_url': 'dsd2_trunk_add',
        'edit_url': 'dsd2_trunk_update',
        'delete_url': 'dsd2_trunk_delete',
    })


def dsd2_trunk_add(request):
    form = TrunkSewerInspectionFormDSD(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('dsd2_trunk_list')
    return render(request, 'inspection/form.html', {'form': form, 'title': 'Add Trunk Sewer Inspection'})


def dsd2_trunk_update(request, pk):
    obj = get_object_or_404(TrunkSewer_inspection, pk=pk)
    form = TrunkSewerInspectionFormDSD(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('dsd2_trunk_list')
    return render(request, 'inspection/form.html', {'form': form, 'title': 'Edit Trunk Sewer Inspection'})


def dsd2_trunk_delete(request, pk):
    get_object_or_404(TrunkSewer_inspection, pk=pk).delete()
    return redirect('dsd2_trunk_list')




def dsd3_storm_list(request):
    data = StormDrain_inspection.objects.all().order_by('-inspection_date')
    return render(request, 'inspection/list.html', {
        'data': data,
        'title': 'Storm Drain Inspection',
        'add_url': 'dsd3_storm_add',
        'edit_url': 'dsd3_storm_update',
        'delete_url': 'dsd3_storm_delete',
    })


def dsd3_storm_add(request):
    form = StormDrainInspectionFormDSD(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('dsd3_storm_list')
    return render(request, 'inspection/form.html', {'form': form, 'title': 'Add Storm Drain Inspection'})


def dsd3_storm_update(request, pk):
    obj = get_object_or_404(StormDrain_inspection, pk=pk)
    form = StormDrainInspectionFormDSD(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('dsd3_storm_list')
    return render(request, 'inspection/form.html', {'form': form, 'title': 'Edit Storm Drain Inspection'})


def dsd3_storm_delete(request, pk):
    get_object_or_404(StormDrain_inspection, pk=pk).delete()
    return redirect('dsd3_storm_list')




def dsd4_ponding_list(request):
    data = PondingPoints_inspection.objects.all().order_by('-inspection_date')
    return render(request, 'inspection/list.html', {
        'data': data,
        'title': 'Ponding Points Inspection',
        'add_url': 'dsd4_ponding_add',
        'edit_url': 'dsd4_ponding_update',
        'delete_url': 'dsd4_ponding_delete',
    })


def dsd4_ponding_add(request):
    form = PondingPointsInspectionFormDSD(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('dsd4_ponding_list')
    return render(request, 'inspection/form.html', {'form': form, 'title': 'Add Ponding Point Inspection'})


def dsd4_ponding_update(request, pk):
    obj = get_object_or_404(PondingPoints_inspection, pk=pk)
    form = PondingPointsInspectionFormDSD(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('dsd4_ponding_list')
    return render(request, 'inspection/form.html', {'form': form, 'title': 'Edit Ponding Point Inspection'})


def dsd4_ponding_delete(request, pk):
    get_object_or_404(PondingPoints_inspection, pk=pk).delete()
    return redirect('dsd4_ponding_list')




from django.views.generic import ListView
from .models import MajorRoad_Add, TrunkSewer_Add, StormDrain_Add, PondingPoints_Add

# List Views
from django.views.generic import ListView
from django.db.models import Count, Q
from .models import MajorRoad_Add, Location

class MajorRoadListView(ListView):
    model = MajorRoad_Add   # ✅ IMPORTANT
    template_name = 'inspection/major_road_list.html'
    context_object_name = 'major_roads'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        location_filter = self.request.GET.get('location', '')
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # Default last 30 days
        if not from_date and not to_date:
            to_date_obj = date.today()
            from_date_obj = to_date_obj - timedelta(days=30)
        else:
            from_date_obj = parse_date(from_date) if from_date else None
            to_date_obj = parse_date(to_date) if to_date else None

        queryset = MajorRoad_Add.objects.exclude(
            location__location_name='Headoffice'
        ).filter(status='active')

        if search:
            queryset = queryset.filter(road__icontains=search)

        if location_filter:
            queryset = queryset.filter(location__id=location_filter)

        # Count inspections only within date range
        inspection_filter = Q()

        if from_date_obj and to_date_obj:
            inspection_filter &= Q(
                major_roads_inspection_new__inspection_date__range=(from_date_obj, to_date_obj)
            )
        elif from_date_obj:
            inspection_filter &= Q(
                major_roads_inspection_new__inspection_date__gte=from_date_obj
            )
        elif to_date_obj:
            inspection_filter &= Q(
                major_roads_inspection_new__inspection_date__lte=to_date_obj
            )

        queryset = queryset.annotate(
            total_inspections=Count(
                'major_roads_inspection_new',
                filter=inspection_filter,
                distinct=True
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # ✅ If no filter selected → auto last 30 days
        if not from_date and not to_date:
            to_date_obj = date.today()
            from_date_obj = to_date_obj - timedelta(days=30)

            # IMPORTANT: convert to YYYY-MM-DD for input type="date"
            context['from_date'] = from_date_obj.strftime('%Y-%m-%d')
            context['to_date'] = to_date_obj.strftime('%Y-%m-%d')
        else:
            context['from_date'] = from_date
            context['to_date'] = to_date

        context['locations'] = Location.objects.exclude(
            location_name='Headoffice'
        )

        return context


class TrunkSewerListView(ListView):
    model = TrunkSewer_Add
    template_name = 'inspection/trunk_sewer_list.html'
    context_object_name = 'trunk_sewers'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        location_filter = self.request.GET.get('location', '')
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        if not from_date and not to_date:
            to_date_obj = date.today()
            from_date_obj = to_date_obj - timedelta(days=30)
        else:
            from_date_obj = parse_date(from_date) if from_date else None
            to_date_obj = parse_date(to_date) if to_date else None

        queryset = TrunkSewer_Add.objects.exclude(
            location__location_name='Headoffice'
        ).filter(status='active')

        if search:
            queryset = queryset.filter(trunksewer__icontains=search)

        if location_filter:
            queryset = queryset.filter(location__id=location_filter)

        inspection_filter = Q()

        if from_date_obj and to_date_obj:
            inspection_filter &= Q(
                trunk_sewer_inspection_new__inspection_date__range=(from_date_obj, to_date_obj)
            )
        elif from_date_obj:
            inspection_filter &= Q(
                trunk_sewer_inspection_new__inspection_date__gte=from_date_obj
            )
        elif to_date_obj:
            inspection_filter &= Q(
                trunk_sewer_inspection_new__inspection_date__lte=to_date_obj
            )

        queryset = queryset.annotate(
            total_inspections=Count(
                'trunk_sewer_inspection_new',
                filter=inspection_filter,
                distinct=True
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        if not from_date and not to_date:
            to_date_obj = date.today()
            from_date_obj = to_date_obj - timedelta(days=30)
            context['from_date'] = from_date_obj.strftime('%Y-%m-%d')
            context['to_date'] = to_date_obj.strftime('%Y-%m-%d')
        else:
            context['from_date'] = from_date
            context['to_date'] = to_date

        context['locations'] = Location.objects.exclude(
            location_name='Headoffice'
        )

        return context



class StormDrainListView(ListView):
    model = StormDrain_Add
    template_name = 'inspection/storm_drain_list.html'
    context_object_name = 'storm_drains'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        location_filter = self.request.GET.get('location', '')
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # ✅ Default last 30 days
        if not from_date and not to_date:
            to_date_obj = date.today()
            from_date_obj = to_date_obj - timedelta(days=30)
        else:
            from_date_obj = parse_date(from_date) if from_date else None
            to_date_obj = parse_date(to_date) if to_date else None

        queryset = StormDrain_Add.objects.exclude(
            location__location_name='Headoffice'
        ).filter(status='active')

        if search:
            queryset = queryset.filter(stormdrain__icontains=search)

        if location_filter:
            queryset = queryset.filter(location__id=location_filter)

        # ✅ Filter only inspection count
        inspection_filter = Q()

        if from_date_obj and to_date_obj:
            inspection_filter &= Q(
                storm_drain_inspections_new__inspection_date__range=(from_date_obj, to_date_obj)
            )
        elif from_date_obj:
            inspection_filter &= Q(
                storm_drain_inspections_new__inspection_date__gte=from_date_obj
            )
        elif to_date_obj:
            inspection_filter &= Q(
                storm_drain_inspections_new__inspection_date__lte=to_date_obj
            )

        queryset = queryset.annotate(
            total_inspections=Count(
                'storm_drain_inspections_new',
                filter=inspection_filter,
                distinct=True
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # ✅ Auto select last 30 days in date inputs
        if not from_date and not to_date:
            to_date_obj = date.today()
            from_date_obj = to_date_obj - timedelta(days=30)

            context['from_date'] = from_date_obj.strftime('%Y-%m-%d')
            context['to_date'] = to_date_obj.strftime('%Y-%m-%d')
        else:
            context['from_date'] = from_date
            context['to_date'] = to_date

        context['locations'] = Location.objects.exclude(
            location_name='Headoffice'
        )

        return context


class PondingPointsListView_new(ListView):
    model = PondingPoints_Add
    template_name = 'inspection/ponding_points_list.html'
    context_object_name = 'ponding_points'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        location_filter = self.request.GET.get('location', '')
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # ✅ Default last 30 days
        if not from_date and not to_date:
            to_date_obj = date.today()
            from_date_obj = to_date_obj - timedelta(days=30)
        else:
            from_date_obj = parse_date(from_date) if from_date else None
            to_date_obj = parse_date(to_date) if to_date else None

        queryset = PondingPoints_Add.objects.exclude(
            location__location_name='Headoffice'
        ).filter(status='active')

        if search:
            queryset = queryset.filter(pondingpoints__icontains=search)

        if location_filter:
            queryset = queryset.filter(location__id=location_filter)

        # ✅ Filter only inspection count (NOT the queryset)
        inspection_filter = Q()

        if from_date_obj and to_date_obj:
            inspection_filter &= Q(
                ponding_points_inspections_new__inspection_date__range=(from_date_obj, to_date_obj)
            )
        elif from_date_obj:
            inspection_filter &= Q(
                ponding_points_inspections_new__inspection_date__gte=from_date_obj
            )
        elif to_date_obj:
            inspection_filter &= Q(
                ponding_points_inspections_new__inspection_date__lte=to_date_obj
            )

        queryset = queryset.annotate(
            total_inspections=Count(
                'ponding_points_inspections_new',
                filter=inspection_filter,
                distinct=True
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')

        # ✅ Auto-fill last 30 days if no date selected
        if not from_date and not to_date:
            to_date_obj = date.today()
            from_date_obj = to_date_obj - timedelta(days=30)

            context['from_date'] = from_date_obj.strftime('%Y-%m-%d')
            context['to_date'] = to_date_obj.strftime('%Y-%m-%d')
        else:
            context['from_date'] = from_date
            context['to_date'] = to_date

        context['locations'] = Location.objects.exclude(
            location_name='Headoffice'
        )

        return context


from django.views.generic import ListView
from django.utils.dateparse import parse_date
from .models import MajorRoad_inspection, TrunkSewer_inspection, StormDrain_inspection, PondingPoints_inspection, MajorRoad_Add, TrunkSewer_Add, StormDrain_Add, PondingPoints_Add
from datetime import date, timedelta
from django.views.generic import ListView
from django.utils.dateparse import parse_date
from django.db.models import Q, Count, Case, When, IntegerField
from django.db.models.functions import TruncDate
from collections import defaultdict


# ================= Major Roads Inspection Detail =================
from datetime import date, timedelta
from django.views.generic import ListView
from django.utils.dateparse import parse_date
from django.db.models import Count, Case, When, IntegerField


from datetime import date, timedelta
from django.db.models import Count, Case, When, IntegerField
from django.utils.dateparse import parse_date
from django.views.generic import ListView

class MajorRoadInspectionDetailView(ListView):
    model = None
    template_name = 'inspection/major_road_inspection_detail.html'
    context_object_name = 'inspections'

    def get_queryset(self):
        from .models import MajorRoad_inspection

        self.model = MajorRoad_inspection
        facility_id = self.kwargs['pk']

        today = date.today()
        last_30_days = today - timedelta(days=30)  # <-- Default from_date: 30 days ago

        # Get from/to from request, fallback to last 30 days
        from_date = self.request.GET.get('from')
        to_date = self.request.GET.get('to')

        from_date_obj = parse_date(from_date) if from_date else last_30_days
        to_date_obj = parse_date(to_date) if to_date else today

        qs = MajorRoad_inspection.objects.filter(
            facility_name_id=facility_id,
            inspection_date__gte=from_date_obj,
            inspection_date__lte=to_date_obj
        ).order_by('-inspection_date')

        return qs

    def get_context_data(self, **kwargs):
        from .models import MajorRoad_Add

        context = super().get_context_data(**kwargs)
        facility = MajorRoad_Add.objects.get(pk=self.kwargs['pk'])
        inspections = context['inspections']

        # -------------------------------
        # DATE RANGE (USED EVERYWHERE)
        # -------------------------------
        from_date_obj = parse_date(self.request.GET.get('from')) if self.request.GET.get('from') else date.today() - timedelta(days=30)
        to_date_obj = parse_date(self.request.GET.get('to')) if self.request.GET.get('to') else date.today()

        # -------------------------------
        # CARD 1: ACTUAL INSPECTIONS
        # -------------------------------
        actual_count = inspections.count()

        # -------------------------------
        # CARD 2: EXPECTED INSPECTIONS
        # -------------------------------
        expected_count = 0
        current = from_date_obj
        while current <= to_date_obj:
            if current.weekday() != 6:  # Exclude Sundays
                expected_count += 1
            current += timedelta(days=1)

        # -------------------------------
        # CARD 3: COMPLIANCE COUNT
        # -------------------------------
        compliance_count = inspections.filter(
            free_from_garbage_rubble='Yes',
            dry_and_clean='Yes'
        ).count()

        # -------------------------------
        # CARD 4: COMPLIANCE RATE
        # -------------------------------
        compliance_rate = (compliance_count / actual_count * 100) if actual_count > 0 else 0

        # -------------------------------
        # CARD 5: INSPECTION RATE
        # -------------------------------
        inspection_rate = (actual_count / expected_count * 100) if expected_count > 0 else 0

        # -------------------------------
        # DAILY TREND DATA
        # -------------------------------
        daily_data = inspections.values('inspection_date').annotate(
            total=Count('id'),
            compliant=Count(Case(
                When(free_from_garbage_rubble='Yes', dry_and_clean='Yes', then=1),
                output_field=IntegerField()
            ))
        ).order_by('inspection_date')

        trend_dates = [d['inspection_date'].strftime('%Y-%m-%d') for d in daily_data]
        trend_totals = [d['total'] for d in daily_data]
        trend_compliant = [d['compliant'] for d in daily_data]

        # -------------------------------
        # COMPLIANCE BREAKDOWN
        # -------------------------------
        garbage_yes = inspections.filter(free_from_garbage_rubble='Yes').count()
        garbage_no = inspections.filter(free_from_garbage_rubble='No').count()

        clean_yes = inspections.filter(dry_and_clean='Yes').count()
        clean_no = inspections.filter(dry_and_clean='No').count()

        # -------------------------------
        # ZONE-WISE ANALYSIS
        # -------------------------------
        zone_stats = inspections.values('zone__location_name').annotate(
            total=Count('id'),
            compliant=Count(Case(
                When(free_from_garbage_rubble='Yes', dry_and_clean='Yes', then=1),
                output_field=IntegerField()
            ))
        ).order_by('-total')

        zone_names = [z['zone__location_name'] for z in zone_stats]
        zone_totals = [z['total'] for z in zone_stats]
        zone_compliant = [z['compliant'] for z in zone_stats]

        # -------------------------------
        # EMPLOYEE PERFORMANCE
        # -------------------------------
        emp_stats = inspections.exclude(
            emp_name__isnull=True
        ).exclude(
            emp_name=''
        ).values('emp_name').annotate(
            total=Count('id'),
            compliant=Count(Case(
                When(free_from_garbage_rubble='Yes', dry_and_clean='Yes', then=1),
                output_field=IntegerField()
            ))
        ).order_by('-total')[:10]

        emp_names = [e['emp_name'] for e in emp_stats]
        emp_totals = [e['total'] for e in emp_stats]
        emp_compliant = [e['compliant'] for e in emp_stats]

        # -------------------------------
        # MISSING INSPECTION DATES
        # -------------------------------
        inspection_dates = set(inspections.values_list('inspection_date', flat=True))
        missing_dates = []
        current = from_date_obj
        while current <= to_date_obj:
            if current.weekday() != 6 and current not in inspection_dates:
                missing_dates.append(current)
            current += timedelta(days=1)

        # -------------------------------
        # RECENT NON-COMPLIANT
        # -------------------------------
        non_compliant = inspections.exclude(
            free_from_garbage_rubble='Yes',
            dry_and_clean='Yes'
        ).order_by('-inspection_date')[:5]

        # -------------------------------
        # CONTEXT
        # -------------------------------
        context.update({
            'facility': facility,
            'from_date': from_date_obj.strftime('%Y-%m-%d'),
            'to_date': to_date_obj.strftime('%Y-%m-%d'),

            'actual_count': actual_count,
            'expected_count': expected_count,
            'compliance_count': compliance_count,
            'compliance_rate': round(compliance_rate, 1),
            'inspection_rate': round(inspection_rate, 1),

            'trend_dates': trend_dates,
            'trend_totals': trend_totals,
            'trend_compliant': trend_compliant,

            'garbage_yes': garbage_yes,
            'garbage_no': garbage_no,
            'clean_yes': clean_yes,
            'clean_no': clean_no,

            'zone_names': zone_names,
            'zone_totals': zone_totals,
            'zone_compliant': zone_compliant,

            'emp_names': emp_names,
            'emp_totals': emp_totals,
            'emp_compliant': emp_compliant,

            'missing_dates': missing_dates,
            'non_compliant': non_compliant,
        })

        return context

# ================= Trunk Sewer Inspection Detail =================
from datetime import date, timedelta
from django.db.models import Count, Case, When, IntegerField
from django.utils.dateparse import parse_date
from django.views.generic import ListView

class TrunkSewerInspectionDetailView(ListView):
    model = None
    template_name = 'inspection/trunk_sewer_inspection_detail.html'
    context_object_name = 'inspections'

    def get_queryset(self):
        from .models import TrunkSewer_inspection

        self.model = TrunkSewer_inspection
        facility_id = self.kwargs['pk']

        today = date.today()
        last_30_days = today - timedelta(days=30)  # <-- Default from_date: last 30 days

        from_param = self.request.GET.get('from')
        to_param = self.request.GET.get('to')

        from_date = parse_date(from_param) if from_param else last_30_days
        to_date = parse_date(to_param) if to_param else today

        return TrunkSewer_inspection.objects.filter(
            facility_name_id=facility_id,
            inspection_date__gte=from_date,
            inspection_date__lte=to_date
        ).order_by('-inspection_date')

    def get_context_data(self, **kwargs):
        from .models import TrunkSewer_Add

        context = super().get_context_data(**kwargs)
        inspections = context['inspections']
        facility = TrunkSewer_Add.objects.get(pk=self.kwargs['pk'])

        today = date.today()
        from_date = parse_date(self.request.GET.get('from')) if self.request.GET.get('from') else today - timedelta(days=30)
        to_date = parse_date(self.request.GET.get('to')) if self.request.GET.get('to') else today

        # -------------------------------
        # CARD 1: ACTUAL INSPECTIONS
        # -------------------------------
        actual_count = inspections.count()

        # -------------------------------
        # CARD 2: EXPECTED INSPECTIONS
        # -------------------------------
        expected_count = 0
        current = from_date
        while current <= to_date:
            if current.weekday() != 6:  # Exclude Sundays
                expected_count += 1
            current += timedelta(days=1)

        # -------------------------------
        # CARD 3: FULL COMPLIANCE COUNT
        # -------------------------------
        compliance_filter = {
            'manhole_covered': 'Yes',
            'manhole_free_from_damage': 'Yes',
            'no_sediment_around_manhole': 'Yes',
            'no_outflow_of_sewage_from_manhole': 'Yes',
            'no_bad_odour_around_manhole': 'Yes',
            'no_blockage_at_outflow_of_drain': 'Yes',
            'fastflow_of_water_at_outflow_of_drain': 'Yes',
        }

        compliance_count = inspections.filter(**compliance_filter).count()

        # -------------------------------
        # CARD 4: COMPLIANCE RATE
        # -------------------------------
        compliance_rate = (compliance_count / actual_count * 100) if actual_count else 0

        # -------------------------------
        # CARD 5: INSPECTION RATE
        # -------------------------------
        inspection_rate = (actual_count / expected_count * 100) if expected_count else 0

        # -------------------------------
        # DAILY TREND DATA
        # -------------------------------
        daily_data = inspections.values('inspection_date').annotate(
            total=Count('id'),
            compliant=Count(
                Case(
                    When(**compliance_filter, then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('inspection_date')

        trend_dates = [i['inspection_date'].strftime('%Y-%m-%d') for i in daily_data]
        trend_totals = [i['total'] for i in daily_data]
        trend_compliant = [i['compliant'] for i in daily_data]

        # -------------------------------
        # FIELD-WISE COMPLIANCE COUNTS
        # -------------------------------
        manhole_covered_yes = inspections.filter(manhole_covered='Yes').count()
        manhole_covered_no = inspections.filter(manhole_covered='No').count()

        manhole_free_yes = inspections.filter(manhole_free_from_damage='Yes').count()
        manhole_free_no = inspections.filter(manhole_free_from_damage='No').count()

        no_sediment_yes = inspections.filter(no_sediment_around_manhole='Yes').count()
        no_sediment_no = inspections.filter(no_sediment_around_manhole='No').count()

        no_outflow_yes = inspections.filter(no_outflow_of_sewage_from_manhole='Yes').count()
        no_outflow_no = inspections.filter(no_outflow_of_sewage_from_manhole='No').count()

        no_odour_yes = inspections.filter(no_bad_odour_around_manhole='Yes').count()
        no_odour_no = inspections.filter(no_bad_odour_around_manhole='No').count()

        no_blockage_yes = inspections.filter(no_blockage_at_outflow_of_drain='Yes').count()
        no_blockage_no = inspections.filter(no_blockage_at_outflow_of_drain='No').count()

        fastflow_yes = inspections.filter(fastflow_of_water_at_outflow_of_drain='Yes').count()
        fastflow_no = inspections.filter(fastflow_of_water_at_outflow_of_drain='No').count()

        # -------------------------------
        # ZONE-WISE ANALYSIS
        # -------------------------------
        zone_stats = inspections.values('zone__location_name').annotate(
            total=Count('id'),
            compliant=Count(
                Case(
                    When(**compliance_filter, then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('-total')

        zone_names = [i['zone__location_name'] for i in zone_stats]
        zone_totals = [i['total'] for i in zone_stats]
        zone_compliant = [i['compliant'] for i in zone_stats]

        # -------------------------------
        # EMPLOYEE PERFORMANCE (Top 10)
        # -------------------------------
        emp_stats = inspections.exclude(
            emp_name__isnull=True
        ).exclude(
            emp_name=''
        ).values('emp_name').annotate(
            total=Count('id'),
            compliant=Count(
                Case(
                    When(**compliance_filter, then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('-total')[:10]

        emp_names = [i['emp_name'] for i in emp_stats]
        emp_totals = [i['total'] for i in emp_stats]
        emp_compliant = [i['compliant'] for i in emp_stats]

        # -------------------------------
        # MISSING INSPECTION DATES
        # -------------------------------
        inspection_dates = set(inspections.values_list('inspection_date', flat=True))
        missing_dates = []

        current = from_date
        while current <= to_date:
            if current.weekday() != 6 and current not in inspection_dates:
                missing_dates.append(current)
            current += timedelta(days=1)

        # -------------------------------
        # RECENT NON-COMPLIANT INSPECTIONS
        # -------------------------------
        non_compliant = inspections.exclude(**compliance_filter)[:5]

        # -------------------------------
        # CONTEXT
        # -------------------------------
        context.update({
            'facility': facility,
            'from_date': from_date.strftime('%Y-%m-%d'),
            'to_date': to_date.strftime('%Y-%m-%d'),

            'actual_count': actual_count,
            'expected_count': expected_count,
            'compliance_count': compliance_count,
            'compliance_rate': round(compliance_rate, 1),
            'inspection_rate': round(inspection_rate, 1),

            'trend_dates': trend_dates,
            'trend_totals': trend_totals,
            'trend_compliant': trend_compliant,

            'field_names': [
                'Manhole Covered', 'Free from Damage', 'No Sediment', 'No Sewage Outflow',
                'No Bad Odour', 'No Blockage', 'Fast Flow'
            ],
            'field_yes_counts': [
                manhole_covered_yes, manhole_free_yes, no_sediment_yes,
                no_outflow_yes, no_odour_yes, no_blockage_yes, fastflow_yes
            ],
            'field_no_counts': [
                manhole_covered_no, manhole_free_no, no_sediment_no,
                no_outflow_no, no_odour_no, no_blockage_no, fastflow_no
            ],

            'zone_names': zone_names,
            'zone_totals': zone_totals,
            'zone_compliant': zone_compliant,

            'emp_names': emp_names,
            'emp_totals': emp_totals,
            'emp_compliant': emp_compliant,

            'missing_dates': missing_dates,
            'non_compliant': non_compliant,
        })

        return context

# ================= Storm Drain Inspection Detail =================
from datetime import date, timedelta
from django.db.models import Count, Case, When, IntegerField
from django.utils.dateparse import parse_date
from django.views.generic import ListView

class StormDrainInspectionDetailView(ListView):
    model = None
    template_name = 'inspection/storm_drain_inspection_detail.html'
    context_object_name = 'inspections'

    def get_queryset(self):
        from .models import StormDrain_inspection

        self.model = StormDrain_inspection
        facility_id = self.kwargs['pk']

        today = date.today()
        last_30_days = today - timedelta(days=30)  # <-- Default from_date: last 30 days

        from_param = self.request.GET.get('from')
        to_param = self.request.GET.get('to')

        from_date = parse_date(from_param) if from_param else last_30_days
        to_date = parse_date(to_param) if to_param else today

        return StormDrain_inspection.objects.filter(
            facility_name_id=facility_id,
            inspection_date__gte=from_date,
            inspection_date__lte=to_date
        ).order_by('-inspection_date')

    def get_context_data(self, **kwargs):
        from .models import StormDrain_Add

        context = super().get_context_data(**kwargs)
        inspections = context['inspections']
        facility = StormDrain_Add.objects.get(pk=self.kwargs['pk'])

        today = date.today()
        from_date = parse_date(self.request.GET.get('from')) if self.request.GET.get('from') else today - timedelta(days=30)
        to_date = parse_date(self.request.GET.get('to')) if self.request.GET.get('to') else today

        # -------------------------------
        # CARD 1: ACTUAL INSPECTIONS
        # -------------------------------
        actual_count = inspections.count()

        # -------------------------------
        # CARD 2: EXPECTED INSPECTIONS
        # -------------------------------
        expected_count = 0
        current = from_date
        while current <= to_date:
            if current.weekday() != 6:  # Exclude Sundays
                expected_count += 1
            current += timedelta(days=1)

        # -------------------------------
        # CARD 3: COMPLIANCE COUNT
        # -------------------------------
        compliance_count = inspections.filter(
            entry_clear='Yes',
            exit_clear='Yes'
        ).count()

        # -------------------------------
        # CARD 4: COMPLIANCE RATE
        # -------------------------------
        compliance_rate = (compliance_count / actual_count * 100) if actual_count else 0

        # -------------------------------
        # CARD 5: INSPECTION RATE
        # -------------------------------
        inspection_rate = (actual_count / expected_count * 100) if expected_count else 0

        # -------------------------------
        # DAILY TREND DATA
        # -------------------------------
        daily_data = inspections.values('inspection_date').annotate(
            total=Count('id'),
            compliant=Count(
                Case(
                    When(entry_clear='Yes', exit_clear='Yes', then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('inspection_date')

        trend_dates = [i['inspection_date'].strftime('%Y-%m-%d') for i in daily_data]
        trend_totals = [i['total'] for i in daily_data]
        trend_compliant = [i['compliant'] for i in daily_data]

        # -------------------------------
        # COMPLIANCE BREAKDOWN
        # -------------------------------
        entry_yes = inspections.filter(entry_clear='Yes').count()
        entry_no = inspections.filter(entry_clear='No').count()
        exit_yes = inspections.filter(exit_clear='Yes').count()
        exit_no = inspections.filter(exit_clear='No').count()

        # -------------------------------
        # ZONE-WISE ANALYSIS
        # -------------------------------
        zone_stats = inspections.values('zone__location_name').annotate(
            total=Count('id'),
            compliant=Count(
                Case(
                    When(entry_clear='Yes', exit_clear='Yes', then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('-total')

        zone_names = [i['zone__location_name'] for i in zone_stats]
        zone_totals = [i['total'] for i in zone_stats]
        zone_compliant = [i['compliant'] for i in zone_stats]

        # -------------------------------
        # EMPLOYEE PERFORMANCE (Top 10)
        # -------------------------------
        emp_stats = inspections.exclude(
            emp_name__isnull=True
        ).exclude(
            emp_name=''
        ).values('emp_name').annotate(
            total=Count('id'),
            compliant=Count(
                Case(
                    When(entry_clear='Yes', exit_clear='Yes', then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('-total')[:10]

        emp_names = [i['emp_name'] for i in emp_stats]
        emp_totals = [i['total'] for i in emp_stats]
        emp_compliant = [i['compliant'] for i in emp_stats]

        # -------------------------------
        # MISSING INSPECTION DATES
        # -------------------------------
        inspection_dates = set(inspections.values_list('inspection_date', flat=True))
        missing_dates = []

        current = from_date
        while current <= to_date:
            if current.weekday() != 6 and current not in inspection_dates:
                missing_dates.append(current)
            current += timedelta(days=1)

        # -------------------------------
        # RECENT NON-COMPLIANT INSPECTIONS
        # -------------------------------
        non_compliant = inspections.exclude(
            entry_clear='Yes',
            exit_clear='Yes'
        )[:5]

        context.update({
            'facility': facility,
            'from_date': from_date.strftime('%Y-%m-%d'),
            'to_date': to_date.strftime('%Y-%m-%d'),

            'actual_count': actual_count,
            'expected_count': expected_count,
            'compliance_count': compliance_count,
            'compliance_rate': round(compliance_rate, 1),
            'inspection_rate': round(inspection_rate, 1),

            'trend_dates': trend_dates,
            'trend_totals': trend_totals,
            'trend_compliant': trend_compliant,

            'entry_yes': entry_yes,
            'entry_no': entry_no,
            'exit_yes': exit_yes,
            'exit_no': exit_no,

            'zone_names': zone_names,
            'zone_totals': zone_totals,
            'zone_compliant': zone_compliant,

            'emp_names': emp_names,
            'emp_totals': emp_totals,
            'emp_compliant': emp_compliant,

            'missing_dates': missing_dates,
            'non_compliant': non_compliant,
        })

        return context


# ================= Ponding Points Inspection Detail =================
from datetime import date, timedelta
from django.db.models import Count, Case, When, IntegerField
from django.utils.dateparse import parse_date
from django.views.generic import ListView

class PondingPointsInspectionDetailView(ListView):
    model = None
    template_name = 'inspection/ponding_points_inspection_detail.html'
    context_object_name = 'inspections'

    def get_queryset(self):
        from .models import PondingPoints_inspection

        self.model = PondingPoints_inspection
        facility_id = self.kwargs['pk']

        today = date.today()
        last_30_days = today - timedelta(days=30)  # <-- default from_date: last 30 days

        from_param = self.request.GET.get('from')
        to_param = self.request.GET.get('to')

        from_date = parse_date(from_param) if from_param else last_30_days
        to_date = parse_date(to_param) if to_param else today

        return PondingPoints_inspection.objects.filter(
            facility_name_id=facility_id,
            inspection_date__gte=from_date,
            inspection_date__lte=to_date
        ).order_by('-inspection_date')

    def get_context_data(self, **kwargs):
        from .models import PondingPoints_Add

        context = super().get_context_data(**kwargs)

        inspections = context['inspections']
        facility = PondingPoints_Add.objects.get(pk=self.kwargs['pk'])

        today = date.today()
        from_date = parse_date(self.request.GET.get('from')) if self.request.GET.get('from') else today - timedelta(days=30)
        to_date = parse_date(self.request.GET.get('to')) if self.request.GET.get('to') else today

        # -------------------------------
        # CARD 1: ACTUAL INSPECTIONS
        # -------------------------------
        actual_count = inspections.count()

        # -------------------------------
        # CARD 2: EXPECTED INSPECTIONS
        # -------------------------------
        expected_count = 0
        current = from_date
        while current <= to_date:
            if current.weekday() != 6:  # Exclude Sundays
                expected_count += 1
            current += timedelta(days=1)

        # -------------------------------
        # CARD 3: GOVERNMENT ATTEMPT COUNT
        # -------------------------------
        govt_attempt_count = inspections.filter(any_attempt_by_government='Yes').count()

        # -------------------------------
        # CARD 4: GOVERNMENT ATTEMPT RATE
        # -------------------------------
        govt_attempt_rate = (govt_attempt_count / actual_count * 100) if actual_count else 0

        # -------------------------------
        # CARD 5: INSPECTION RATE
        # -------------------------------
        inspection_rate = (actual_count / expected_count * 100) if expected_count else 0

        # -------------------------------
        # DAILY TREND DATA
        # -------------------------------
        daily_data = inspections.values('inspection_date').annotate(
            total=Count('id'),
            govt_attempt=Count(
                Case(
                    When(any_attempt_by_government='Yes', then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('inspection_date')

        trend_dates = [i['inspection_date'].strftime('%Y-%m-%d') for i in daily_data]
        trend_totals = [i['total'] for i in daily_data]
        trend_govt_attempt = [i['govt_attempt'] for i in daily_data]

        # -------------------------------
        # GOVERNMENT ATTEMPT BREAKDOWN
        # -------------------------------
        govt_yes = govt_attempt_count
        govt_no = inspections.filter(any_attempt_by_government='No').count()

        # -------------------------------
        # ZONE-WISE ANALYSIS
        # -------------------------------
        zone_stats = inspections.values('zone__location_name').annotate(
            total=Count('id'),
            govt_attempt=Count(
                Case(
                    When(any_attempt_by_government='Yes', then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('-total')

        zone_names = [i['zone__location_name'] for i in zone_stats]
        zone_totals = [i['total'] for i in zone_stats]
        zone_govt_attempt = [i['govt_attempt'] for i in zone_stats]

        # -------------------------------
        # EMPLOYEE PERFORMANCE (Top 10)
        # -------------------------------
        emp_stats = inspections.exclude(
            emp_name__isnull=True
        ).exclude(
            emp_name=''
        ).values('emp_name').annotate(
            total=Count('id'),
            govt_attempt=Count(
                Case(
                    When(any_attempt_by_government='Yes', then=1),
                    output_field=IntegerField()
                )
            )
        ).order_by('-total')[:10]

        emp_names = [i['emp_name'] for i in emp_stats]
        emp_totals = [i['total'] for i in emp_stats]
        emp_govt_attempt = [i['govt_attempt'] for i in emp_stats]

        # -------------------------------
        # MISSING INSPECTION DATES
        # -------------------------------
        inspection_dates = set(inspections.values_list('inspection_date', flat=True))
        missing_dates = []

        current = from_date
        while current <= to_date:
            if current.weekday() != 6 and current not in inspection_dates:
                missing_dates.append(current)
            current += timedelta(days=1)

        # -------------------------------
        # RECENT INSPECTIONS
        # -------------------------------
        govt_attempts = inspections.filter(any_attempt_by_government='Yes')[:5]
        no_govt_attempts = inspections.filter(any_attempt_by_government='No')[:5]

        context.update({
            'facility': facility,
            'from_date': from_date.strftime('%Y-%m-%d'),
            'to_date': to_date.strftime('%Y-%m-%d'),

            'actual_count': actual_count,
            'expected_count': expected_count,
            'govt_attempt_count': govt_attempt_count,
            'govt_attempt_rate': round(govt_attempt_rate, 1),
            'inspection_rate': round(inspection_rate, 1),

            'trend_dates': trend_dates,
            'trend_totals': trend_totals,
            'trend_govt_attempt': trend_govt_attempt,

            'govt_yes': govt_yes,
            'govt_no': govt_no,

            'zone_names': zone_names,
            'zone_totals': zone_totals,
            'zone_govt_attempt': zone_govt_attempt,

            'emp_names': emp_names,
            'emp_totals': emp_totals,
            'emp_govt_attempt': emp_govt_attempt,

            'missing_dates': missing_dates,
            'govt_attempts': govt_attempts,
            'no_govt_attempts': no_govt_attempts,
        })

        return context




from django.shortcuts import render
from django.db.models import Count
from datetime import date

from .models import (
    MajorRoad_Add, TrunkSewer_Add, StormDrain_Add, PondingPoints_Add,
    MajorRoad_inspection, TrunkSewer_inspection,
    StormDrain_inspection, PondingPoints_inspection
)


from django.db.models import Count, Q, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta, date



@login_required
def dsd_dashboard(request):
    today = date.today()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    current_month_start = today.replace(day=1)
    
    # ===== Active Facilities Only =====
    active_major_roads = MajorRoad_Add.objects.filter(status='active')
    active_trunk_sewers = TrunkSewer_Add.objects.filter(status='active')
    active_storm_drains = StormDrain_Add.objects.filter(status='active')
    active_ponding_points = PondingPoints_Add.objects.filter(status='active')

    # ===== Facility Counts (Active Only) =====
    major_road_count = active_major_roads.count()
    trunk_sewer_count = active_trunk_sewers.count()
    storm_drain_count = active_storm_drains.count()
    ponding_point_count = active_ponding_points.count()
    total_facilities = major_road_count + trunk_sewer_count + storm_drain_count + ponding_point_count

    # ===== Inspection Counts (Active Facilities Only) =====
    major_road_inspections = MajorRoad_inspection.objects.filter(facility_name__status='active').count()
    trunk_sewer_inspections = TrunkSewer_inspection.objects.filter(facility_name__status='active').count()
    storm_drain_inspections = StormDrain_inspection.objects.filter(facility_name__status='active').count()
    ponding_point_inspections = PondingPoints_inspection.objects.filter(facility_name__status='active').count()
    total_inspections = (major_road_inspections + trunk_sewer_inspections +
                        storm_drain_inspections + ponding_point_inspections)

    # ===== Expected Inspections Calculation (1 Dec 2025 to Today, excluding Sundays) =====
    start_date = date(2025, 12, 1)

    if today < start_date:
        working_days = 0
    else:
        working_days = sum(
            1 for i in range((today - start_date).days + 1)
            if (start_date + timedelta(days=i)).weekday() != 6
        )

    expected_inspections_total = working_days * total_facilities
    inspection_achievement_rate = (
        (total_inspections / expected_inspections_total) * 100
        if expected_inspections_total > 0 else 0
    )

    expected_major_road = working_days * major_road_count
    expected_trunk_sewer = working_days * trunk_sewer_count
    expected_storm_drain = working_days * storm_drain_count
    expected_ponding_point = working_days * ponding_point_count

    major_road_achievement = (major_road_inspections / expected_major_road * 100) if expected_major_road > 0 else 0
    trunk_sewer_achievement = (trunk_sewer_inspections / expected_trunk_sewer * 100) if expected_trunk_sewer > 0 else 0
    storm_drain_achievement = (storm_drain_inspections / expected_storm_drain * 100) if expected_storm_drain > 0 else 0
    ponding_point_achievement = (ponding_point_inspections / expected_ponding_point * 100) if expected_ponding_point > 0 else 0

    # ===== Recent Inspections (Last 7 & 30 Days) — Active Only =====
    major_road_last_7 = MajorRoad_inspection.objects.filter(facility_name__status='active', inspection_date__gte=last_7_days).count()
    trunk_sewer_last_7 = TrunkSewer_inspection.objects.filter(facility_name__status='active', inspection_date__gte=last_7_days).count()
    storm_drain_last_7 = StormDrain_inspection.objects.filter(facility_name__status='active', inspection_date__gte=last_7_days).count()
    ponding_point_last_7 = PondingPoints_inspection.objects.filter(facility_name__status='active', inspection_date__gte=last_7_days).count()
    total_last_7_days = major_road_last_7 + trunk_sewer_last_7 + storm_drain_last_7 + ponding_point_last_7

    major_road_last_30 = MajorRoad_inspection.objects.filter(facility_name__status='active', inspection_date__gte=last_30_days).count()
    trunk_sewer_last_30 = TrunkSewer_inspection.objects.filter(facility_name__status='active', inspection_date__gte=last_30_days).count()
    storm_drain_last_30 = StormDrain_inspection.objects.filter(facility_name__status='active', inspection_date__gte=last_30_days).count()
    ponding_point_last_30 = PondingPoints_inspection.objects.filter(facility_name__status='active', inspection_date__gte=last_30_days).count()
    total_last_30_days = major_road_last_30 + trunk_sewer_last_30 + storm_drain_last_30 + ponding_point_last_30

    # ===== This Month Inspections — Active Only =====
    major_road_this_month = MajorRoad_inspection.objects.filter(facility_name__status='active', inspection_date__gte=current_month_start).count()
    trunk_sewer_this_month = TrunkSewer_inspection.objects.filter(facility_name__status='active', inspection_date__gte=current_month_start).count()
    storm_drain_this_month = StormDrain_inspection.objects.filter(facility_name__status='active', inspection_date__gte=current_month_start).count()
    ponding_point_this_month = PondingPoints_inspection.objects.filter(facility_name__status='active', inspection_date__gte=current_month_start).count()
    total_this_month = major_road_this_month + trunk_sewer_this_month + storm_drain_this_month + ponding_point_this_month

    # ===== Compliance/Pass Rates — Active Only =====
    major_road_pass = MajorRoad_inspection.objects.filter(
        facility_name__status='active',
        free_from_garbage_rubble='Yes',
        dry_and_clean='Yes'
    ).count()
    major_road_pass_rate = (major_road_pass / major_road_inspections * 100) if major_road_inspections > 0 else 0

    trunk_sewer_pass = TrunkSewer_inspection.objects.filter(
        facility_name__status='active',
        manhole_covered='Yes',
        manhole_free_from_damage='Yes',
        no_sediment_around_manhole='Yes',
        no_outflow_of_sewage_from_manhole='Yes',
        no_bad_odour_around_manhole='Yes',
        no_blockage_at_outflow_of_drain='Yes',
        fastflow_of_water_at_outflow_of_drain='Yes'
    ).count()
    trunk_sewer_pass_rate = (trunk_sewer_pass / trunk_sewer_inspections * 100) if trunk_sewer_inspections > 0 else 0

    storm_drain_pass = StormDrain_inspection.objects.filter(
        facility_name__status='active',
        entry_clear='Yes',
        exit_clear='Yes'
    ).count()
    storm_drain_pass_rate = (storm_drain_pass / storm_drain_inspections * 100) if storm_drain_inspections > 0 else 0

    ponding_point_pass = PondingPoints_inspection.objects.filter(
        facility_name__status='active',
        any_attempt_by_government='Yes'
    ).count()
    ponding_point_pass_rate = (ponding_point_pass / ponding_point_inspections * 100) if ponding_point_inspections > 0 else 0

    total_pass = major_road_pass + trunk_sewer_pass + storm_drain_pass + ponding_point_pass
    overall_compliance_rate = (total_pass / total_inspections * 100) if total_inspections > 0 else 0

    # ===== Inspection Coverage — Active Only =====
    major_roads_inspected = MajorRoad_inspection.objects.filter(facility_name__status='active').values('facility_name').distinct().count()
    trunk_sewers_inspected = TrunkSewer_inspection.objects.filter(facility_name__status='active').values('facility_name').distinct().count()
    storm_drains_inspected = StormDrain_inspection.objects.filter(facility_name__status='active').values('facility_name').distinct().count()
    ponding_points_inspected = PondingPoints_inspection.objects.filter(facility_name__status='active').values('facility_name').distinct().count()

    major_road_coverage = (major_roads_inspected / major_road_count * 100) if major_road_count > 0 else 0
    trunk_sewer_coverage = (trunk_sewers_inspected / trunk_sewer_count * 100) if trunk_sewer_count > 0 else 0
    storm_drain_coverage = (storm_drains_inspected / storm_drain_count * 100) if storm_drain_count > 0 else 0
    ponding_point_coverage = (ponding_points_inspected / ponding_point_count * 100) if ponding_point_count > 0 else 0

    total_facilities_inspected = (major_roads_inspected + trunk_sewers_inspected +
                                 storm_drains_inspected + ponding_points_inspected)
    overall_coverage = (total_facilities_inspected / total_facilities * 100) if total_facilities > 0 else 0

    # ===== Zone-wise Statistics — Active Only =====
    zones = Location.objects.all()
    zone_stats = []

    for zone in zones:
        zone_data = {
            'name': zone.location_name,
            'major_road_inspections': MajorRoad_inspection.objects.filter(zone=zone, facility_name__status='active').count(),
            'trunk_sewer_inspections': TrunkSewer_inspection.objects.filter(zone=zone, facility_name__status='active').count(),
            'storm_drain_inspections': StormDrain_inspection.objects.filter(zone=zone, facility_name__status='active').count(),
            'ponding_point_inspections': PondingPoints_inspection.objects.filter(zone=zone, facility_name__status='active').count(),
        }
        zone_data['total'] = (zone_data['major_road_inspections'] + zone_data['trunk_sewer_inspections'] +
                             zone_data['storm_drain_inspections'] + zone_data['ponding_point_inspections'])
        zone_stats.append(zone_data)

    zone_stats = sorted(zone_stats, key=lambda x: x['total'], reverse=True)

    # ===== Top Performing Zones (by compliance) — Active Only =====
    zone_compliance = []
    for zone in zones:
        mr_total = MajorRoad_inspection.objects.filter(zone=zone, facility_name__status='active').count()
        mr_pass = MajorRoad_inspection.objects.filter(
            zone=zone, facility_name__status='active',
            free_from_garbage_rubble='Yes', dry_and_clean='Yes'
        ).count()

        ts_total = TrunkSewer_inspection.objects.filter(zone=zone, facility_name__status='active').count()
        ts_pass = TrunkSewer_inspection.objects.filter(
            zone=zone, facility_name__status='active',
            manhole_covered='Yes', manhole_free_from_damage='Yes',
            no_sediment_around_manhole='Yes', no_outflow_of_sewage_from_manhole='Yes',
            no_bad_odour_around_manhole='Yes', no_blockage_at_outflow_of_drain='Yes',
            fastflow_of_water_at_outflow_of_drain='Yes'
        ).count()

        sd_total = StormDrain_inspection.objects.filter(zone=zone, facility_name__status='active').count()
        sd_pass = StormDrain_inspection.objects.filter(
            zone=zone, facility_name__status='active',
            entry_clear='Yes', exit_clear='Yes'
        ).count()

        pp_total = PondingPoints_inspection.objects.filter(zone=zone, facility_name__status='active').count()
        pp_pass = PondingPoints_inspection.objects.filter(
            zone=zone, facility_name__status='active',
            any_attempt_by_government='Yes'
        ).count()

        total_zone_inspections = mr_total + ts_total + sd_total + pp_total
        total_zone_pass = mr_pass + ts_pass + sd_pass + pp_pass

        if total_zone_inspections > 0:
            compliance_rate = (total_zone_pass / total_zone_inspections * 100)
            zone_compliance.append({
                'name': zone.location_name,
                'compliance_rate': compliance_rate,
                'total_inspections': total_zone_inspections
            })

    zone_compliance = sorted(zone_compliance, key=lambda x: x['compliance_rate'], reverse=True)[:5]

    # ===== Recent Inspections List — Active Only =====
    recent_major_roads = MajorRoad_inspection.objects.filter(facility_name__status='active').select_related('zone', 'facility_name').order_by('-inspection_date')[:3]
    recent_trunk_sewers = TrunkSewer_inspection.objects.filter(facility_name__status='active').select_related('zone', 'facility_name').order_by('-inspection_date')[:3]
    recent_storm_drains = StormDrain_inspection.objects.filter(facility_name__status='active').select_related('zone', 'facility_name').order_by('-inspection_date')[:3]
    recent_ponding_points = PondingPoints_inspection.objects.filter(facility_name__status='active').select_related('zone', 'facility_name').order_by('-inspection_date')[:3]

    # ===== Issues/Failures Count — Active Only =====
    major_road_issues = MajorRoad_inspection.objects.filter(
        facility_name__status='active'
    ).filter(Q(free_from_garbage_rubble='No') | Q(dry_and_clean='No')).count()

    trunk_sewer_issues = TrunkSewer_inspection.objects.filter(
        facility_name__status='active'
    ).filter(
        Q(manhole_covered='No') | Q(manhole_free_from_damage='No') |
        Q(no_sediment_around_manhole='No') | Q(no_outflow_of_sewage_from_manhole='No') |
        Q(no_bad_odour_around_manhole='No') | Q(no_blockage_at_outflow_of_drain='No') |
        Q(fastflow_of_water_at_outflow_of_drain='No')
    ).count()

    storm_drain_issues = StormDrain_inspection.objects.filter(
        facility_name__status='active'
    ).filter(Q(entry_clear='No') | Q(exit_clear='No')).count()

    ponding_point_issues = PondingPoints_inspection.objects.filter(
        facility_name__status='active',
        any_attempt_by_government='No'
    ).count()

    total_issues = major_road_issues + trunk_sewer_issues + storm_drain_issues + ponding_point_issues

    # ===== Average Inspections per Active Facility =====
    avg_major_road = (major_road_inspections / major_road_count) if major_road_count > 0 else 0
    avg_trunk_sewer = (trunk_sewer_inspections / trunk_sewer_count) if trunk_sewer_count > 0 else 0
    avg_storm_drain = (storm_drain_inspections / storm_drain_count) if storm_drain_count > 0 else 0
    avg_ponding_point = (ponding_point_inspections / ponding_point_count) if ponding_point_count > 0 else 0

    # ===== Percentage Distribution for Progress Bars =====
    major_road_percentage = (major_road_inspections / total_inspections * 100) if total_inspections > 0 else 0
    trunk_sewer_percentage = (trunk_sewer_inspections / total_inspections * 100) if total_inspections > 0 else 0
    storm_drain_percentage = (storm_drain_inspections / total_inspections * 100) if total_inspections > 0 else 0
    ponding_point_percentage = (ponding_point_inspections / total_inspections * 100) if total_inspections > 0 else 0

    context = {
        # Facilities
        'major_road_count': major_road_count,
        'trunk_sewer_count': trunk_sewer_count,
        'storm_drain_count': storm_drain_count,
        'ponding_point_count': ponding_point_count,
        'total_facilities': total_facilities,

        # Inspections
        'major_road_inspections': major_road_inspections,
        'trunk_sewer_inspections': trunk_sewer_inspections,
        'storm_drain_inspections': storm_drain_inspections,
        'ponding_point_inspections': ponding_point_inspections,
        'total_inspections': total_inspections,

        # Recent Activity
        'total_last_7_days': total_last_7_days,
        'total_last_30_days': total_last_30_days,
        'total_this_month': total_this_month,
        'major_road_last_7': major_road_last_7,
        'trunk_sewer_last_7': trunk_sewer_last_7,
        'storm_drain_last_7': storm_drain_last_7,
        'ponding_point_last_7': ponding_point_last_7,

        # Compliance Rates
        'major_road_pass_rate': round(major_road_pass_rate, 1),
        'trunk_sewer_pass_rate': round(trunk_sewer_pass_rate, 1),
        'storm_drain_pass_rate': round(storm_drain_pass_rate, 1),
        'ponding_point_pass_rate': round(ponding_point_pass_rate, 1),
        'overall_compliance_rate': round(overall_compliance_rate, 1),
        'major_road_pass': major_road_pass,
        'trunk_sewer_pass': trunk_sewer_pass,
        'storm_drain_pass': storm_drain_pass,
        'ponding_point_pass': ponding_point_pass,

        # Coverage Statistics
        'major_road_coverage': round(major_road_coverage, 1),
        'trunk_sewer_coverage': round(trunk_sewer_coverage, 1),
        'storm_drain_coverage': round(storm_drain_coverage, 1),
        'ponding_point_coverage': round(ponding_point_coverage, 1),
        'overall_coverage': round(overall_coverage, 1),
        'major_roads_inspected': major_roads_inspected,
        'trunk_sewers_inspected': trunk_sewers_inspected,
        'storm_drains_inspected': storm_drains_inspected,
        'ponding_points_inspected': ponding_points_inspected,

        # Zone Statistics
        'zone_stats': zone_stats[:5],
        'zone_compliance': zone_compliance,

        # Recent Inspections
        'recent_major_roads': recent_major_roads,
        'recent_trunk_sewers': recent_trunk_sewers,
        'recent_storm_drains': recent_storm_drains,
        'recent_ponding_points': recent_ponding_points,

        # Issues
        'major_road_issues': major_road_issues,
        'trunk_sewer_issues': trunk_sewer_issues,
        'storm_drain_issues': storm_drain_issues,
        'ponding_point_issues': ponding_point_issues,
        'total_issues': total_issues,

        # Averages
        'avg_major_road': round(avg_major_road, 2),
        'avg_trunk_sewer': round(avg_trunk_sewer, 2),
        'avg_storm_drain': round(avg_storm_drain, 2),
        'avg_ponding_point': round(avg_ponding_point, 2),

        # Percentages for progress bars
        'major_road_percentage': round(major_road_percentage, 1),
        'trunk_sewer_percentage': round(trunk_sewer_percentage, 1),
        'storm_drain_percentage': round(storm_drain_percentage, 1),
        'ponding_point_percentage': round(ponding_point_percentage, 1),

        # Expected vs Actual
        'working_days': working_days,
        'expected_inspections_total': expected_inspections_total,
        'inspection_achievement_rate': round(inspection_achievement_rate, 1),
        'expected_major_road': expected_major_road,
        'expected_trunk_sewer': expected_trunk_sewer,
        'expected_storm_drain': expected_storm_drain,
        'expected_ponding_point': expected_ponding_point,
        'major_road_achievement': round(major_road_achievement, 1),
        'trunk_sewer_achievement': round(trunk_sewer_achievement, 1),
        'storm_drain_achievement': round(storm_drain_achievement, 1),
        'ponding_point_achievement': round(ponding_point_achievement, 1),
    }

    return render(request, 'inspection/dsd_dashboard.html', context)


from django.core.paginator import Paginator
from django.db.models import Q
from .models import *

from django.core.paginator import Paginator
from django.db.models import Q
from .models import *


@login_required
def major_road_report(request):
    data = MajorRoad_inspection.objects.select_related(
        'zone', 'facility_name'
    ).order_by('-inspection_date')

    # -------- FILTERS ----------
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    zone = request.GET.get('zone')
    facility = request.GET.get('facility')
    search = request.GET.get('search')

    if from_date and to_date:
        data = data.filter(inspection_date__range=[from_date, to_date])

    if zone:
        data = data.filter(zone_id=zone)

    if facility:
        data = data.filter(facility_name_id=facility)

    if search:
        data = data.filter(
            Q(facility_name__road__icontains=search) |
            Q(emp_name__icontains=search)
        )

    # -------- PAGINATION ----------
    per_page = request.GET.get('per_page', 10)  # default 10
    if per_page == 'all':
        page_obj = data  # show all
    else:
        paginator = Paginator(data, int(per_page))
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'zones': Location.objects.all(),
        'facilities': MajorRoad_Add.objects.all(),
        'title': 'Major Roads Inspection Report',
        'per_page': per_page,
    }
    return render(request, 'inspection/reports/major_road_report.html', context)



@login_required
def trunk_sewer_report(request):
    data = TrunkSewer_inspection.objects.select_related(
        'zone', 'facility_name'
    ).order_by('-inspection_date')

    # Filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    zone = request.GET.get('zone')
    facility = request.GET.get('facility')
    search = request.GET.get('search')

    if from_date and to_date:
        data = data.filter(inspection_date__range=[from_date, to_date])

    if zone:
        data = data.filter(zone_id=zone)

    if facility:
        data = data.filter(facility_name_id=facility)

    if search:
        data = data.filter(
            Q(facility_name__trunksewer__icontains=search) |
            Q(emp_name__icontains=search)
        )

    # Pagination
    per_page = request.GET.get('per_page', 10)
    if per_page == 'all':
        page_obj = data
    else:
        paginator = Paginator(data, int(per_page))
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'zones': Location.objects.all(),
        'facilities': TrunkSewer_Add.objects.all(),
        'title': 'Trunk Sewer Inspection Report',
        'per_page': per_page,
    }
    return render(request, 'inspection/reports/trunk_sewer_report.html', context)



@login_required
def storm_drain_report(request):
    data = StormDrain_inspection.objects.select_related(
        'zone', 'facility_name'
    ).order_by('-inspection_date')

    # Filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    zone = request.GET.get('zone')
    facility = request.GET.get('facility')
    search = request.GET.get('search')

    if from_date and to_date:
        data = data.filter(inspection_date__range=[from_date, to_date])

    if zone:
        data = data.filter(zone_id=zone)

    if facility:
        data = data.filter(facility_name_id=facility)

    if search:
        data = data.filter(
            Q(facility_name__stormdrain__icontains=search) |
            Q(emp_name__icontains=search)
        )

    # Pagination
    per_page = request.GET.get('per_page', 10)
    if per_page == 'all':
        page_obj = data
    else:
        paginator = Paginator(data, int(per_page))
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'zones': Location.objects.all(),
        'facilities': StormDrain_Add.objects.all(),
        'title': 'Storm Drain Inspection Report',
        'per_page': per_page,
    }
    return render(request, 'inspection/reports/storm_drain_report.html', context)



@login_required
def ponding_points_report(request):
    data = PondingPoints_inspection.objects.select_related(
        'zone', 'facility_name'
    ).order_by('-inspection_date')

    # Filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    zone = request.GET.get('zone')
    facility = request.GET.get('facility')
    search = request.GET.get('search')

    if from_date and to_date:
        data = data.filter(inspection_date__range=[from_date, to_date])

    if zone:
        data = data.filter(zone_id=zone)

    if facility:
        data = data.filter(facility_name_id=facility)

    if search:
        data = data.filter(
            Q(facility_name__pondingpoints__icontains=search) |
            Q(emp_name__icontains=search)
        )

    # Pagination
    per_page = request.GET.get('per_page', 10)
    if per_page == 'all':
        page_obj = data
    else:
        paginator = Paginator(data, int(per_page))
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'zones': Location.objects.all(),
        'facilities': PondingPoints_Add.objects.all(),
        'title': 'Ponding Points Inspection Report',
        'per_page': per_page,
    }
    return render(request, 'inspection/reports/ponding_points_report.html', context)





from django.shortcuts import render
from .models import TubeWell, Location


@login_required
def HorsePowerSummaryView(request):
    """
    Horse Power Summary View:
    - Excludes Headoffice
    - Orders zones manually: A → B → C → D → E
    - Ignores motor_hours_power = 0, treat as 'Data Missing'
    """
    zone_order = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']

    # Remove 0 from columns
    motor_hours_values = [10, 15, 18, 20, 25, 30, 35, 40]

    locations = list(Location.objects.exclude(location_name__iexact='Headoffice'))
    locations.sort(key=lambda x: zone_order.index(x.location_name) if x.location_name in zone_order else 999)

    summary = []

    for loc in locations:
        row = {'location': loc.location_name, 'grand_total': 0}

        # Initialize counts for each motor_hours_power column
        for mh in motor_hours_values:
            row[mh] = 0

        # Count TubeWells (ignore 0)
        for mh in motor_hours_values:
            count = TubeWell.objects.filter(location=loc, motor_hours_power=str(mh)).count()
            row[mh] = count
            row['grand_total'] += count

        # Count 0 separately as 'Data Missing' in grand total
        missing_count = TubeWell.objects.filter(location=loc, motor_hours_power='0').count()
        if missing_count > 0:
            row['grand_total'] += missing_count  # add to total
            row['missing'] = missing_count
        else:
            row['missing'] = 0

        summary.append(row)

    # Grand total row
    grand_total_row = {'location': 'Grand Total', 'grand_total': 0, 'missing': 0}
    for mh in motor_hours_values:
        grand_total_row[mh] = TubeWell.objects.filter(motor_hours_power=str(mh)).count()
        grand_total_row['grand_total'] += grand_total_row[mh]
    # Add missing (0 hours)
    grand_total_row['missing'] = TubeWell.objects.filter(motor_hours_power='0').count()
    grand_total_row['grand_total'] += grand_total_row['missing']

    summary.append(grand_total_row)

    context = {
        'summary': summary,
        'motor_hours_values': motor_hours_values,
        'title': 'Tubewell Horse Power Summary',
    }
    return render(request, 'Horse_Power_Summary.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Complaint, ComplaintResponse
from .forms import ComplaintResponseForm
from django.utils.timezone import now

# ----------------------------
# List ONLY resolved complaints
# ----------------------------
from django.shortcuts import render
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Complaint

@login_required
def resolved_complaint_list(request):
    today = now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = today

    # Get filter values from GET
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    complaints = Complaint.objects.filter(status='resolved')

    # Apply date filter
    if from_date and to_date:
        complaints = complaints.filter(date__range=[from_date, to_date])
    else:
        from_date = first_day_of_month.strftime('%Y-%m-%d')
        to_date = last_day_of_month.strftime('%Y-%m-%d')
        complaints = complaints.filter(date__range=[from_date, to_date])

    complaints = complaints.order_by('-updated_at')

    # Pagination
    page_number = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', '100')  # default is now 100

    if isinstance(page_size, str) and page_size.lower() == 'all':
        paginated_complaints = complaints  # Show all complaints
    else:
        try:
            page_size = int(page_size)
        except (ValueError, TypeError):
            page_size = 100  # fallback to 100
        paginator = Paginator(complaints, page_size)
        paginated_complaints = paginator.get_page(page_number)

    return render(request, 'complaints/resolved_list.html', {
        'complaints': paginated_complaints,
        'from_date': from_date,
        'to_date': to_date,
        'page_size': str(page_size),  # keep as string for template
    })


# ----------------------------
# Add feedback / response for a resolved complaint
# ----------------------------
@login_required
def add_complaint_response(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, status='resolved')

    # Optional: prevent duplicate response
    if complaint.responses.exists():
        messages.warning(request, 'Response already submitted for this complaint.')
        return redirect('resolved_complaint_list')

    if request.method == 'POST':
        form = ComplaintResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.complaint = complaint
            response.save()
            messages.success(request, 'Response submitted successfully.')
            return redirect('resolved_complaint_list')
    else:
        form = ComplaintResponseForm()

    return render(request, 'complaints/feedback_form.html', {
        'form': form,
        'complaint': complaint
    })




from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@login_required
def daily_sweeping_entry(request):
    # --- Get selected date or default to today ---
    date_str = request.GET.get('date')
    selected_date = (
        datetime.strptime(date_str, "%Y-%m-%d").date()
        if date_str else timezone.now().date()
    )

    # --- Prevent future dates ---
    today = timezone.now().date()
    if selected_date > today:
        messages.warning(request, "Future date is not allowed.")
        selected_date = today

    # --- Get user's permitted locations ---
    permitted_locations = get_user_permitted_locations(request.user)

    # --- Filter streets by permission ---
    if request.user.is_superuser:
        streets = Street.objects.select_related('location', 'uc_name', 'nc_name')
    else:
        streets = Street.objects.select_related('location', 'uc_name', 'nc_name') \
            .filter(location__in=permitted_locations)

    # --- Handle POST submission ---
    if request.method == 'POST':
        for street in streets:
            sweeping_value = request.POST.get(f"sweeping_{street.id}")
            sweeping_done = True if sweeping_value == 'yes' else False

            sweeping_type = request.POST.get(f"type_{street.id}") or None
            sweeping_length = request.POST.get(f"length_{street.id}") or None
            remarks = request.POST.get(f"remarks_{street.id}") or ''

            # ✅ Always save if user selected Yes/No for sweeping
            if sweeping_value is not None:
                DailyStreetSweeping.objects.update_or_create(
                    street=street,
                    sweeping_date=selected_date,
                    defaults={
                        'sweeping_done': sweeping_done,
                        'sweeping_type': sweeping_type if sweeping_done else None,
                        'sweeping_length_km': sweeping_length if sweeping_done else None,
                        'remarks': remarks
                    }
                )

        messages.success(request, f"Sweeping data saved for {selected_date}")
        return redirect(f"{reverse('daily_sweeping_entry')}?date={selected_date}")

    # --- Load existing records for selected date ---
    existing = DailyStreetSweeping.objects.filter(sweeping_date=selected_date)
    records_dict = {r.street_id: r for r in existing}

    return render(request, 'daily_sweeping_entry.html', {
        'streets': streets,
        'selected_date': selected_date,  # ✅ pass selected date
        'records_dict': records_dict,
    })




# views.py
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils.timezone import now
from .models import ComplaintResponse, Complaint
from django.contrib.auth.decorators import login_required

from django.utils.timezone import now
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Complaint, ComplaintResponse

@login_required
def complaint_response_report(request):
    # --- Date Filters ---
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    officer_filter = request.GET.get('officer')

    today = now().date()

    # If no dates provided, default to current month
    if not from_date or not to_date:
        from_date = today.replace(day=1).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

    # --- Responses in date range, only resolved complaints ---
    resolved_complaints_ids = Complaint.objects.filter(
        date__range=[from_date, to_date],
        status='resolved'
    ).values_list('id', flat=True)

    responses = ComplaintResponse.objects.select_related(
        'complaint',
        'complaint__location'
    ).filter(
        complaint_id__in=resolved_complaints_ids
    )

    # Filter by officer if selected
    if officer_filter:
        responses = responses.filter(
            officer_name__iexact=officer_filter
        )

    # Total resolved complaints in the range
    total_complaints = resolved_complaints_ids.count()

    # --- Officer-wise summary ---
    summary = responses.values('officer_name').annotate(
        total_feedback=Count('id'),
        yes=Count('id', filter=Q(feedback='yes')),
        no=Count('id', filter=Q(feedback='no')),
        neutral=Count('id', filter=Q(feedback='neutral')),
        not_responded=Count(
            'id',
            filter=Q(feedback='not_responded')
        ),
    ).order_by('officer_name')

    # Officer percentages based on total resolved complaints
    for s in summary:
        s['percentage'] = (
            round((s['total_feedback'] / total_complaints) * 100, 2)
            if total_complaints > 0 else 0
        )

    # Totals across all officers
    total_feedback = sum(s['total_feedback'] for s in summary)

    total_summary = {
        'total_feedback': total_feedback,
        'yes': sum(s['yes'] for s in summary),
        'no': sum(s['no'] for s in summary),
        'neutral': sum(s['neutral'] for s in summary),
        'not_responded': sum(
            s['not_responded'] for s in summary
        ),
        'percentage': (
            round((total_feedback / total_complaints) * 100, 2)
            if total_complaints > 0 else 0
        ),
    }

    # Distinct officer list for filter dropdown
    officers = ComplaintResponse.objects.values_list(
        'officer_name',
        flat=True
    ).distinct()

    return render(
        request,
        'complaints/complaint_feedback_report.html',
        {
            'responses': responses,
            'summary': summary,
            'total_summary': total_summary,
            'officers': officers,
            'selected_officer': officer_filter,
            'from_date': from_date,
            'to_date': to_date,
            'total_complaints': total_complaints,
        }
    )

from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, time
from .models import VisitSchedule

@login_required
def visit_schedule_view(request):
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    schedules = VisitSchedule.objects.select_related(
        "employee"
    ).prefetch_related(
        "locations",
        "ucs",
    )

    if from_date and to_date:
        schedules = schedules.filter(visit_date__range=[from_date, to_date])
    elif from_date:
        schedules = schedules.filter(visit_date__gte=from_date)
    elif to_date:
        schedules = schedules.filter(visit_date__lte=to_date)

    schedules = schedules.order_by("visit_date")

    now = timezone.localtime()
    today = now.date()

    for schedule in schedules:
        ucs = schedule.ucs.all()

        # Load UC-based assets (optional)
        schedule.uc_employees = Employee.objects.filter(uc__in=ucs).distinct()
        schedule.uc_tubewells = TubeWell.objects.filter(uc__in=ucs).distinct()
        schedule.uc_bins = Bin.objects.filter(uc__in=ucs).distinct()
        schedule.uc_vehicles = Vehicle.objects.filter(driver_name__uc__in=ucs).distinct()

        visit_datetime = timezone.make_aware(datetime.combine(schedule.visit_date, time(7,0)), timezone.get_current_timezone())

        if schedule.visit_date < today:
            # Past → show as visited
            schedule.show_details = True
            schedule.visited_closed = True
        elif schedule.visit_date == today:
            # Today → show after 7AM
            schedule.show_details = now >= visit_datetime
            schedule.visited_closed = False
        else:
            # Future → hide
            schedule.show_details = False
            schedule.visited_closed = False

    context = {
        "schedules": schedules,
        "from_date": from_date,
        "to_date": to_date,
    }

    return render(request, "visit_schedule_list.html", context)



from django.shortcuts import render, redirect, get_object_or_404
from .models import Manhole_inspection
from .forms import ManholeInspectionForm


# ✅ LIST VIEW
@login_required
def dsd5_manhole_list(request):
    data = Manhole_inspection.objects.all().order_by('-inspection_date')
    return render(request, 'inspection/list.html', {
        'data': data,
        'title': 'DSD.5 Manhole Inspection',
        'add_url': 'dsd5_manhole_add',
        'edit_url': 'dsd5_manhole_update',
        'delete_url': 'dsd5_manhole_delete',
    })


# ✅ ADD VIEW
@login_required
def dsd5_manhole_add(request):
    form = ManholeInspectionForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('dsd5_manhole_list')

    return render(request, 'inspection/form.html', {
        'form': form,
        'title': 'Add Manhole Inspection'
    })


# ✅ UPDATE VIEW
@login_required
def dsd5_manhole_update(request, pk):
    obj = get_object_or_404(Manhole_inspection, pk=pk)
    form = ManholeInspectionForm(request.POST or None, request.FILES or None, instance=obj)

    if form.is_valid():
        form.save()
        return redirect('dsd5_manhole_list')

    return render(request, 'inspection/form.html', {
        'form': form,
        'title': 'Edit Manhole Inspection'
    })


# ✅ DELETE VIEW
@login_required
def dsd5_manhole_delete(request, pk):
    get_object_or_404(Manhole_inspection, pk=pk).delete()
    return redirect('dsd5_manhole_list')




from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Manhole_inspection
from .models import Location, UC

@login_required
def dsd5_manhole_report(request):
    data = Manhole_inspection.objects.select_related(
        'zone', 'facility_name'
    ).order_by('-inspection_date')

    # Filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    zone = request.GET.get('zone')
    facility = request.GET.get('facility')
    search = request.GET.get('search')

    if from_date and to_date:
        data = data.filter(inspection_date__range=[from_date, to_date])

    if zone:
        data = data.filter(zone_id=zone)

    if facility:
        data = data.filter(facility_name_id=facility)

    if search:
        data = data.filter(
            Q(facility_name__name__icontains=search) |
            Q(emp_name__icontains=search)
        )

    # Pagination
    per_page = request.GET.get('per_page', 10)
    if per_page == 'all':
        page_obj = data
    else:
        paginator = Paginator(data, int(per_page))
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'zones': Location.objects.all(),
        'facilities': UC.objects.all(),
        'title': 'Manhole Inspection Report',
        'per_page': per_page,
    }

    return render(request, 'inspection/reports/dsd5_manhole_report.html', context)




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import VisitEvaluation
from .forms import VisitEvaluationForm


# ==========================
# LIST VIEW
# ==========================
@login_required
def visit_evaluation_list(request):
    evaluations = VisitEvaluation.objects.all().order_by("-created_at")
    return render(request, "M&E/list.html", {
        "evaluations": evaluations
    })


# ==========================
# CREATE VIEW
# ==========================
@login_required
def visit_evaluation_create(request):
    if request.method == "POST":
        form = VisitEvaluationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("visit_evaluation_list")
    else:
        form = VisitEvaluationForm()

    return render(request, "M&E/form.html", {
        "form": form,
        "title": "Create Visit Evaluation"
    })


# ==========================
# UPDATE VIEW
# ==========================
@login_required
def visit_evaluation_update(request, pk):
    evaluation = get_object_or_404(VisitEvaluation, pk=pk)

    # ❌ Block if completed
    if evaluation.status == "completed":
        return render(request, "M&E/locked.html", {
            "evaluation": evaluation
        })

    if request.method == "POST":

        form = VisitEvaluationForm(
            request.POST,
            request.FILES,
            instance=evaluation
        )

        if form.is_valid():

            obj = form.save(commit=False)  # ✅ STOP auto save

            # ✅ Check button clicked
            if "save_draft" in request.POST:
                obj.status = "draft"

            elif "save_complete" in request.POST:
                obj.status = "completed"

            # ✅ Now save AFTER status update
            obj.save()

            return redirect("visit_evaluation_list")

    else:
        form = VisitEvaluationForm(instance=evaluation)

    return render(request, "M&E/form.html", {
        "form": form,
        "evaluation": evaluation
    })
    
# ==========================
# DELETE VIEW
# ==========================
@login_required
def visit_evaluation_delete(request, pk):
    evaluation = get_object_or_404(VisitEvaluation, pk=pk)

    if request.method == "POST":
        evaluation.delete()
        return redirect("visit_evaluation_list")

    return render(request, "M&E/delete.html", {
        "evaluation": evaluation
    })


from django.shortcuts import get_object_or_404

@login_required
def visit_evaluation_detail(request, pk):
    evaluation = get_object_or_404(
        VisitEvaluation.objects.select_related(
            "visit_schedule",
            "visit_schedule__employee"
        ).prefetch_related(
            "visit_schedule__locations",
            "visit_schedule__ucs"
        ),
        pk=pk
    )

    return render(request, "M&E/detail.html", {
        "evaluation": evaluation
    })    





from django.shortcuts import render, get_object_or_404, redirect
from .models import Manhole
from .forms import ManholeForm


# 📋 List Manholes
@login_required
def manhole_list(request):

    manholes = Manhole.objects.select_related(
        'uc',
        'uc__location',
        'shape',
        'cover_material'
    ).all()

    # 🔍 Filters
    zone_id = request.GET.get('zone')
    uc_id = request.GET.get('uc')
    status = request.GET.get('status')

    if zone_id:
        manholes = manholes.filter(uc__location_id=zone_id)

    if uc_id:
        manholes = manholes.filter(uc_id=uc_id)

    if status:
        manholes = manholes.filter(status=status)

    # 📊 Summary
    summary = manholes.aggregate(
        total=Count('id'),
        open=Count('id', filter=models.Q(status='open')),
        covered=Count('id', filter=models.Q(status='covered')),
    )

    # 📄 Pagination
    paginator = Paginator(manholes, 100)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 🌍 Filters data
    zones = Location.objects.all()
    ucs = UC.objects.all()

    context = {
        'page_obj': page_obj,
        'zones': zones,
        'ucs': ucs,
        'summary': summary,
        'selected_zone': zone_id,
        'selected_uc': uc_id,
        'selected_status': status,
    }

    return render(request, 'manhole/manhole_list.html', context)


# ➕ Create Manhole
@login_required
def manhole_create(request):

    if request.method == "POST":
        form = ManholeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('manhole_list')

    else:
        form = ManholeForm()

    return render(request, 'manhole/manhole_form.html', {'form': form})


# ✏ Update Manhole
@login_required
def manhole_update(request, pk):

    manhole = get_object_or_404(Manhole, pk=pk)

    if request.method == "POST":
        form = ManholeForm(request.POST, instance=manhole)

        if form.is_valid():
            form.save()
            return redirect('manhole_list')

    else:
        form = ManholeForm(instance=manhole)

    return render(request, 'manhole/manhole_form.html', {'form': form})


# ❌ Delete Manhole
@login_required
def manhole_delete(request, pk):

    manhole = get_object_or_404(Manhole, pk=pk)

    if request.method == "POST":
        manhole.delete()
        return redirect('manhole_list')

    return render(request, 'manhole/manhole_confirm_delete.html', {'manhole': manhole})        






from django.shortcuts import render
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import Manhole, UC, Location, ManholeShape, ManholeCoverMaterial
import json



from django.shortcuts import render
from django.db.models import Count, Q
import json
@login_required
def manhole_dashboard(request):
    # ── GET filters ─────────────────────────────
    f_location = request.GET.get('location')
    f_uc       = request.GET.get('uc')
    f_status   = request.GET.get('status')
    f_shape    = request.GET.get('shape')
    f_material = request.GET.get('material')
    f_search   = request.GET.get('search', '').strip()

    # ── Base queryset ───────────────────────────
    qs = Manhole.objects.select_related(
        'uc', 'uc__location', 'shape', 'cover_material'
    )

    # ── Apply filters ───────────────────────────
    if f_location:
        qs = qs.filter(uc__location_id=f_location)
    if f_uc:
        qs = qs.filter(uc_id=f_uc)
    if f_status:
        qs = qs.filter(status=f_status)
    if f_shape:
        qs = qs.filter(shape_id=f_shape)
    if f_material:
        qs = qs.filter(cover_material_id=f_material)
    if f_search:
        qs = qs.filter(
            Q(uc__uc_name__icontains=f_search) |
            Q(uc__location__location_name__icontains=f_search) |
            Q(shape__name__icontains=f_search) |
            Q(cover_material__material__icontains=f_search)
        )

    # ── Summary Stats ───────────────────────────
    total = qs.count()

    status_counts = qs.values('status').annotate(count=Count('id'))
    status_map = {x['status']: x['count'] for x in status_counts}

    open_c  = status_map.get('open', 0)
    covered = status_map.get('covered', 0)

    uc_count       = qs.values('uc').distinct().count()
    location_count = qs.values('uc__location').distinct().count()

    # Percentages
    open_pct    = round((open_c / total) * 100, 1) if total else 0
    covered_pct = round((covered / total) * 100, 1) if total else 0

    # ── Charts Data ─────────────────────────────
    # UC chart
    chart_by_uc = list(
        qs.values('uc__uc_name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Material chart
    chart_by_material = list(
        qs.values('cover_material__material')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Shape chart
    chart_by_shape = list(
        qs.values('shape__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Zone / Location summary
    chart_by_zone = list(
        qs.values('uc__location__location_name')
        .annotate(
            total=Count('id'),
            open=Count('id', filter=Q(status='open')),
            covered=Count('id', filter=Q(status='covered')),
        )
        .order_by('uc__location__location_name')
    )

    # ── Context ────────────────────────────────
    context = {
        # Filters
        'locations': Location.objects.all().order_by('location_name'),
        'ucs': UC.objects.select_related('location').order_by('uc_name'),
        'shapes': ManholeShape.objects.all().order_by('name'),
        'materials': ManholeCoverMaterial.objects.all().order_by('material'),

        'f_location': f_location,
        'f_uc': f_uc,
        'f_status': f_status,
        'f_shape': f_shape,
        'f_material': f_material,
        'f_search': f_search,

        # Summary
        'total': total,
        'open_c': open_c,
        'covered': covered,
        'uc_count': uc_count,
        'location_count': location_count,
        'open_pct': open_pct,
        'covered_pct': covered_pct,

        # Charts
        'chart_status': json.dumps({
            'open': open_c,
            'covered': covered,
            'open_pct': open_pct,
            'covered_pct': covered_pct
        }),
        'chart_by_uc': json.dumps(chart_by_uc),
        'chart_by_material': json.dumps(chart_by_material),
        'chart_by_shape': json.dumps(chart_by_shape),
        'chart_by_zone': json.dumps(chart_by_zone),
    }

    return render(request, 'manhole/dashboard.html', context)    





from django.shortcuts import render
from django.db.models import Sum, Count, FloatField
from django.db.models.functions import Cast
from datetime import date
from calendar import monthrange

from .models import (
    Fuel,
    Watertest,
    TubeWellWaterProduce,
    TubeWellElectricityUsage,
    Sanitation,
    Location
)


@login_required
def monthly_report(request):


    # =========================
    # DATE FILTER
    # =========================
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    today = date.today()
    start_date = today.replace(day=1)
    end_date = today.replace(day=monthrange(today.year, today.month)[1])

    if from_date and to_date:
        start_date = from_date
        end_date = to_date

    # =========================
    # ZONES (ORDER + EXCLUDE HEAD OFFICE)
    # =========================
    zones = list(
        Location.objects
        .exclude(location_name__iexact='Headoffice')
        .order_by('location_name')
        .values_list('location_name', flat=True)
    )

    # =========================
    # FUEL DATA
    # =========================
    fuel_qs = Fuel.objects.filter(
        date__range=[start_date, end_date]
    ).values('location__location_name').annotate(
        secondary_trips=Sum('lfs_trips_no'),
        primary_trips=Sum('primary_trips'),
        fuel_issue=Sum('fuel_top_up_liters')
    )

    fuel_map = {i['location__location_name']: i for i in fuel_qs}

    fuel_data = [
        {
            'zone': z,
            'secondary_trips': fuel_map.get(z, {}).get('secondary_trips', 0),
            'primary_trips': fuel_map.get(z, {}).get('primary_trips', 0),
            'fuel_issue': fuel_map.get(z, {}).get('fuel_issue', 0),
        }
        for z in zones
    ]

    fuel_totals = Fuel.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(
        total_secondary=Sum('lfs_trips_no'),
        total_primary=Sum('primary_trips'),
        total_fuel=Sum('fuel_top_up_liters')
    )

    # =========================
    # WATER TEST DATA
    # =========================
    water_qs = Watertest.objects.filter(
        date__range=[start_date, end_date]
    ).values('location__location_name').annotate(
        test_count=Count('id')
    )

    water_map = {i['location__location_name']: i['test_count'] for i in water_qs}

    water_data = [
        {
            'zone': z,
            'test_count': water_map.get(z, 0)
        }
        for z in zones
    ]

    water_total = Watertest.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(
        total_tests=Count('id')
    )

    # =========================
    # WATER PRODUCE (FIXED DATE FIELD)
    # =========================
    water_qs = TubeWellWaterProduce.objects.filter(
        water_produce_date__range=[start_date, end_date],
        tubewell__location__isnull=False
    ).values('tubewell__location__location_name').annotate(
        run_hour=Sum(Cast('run_hour', FloatField())),
        water_produce=Sum(Cast('water_produce', FloatField()))
    )

    # =========================
    # ELECTRICITY (FIXED DATE FIELD)
    # =========================
    electricity_qs = TubeWellElectricityUsage.objects.filter(
        usage_date__range=[start_date, end_date],
        tubewell__location__isnull=False
    ).values('tubewell__location__location_name').annotate(
        electricity=Sum('electricity_consumed')
    )

    water_map = {i['tubewell__location__location_name']: i for i in water_qs}
    electricity_map = {i['tubewell__location__location_name']: i['electricity'] for i in electricity_qs}

    water_supply = [
        {
            'zone': z,
            'run_hour': water_map.get(z, {}).get('run_hour', 0),
            'water_produce': water_map.get(z, {}).get('water_produce', 0),
            'electricity': electricity_map.get(z, 0),
        }
        for z in zones
    ]

    water_supply_total = {
        'total_run_hour': sum(float(i['run_hour'] or 0) for i in water_supply),
        'total_electricity': sum(float(i['electricity'] or 0) for i in water_supply),
        'total_water_produce': sum(float(i['water_produce'] or 0) for i in water_supply),
    }

    # =========================
    # SANITATION DATA
    # =========================
    san_qs = Sanitation.objects.filter(
        date__range=[start_date, end_date]
    ).values('location__location_name').annotate(
        primary_waste=Sum('primary_waste_collection_tons'),
        secondary_waste=Sum('waste_dumped_at_lfs_tons'),
        local_dumped=Sum('waste_locally_dumped_tons'),
        door_to_door=Sum('door_to_door_solid_waste_collection_no'),
        manhole_replacement=Sum('replacement_of_manhole_covers'),
        manhole_cleaning=Sum('cleaning_de_siltation_of_manholes'),
        drain_cleaning=Sum('cleaning_de_siltation_of_drain_sewars_km')
    )

    san_map = {i['location__location_name']: i for i in san_qs}

    sanitation_data = [
        {
            'zone': z,
            'primary_waste': san_map.get(z, {}).get('primary_waste', 0),
            'secondary_waste': san_map.get(z, {}).get('secondary_waste', 0),
            'local_dumped': san_map.get(z, {}).get('local_dumped', 0),
            'door_to_door': san_map.get(z, {}).get('door_to_door', 0),
            'manhole_replacement': san_map.get(z, {}).get('manhole_replacement', 0),
            'manhole_cleaning': san_map.get(z, {}).get('manhole_cleaning', 0),
            'drain_cleaning': san_map.get(z, {}).get('drain_cleaning', 0),
        }
        for z in zones
    ]

    sanitation_total = Sanitation.objects.filter(
        date__range=[start_date, end_date]
    ).aggregate(
        primary_waste=Sum('primary_waste_collection_tons'),
        secondary_waste=Sum('waste_dumped_at_lfs_tons'),
        local_dumped=Sum('waste_locally_dumped_tons'),
        door_to_door=Sum('door_to_door_solid_waste_collection_no'),
        manhole_replacement=Sum('replacement_of_manhole_covers'),
        manhole_cleaning=Sum('cleaning_de_siltation_of_manholes'),
        drain_cleaning=Sum('cleaning_de_siltation_of_drain_sewars_km')
    )

    # =========================
    # CONTEXT
    # =========================
    context = {
        'fuel_data': fuel_data,
        'fuel_totals': fuel_totals,

        'water_data': water_data,
        'water_total': water_total,

        'water_supply': water_supply,
        'water_supply_total': water_supply_total,

        'sanitation_data': sanitation_data,
        'sanitation_total': sanitation_total,

        'from_date': start_date,
        'to_date': end_date,
    }

    return render(request, 'report/monthly_report.html', context)








@login_required
def daily_progress_report(request):

    # =========================
    # 1. DATE HANDLING
    # =========================
    date_str = request.GET.get('date')

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.today().date()
    except ValueError:
        selected_date = datetime.today().date()

    # =========================
    # ORDERED LOCATIONS (Zone A → E → Head Office)
    # =========================
    locations = sorted(
        Location.objects.all(),
        key=lambda x: {
            2: 0,  # Zone A
            3: 1,  # Zone B
            4: 2,  # Zone C
            5: 3,  # Zone D
            6: 4,  # Zone E
            1: 5,  # Head Office
        }.get(x.id, 999)
    )
    HEAD_OFFICE_ID = 1
    HEAD_OFFICE_SOURCE_ID = 1

    # =========================
    # 2. MODULE CONFIG
    # =========================
    modules = {
        "employee": EmployeeAttendance.objects.filter(attendance_date=selected_date),
        "vehicle": VehicleAttendance.objects.filter(attendance_date=selected_date),

        "fuel": Fuel.objects.filter(
            date=selected_date,
            fuel_top_up_liters__gt=0
        ),

        "trip": Fuel.objects.filter(
            date=selected_date
        ).filter(
            Q(lfs_trips_no__gt=0) | Q(primary_trips__gt=0)
        ),

        "field_visit": FieldVisitReport.objects.filter(date=selected_date),
        "tubewell": TubeWellAttendance.objects.filter(attendance_date=selected_date),
        "filter": FilterAttendance.objects.filter(attendance_date=selected_date),
        "complaint": Complaint.objects.filter(created_at__date=selected_date),
        "clc": CLC.objects.filter(date=selected_date),
        "bin": BinAttendance.objects.filter(attendance_date=selected_date),

        # ✅ SANITATION ADDED
        "sanitation": Sanitation.objects.filter(date=selected_date),
    }

    # =========================
    # 3. SAFE MAPPING
    # =========================
    fuel_map = {f.location_id: f.fuel_top_up_liters for f in modules["fuel"]}

    trip_map = {
        f.location_id: (f.lfs_trips_no or 0) + (f.primary_trips or 0)
        for f in modules["trip"]
    }

    sanitation_map = {
        s.location_id: s
        for s in modules["sanitation"]
    }

    employee_set = set(modules["employee"].values_list("location_id", flat=True))
    vehicle_set = set(modules["vehicle"].values_list("location_id", flat=True))
    field_visit_set = set(modules["field_visit"].values_list("location_id", flat=True))
    tubewell_set = set(modules["tubewell"].values_list("location_id", flat=True))
    filter_set = set(modules["filter"].values_list("location_id", flat=True))
    clc_set = set(modules["clc"].values_list("location_id", flat=True))
    bin_set = set(modules["bin"].values_list("location_id", flat=True))

    # =========================
    # 4. BUILD REPORT
    # =========================
    report_dict = {}
    report_list = []

    for loc in locations:

        data = {"location": loc}

        for module_name in modules.keys():

            # =========================
            # HEAD OFFICE LOGIC
            # =========================
            if loc.id == HEAD_OFFICE_ID:

                if module_name == "employee":
                    data[module_name] = loc.id in employee_set

                elif module_name == "complaint":
                    data[module_name] = Complaint.objects.filter(
                        created_at__date=selected_date,
                        complaint_source_id=HEAD_OFFICE_SOURCE_ID
                    ).exists()

                # ✅ Explicitly exclude sanitation (and all other modules) for Head Office
                elif module_name == "sanitation":
                    data[module_name] = "—"

                else:
                    data[module_name] = "—"

            # =========================
            # NORMAL ZONES
            # =========================
            else:

                if module_name == "employee":
                    data[module_name] = loc.id in employee_set

                elif module_name == "vehicle":
                    data[module_name] = loc.id in vehicle_set

                elif module_name == "fuel":
                    value = fuel_map.get(loc.id)
                    data[module_name] = value is not None and value > 0

                elif module_name == "trip":
                    value = trip_map.get(loc.id)
                    data[module_name] = value is not None and value > 0

                elif module_name == "field_visit":
                    data[module_name] = loc.id in field_visit_set

                elif module_name == "tubewell":
                    data[module_name] = loc.id in tubewell_set

                elif module_name == "filter":
                    data[module_name] = loc.id in filter_set

                elif module_name == "clc":
                    data[module_name] = loc.id in clc_set

                elif module_name == "bin":
                    data[module_name] = loc.id in bin_set

                elif module_name == "complaint":
                    data[module_name] = Complaint.objects.filter(
                        location_id=loc.id,
                        created_at__date=selected_date
                    ).exists()

                # =========================
                # ✅ SANITATION (OBJECT PASS)
                # =========================
                elif module_name == "sanitation":
                    data[module_name] = sanitation_map.get(loc.id)

        # =========================
        # CORE STATUS
        # =========================
        data["status"] = "Complete" if (
            data.get("employee") and
            data.get("vehicle") and
            data.get("fuel")
        ) else "Incomplete"

        report_dict[loc.id] = data
        report_list.append(data)

    # =========================
    # 5. FILTER
    # =========================
    if request.GET.get('missing') == '1':
        locations = [
            loc for loc in locations
            if report_dict[loc.id]["status"] != "Complete"
        ]

    # =========================
    # 6. SUMMARY
    # =========================
    total = len(report_list)
    completed = sum(1 for r in report_list if r["status"] == "Complete")
    missing = total - completed

    # =========================
    # 7. MODULE STATUS
    # =========================
    def calc_status(module_name):
        total_zones = len(locations)
        count = sum(
            1 for loc in locations
            if report_dict[loc.id].get(module_name) not in [False, None, "—", "✖"]
        )

        if total_zones == 0:
            return "Incomplete"
        if count == total_zones:
            return "Complete"
        if count == 0:
            return "Incomplete"
        return "Partial"

    module_status = {name: calc_status(name) for name in modules.keys()}

    # =========================
    # 8. REVENUE
    # =========================
    revenue = (
        Revenue.objects.filter(date=selected_date).first()
        or Revenue.objects.filter(date__lte=selected_date).order_by('-date').first()
    )

    # =========================
    # 9. POSTS
    # =========================
    total_posts = PostAttendance.objects.filter(post_date=selected_date).count()

    # =========================
    # 10. CONTEXT
    # =========================
    context = {
        "locations": locations,
        "report_dict": report_dict,
        "selected_date": selected_date,
        "total": total,
        "completed": completed,
        "missing": missing,
        "module_status": module_status,
        "revenue": revenue,
        "total_posts": total_posts,
    }


    return render(request, "report/daily_report.html", context)







from django.http import JsonResponse
from .models import Manhole

from collections import defaultdict
from django.http import JsonResponse


@login_required
def manhole_geojson(request):

    zone = request.GET.get("zone")
    uc = request.GET.get("uc")

    data = {
        "type": "FeatureCollection",
        "features": []
    }

    zone_counts = defaultdict(int)
    uc_counts = defaultdict(int)

    # NEW
    status_counts = defaultdict(int)
    material_counts = defaultdict(int)
    shape_counts = defaultdict(int)

    # =========================
    # QUERY
    # =========================
    qs = Manhole.objects.select_related(
        'uc',
        'uc__location',
        'shape',
        'cover_material'
    )

    # =========================
    # FILTERS
    # =========================
    if uc:
        if uc.isdigit():
            qs = qs.filter(uc_id=int(uc))
        else:
            qs = qs.filter(uc__uc_name__iexact=uc)

    if zone:
        qs = qs.filter(
            uc__location__location_name__iexact=zone
        )

    # =========================
    # COUNTS
    # =========================
    total_manholes = qs.count()

    # =========================
    # GEOJSON
    # =========================
    for m in qs:

        if m.latitude and m.longitude:

            zone_name = (
                m.uc.location.location_name
                if m.uc and m.uc.location else ""
            )

            uc_name = (
                m.uc.uc_name
                if m.uc else ""
            )

            material_name = (
                str(m.cover_material)
                if m.cover_material else "Unknown"
            )

            shape_name = (
                str(m.shape)
                if m.shape else "Unknown"
            )

            # COUNTS
            zone_counts[zone_name] += 1
            uc_counts[uc_name] += 1

            status_counts[m.status] += 1
            material_counts[material_name] += 1
            shape_counts[shape_name] += 1

            # FEATURE
            data["features"].append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(m.longitude),
                        float(m.latitude)
                    ]
                },
                "properties": {
                    "id": m.id,
                    "zone": zone_name,
                    "uc": uc_name,
                    "status": m.status,
                    "shape": shape_name,
                    "cover_size": m.cover_size,
                    "material": material_name
                }
            })

    return JsonResponse({

        "geojson": data,

        # totals
        "total_manholes": total_manholes,
        "open_count": status_counts.get("open", 0),
        "covered_count": status_counts.get("covered", 0),

        # charts
        "material_counts": dict(material_counts),
        "shape_counts": dict(shape_counts),

        # filters
        "zone_counts": dict(zone_counts),
        "uc_counts": dict(uc_counts),
    })

    
# views.py
from django.shortcuts import render


@login_required
def manhole_map_view(request):
    return render(request, "manhole/map.html")            