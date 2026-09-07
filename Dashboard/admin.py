from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Location, UC, TubeWell, Vehicle, FieldVisitReport, Department, ComplaintSource,
    ComplaintType, Designation, Employee, EmployeeAttendance, VehicleAttendance,
    TubeWellAttendance, WaterSupply, Revenue, Complaint, Post, PostDetail,
    PostAttendance, Watertest, Sanitation, Category, Capacity, official, Activity,
    CLCStaff, CLC, LiftingFrequency, LiftingSchedule, Bin, BinAttendance,
    VehiclePerformance, Filter, FilterAttendance, VehiclePE, Tracker, TrackerAttendance,
    NC, Street, Street_cleaning, perfoma_tube, DepartmentPermission, officialFPermission,
    officialCPermission, Status, UcPermission, Management_Staff, DayFrequency, LocationPermission,
    Vehiclerepair, Tubewellrepair, UserActivityLog, Log, locationmap, Binfoam, KMZUpload, ViewName,
    UserViewPermission, Fuel
)
from .forms import (
    EmployeeForm, EmployeeAttendanceForm, TubeWellForm, TubeWellAttendanceForm, PostAttendance
)
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .utils import log_admin_action
from django.http import HttpResponse
import csv
from django.utils.http import urlencode
from django.http import HttpRequest





class CustomAdminMixin:
    def save_model(self, request, obj, form, change):
        action = 'UPDATE' if change else 'ADD'
        super().save_model(request, obj, form, change)
        # Log the action
        UserActivityLog.objects.create(
            user=request.user,
            action=action,
            model_name=obj._meta.model_name,
            object_id=obj.pk,
            description=f"{action} {obj._meta.verbose_name} (ID: {obj.pk})",
        )

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # Log the action for individual deletions
        UserActivityLog.objects.create(
            user=request.user,
            action='DELETE',
            model_name=obj._meta.model_name,
            object_id=obj.pk,
            description=f"Deleted {obj._meta.verbose_name} (ID: {obj.pk})",
        )

    def delete_queryset(self, request, queryset):
        # Log the action for bulk deletions
        for obj in queryset:
            UserActivityLog.objects.create(
                user=request.user,
                action='DELETE',
                model_name=obj._meta.model_name,
                object_id=obj.pk,
                description=f"Deleted {obj._meta.verbose_name} (ID: {obj.pk})",
            )
        super().delete_queryset(request, queryset)



# Unregister the default User model before registering it again
# admin.site.unregister(User)

# class CustomUserAdmin(CustomAdminMixin, ImportExportModelAdmin):

#     search_fields = ('username', 'first_name', 'last_name', 'email')
#     list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
#     list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active')

# admin.site.register(User, CustomUserAdmin)













from django.contrib import admin
from .models import ComplaintSubType

@admin.register(ComplaintSubType)
class ComplaintSubTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'complaint_type', 'type_name')  # Columns in list view
    list_filter = ('complaint_type',)  # Sidebar filter
    search_fields = ('type_name',)  # Search bar
    ordering = ('complaint_type',)  # Default order

    # Optional: if you want to make type_name clickable
    list_display_links = ('id', 'type_name')




@admin.register(Location)
class LocationAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'location_name')
    search_fields = ('location_name',)


@admin.register(UC)
class UCAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'uc_name', 'location')
    search_fields = ('uc_name',)
    list_filter = ('location',)


@admin.register(NC)
class NCAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'nc_name', 'uc_name')
    search_fields = ('nc_name',)
    list_filter = ('uc_name',)


@admin.register(Street)
class StreetAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'street_name')
    search_fields = ('Street_name',)


@admin.register(Department)
class DepartmentAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'department_name',)
    search_fields = ('department_name',)


@admin.register(Designation)
class DesignationAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'designation_name',)
    search_fields = ('designation_name',)


@admin.register(Post)
class PostAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(PostDetail)
class PostDetailAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'post', 'media_channel')
    search_fields = ('post__name', 'media_channel')
    list_filter = ('post',)
    ordering = ('post',)

    def get_queryset(self, request):
        # Optimize retrieval of related fields
        queryset = super().get_queryset(request)
        return queryset.select_related('post')


@admin.register(official)
class OfficialAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'employee_id', 'name', 'designation', 'department', 'location')
    search_fields = ('employee_id', 'name', 'designation', 'department')
    list_filter = ('location', 'designation', 'department')


@admin.register(Management_Staff)
class ManagementStaffAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'father_name', 'location', 'designation')
    search_fields = ('employee_id', 'name', 'father_name', 'designation')
    list_filter = ('location', 'designation')
    ordering = ('employee_id',)
  
    fieldsets = (
        (None, {
            'fields': ('employee_id', 'name', 'father_name', 'location', 'designation')
        }),
    )


@admin.register(DayFrequency)
class DayFrequencyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name') 
    search_fields = ('name',) 


class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'status') 
    search_fields = ('status',)  
admin.site.register(Status, StatusAdmin)


@admin.register(Category)
class CategoryAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('category', 'id')
    search_fields = ('category',)


@admin.register(Capacity)
class CapacityAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('capacity', 'id')
    search_fields = ('capacity',)


@admin.register(LiftingFrequency)
class LiftingFrequencyAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('frequency', 'id')
    search_fields = ('frequency',)


@admin.register(LiftingSchedule)
class LiftingScheduleAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('from_time', 'to_time', 'id')
    search_fields = ('from_time', 'to_time')


@admin.register(ComplaintSource)
class ComplaintSourceAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'source_name')  # Displays ID and name
    search_fields = ('source_name',)  # Adds a search bar
    ordering = ('source_name',)  # Orders by name alphabetically
    list_per_page = 20  # Limits the number of items displayed per page


@admin.register(ComplaintType)
class ComplaintTypeAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'type_name')  # Displays ID and name
    search_fields = ('type_name',)  # Adds a search bar
    ordering = ('type_name',)  # Orders by name alphabetically
    list_per_page = 20  # Limits the number of items displayed per page


class ActivityAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('name',)  
    search_fields = ('name',)  
admin.site.register(Activity, ActivityAdmin)


class CLCStaffAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('employee_id', 'name', 'location', 'designation') 
    search_fields = ('name', 'employee_id', 'location__location_name')  
    list_filter = ('location', 'designation')  
admin.site.register(CLCStaff, CLCStaffAdmin)


@admin.register(TubeWell)
class TubeWellAdmin(CustomAdminMixin, ImportExportModelAdmin):
    form = TubeWellForm
    list_display = ('id', 'tubewell_id', 'tubewell_name', 'location', 'uc', 'latitude', 'longitude')
    search_fields = ('tubewell_id', 'tubewell_name')
    list_filter = ('location', 'uc')

    # Custom action for CSV export
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        """
        Custom action to export selected TubeWell data as CSV.
        """
        # Define the HTTP response for CSV download
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=tubewells.csv'

        # Create a CSV writer object
        writer = csv.writer(response)
        
        # Write the header row
        writer.writerow(['TubeWell ID', 'TubeWell Name', 'Location', 'UC', 'Latitude', 'Longitude'])
        
        # Write the data rows
        for tubewell in queryset:
            writer.writerow([
                
                tubewell.tubewell_id,
                tubewell.tubewell_name,
                tubewell.location,
                tubewell.uc,
                tubewell.latitude,
                tubewell.longitude,
            ])
        
        return response

    export_as_csv.short_description = "Export selected tubewells as CSV"


@admin.register(Vehicle)
class VehicleAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'vehicle_id', 'vehicle_name', 'location', 'vehicle_type')
    search_fields = ('vehicle_name',)
    list_filter = ('vehicle_type', 'location')

    # Custom action for CSV export
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        """
        Custom action to export selected vehicle data as CSV.
        """
        # Define the HTTP response for CSV download
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=vehicles.csv'

        # Create a CSV writer object
        writer = csv.writer(response)
        
        # Write the header row
        writer.writerow(['Vehicle ID', 'Vehicle Name', 'Location', 'Vehicle Type'])
        
        # Write the data rows
        for vehicle in queryset:
            writer.writerow([
                vehicle.vehicle_id,
                vehicle.vehicle_name,
                vehicle.location,
                vehicle.vehicle_type,
            ])
        
        return response

    export_as_csv.short_description = "Export selected vehicles as CSV"

from django.utils.html import format_html
from django.utils.html import format_html
import os
import zipfile
from io import BytesIO
from django.http import HttpResponse
from django.utils.text import slugify



@admin.register(Employee)
# class EmployeeAdmin(CustomAdminMixin, ImportExportModelAdmin):
class EmployeeAdmin(CustomAdminMixin, admin.ModelAdmin):
    
    form = EmployeeForm
    list_display = (
        'employee_id',
        'name',
        'father_name',
        'location',
        'uc',
        'department',
        'designation',
        'profile_image_tag',
        'status',
        'id',
    )
    search_fields = ('employee_id', 'name')
    list_filter = ('location', 'uc', 'designation', 'department', 'status')



    def get_queryset(self, request):
        """
        Superusers see all bins.
        Other users see only bins in locations they have permissions for.
        """
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs  # Superuser sees everything
        
        # Get locations the user has permission for
        allowed_locations = Location.objects.filter(locationpermission__user=request.user)

        # Filter bins based on allowed locations
        return qs.filter(location__in=allowed_locations)
    
    def get_readonly_fields(self, request, obj=None):
        """
        Superusers can edit everything.
        Other users can only edit 'profile_image'.
        """
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)
        
        # Normal users: make all fields readonly except profile_image
        all_fields = [f.name for f in self.model._meta.get_fields() if f.editable and f.name != 'profile_image']
        return all_fields
    

    

    # ✅ Small image preview in admin
    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html(
                '<a href="{url}" target="_blank">'
                '<img src="{url}" width="80" height="80" style="border-radius:5px;" />'
                '</a>',
                url=obj.profile_image.url
            )
        return "No Image"

    profile_image_tag.short_description = "Profile Image"

    # Custom action for Excel export
    actions = ['export_as_excel', 'export_as_excel_data_only', 'download_images_as_zip']


    def download_images_as_zip(self, request, queryset):
        # Create an in-memory ZIP
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for emp in queryset:
                if emp.profile_image and os.path.exists(emp.profile_image.path):
                    # Create a safe, readable filename
                    emp_name = emp.name or "Unknown"
                    filename = f"{emp.employee_id} - {slugify(emp_name)}{os.path.splitext(emp.profile_image.path)[1]}"
                    try:
                        zip_file.write(emp.profile_image.path, arcname=filename)
                    except Exception as e:
                        print(f"⚠️ Could not add image for {emp.name}: {e}")

        # Prepare response
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response['Content-Disposition'] = 'attachment; filename=employee_images.zip'
        return response

    download_images_as_zip.short_description = "🖼️ Download selected employees' images (ZIP)"


    # ---------------------------------------------------------------------
    # 🟡 2. Export Excel DATA ONLY (No Images)
    # ---------------------------------------------------------------------
    def export_as_excel_data_only(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = "Employees (Data Only)"

        headers = [
            'Employee ID', 'Name', 'Father Name', 'Location', 'UC',
            'Department', 'Designation', 'CNIC', 'Acting Role', 'Status'
        ]
        ws.append(headers)

        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 20
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 20
        ws.column_dimensions['G'].width = 20
        ws.column_dimensions['H'].width = 20
        ws.column_dimensions['I'].width = 20
        ws.column_dimensions['J'].width = 15

        for emp in queryset:
            ws.append([
                emp.employee_id,
                emp.name,
                emp.father_name,
                str(emp.location),
                str(emp.uc),
                str(emp.department),
                str(emp.designation),
                str(getattr(emp, 'cnic', '')),
                str(getattr(emp, 'acting_role', '')),
                str(emp.status),
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=employees_data_only.xlsx'

        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        response.write(excel_buffer.read())
        return response

    export_as_excel_data_only.short_description = "📄 Export selected employees as Excel (Data Only)"


        # ✅ Excel Export with Image
    def export_as_excel(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = "Employees"

        # Header
        headers = [
            'Employee ID', 'Name', 'Father Name', 'Location', 'UC',
            'Department', 'Designation', 'CNIC', 'Acting Role', 'Status', 'Profile Image'
        ]
        ws.append(headers)

        # Column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 20
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 20
        ws.column_dimensions['G'].width = 20
        ws.column_dimensions['H'].width = 20
        ws.column_dimensions['I'].width = 20
        ws.column_dimensions['J'].width = 15
        ws.column_dimensions['K'].width = 25  # Image column

        row = 2
        for emp in queryset:
            ws.cell(row=row, column=1, value=emp.employee_id)
            ws.cell(row=row, column=2, value=emp.name)
            ws.cell(row=row, column=3, value=emp.father_name)
            ws.cell(row=row, column=4, value=str(emp.location))
            ws.cell(row=row, column=5, value=str(emp.uc))
            ws.cell(row=row, column=6, value=str(emp.department))
            ws.cell(row=row, column=7, value=str(emp.designation))
            ws.cell(row=row, column=8, value=str(getattr(emp, 'cnic', '')))
            ws.cell(row=row, column=9, value=str(getattr(emp, 'acting_role', '')))
            ws.cell(row=row, column=10, value=str(emp.status))

            # 🖼️ Add image if available
            if emp.profile_image and os.path.exists(emp.profile_image.path):
                try:
                    with PILImage.open(emp.profile_image.path) as im:
                        im.thumbnail((100, 100))  # Resize image
                        bio = BytesIO()
                        im.save(bio, format='PNG')
                        bio.seek(0)
                        img = XLImage(bio)
                        img.width = 80
                        img.height = 80
                        ws.add_image(img, f'K{row}')  # Add image in column K
                        ws.row_dimensions[row].height = 65  # Match image height
                except Exception as e:
                    print(f"⚠️ Image error for {emp.name}: {e}")

            row += 1

        # ✅ Prepare HTTP response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=employees_with_images.xlsx'

        # Save workbook to response
        excel_buffer = BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        response.write(excel_buffer.read())

        return response

    export_as_excel.short_description = "📘 Export selected employees as Excel (with Images)"

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import User
from .models import Bin, LocationPermission, Location

class BinAdmin(ImportExportModelAdmin):
    fieldsets = (
        ('Bin Information', {
            'fields': ('bin_id', 'name', 'name_container', 'location', 'uc', 'nc', 'category', 'capacity', 'vehicle', 'street')
        }),
        ('Schedule Detail', {
            'fields': ('lifting_frequency', 'first_lifting_time', 'second_lifting_time', 'third_lifting_time', 'days'),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
        ('Coordinate', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
    )

    list_display = ('bin_id', 'name_container', 'location', 'uc', 'category', 'capacity', 'lifting_frequency')
    search_fields = ('bin_id', 'name_container', 'location__location_name', 'uc__uc_name')
    list_filter = ('location', 'uc', 'name', 'category', 'lifting_schedule', 'lifting_frequency')
    # readonly_fields = ('bin_id', 'name', 'location', 'uc', 'nc')
    filter_horizontal = ['days']

    def get_queryset(self, request):
        """
        Superusers see all bins.
        Other users see only bins in locations they have permissions for.
        """
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs  # Superuser sees everything
        
        # Get locations the user has permission for
        allowed_locations = Location.objects.filter(locationpermission__user=request.user)

        # Filter bins based on allowed locations
        return qs.filter(location__in=allowed_locations)

admin.site.register(Bin, BinAdmin)


@admin.register(Filter)
class FilterAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'filter_id', 'name', 'location')
    search_fields = ('name', 'location__location_name')
    list_filter = ('location',)


@admin.register(Tracker)
class TrackerAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'vehicle_id', 'vehicle_name', 'location', 'vehicle_type')
    search_fields = ('vehicle_id', 'vehicle_name')
    list_filter = ('location', 'vehicle_type')













@admin.register(Street_cleaning)
class Street_cleaningAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'street_name', 'uc_name')
    search_fields = ('Street_name',)
    list_filter = ('uc_name',)


@admin.register(EmployeeAttendance)
class EmployeeAttendanceAdmin(CustomAdminMixin, ImportExportModelAdmin):
    form = EmployeeAttendanceForm
    list_display = ('id', 'attendance_date', 'location', 'employee_name', 'present', 'absent', 'leave')
    search_fields = ('location__location_name', 'employee_name__name')
    list_filter = ('location', 'attendance_date')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'attendance_date'


@admin.register(VehicleAttendance)
class VehicleAttendanceAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'attendance_date', 'location', 'vehicle_name', 'functional', 'non_functional')
    search_fields = ('location__location_name', 'vehicle_name__vehicle_name')
    list_filter = ('location', 'attendance_date')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'attendance_date'


@admin.register(TubeWellAttendance)
class TubeWellAttendanceAdmin(CustomAdminMixin, ImportExportModelAdmin):
    form = TubeWellAttendanceForm
    list_display = ('id', 'tubewell', 'location', 'functional', 'non_functional', 'attendance_date')
    search_fields = ('tubewell__tubewell_name', 'location__location_name')
    list_filter = ('location', 'functional', 'non_functional', 'attendance_date')
    date_hierarchy = 'attendance_date'


@admin.register(WaterSupply)
class WaterSupplyAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'location', 'date')
    list_filter = ('location', 'date')
    search_fields = ('location__location_name',)
    date_hierarchy = 'date'


@admin.register(Revenue)
class RevenueAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = (
        'id', 'location', 'date', 'recovery_day_water_supply', 'recovery_day_solid_waste_management',
        'bill_paid_day_water_supply', 'bill_paid_day_solid_waste_management', 'total_paid_month_water_supply',
        'total_paid_month_solid_waste_management', 'number_of_bills_paid'
    )
    list_filter = ('location', 'date')
    search_fields = ('location__location_name',)
    date_hierarchy = 'date'


@admin.register(Watertest)
class WatertestAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'date', 'location', 'tubewell', 'temperature_c', 'ph', 'output')
    search_fields = ('location__name', 'tubewell__tubewell_name')
    list_filter = ('location', 'uc', 'output', 'date')
    ordering = ('-date',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('location', 'uc', 'tubewell', 'location_type', 'date')}),
        ('Water Quality Measurements', {
            'fields': (
                'temperature_c', 'ph', 'electrical_conductivity_uc_cm', 'dissolved_oxygen_mg_l',
                'tss_mg_l', 'turbidity_ntu', 'tds_mg_l', 'resistivity_ojm_cm', 'salinity_mg_l', 'coliform', 'output'
            )
        }),
        ('Geolocation', {'fields': ('longitude', 'latitude')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)})
    )


@admin.register(BinAttendance)
class BinAttendanceAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('attendance_date', 'bin_name', 'location', 'uc', 'lifted', 'unlifted')
    search_fields = ('attendance_date', 'bin_name__name', 'location__location_name', 'uc__uc_name')
    list_filter = ('attendance_date', 'location', 'uc')
    date_hierarchy = 'attendance_date'


@admin.register(FilterAttendance)
class FilterAttendanceAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'filter_name', 'attendance_date', 'location', 'functional', 'non_functional')
    list_filter = ('attendance_date', 'location', 'functional', 'non_functional')
    search_fields = ('filter_name__name', 'location__location_name')
    ordering = ('attendance_date',)
    date_hierarchy = 'attendance_date'


@admin.register(VehiclePE)
class VehiclePEAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = (
       'id', 'vehicle_name', 'location', 'vehicle_type', 'attendance_date', 'vehicle_trips', 'fuel_issued',
        'odometer_start', 'odometer_end', 'manual_running_km', 'running_km', 'created_at', 'updated_at'
    )
    list_filter = ('location', 'vehicle_type', 'attendance_date')
    search_fields = ('vehicle_name__vehicle_name', 'location__location_name')
    ordering = ('-attendance_date',)
    readonly_fields = ('running_km', 'created_at', 'updated_at')
    date_hierarchy = 'attendance_date'


@admin.register(TrackerAttendance)
class TrackerAttendanceAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'vehicle_name', 'attendance_date', 'location', 'functional', 'non_functional')
    list_filter = ('attendance_date', 'location', 'functional', 'non_functional')
    search_fields = ('vehicle_name__vehicle_name',)
    ordering = ('-attendance_date',)
    date_hierarchy = 'attendance_date'


@admin.register(Sanitation)
class SanitationAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('location', 'date', 'container_lifted', 'moqas_cleared', 'primary_vehicle_trips', 
                    'primary_waste_collection_tons', 'waste_locally_dumped_tons', 'waste_dumped_at_lfs_tons', 
                    'lfs_trips_no', 'local_dumping_trips_no', 'fuel_top_up_liters', 
                    'door_to_door_solid_waste_collection_no', 'replacement_of_manhole_covers', 
                    'cleaning_de_siltation_of_manholes', 'cleaning_de_siltation_of_drain_sewars_km', 
                    'fumigation_sprays_no', 'ir_spray_no', 'created_at', 'updated_at')
    list_filter = ('location', 'date', 'created_at')  # Filters for easier search
    search_fields = ('location__name', 'date', 'created_at')  # Search fields for easy lookup
    date_hierarchy = 'date'  # Makes the date field a useful filter in the admin interface
    ordering = ('-created_at',)  # Order entries by the created date (most recent first)


@admin.register(Vehiclerepair)
class VehiclerepairAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'Vehicle', 'location', 'Vehicle_repair_description', 'cost', 'date', 'created_at', 'updated_at')
    list_filter = ('location', 'date', 'Vehicle')
    search_fields = ('Vehicle__vehicle_name', 'location__location_name', 'Vehicle_repair_description')
    ordering = ('-date',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    fieldsets = (
        ('Repair Details', {
            'fields': ('Vehicle', 'location', 'Vehicle_repair_description', 'cost', 'remarks', 'image', 'date'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    list_per_page = 25


@admin.register(Tubewellrepair)
class TubewellrepairAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'tubewell', 'location', 'uc', 'tubewell_repair_description', 'cost', 'date', 'created_at', 'updated_at')
    list_filter = ('location', 'uc', 'date', 'tubewell')
    search_fields = ('tubewell__name', 'location__location_name', 'uc__name', 'tubewell_repair_description')
    ordering = ('-date',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    fieldsets = (
        ('Repair Details', {
            'fields': ('tubewell', 'location', 'uc', 'tubewell_repair_description', 'cost', 'remarks', 'image', 'date'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    list_per_page = 25


@admin.register(Binfoam)
class BinfoamAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = (
        'attendance_date', 
        'location', 
        'uc', 
        'bin_name', 
        'liftingfrequency', 
        'firstliftingtime', 
        'secondliftingtime', 
        'thirdliftingtime', 
        'created_at', 
        'updated_at'
    )
    list_filter = (
        'attendance_date', 
        'location', 
        'uc', 
        'bin_name', 
        'liftingfrequency'
    )
    search_fields = (
        'location__name', 
        'uc__name', 
        'bin_name__name', 
        'attendance_date'
    )
    ordering = ('-attendance_date',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'attendance_date'


from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from .models import Complaint, ComplaintActionLog

from django.contrib import admin
from .models import Complaint, ComplaintResolution

class ComplaintResolutionInline(admin.StackedInline):
    model = ComplaintResolution
    extra = 1  # Show one empty inline form
    can_delete = False


# Inline admin to show actions under Complaint
class ComplaintActionLogInline(admin.TabularInline):
    model = ComplaintActionLog
    extra = 0
    readonly_fields = ('complaint', 'user', 'action', 'timestamp')
    can_delete = False


from .models import ComplaintFeedback  # Import your model

class ComplaintFeedbackInline(admin.StackedInline):
    model = ComplaintFeedback
    extra = 0               # Don’t show extra empty forms
    max_num = 1             # Only one feedback per complaint
    can_delete = True       # Allow deleting the feedback
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Complaint)
class ComplaintAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = (
        'id',
        'first_name',
        'phone_number',
        'location',
        'uc',
        'complaint_source',
        'complaint_type',
        'status',
        'date',
        'created_at',
        'updated_at',
    )
    list_filter = ('status', 'date', 'location', 'uc', 'complaint_type', 'SubType', 'complaint_source',)
    search_fields = (
        'id',
        'first_name',
        'last_name',
        'bill_number',
        'area',
        'address',
        'tehsil',
        'cnic',
        'cell_number',
    )
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Applicant Information', {
            'fields': (
                'first_name',
                'last_name',
                'bill_number',
                'cnic',
                'gender',
                'consumer_type',
                'cell_number',
                'phone_number',
                'area',
                'address',
                'tehsil',
            )
        }),
        ('Complaint Details', {
            'fields': (
                'location',
                'uc',
                'title',
                'complaint_source',
                'Pcp_compalin_no',
                'Eak_compalin_no',
                'Ebaldia_compalin_no',
                'complaint_type',
                'SubType',
                'complaint_detail',
                'type',
                'before_image',
                'date',
                'status',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # ✅ Custom Action to Export CSV
    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)

        # Header
        writer.writerow(field_names)

        # Rows
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Download Selected as CSV"

    inlines = [ComplaintResolutionInline, ComplaintFeedbackInline, ComplaintActionLogInline]




from io import BytesIO
import pandas as pd


# Custom Admin for CLC
from django.contrib import admin
from django.utils import timezone
from django import forms
from django.db.models import Q
from datetime import datetime
from .models import CLC  # Assuming you have your custom mixins
from import_export.admin import ImportExportModelAdmin
from django.http import HttpResponse
from io import BytesIO
import zipfile
import pandas as pd
from django.utils.html import format_html



from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.contrib import admin
from .models import CLC
import os
from reportlab.pdfgen import canvas



# Custom Date Range Filter
class DateRangeFilter(admin.SimpleListFilter):
    title = 'date range'
    parameter_name = 'date_range'

    def lookups(self, request, model_admin):
        return (
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            # ('custom', 'Custom Range'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            today = timezone.now().date()

            if value == 'this_week':
                start_date = today - timezone.timedelta(days=today.weekday())
                end_date = start_date + timezone.timedelta(days=6)
                return queryset.filter(date__range=[start_date, end_date])
            elif value == 'last_week':
                start_date = today - timezone.timedelta(days=today.weekday() + 7)
                end_date = start_date + timezone.timedelta(days=6)
                return queryset.filter(date__range=[start_date, end_date])
            elif value == 'this_month':
                start_date = today.replace(day=1)
                end_date = today.replace(day=28) + timezone.timedelta(days=4)  # Last day of the month
                return queryset.filter(date__range=[start_date, end_date])
            elif value == 'last_month':
                start_date = (today.replace(day=1) - timezone.timedelta(days=1)).replace(day=1)
                end_date = today.replace(day=1) - timezone.timedelta(days=1)
                return queryset.filter(date__range=[start_date, end_date])
            elif value == 'custom':
                # Handle custom date filter here (e.g., show a date range picker if needed)
                pass
        return queryset

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from io import BytesIO
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from PIL import Image as PILImage
import zipfile
import os
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, Border, Side
from io import BytesIO
from PIL import Image as PILImage
import os
from django.utils import timezone

class CLCAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('date', 'location', 'name_of_official', 'activity', 'brief_report', 'display_asset_image1')
    search_fields = ('name_of_official__name', 'location__location_name', 'activity__name')
    list_filter = ('location', 'activity', 'name_of_official', DateRangeFilter)
    list_per_page = 20
    date_hierarchy = 'date'

    def display_asset_image1(self, obj):
        if obj.image:
            image_url = obj.image.url
            return format_html('<a href="{}" target="_blank"><img src="{}" width="50" height="50" /></a>', image_url, image_url)
        else:
            return None

    display_asset_image1.short_description = "Image"

    # ================================
    # 🔹 ACTION 1 — Download Images as ZIP
    # ================================
    actions = ['download_images', 'download_clc_report_with_images']

    def download_images(self, request, queryset):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a') as zip_file:
            for obj in queryset:
                if obj.image:
                    image_path = obj.image.path
                    image_name = os.path.basename(image_path)
                    with open(image_path, 'rb') as image_file:
                        zip_file.writestr(image_name, image_file.read())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=CLC_Images.zip'
        return response

    download_images.short_description = "Download selected images (ZIP)"

    # ================================
    # 🔹 ACTION 2 — Export Excel Report (with images)
    # ================================
    def download_clc_report_with_images(self, request, queryset):

        # 🔹 Optimize DB queries
        queryset = queryset.select_related('uc', 'nc', 'uc__location')

        wb = Workbook()
        ws = wb.active
        ws.title = "CLC Visit Report"

        # 🔹 Heading
        ws.merge_cells('A1:J1')
        title_cell = ws['A1']
        title_cell.value = "WSSP CLC Visit Report"
        title_cell.font = Font(size=16, bold=True)
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 28

        # 🔹 Headers
        headers = [
            "EMP Name", "Activity", "Location", "UC", "NC",
            "No. of Participants", "IEC Material Distribution",
            "Brief Report", "Date", "Image"
        ]
        ws.append(headers)

        # 🔹 Header Styling
        header_font = Font(bold=True)
        border_style = Side(border_style="thin")
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=2, column=col)
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = Border(
                top=border_style, left=border_style,
                right=border_style, bottom=border_style
            )

        # 🔹 Column widths
        col_widths = [22, 25, 25, 18, 18, 22, 30, 45, 15, 22]
        for i, width in enumerate(col_widths, 1):
            ws.column_dimensions[chr(64 + i)].width = width

        # 🔹 Data rows
        row_index = 3
        for obj in queryset:
            ws.cell(row=row_index, column=1, value=str(obj.name_of_official))
            ws.cell(row=row_index, column=2, value=str(obj.activity))

            # ✅ Location (via UC → Location)
            ws.cell(
                row=row_index,
                column=3,
                value=obj.uc.location.location_name if obj.uc and obj.uc.location else ''
            )

            # ✅ UC & NC FIXED
            ws.cell(
                row=row_index,
                column=4,
                value=obj.uc.uc_name if obj.uc else ''
            )
            ws.cell(
                row=row_index,
                column=5,
                value=obj.nc.nc_name if obj.nc else ''
            )

            ws.cell(row=row_index, column=6, value=obj.no_of_participants or '')
            ws.cell(row=row_index, column=7, value=obj.IEC_material_distribution or '')
            ws.cell(row=row_index, column=8, value=obj.brief_report)
            ws.cell(row=row_index, column=9, value=obj.date.strftime('%d-%b-%Y') if obj.date else '')

            # 🔹 Insert Image
            if obj.image and os.path.exists(obj.image.path):
                try:
                    with PILImage.open(obj.image.path) as im:
                        im.thumbnail((150, 150))
                        bio = BytesIO()
                        im.save(bio, format="PNG")
                        bio.seek(0)

                        img = XLImage(bio)
                        img.width = 120
                        img.height = 120
                        ws.add_image(img, f"J{row_index}")
                except Exception as e:
                    print(f"⚠️ Image error for {obj}: {e}")

            ws.row_dimensions[row_index].height = 95
            row_index += 1

        # 🔹 Footer
        ws.merge_cells(f"A{row_index + 1}:J{row_index + 1}")
        footer = ws[f"A{row_index + 1}"]
        footer.value = (
            f"Generated on {timezone.now().strftime('%d-%b-%Y')} "
            f"by {request.user.get_full_name() or request.user.username}"
        )
        footer.font = Font(italic=True, size=10)
        footer.alignment = Alignment(horizontal='right')

        # 🔹 Download
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="WSSP_CLC_Visit_Report.xlsx"'
        return response


    download_clc_report_with_images.short_description = "📸 Download CLC Visit Report (with Images)"

admin.site.register(CLC, CLCAdmin)


class PerfomaTubeAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = (
        'tube_well_id',
        'tube_well_functional',
        'operator_present',
        'supervisor_present',
        'bookkeeping_updated',
        'filtration_plant_functional',
        'scada_system_functional',
        'water_quality_device_functional',
        'operator_in_uniform',
        'mechanical_fault',
        'pipe_leakage',
        'maintenance_record_maintained',
        'registered_connection',
        'illegal_connection',
        'complaints_redressal',
    )
    list_filter = (
        'tube_well_functional',
        'operator_present',
        'supervisor_present',
        'bookkeeping_updated',
        'filtration_plant_functional',
        'scada_system_functional',
        'water_quality_device_functional',
        'operator_in_uniform',
        'mechanical_fault',
        'pipe_leakage',
        'maintenance_record_maintained',
        'registered_connection',
        'illegal_connection',
        'complaints_redressal',
    )
    search_fields = ('tube_well_id',)
admin.site.register(perfoma_tube, PerfomaTubeAdmin)


from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Font, Border, Side, PatternFill
from io import BytesIO
from PIL import Image as PILImage
import os
from django.utils import timezone


@admin.register(FieldVisitReport)
class FieldVisitReportAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'date', 'location', 'name_of_official', 'visit_area', 'display_image_preview')
    search_fields = ('location__name', 'name_of_official__name', 'visit_area')
    list_filter = ('location', 'date')
    date_hierarchy = 'date'
    actions = ['download_field_visit_report_with_images']

    def display_image_preview(self, obj):
        """Show small image preview in admin list."""
        if obj.image:
            image_url = obj.image.url
            return format_html('<a href="{}" target="_blank"><img src="{}" width="50" height="50" /></a>', image_url, image_url)
        return "-"
    display_image_preview.short_description = "Image"

    def download_field_visit_report_with_images(self, request, queryset):
        wb = Workbook()
        ws = wb.active
        ws.title = "Field Visit Report"

        # --- 🔹 Title ---
        ws.merge_cells('A1:H1')
        title_cell = ws['A1']
        title_cell.value = "WSSP Field Visit Report"
        title_cell.font = Font(size=16, bold=True)
        title_cell.alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 28

        # --- 🔹 Headers ---
        headers = [
            "S.No", "Date", "Location", "Official Name", "Visit Area",
            "Brief Report", "Latitude / Longitude", "Image"
        ]
        ws.append(headers)

        # --- 🔹 Style Header Row ---
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")  # Blue tone
        border_style = Side(border_style="thin", color="000000")

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = Border(top=border_style, left=border_style, right=border_style, bottom=border_style)

        # --- 🔹 Column Widths ---
        col_widths = [8, 15, 25, 25, 25, 45, 25, 22]
        for i, width in enumerate(col_widths, 1):
            ws.column_dimensions[chr(64 + i)].width = width

        # --- 🔹 Data Rows ---
        row_index = 3
        counter = 1
        for obj in queryset:
            ws.cell(row=row_index, column=1, value=counter)
            ws.cell(row=row_index, column=2, value=str(obj.date))
            ws.cell(row=row_index, column=3, value=str(obj.location))
            ws.cell(row=row_index, column=4, value=str(obj.name_of_official))
            ws.cell(row=row_index, column=5, value=str(obj.visit_area))
            ws.cell(row=row_index, column=6, value=str(obj.brief_report))
            ws.cell(row=row_index, column=7, value=f"{obj.latitude or ''}, {obj.longitude or ''}")

            # --- 🔹 Insert Image ---
            if obj.image and os.path.exists(obj.image.path):
                try:
                    with PILImage.open(obj.image.path) as im:
                        im.thumbnail((150, 150))
                        bio = BytesIO()
                        im.save(bio, format="PNG")
                        bio.seek(0)
                        img = XLImage(bio)
                        img.width = 120
                        img.height = 120
                        ws.add_image(img, f"H{row_index}")
                except Exception as e:
                    print(f"⚠️ Error adding image for {obj}: {e}")

            ws.row_dimensions[row_index].height = 90
            counter += 1
            row_index += 1

        # --- 🔹 Footer ---
        ws.merge_cells(f"A{row_index + 1}:H{row_index + 1}")
        footer_cell = ws[f"A{row_index + 1}"]
        footer_cell.value = f"Generated on {timezone.now().strftime('%d-%b-%Y %I:%M %p')} by {request.user.get_full_name() or request.user.username}"
        footer_cell.font = Font(italic=True, size=10)
        footer_cell.alignment = Alignment(horizontal='right', vertical='center')

        # --- 🔹 Save and return ---
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response['Content-Disposition'] = 'attachment; filename="WSSP_Field_Visit_Report.xlsx"'
        return response

    download_field_visit_report_with_images.short_description = "📊 Download Field Visit Report (with Images)"



@admin.register(PostAttendance)
class PostAttendanceAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'post_type', 'post_detail', 'no_of_post', 'post_date', 'created_at')
    search_fields = ('post_type__name', 'post_detail__media_channel', 'no_of_post')
    list_filter = ('post_type', 'post_detail', 'post_date', 'no_of_post')
    ordering = ('-post_date',)
    date_hierarchy = 'post_date'

    def get_queryset(self, request):
        # Ensure related fields are retrieved efficiently
        queryset = super().get_queryset(request)
        return queryset.select_related('post_type', 'post_detail')









@admin.register(locationmap)
class LocationMapAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude') 
    search_fields = ('name',) 
    list_filter = ('latitude',)


class KMZUploadAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at', 'visualization_link')
    readonly_fields = ('visualization_link',)
admin.site.register(KMZUpload, KMZUploadAdmin)





@admin.register(ViewName)
class ViewNameAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ['id', 'name']
    list_filter = ['name']
    search_fields = ['name']



@admin.register(UserViewPermission)
class UserViewPermissionAdmin(ImportExportModelAdmin):
    list_display = ['id', 'display_users', 'display_views', 'can_view']
    search_fields = ['user__username']  # Fixed field name
    filter_horizontal = ['view_name', 'user']

    def display_users(self, obj):
        return ", ".join(user.username for user in obj.user.all())
    display_users.short_description = 'Users'

    def display_views(self, obj):
        return ", ".join(view.name for view in obj.view_name.all())
    display_views.short_description = 'Assigned Views'



class LocationPermissionAdmin(ImportExportModelAdmin):
    list_display = ('id', 'display_users', 'get_locations', 'can_view')
    list_filter = ('can_view', 'locations')
    search_fields = ('user__username', 'locations__location_name')  # Fixed field name
    filter_horizontal = ['locations', 'user']

    def display_users(self, obj):
        return ", ".join(user.username for user in obj.user.all())
    display_users.short_description = 'Users'

    def get_locations(self, obj):
        return ", ".join(location.location_name for location in obj.locations.all())
    get_locations.short_description = 'Locations'





class UcPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'can_view')  
    filter_horizontal = ('Uc',) 

class DepartmentPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'can_view')
    list_filter = ('can_view',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('Department',)

class OfficialFPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'can_view')
    list_filter = ('can_view',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('Official',)

class OfficialCPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'can_view')
    list_filter = ('can_view',)
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('Official',)

admin.site.register(DepartmentPermission, DepartmentPermissionAdmin)
admin.site.register(officialFPermission, OfficialFPermissionAdmin)
admin.site.register(officialCPermission, OfficialCPermissionAdmin)
admin.site.register(UcPermission, UcPermissionAdmin)
admin.site.register(LocationPermission, LocationPermissionAdmin)





@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'model_name', 'object_id')
    date_hierarchy = 'timestamp'

    # Remove the delete action from the admin interface
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']  # Remove the delete action
        return actions

    # Disable the "delete" button for individual items
    def has_delete_permission(self, request, obj=None):
        return False  # Disable delete button in change view

    # Prevent deletion for individual UserActivityLog entries
    def delete_model(self, request, obj):
        pass  # Prevent delete operation

    # Prevent bulk deletion
    def delete_queryset(self, request, queryset):
        pass  # Prevent bulk delete operation

    # Disable update/save operations
    def has_change_permission(self, request, obj=None):
        return False  # Disable the change functionality

    def save_model(self, request, obj, form, change):
        pass  # Prevent saving or updating entries


class LogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'method', 'path', 'ip_address', 'timestamp')
    readonly_fields = ('user', 'action', 'method', 'path', 'timestamp', 'ip_address')
    list_filter = ('user', 'action', 'method', 'timestamp')
    search_fields = ('user__username', 'action', 'path', 'ip_address')
    date_hierarchy = 'timestamp'


     # Remove the delete action from the admin interface
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']  # Remove the delete action
        return actions


    
    # Prevent bulk deletion
    def delete_queryset(self, request, queryset):
        pass  # Prevent bulk delete operation

    # Disable update/save operations
    def has_change_permission(self, request, obj=None):
        return False  # Disable the change functionality

    def save_model(self, request, obj, form, change):
        pass  # Prevent saving or updating entries



    def save_model(self, request, obj, form, change):
        action = "Updated" if change else "Added"
        log_admin_action(request, action, obj)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        log_admin_action(request, "Deleted", obj)
        super().delete_model(request, obj)

    def changelist_view(self, request, extra_context=None):
        log_admin_action(request, "Viewed List")
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        log_admin_action(request, "Viewed", obj)
        return super().change_view(request, object_id, form_url, extra_context)

admin.site.register(Log, LogAdmin) 


def get_client_ip(request: HttpRequest):
    """
    Extract the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_admin_action(request, action, obj=None):
    """
    Log admin actions with additional details.
    """
    Log.objects.create(  # Use Log instead of UserActivityLog
        user=request.user,
        action=action if obj is None else f"{action}: {obj}",
        method=request.method,
        path=request.path,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )



# admin.py

from django.contrib import admin
from .models import Document, ADP

admin.site.register(Document)
admin.site.register(ADP)


@admin.register(Fuel)
class FuelAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'location', 'date', 'lfs_trips_no', 'fuel_top_up_liters', 'created_at', 'updated_at')
    search_fields = ('location__location_name', 'date')
    list_filter = ('location', 'date')
    ordering = ('-date',)  # Orders by latest date first

from .models import TubeWellwaterdepth

@admin.register(TubeWellwaterdepth)
class TubeWellwaterdepthAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('tubewell', 'water_table_depth', 'water_table_measurment_date', 'created_at', 'updated_at')
    list_filter = ('tubewell', 'water_table_measurment_date')
    search_fields = ('tubewell__tubewell_name', 'water_table_depth')
    ordering = ('-water_table_measurment_date',)   
    autocomplete_fields = ('tubewell',)  

# admin.py
from django.contrib import admin
from .models import TubeWellWaterProduce

import csv
from django.http import HttpResponse
from django.contrib import admin
from .models import TubeWellWaterProduce

@admin.register(TubeWellWaterProduce)
class TubeWellWaterProduceAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = (
        'tubewell',
        'run_hour',
        'water_produce',
        'water_meter_reading_start',
        'water_meter_reading_end',
        'water_produce_date',
        'remarks',
        'created_at',
        'updated_at',
    )
    list_filter = ('water_produce_date', 'tubewell')
    search_fields = ('tubewell__tubewell_name', 'remarks')
    ordering = ('-water_produce_date',)
    date_hierarchy = 'water_produce_date'
    readonly_fields = ('created_at', 'updated_at')

    # 📥 Custom CSV export action
    actions = ['download_csv']

    def download_csv(self, request, queryset):
        # Prepare response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tubewell_water_produce.csv"'

        writer = csv.writer(response)
        # Write header row
        writer.writerow([
            'Tube Well', 'Run Hour', 'Water Produce', 
            'Start Reading', 'End Reading', 
            'Produce Date', 'Remarks', 'Created At', 'Updated At'
        ])
        # Write data rows
        for obj in queryset:
            writer.writerow([
                obj.tubewell,
                obj.run_hour,
                obj.water_produce,
                obj.water_meter_reading_start,
                obj.water_meter_reading_end,
                obj.water_produce_date,
                obj.remarks,
                obj.created_at,
                obj.updated_at,
            ])
        return response

    download_csv.short_description = "Download selected as CSV"

    # Optional: if you want to auto-calculate water_produce in admin, override save_model
    def save_model(self, request, obj, form, change):
        try:
            run_hour = float(obj.run_hour)
            meter_start = float(obj.water_meter_reading_start)
            meter_end = float(obj.water_meter_reading_end)
            average_discharge = float(obj.tubewell.average_discharge)

            # Calculate water_produce using your logic:
            if meter_start == 0 and meter_end == 0:
                obj.water_produce = str(average_discharge * run_hour)
            else:
                obj.water_produce = str(meter_end - meter_start)
        except Exception:
            pass  # fallback if conversion fails, keep existing value

        super().save_model(request, obj, form, change)

from django.contrib import admin
from .models import TubeWellElectricityUsage


@admin.register(TubeWellElectricityUsage)
class TubeWellElectricityUsageAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = (
        'tubewell',
        'usage_date',
        'meter_reading_start',
        'meter_reading_end',
        'electricity_consumed',
        'remarks',
        'created_at',
        'updated_at',
    )
    list_filter = ('tubewell', 'usage_date')
    search_fields = ('tubewell__tubewell_name', 'remarks')
    date_hierarchy = 'usage_date'
    ordering = ('-usage_date',)
    readonly_fields = ('tubewell', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': (
                'tubewell',
                'usage_date',
                'meter_reading_start',
                'meter_reading_end',
                'electricity_consumed',
                'remarks',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # 📥 Custom CSV export action
    actions = ['download_csv']

    def download_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tubewell_electricity_usage.csv"'

        writer = csv.writer(response)
        # Header row
        writer.writerow([
            'Tube Well', 'Usage Date', 'Start Reading', 'End Reading',
            'Electricity Consumed', 'Remarks', 'Created At', 'Updated At'
        ])
        # Data rows
        for obj in queryset:
            writer.writerow([
                obj.tubewell,
                obj.usage_date,
                obj.meter_reading_start,
                obj.meter_reading_end,
                obj.electricity_consumed,
                obj.remarks,
                obj.created_at,
                obj.updated_at,
            ])
        return response

    download_csv.short_description = "Download selected as CSV"

    def get_queryset(self, request):
        """
        Superusers see all records.
        Other users see only records in locations they have permissions for.
        """
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        # Get locations the user has permission for
        allowed_locations = Location.objects.filter(
            locationpermission__user=request.user
        )

        # Filter by the tubewell's location
        return qs.filter(tubewell__location__in=allowed_locations)

from django.contrib import admin
from .models import Hotspot


@admin.register(Hotspot)
class HotspotAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = (
        'name',
        'supervisor_name',
        'supervisor_phone_number',
        'officer_name',
        'officer_phone_number',
        'latitude',
        'longitude',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'name',
        'supervisor_name',
        'officer_name',
        'supervisor_phone_number',
        'officer_phone_number',
    )
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)

from django.contrib import admin
from .models import Hotspot, HotspotEvent


@admin.register(HotspotEvent)
class HotspotEventAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = (
        'hotspot',
        'rain_start_time',
        'rain_end_time',
        'urban_start_time',
        'urban_end_time',
        'rainfall_intensity',
        'created_at',
    )
    list_filter = ('rainfall_intensity', 'created_at', 'updated_at')
    search_fields = ('hotspot__name', 'remarks')
    ordering = ('-created_at',)


from django.contrib import admin
from .models import AdpScheme, FinancialProgress, PhysicalProgress, Schemestatus


class FinancialProgressInline(admin.TabularInline):
    model = FinancialProgress
    extra = 1  
    fields = ('progress', 'date', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class PhysicalProgressInline(admin.TabularInline):
    model = PhysicalProgress
    extra = 1
    fields = ('progress', 'date', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class SchemestatusInline(admin.TabularInline):
    model = Schemestatus
    extra = 1  
    fields = ('status', 'date', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AdpScheme)
class AdpSchemeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'aa_cost', 'release', 'exp', 'start_date', 'end_date')
    search_fields = ('code', 'name')
    list_filter = ('start_date', 'end_date')
    ordering = ('-start_date', 'code')
    inlines = [FinancialProgressInline, PhysicalProgressInline, SchemestatusInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FinancialProgress)
class FinancialProgressAdmin(admin.ModelAdmin):
    list_display = ('scheme', 'progress', 'created_at', 'updated_at')
    search_fields = ('scheme__code', 'scheme__name', 'progress')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PhysicalProgress)
class PhysicalProgressAdmin(admin.ModelAdmin):
    list_display = ('scheme', 'progress', 'created_at', 'updated_at')
    search_fields = ('scheme__code', 'scheme__name', 'progress')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


from django.contrib import admin
from .models import TubeWelldischarge

@admin.register(TubeWelldischarge)
class TubeWelldischargeAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('tubewell', 'updated_average_discharge', 'updated_average_discharge_date', 'created_at')
    list_filter = ('tubewell', 'updated_average_discharge_date')
    search_fields = ('tubewell__tubewell_name', 'updated_average_discharge')
    ordering = ('-updated_average_discharge_date',)
    list_per_page = 25    




# from django.contrib import admin
# from .models import MajorRoad, TrunkSewerInspection, StormDrainInspection, PondingPointsInspection

# @admin.register(MajorRoad)
# class MajorRoadAdmin(CustomAdminMixin, ImportExportModelAdmin):
#     list_display = (
#         'facility_name', 'location', 'emp_name', 'inspection_date', 
#          'free_from_garbage_rubble'
#     )
#     search_fields = ('facility_name', 'location__name', 'emp_name')
#     list_filter = ('inspection_date', 'free_from_garbage_rubble')
#     fields = (
#         'location', 'facility_name', 'dry_and_clean', 'no_traffic_violations',
#         'emp_name', 'remark', 'inspection_date'
#     )

# @admin.register(TrunkSewerInspection)
# class TrunkSewerInspectionAdmin(CustomAdminMixin, ImportExportModelAdmin):
#     list_display = (
#         'facility_name', 'location', 'emp_name', 'inspection_date',
#         'manhole_covered', 'manhole_free_from_damage', 'no_sediment_around_manhole'
#     )
#     search_fields = ('facility_name', 'location__name', 'emp_name')
#     list_filter = ('inspection_date', 'manhole_covered', 'manhole_free_from_damage')
#     fields = (
#         'location', 'facility_name',
#         'manhole_covered', 'manhole_free_from_damage', 'no_sediment_around_manhole',
#         'no_outflow_of_sewage_from_manhole', 'no_bad_odour_around_manhole',
#         'no_blockage_at_outflow_of_drain', 'fastflow_of_water_at_outflow_of_drain',
#         'emp_name', 'remark', 'inspection_date'
#     )

# @admin.register(StormDrainInspection)
# class StormDrainInspectionAdmin(CustomAdminMixin, ImportExportModelAdmin):
#     list_display = ('facility_name', 'location', 'emp_name', 'inspection_date', 'entry_clear', 'exit_clear')
#     search_fields = ('facility_name', 'location__name', 'emp_name')
#     list_filter = ('inspection_date', 'entry_clear', 'exit_clear')
#     fields = (
#         'location', 'facility_name', 'entry_clear', 'exit_clear',
#         'emp_name', 'remark', 'inspection_date'
#     )

# @admin.register(PondingPointsInspection)
# class PondingPointsInspectionAdmin(CustomAdminMixin, ImportExportModelAdmin):
#     list_display = ('facility_name', 'location', 'emp_name', 'inspection_date', 'any_attempt_by_government')
#     search_fields = ('facility_name', 'location__name', 'emp_name')
#     list_filter = ('inspection_date', 'any_attempt_by_government')
#     fields = (
#         'location', 'facility_name', 'any_attempt_by_government',
#         'emp_name', 'remark', 'inspection_date'
#     )





from django.contrib import admin
from .models import (
    MajorRoad_Add,
    TrunkSewer_Add,
    StormDrain_Add,
    PondingPoints_Add,
)

# ===========================
# Major Roads Admin
# ===========================
@admin.register(MajorRoad_Add)
class MajorRoadAddAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'road', 'location')
    search_fields = ('road',)
    list_filter = ('location',)
    ordering = ('road',)


# ===========================
# Trunk Sewer Admin
# ===========================
@admin.register(TrunkSewer_Add)
class TrunkSewerAddAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'trunksewer', 'location')
    search_fields = ('trunksewer',)
    list_filter = ('location',)
    ordering = ('trunksewer',)


# ===========================
# Storm Drain Admin
# ===========================
@admin.register(StormDrain_Add)
class StormDrainAddAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'stormdrain', 'location')
    search_fields = ('stormdrain',)
    list_filter = ('location',)
    ordering = ('stormdrain',)


# ===========================
# Ponding Points Admin
# ===========================
@admin.register(PondingPoints_Add)
class PondingPointsAddAdmin(CustomAdminMixin, ImportExportModelAdmin):
    list_display = ('id', 'pondingpoints', 'location')
    search_fields = ('pondingpoints',)
    list_filter = ('location',)
    ordering = ('pondingpoints',)



from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .models import (
    MajorRoad_inspection,
    TrunkSewer_inspection,
    StormDrain_inspection,
    PondingPoints_inspection
)



# ================= IMAGE PREVIEW MIXIN =================
class ImagePreviewMixin:
    def image_preview_1(self, obj):
        if obj.image_1:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="60" style="border-radius:4px"/>'
                '</a>',
                obj.image_1.url, obj.image_1.url
            )
        return "-"

    def image_preview_2(self, obj):
        if obj.image_2:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="60" style="border-radius:4px"/>'
                '</a>',
                obj.image_2.url, obj.image_2.url
            )
        return "-"

    image_preview_1.short_description = "Image 1"
    image_preview_2.short_description = "Image 2"


# ================= MAJOR ROADS =================
@admin.register(MajorRoad_inspection)
class MajorRoadInspectionAdmin(
    CustomAdminMixin,
    ImportExportModelAdmin,
    ImagePreviewMixin
):
    list_display = (
        'facility_name', 'zone',
        'free_from_garbage_rubble', 'dry_and_clean',
        'inspection_date',
        'image_preview_1', 'image_preview_2'
    )

    list_filter = (
        'zone', 'inspection_date',
        'free_from_garbage_rubble', 'dry_and_clean'
    )

    search_fields = (
        'facility_name__road',
        'zone__location_name',
        'emp_name'
    )

    date_hierarchy = 'inspection_date'
    readonly_fields = ('image_preview_1', 'image_preview_2')


# ================= TRUNK SEWER =================
@admin.register(TrunkSewer_inspection)
class TrunkSewerInspectionAdmin(
    CustomAdminMixin,
    ImportExportModelAdmin,
    ImagePreviewMixin
):
    list_display = (
        'facility_name', 'zone',
        'manhole_covered',
        'no_outflow_of_sewage_from_manhole',
        'no_blockage_at_outflow_of_drain',
        'inspection_date',
        'image_preview_1', 'image_preview_2'
    )

    list_filter = (
        'zone', 'inspection_date',
        'manhole_covered',
        'no_outflow_of_sewage_from_manhole',
        'no_blockage_at_outflow_of_drain'
    )

    search_fields = (
        'facility_name__trunksewer',
        'zone__location_name',
        'emp_name'
    )

    date_hierarchy = 'inspection_date'
    readonly_fields = ('image_preview_1', 'image_preview_2')


# ================= STORM DRAIN =================
@admin.register(StormDrain_inspection)
class StormDrainInspectionAdmin(
    CustomAdminMixin,
    ImportExportModelAdmin,
    ImagePreviewMixin
):
    list_display = (
        'facility_name', 'zone',
        'entry_clear', 'exit_clear',
        'inspection_date',
        'image_preview_1', 'image_preview_2'
    )

    list_filter = (
        'zone', 'inspection_date',
        'entry_clear', 'exit_clear'
    )

    search_fields = (
        'facility_name__stormdrain',
        'zone__location_name',
        'emp_name'
    )

    date_hierarchy = 'inspection_date'
    readonly_fields = ('image_preview_1', 'image_preview_2')


# ================= PONDING POINTS =================
@admin.register(PondingPoints_inspection)
class PondingPointsInspectionAdmin(
    CustomAdminMixin,
    ImportExportModelAdmin,
    ImagePreviewMixin
):
    list_display = (
        'facility_name', 'zone',
        'any_attempt_by_government',
        'inspection_date',
        'image_preview_1', 'image_preview_2'
    )

    list_filter = (
        'zone', 'inspection_date',
        'any_attempt_by_government'
    )

    search_fields = (
        'facility_name__pondingpoints',
        'zone__location_name',
        'emp_name'
    )

    date_hierarchy = 'inspection_date'
    readonly_fields = ('image_preview_1', 'image_preview_2')



from .models import VisitSchedule, Manhole_inspection


@admin.register(VisitSchedule)
class VisitScheduleAdmin(CustomAdminMixin, ImportExportModelAdmin):
    autocomplete_fields = ("employee",)

    list_display = (
        "visit_date",
        "employee",
        "get_locations",
        "get_ucs",
        "short_remarks",
    )

    list_filter = (
        "visit_date",
        "employee",
        "locations",
        "ucs",
    )

    search_fields = (
        "employee__name",
        "employee__employee_id",
        "visit_roads",
        "remarks",
    )

    filter_horizontal = (
        "locations",
        "ucs",
    )

    date_hierarchy = "visit_date"

    ordering = ("-visit_date",)

    # ✅ Show selected locations in list display
    def get_locations(self, obj):
        return ", ".join([loc.location_name for loc in obj.locations.all()])
    get_locations.short_description = "Locations"

    # ✅ Show selected UCs in list display
    def get_ucs(self, obj):
        return ", ".join([uc.uc_name for uc in obj.ucs.all()])
    get_ucs.short_description = "UCs"

    # ✅ Short remarks preview
    def short_remarks(self, obj):
        if obj.remarks:
            return obj.remarks[:40] + "..." if len(obj.remarks) > 40 else obj.remarks
        return "-"
    short_remarks.short_description = "Remarks"



# ================= Manhole_inspection =================
@admin.register(Manhole_inspection)
class Manhole_inspectionAdmin(
    CustomAdminMixin,
    ImportExportModelAdmin,
    ImagePreviewMixin
):
    list_display = (
        'facility_name', 'zone',
        'manhole_covered',
        'any_demage_manhole_covered',
        'level_with_road',

        'inspection_date',
        'image_preview_1', 'image_preview_2'
    )

    list_filter = (
        'zone', 'inspection_date',
        'manhole_covered'
    )

    search_fields = (
        'facility_name__uc_name',
        'zone__name',
        'emp_name'
    )

    date_hierarchy = 'inspection_date'






from django.contrib import admin
from .models import Manhole, ManholeShape, ManholeCoverSize, ManholeCoverMaterial
from django.db.models import Count


# 🔹 Manhole Shape Admin
@admin.register(ManholeShape)
class ManholeShapeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# 🔹 Manhole Cover Size Admin
@admin.register(ManholeCoverSize)
class ManholeCoverSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'size')
    search_fields = ('size',)


# 🔹 Manhole Cover Material Admin
@admin.register(ManholeCoverMaterial)
class ManholeCoverMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'material')
    search_fields = ('material',)


# 🔹 Manhole Admin
class LocationFilter(admin.SimpleListFilter):
    title = 'Location'
    parameter_name = 'location'

    def lookups(self, request, model_admin):
        locations = Location.objects.annotate(
            manhole_count=Count('uc__manhole')
        ).order_by('location_name')

        return [
            (loc.id, f"{loc.location_name} ({loc.manhole_count})")
            for loc in locations
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(uc__location__id=self.value())
        return queryset




import openpyxl
from django.http import HttpResponse
from openpyxl import Workbook


def export_manhole_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Manholes"

    # Headers
    headers = [
        'UC',
        'Zone',
        'Status',
        'Shape',
        'Cover Size',
        'Material',
        'Latitude',
        'Longitude',
    ]
    ws.append(headers)

    # Data rows
    for obj in queryset:
        ws.append([
            obj.uc.uc_name if obj.uc else "",
            obj.uc.location.location_name if obj.uc and obj.uc.location else "",
            obj.status,
            obj.shape.name if obj.shape else "",
            obj.cover_size,
            obj.cover_material.material if obj.cover_material else "",
            obj.latitude,
            obj.longitude,
        ])

    # Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=manholes.xlsx'

    wb.save(response)
    return response


export_manhole_excel.short_description = "Download Excel"        

@admin.register(Manhole)
class ManholeAdmin(CustomAdminMixin, ImportExportModelAdmin):


    list_display = (
        'id',
        'uc',
        'get_location',  
        'status',
        'shape',
        'cover_size',
        'cover_material',
        'latitude',
        'longitude',
        'created_at'
    )

    list_filter = (
        'status',
        'shape',
        'cover_material',
        'uc',
        LocationFilter,  
    )


    actions = [export_manhole_excel]  


    search_fields = (
        'id',
        'uc__uc_name',   
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )

    def get_location(self, obj):
        if obj.uc and obj.uc.location:
            return obj.uc.location.location_name
        return "-"
    
    get_location.short_description = 'Location'