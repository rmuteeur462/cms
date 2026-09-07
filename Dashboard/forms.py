from django import forms
from .models import (
    Employee,Watertest,Bin, BinAttendance ,
    EmployeeAttendance,
    TubeWell,
    TubeWellAttendance,FieldVisitReport,Sanitation,CLC,
    WaterSupply,
    Revenue,
    Complaint,
    Location,
    UC,PostAttendance,FieldVisitReport,VehiclePerformance
)
import os

from dal import autocomplete

from dal import autocomplete
from django import forms
from .models import Employee, Location, UC

class BaseLocationForm(forms.ModelForm):
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=autocomplete.ModelSelect2(url='location-autocomplete'),
        required=True
    )

    uc = forms.ModelChoiceField(
        queryset=UC.objects.none(),  # Initially empty
        widget=autocomplete.ModelSelect2(
            url='uc-autocomplete',
            forward=['location']  # Depends on location
        ),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only adjust queryset if field exists
        if 'uc' in self.fields:
            if 'location' in self.data:
                try:
                    location_id = int(self.data.get('location'))
                    self.fields['uc'].queryset = UC.objects.filter(location_id=location_id)
                except (ValueError, TypeError):
                    self.fields['uc'].queryset = UC.objects.none()
            elif self.instance.pk and self.instance.location:
                self.fields['uc'].queryset = UC.objects.filter(location=self.instance.location)
            else:
                self.fields['uc'].queryset = UC.objects.none()


class EmployeeForm(BaseLocationForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'name', 'father_name', 'location', 'uc',
            'designation', 'department', 'cnic', 'acting_role', 'status', 'profile_image'
        ]

class EmployeeAttendanceForm(BaseLocationForm):
    employee_name = forms.ModelChoiceField(
        queryset=Employee.objects.none(),  # Initially empty
        widget=autocomplete.ModelSelect2(
            url='employee-autocomplete',
            forward=['uc']  # Make this field dependent on UC
        ),
        required=True
    )

    class Meta:
        model = EmployeeAttendance
        fields = ['location', 'uc', 'employee_name', 'attendance_date', 'absent', 'present', 'leave']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set employee queryset based on selected UC
        if 'uc' in self.data:
            try:
                uc_id = int(self.data.get('uc'))
                self.fields['employee_name'].queryset = Employee.objects.filter(uc_id=uc_id)
            except (ValueError, TypeError):
                pass  # Leave queryset empty if invalid input
        elif self.instance.pk:
            self.fields['employee_name'].queryset = Employee.objects.filter(uc=self.instance.uc)


class TubeWellForm(BaseLocationForm):
    class Meta:
        model = TubeWell
        fields = ['tubewell_id', 'tubewell_name', 'location', 'uc', 'tubewell_no_connection', 'average_discharge', 'scada', 'flow_meter', 'pesco_id', 'motor_hours_power', 'latitude', 'longitude']


class TubeWellAttendanceForm(BaseLocationForm):
    tubewell = forms.ModelChoiceField(
        queryset=TubeWell.objects.none(),  # Initially empty
        widget=autocomplete.ModelSelect2(
            url='tubewell-autocomplete',
            forward=['uc']  # Make this field dependent on UC
        ),
        required=True
    )

    class Meta:
        model = TubeWellAttendance
        fields = ['tubewell', 'location', 'uc', 'functional', 'non_functional', 'non_operational',  'run_hour', 'electricity_consume', 'water_produce', 'remarks', 'meter_reading_start', 'meter_reading_end', 'attendance_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set TubeWell queryset based on selected UC
        if 'uc' in self.data:
            try:
                uc_id = int(self.data.get('uc'))
                self.fields['tubewell'].queryset = TubeWell.objects.filter(uc_id=uc_id)
            except (ValueError, TypeError):
                pass  # Leave queryset empty if invalid input
        elif self.instance.pk:
            self.fields['tubewell'].queryset = TubeWell.objects.filter(uc=self.instance.uc)



class WaterSupplyReportForm(forms.ModelForm):

    class Meta:
        model = WaterSupply
        fields = [
            'location',
            'date',
            'new_water_supply_connection_registered',
            'functional_filtration_plants',  # Added
            'non_functional_filtration_plants'  # Added
        ]

        widgets = {
            'location': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'new_water_supply_connection_registered': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set location, uc, location_type, tubewell, and output as required fields
        self.fields['location'].required = True
        self.fields['date'].required = True  # Ensuring that the date field is required





from django import forms
from .models import Revenue, Location  # Assuming Location is your ForeignKey model

from django import forms
from .models import Revenue, Location  # Assuming Location is your ForeignKey model

class RevenueManagementReportForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = [
            'location',
            'recovery_day_water_supply',
            'recovery_day_solid_waste_management',
            'bill_paid_day_water_supply',
            'bill_paid_day_solid_waste_management',
            'total_paid_month_water_supply',
            'total_paid_month_solid_waste_management',
            'bills_paid_month_water_supply',
            'bills_paid_month_solid_waste_management',
            'recovery_of_day',
            'recovery_of_month',
            'disconnection_of_defaulters',
            'billed_amount_total',
            'number_of_bills_paid',
            'date',
        ]
        widgets = {
            'location': forms.Select(attrs={'class': 'form-control'}),  # ForeignKey field (Location)
            'recovery_day_water_supply': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter recovery day amount for water supply'}),
            'recovery_day_solid_waste_management': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter recovery day amount for solid waste management'}),
            'bill_paid_day_water_supply': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter bill paid for water supply'}),
            'bill_paid_day_solid_waste_management': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter bill paid for solid waste management'}),
            'total_paid_month_water_supply': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter total paid for water supply this month'}),
            'total_paid_month_solid_waste_management': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter total paid for solid waste management this month'}),
            'bills_paid_month_water_supply': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of bills paid for water supply this month'}),
            'bills_paid_month_solid_waste_management': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of bills paid for solid waste management this month'}),
            'recovery_of_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter recovery for the day'}),
            'recovery_of_month': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter recovery for the month'}),
            'disconnection_of_defaulters': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of disconnections for defaulters'}),
            'billed_amount_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter total revenue of the day amount'}),
            'number_of_bills_paid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter number of bills paid'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),  # Date input with class for styling
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make location a required field
        self.fields['location'].required = True
     


from django import forms
from .models import Complaint

from django import forms
from .models import Complaint

class ComplaintManagementForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=Complaint.STATUS_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='pending',
        label="Status"
    )

    gender = forms.ChoiceField(
        choices=Complaint.gender_choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    consumer_type = forms.ChoiceField(
        choices=Complaint.consumer_type_choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Complaint
        fields = [
            # Applicant Information
            'first_name', 'last_name', 'bill_number', 'area', 'address', 'tehsil',
            'cnic', 'cell_number', 'phone_number', 'gender', 'consumer_type',

            # Complaint Information
            'location', 'uc', 'complaint_source', 'Pcp_compalin_no', 'Eak_compalin_no', 'Ebaldia_compalin_no',
            'complaint_type', 'SubType', 'title', 'type', 'complaint_detail', 'date', 'before_image', 'status',
        ]

        widgets = {
            # Applicant Info
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bill_number': forms.TextInput(attrs={'class': 'form-control'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tehsil': forms.TextInput(attrs={'class': 'form-control'}),
            'cnic': forms.TextInput(attrs={'class': 'form-control'}),
            'cell_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),

            # Complaint Info
            'location': forms.Select(attrs={'class': 'form-control', 'id': 'id_location'}),
            'uc': forms.Select(attrs={'class': 'form-control', 'id': 'id_uc'}),
            'complaint_source': forms.Select(attrs={'class': 'form-control'}),
            'Pcp_compalin_no': forms.TextInput(attrs={'class': 'form-control'}),
            'Eak_compalin_no': forms.TextInput(attrs={'class': 'form-control'}),
            'Ebaldia_compalin_no': forms.TextInput(attrs={'class': 'form-control'}),
            'complaint_type': forms.Select(attrs={'class': 'form-control'}),
            'SubType': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'complaint_detail': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
             'before_image': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control-file', 
                    'accept': 'image/*'
                }
            ),
        }


from django import forms
from .models import PostAttendance, Post, PostDetail  # Assuming models Post, PostDetail

class PostAttendanceForm(forms.ModelForm):
    class Meta:
        model = PostAttendance
        fields = ['post_type', 'post_detail', 'no_of_post', 'resource_link', 'post_date']
        widgets = {
            'post_type': forms.Select(attrs={'class': 'form-control'}),  # ForeignKey field (Post) as dropdown
            'post_detail': forms.Select(attrs={'class': 'form-control'}),  # ForeignKey field (PostDetail) as dropdown
            'no_of_post': forms.Select(attrs={'class': 'form-control'}),  # Choices field (STATE_CHOICE2)
            'resource_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter resource URL'}),  # URL field
            'post_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),  # Date input with class for styling
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required or optional as needed
        self.fields['post_type'].required = True  # Example: Making post_type required
        self.fields['post_detail'].required = True  # Example: Making post_detail required
       


from django import forms
from .models import FieldVisitReport

class FieldVisitReportForm(forms.ModelForm):
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label="Duty Location",        
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    visited_zone_name = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label="Visited Zone",        
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = FieldVisitReport
        fields = ['date', 'location', 'name_of_official', 'visited_zone_name', 'visit_area', 'brief_report', 'image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name_of_official': forms.Select(attrs={'class': 'form-control'}),
            'visit_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the area visited'}),
            'brief_report': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Provide a brief report of the visit'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(FieldVisitReportForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'image':
                field.required = True
            else:
                field.required = False

       
            

   

from django import forms
from .models import Sanitation

class SanitationForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = Sanitation
        fields = [
            'location',
            'date',
            'container_lifted',
            'moqas_cleared',
            'primary_vehicle_trips',
            'primary_waste_collection_tons',
            'waste_locally_dumped_tons',
            'waste_dumped_at_lfs_tons',
            'lfs_trips_no',
            'local_dumping_trips_no',
            'fuel_top_up_liters',
            'door_to_door_solid_waste_collection_no',
            'replacement_of_manhole_covers',
            'cleaning_de_siltation_of_manholes',
            'cleaning_de_siltation_of_drain_sewars_km',
            'fumigation_sprays_no',
            'ir_spray_no',
            'rate_killing_no',       # ✅ Added
            'dog_catching_no'
        ]
        widgets = {
            'location': forms.Select(attrs={'class': 'form-control'}),
            'container_lifted': forms.NumberInput(attrs={'class': 'form-control'}),
            'moqas_cleared': forms.NumberInput(attrs={'class': 'form-control'}),
            'primary_vehicle_trips': forms.NumberInput(attrs={'class': 'form-control'}),
            'primary_waste_collection_tons': forms.NumberInput(attrs={'class': 'form-control'}),
            'waste_locally_dumped_tons': forms.NumberInput(attrs={'class': 'form-control'}),
            'waste_dumped_at_lfs_tons': forms.NumberInput(attrs={'class': 'form-control'}),
            'lfs_trips_no': forms.NumberInput(attrs={'class': 'form-control'}),
            'local_dumping_trips_no': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_top_up_liters': forms.NumberInput(attrs={'class': 'form-control'}),
            'door_to_door_solid_waste_collection_no': forms.NumberInput(attrs={'class': 'form-control'}),
            'replacement_of_manhole_covers': forms.NumberInput(attrs={'class': 'form-control'}),
            'cleaning_de_siltation_of_manholes': forms.NumberInput(attrs={'class': 'form-control'}),
            'cleaning_de_siltation_of_drain_sewars_km': forms.NumberInput(attrs={'class': 'form-control'}),
            'fumigation_sprays_no': forms.NumberInput(attrs={'class': 'form-control'}),
            'ir_spray_no': forms.NumberInput(attrs={'class': 'form-control'}),
             'rate_killing_no': forms.NumberInput(attrs={'class': 'form-control'}),   # ✅ Widget
            'dog_catching_no': forms.NumberInput(attrs={'class': 'form-control'}),   # ✅ Widget
        }
        


from django import forms
from .models import CLC  # Ensure this imports your CLC model correctly

class CLCForm(forms.ModelForm):
    class Meta:
        model = CLC
        fields = ['date', 'location', 'uc', 'nc', 'name_of_official', 'activity', 'no_of_participants', 'IEC_material_distribution', 'brief_report', 'image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'uc': forms.Select(attrs={'class': 'form-control'}),
            'nc': forms.Select(attrs={'class': 'form-control'}),
            'no_of_participants': forms.NumberInput(attrs={'class': 'form-control'}),
            'IEC_material_distribution': forms.TextInput(attrs={'class': 'form-control'}),

            
            'name_of_official': forms.Select(attrs={'class': 'form-control'}),
            'activity': forms.Select(attrs={'class': 'form-control'}),
            'brief_report': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Provide a brief report of the activity'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(CLCForm, self).__init__(*args, **kwargs)
        # Set all fields to required
        for field_name, field in self.fields.items():
            field.required = True
        # Make 'image' field optional
        self.fields['image'].required = False



class CLCFilterForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,  # Optional date filter
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        required=False  # Optional location filter
    )


from django import forms
from .models import Watertest

class WatertestForm(forms.ModelForm):
    class Meta:
        model = Watertest
        fields = [
            'location',
            'uc',
            'tubewell',
            'location_type',
            'temperature_c',
            'ph',
            'electrical_conductivity_uc_cm',
            'dissolved_oxygen_mg_l',
            'tss_mg_l',
            'turbidity_ntu',
            'tds_mg_l',
            'resistivity_ojm_cm',
            'salinity_mg_l',
            'coliform',
            'output',
            'longitude',
            'latitude',
            'date'
        ]
        widgets = {
            'location': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'uc': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'tubewell': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'location_type': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'temperature_c': forms.NumberInput(attrs={'class': 'form-control'}),
            'ph': forms.NumberInput(attrs={'class': 'form-control'}),
            'electrical_conductivity_uc_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'dissolved_oxygen_mg_l': forms.NumberInput(attrs={'class': 'form-control'}),
            'tss_mg_l': forms.NumberInput(attrs={'class': 'form-control'}),
            'turbidity_ntu': forms.NumberInput(attrs={'class': 'form-control'}),
            'tds_mg_l': forms.NumberInput(attrs={'class': 'form-control'}),
            'resistivity_ojm_cm': forms.NumberInput(attrs={'class': 'form-control'}),
            'salinity_mg_l': forms.NumberInput(attrs={'class': 'form-control'}),
            'coliform': forms.NumberInput(attrs={'class': 'form-control'}),
            'output': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set location, uc, location_type, tubewell, and output as required fields
        self.fields['location'].required = True
        self.fields['uc'].required = True
        self.fields['location_type'].required = True
        self.fields['tubewell'].required = True
        self.fields['output'].required = True
        self.fields['date'].required = True


class BinForm(forms.ModelForm):
    class Meta:
        model = Bin
        fields = ['bin_id', 'name', 'location', 'uc', 'category', 'capacity', 'lifting_schedule', 'lifting_frequency', 'latitude', 'longitude', 'days'] 



from django import forms
from .models import Bin

class BinUpdateForm(forms.ModelForm):
    class Meta:
        model = Bin
        fields = [
            'name_container', 
            'name', 
            'location', 
            'uc', 
            'latitude', 
            'longitude',
            'category', 
            'capacity', 
            'lifting_schedule', 
            'lifting_frequency', 
            'days'
        ]
        widgets = {
            'name_container': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter container name'
            }),
            'name': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select bin type'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select location'
            }),
            'uc': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select UC'
            }),
            'latitude': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter latitude'
            }),
            'longitude': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter longitude'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select category'
            }),
            'capacity': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select capacity'
            }),
            'lifting_schedule': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select lifting schedule'
            }),
            'lifting_frequency': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select lifting frequency'
            }),
            'days': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make specific fields read-only
        read_only_fields = ['name_container', 'name', 'location', 'uc']
        for field in read_only_fields:
            self.fields[field].widget.attrs['readonly'] = True
            self.fields[field].widget.attrs['disabled'] = True  # For select inputs



class BinAttendanceForm(forms.ModelForm):
    bin_name = forms.ModelChoiceField(
        queryset=Bin.objects.none(),  # Initially empty
        required=True
    )

    class Meta:
        model = BinAttendance
        fields = ['location', 'uc', 'bin_name', 'attendance_date', 'lifted', 'unlifted']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set bin queryset based on selected UC
        if 'uc' in self.data:
            try:
                uc_id = int(self.data.get('uc'))
                self.fields['bin_name'].queryset = Bin.objects.filter(uc_id=uc_id)
            except (ValueError, TypeError):
                pass  # Leave queryset empty if invalid input
        elif self.instance.pk:
            self.fields['bin_name'].queryset = Bin.objects.filter(uc=self.instance.uc)



from django import forms
from dal import autocomplete  # Ensure you have Django Autocomplete Light installed
from .models import Filter, FilterAttendance

class FilterForm(forms.ModelForm):
    class Meta:
        model = Filter
        fields = ['filter_id', 'name', 'location']


class FilterAttendanceForm(forms.ModelForm):
    filter_name = forms.ModelChoiceField(
        queryset=Filter.objects.none(),  # Initially empty
        widget=autocomplete.ModelSelect2(
            url='filter-autocomplete',  # URL for autocomplete functionality
            forward=['location']  # Make this field dependent on Location
        ),
        required=True
    )

    class Meta:
        model = FilterAttendance
        fields = ['location', 'filter_name', 'attendance_date', 'functional', 'non_functional']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set filter queryset based on selected location
        if 'location' in self.data:
            try:
                location_id = int(self.data.get('location'))
                self.fields['filter_name'].queryset = Filter.objects.filter(location_id=location_id)
            except (ValueError, TypeError):
                pass  # Leave queryset empty if invalid input
        elif self.instance.pk:
            self.fields['filter_name'].queryset = Filter.objects.filter(location=self.instance.location)




from django import forms
from .models import VehiclePE

class VehiclePEForm(forms.ModelForm):
    class Meta:
        model = VehiclePE
        fields = [
            'location', 'vehicle_name', 'vehicle_type', 'attendance_date',
            'vehicle_trips', 'fuel_issued', 'engine_oil', 'hydraulic_oil', 'odometer_start', 'odometer_end',
            'manual_running_km'
        ]

    widgets = {
        'attendance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        'location': forms.Select(attrs={'class': 'form-control'}),
        'vehicle_name': forms.Select(attrs={'class': 'form-control'}),
        'vehicle_trips': forms.Select(attrs={'class': 'form-control'}),
        'fuel_issued': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        'odometer_start': forms.NumberInput(attrs={'class': 'form-control'}),
        'odometer_end': forms.NumberInput(attrs={'class': 'form-control'}),
        'manual_running_km': forms.NumberInput(attrs={'class': 'form-control'}),
    }

    def clean_odometer_start(self):
        odometer_start = self.cleaned_data.get('odometer_start')
        return odometer_start if odometer_start is not None else None  # Convert empty string to None

    def clean_odometer_end(self):
        odometer_end = self.cleaned_data.get('odometer_end')
        return odometer_end if odometer_end is not None else None  # Convert empty string to None

    def clean_manual_running_km(self):
        manual_running_km = self.cleaned_data.get('manual_running_km')
        return manual_running_km if manual_running_km is not None else None  # Convert empty string to None



# forms.py
from django import forms
from .models import Tracker, TrackerAttendance

class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        fields = ['vehicle_id', 'vehicle_name', 'location', 'vehicle_type']

class TrackerAttendanceForm(forms.ModelForm):
    class Meta:
        model = TrackerAttendance
        fields = ['location', 'vehicle_name', 'attendance_date', 'functional', 'non_functional']



from django import forms
from .models import Tubewellrepair

class TubewellrepairForm(forms.ModelForm):
    class Meta:
        model = Tubewellrepair
        fields = [
            'location', 'uc', 'tubewell', 'tubewell_repair_description', 'cost', 'remarks', 'image', 'date'
        ]
        widgets = {
                        'location': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'uc': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'tubewell': forms.Select(attrs={'class': 'form-select', 'required': True}),

            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tubewell_repair_description': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Set location, uc, location_type, tubewell, and output as required fields
            self.fields['location'].required = True
            self.fields['uc'].required = True
            self.fields['tubewell'].required = True
            self.fields['tubewell_repair_description'].required = True

            self.fields['cost'].required = True
            self.fields['date'].required = True



from django import forms
from .models import Vehiclerepair

class VehiclerepairForm(forms.ModelForm):
    class Meta:
        model = Vehiclerepair
        fields = [
            'location',
            'Vehicle',
            'Vehicle_repair_description',
            'cost',
            'remarks',
            'image',
            'date',
        ]
        widgets = {
            'location': forms.Select(attrs={'class': 'form-select', 'required': True}),
                        'Vehicle': forms.Select(attrs={'class': 'form-select', 'required': True}),

            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),

            'Vehicle_repair_description': forms.TextInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set location, uc, location_type, tubewell, and output as required fields
        self.fields['location'].required = True
        self.fields['Vehicle'].required = True
        self.fields['Vehicle_repair_description'].required = True
        self.fields['cost'].required = True
        self.fields['date'].required = True


from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']


from .models import KMZUpload

class KMZUploadForm(forms.ModelForm):
    class Meta:
        model = KMZUpload
        fields = ['file']


from django import forms
from .models import Binfoam

from django import forms
from .models import Binfoam

class BinfoamForm(forms.ModelForm):
    class Meta:
        model = Binfoam
        fields = [
            'location', 
            'uc', 
            'bin_name', 
            'liftingfrequency', 
            'firstliftingtime', 
            'secondliftingtime', 
            'thirdliftingtime', 
            'attendance_date'
        ]
        widgets = {
            'location': forms.Select(attrs={'class': 'form-control'}),
            'uc': forms.Select(attrs={'class': 'form-control'}),
            'bin_name': forms.Select(attrs={'class': 'form-control'}),
            'liftingfrequency': forms.Select(attrs={'class': 'form-control'}),
            'firstliftingtime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'secondliftingtime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'thirdliftingtime': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'attendance_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark these fields as required explicitly
        self.fields['location'].required = True
        self.fields['uc'].required = True
        self.fields['bin_name'].required = True
        self.fields['attendance_date'].required = True

    def clean(self):
        cleaned_data = super().clean()
        location = cleaned_data.get('location')
        uc = cleaned_data.get('uc')
        bin_name = cleaned_data.get('bin_name')
        attendance_date = cleaned_data.get('attendance_date')

        # Validate required fields
        if not location:
            self.add_error('location', "Location is required.")
        if not uc:
            self.add_error('uc', "UC is required.")
        if not bin_name:
            self.add_error('bin_name', "Bin name is required.")
        if not attendance_date:
            self.add_error('attendance_date', "Attendance date is required.")

        return cleaned_data
      

      

from django import forms
from .models import perfoma_tube

from django import forms
from .models import perfoma_tube

class PerfomaTubeForm(forms.ModelForm):
    class Meta:
        model = perfoma_tube
        fields = '__all__'  # Include all fields from the model
        widgets = {
            'name_of_official': forms.Select(attrs={'class': 'form-control'}),
            'tube_well_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tube Well ID'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            # Add consistent widget styles for other fields
            'tube_well_functional': forms.Select(attrs={'class': 'form-control'}),
            'operator_present': forms.Select(attrs={'class': 'form-control'}),
            'supervisor_present': forms.Select(attrs={'class': 'form-control'}),
            'bookkeeping_updated': forms.Select(attrs={'class': 'form-control'}),
            'filtration_plant_functional': forms.Select(attrs={'class': 'form-control'}),
            'scada_system_functional': forms.Select(attrs={'class': 'form-control'}),
            'water_quality_device_functional': forms.Select(attrs={'class': 'form-control'}),
            'operator_in_uniform': forms.Select(attrs={'class': 'form-control'}),
            'mechanical_fault': forms.Select(attrs={'class': 'form-control'}),
            'pipe_leakage': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_record_maintained': forms.Select(attrs={'class': 'form-control'}),
            'registered_connection': forms.Select(attrs={'class': 'form-control'}),
            'illegal_connection': forms.Select(attrs={'class': 'form-control'}),
            'complaints_redressal': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' Location of containers/bins/Moqa'
            }),
            'bins_clean': forms.Select(attrs={'class': 'form-control'}),
            'surroundings_clean': forms.Select(attrs={'class': 'form-control'}),
            'spillage_observed': forms.Select(attrs={'class': 'form-control'}),
            'waste_lifted_timely': forms.Select(attrs={'class': 'form-control'}),
            'staff_uniform': forms.Select(attrs={'class': 'form-control'}),
            'street_littering': forms.Select(attrs={'class': 'form-control'}),
            'area_sweeping': forms.Select(attrs={'class': 'form-control'}),
            'swm_consumer_billed': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_condition': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_trip_record': forms.Select(attrs={'class': 'form-control'}),
            'pending_complaints': forms.Select(attrs={'class': 'form-control'}),
            'staff_attendance': forms.Select(attrs={'class': 'form-control'}),

            'drain_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' Drain location (specific to urban areas prone to blockages)'
            }),

            'drain_desiltation': forms.Select(attrs={'class': 'form-control'}),
            'manhole_covers': forms.Select(attrs={'class': 'form-control'}),
            'sludge_lifting_timely': forms.Select(attrs={'class': 'form-control'}),
            'manhole_desiltation': forms.Select(attrs={'class': 'form-control'}),
            'dewats_status': forms.Select(attrs={'class': 'form-control'}),
            'staff_attendance': forms.Select(attrs={'class': 'form-control'}),

            'Staff_present_specify_numbers_for_absentees': forms.Select(attrs={'class': 'form-control'}),
            'Staff_wearing_proper_uniform_and_safety_equipment': forms.Select(attrs={'class': 'form-control'}),

            'Total_vehicle_in_the_yard': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' Total vehicle in the parking yard'
            }),
            'Layout_of_vehicles': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' Layout of vehicles'
            }),
            'Layout_and_safety_of_store': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' Layout and safety of store'
            }),

            'firefighting_equipment': forms.Select(attrs={'class': 'form-control'}),
            'presence_of_security_guard': forms.Select(attrs={'class': 'form-control'}),
            'functionality_bio_attendance': forms.Select(attrs={'class': 'form-control'}),
            'cctv_cameras': forms.Select(attrs={'class': 'form-control'}),
            'availability_oil_spare_parts': forms.Select(attrs={'class': 'form-control'}),
            'fuel_register_records': forms.Select(attrs={'class': 'form-control'}),
            'general_cleanliness': forms.Select(attrs={'class': 'form-control'}),
            'odometer_temp_fuel_gauge': forms.Select(attrs={'class': 'form-control'}),
            'sheet_provided': forms.Select(attrs={'class': 'form-control'}),
            'parking_sheds': forms.Select(attrs={'class': 'form-control'}),
            'basic_maintenance_tools': forms.Select(attrs={'class': 'form-control'}),
            'washing_pit': forms.Select(attrs={'class': 'form-control'}),

            'waste_in_out_record': forms.Select(attrs={'class': 'form-control'}),
            'vehicles_in_out_record': forms.Select(attrs={'class': 'form-control'}),
            'scavengers_activity': forms.Select(attrs={'class': 'form-control'}),
            'backlog': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_route': forms.Select(attrs={'class': 'form-control'}),
            'fumigation_spray_arrangements': forms.Select(attrs={'class': 'form-control'}),
            'boundary_wall_control': forms.Select(attrs={'class': 'form-control'}),
            'leachate_collection': forms.Select(attrs={'class': 'form-control'}),
            'buffer_zone_plantation': forms.Select(attrs={'class': 'form-control'}),
            'staff_attendance_2': forms.Select(attrs={'class': 'form-control'}),
            'loading_arrangements': forms.Select(attrs={'class': 'form-control'}),
            'staff_working_station': forms.Select(attrs={'class': 'form-control'}),


            'fuel_sops_followed': forms.Select(attrs={'class': 'form-control'}),
            'fuel_card_swiped': forms.Select(attrs={'class': 'form-control'}),
            'driver_signature_fuel_register': forms.Select(attrs={'class': 'form-control'}),
            'fuel_liters_recorded': forms.Select(attrs={'class': 'form-control'}),
            'staff_on_duty_attendance': forms.Select(attrs={'class': 'form-control'}),


            'random_check_households_bills': forms.Select(attrs={'class': 'form-control'}),
            'random_check_shops_bills': forms.Select(attrs={'class': 'form-control'}),


            'uc_area_work_quality': forms.Select(attrs={'class': 'form-control'}),
            'field_staff_duty_hours': forms.Select(attrs={'class': 'form-control'}),


            


            # Continue for all fields, adjusting the widgets and attributes as necessary
            'suggestions_recommendations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter any suggestions or recommendations'
            }),
        }



from django import forms
from .models import Street_cleaning, Location, UC, NC, Street, DayFrequency, LiftingFrequency, Employee, Bin, Vehicle

class StreetCleaningForm(forms.ModelForm):
    class Meta:
        model = Street_cleaning
        fields = [
            'loction', 'uc_name', 'nc_name', 'street_name', 
            'day_frequency', 'Cleaning_frequency', 
            'employee_assign_for_cleaning', 'bin_assign', 'vehicle_assign_for_cleaning'
        ]
        widgets = {
            'loction': forms.Select(attrs={'class': 'form-control'}),  # Custom widget for ForeignKey
            'uc_name': forms.Select(attrs={'class': 'form-control'}),  # Custom widget for ForeignKey
            'nc_name': forms.Select(attrs={'class': 'form-control'}),  # Custom widget for ForeignKey
            'street_name': forms.Select(attrs={'class': 'form-control'}),  # Custom widget for ForeignKey
            'day_frequency': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),  # Custom widget for ForeignKey
            'Cleaning_frequency': forms.Select(attrs={'class': 'form-control'}),  # Custom widget for ForeignKey
            'employee_assign_for_cleaning': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),  # Checkbox for ManyToMany
            'bin_assign': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),  # Custom widget for ForeignKey
            'vehicle_assign_for_cleaning': forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),  # Checkbox for ManyToMany
        }





from django import forms
from .models import Fuel

class FuelForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Fuel
        fields = [
            'location',
            'date',
            'lfs_trips_no',
            'fuel_top_up_liters',
            'primary_trips'
        ]
        widgets = {
            'location': forms.Select(attrs={'class': 'form-control'}),
            'lfs_trips_no': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_top_up_liters': forms.NumberInput(attrs={'class': 'form-control'}),
            'primary_trips': forms.NumberInput(attrs={'class': 'form-control'}),
        }
# forms.py
from django import forms
from .models import TubeWellWaterProduce, TubeWell
from django.utils import timezone

from django import forms
from django.utils import timezone

class TubeWellWaterProduceForm(forms.ModelForm):
    water_produce_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'value': timezone.now().date().strftime('%Y-%m-%d'),
            #  'readonly': 'readonly'
        }),
        required=True  # or False, based on your requirement
    )

    class Meta:
        model = TubeWellWaterProduce
        fields = [
            'tubewell', 
            'run_hour', 
            'water_meter_reading_start', 
            'water_meter_reading_end', 
            'remarks', 
            'water_produce_date'
        ]
        widgets = {
            'tubewell': forms.Select(attrs={'class': 'form-control select2'}),
            'run_hour': forms.TextInput(attrs={'class': 'form-control'}),
            'water_meter_reading_start': forms.TextInput(attrs={'class': 'form-control'}),
            'water_meter_reading_end': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control'}),
         
        }


from django import forms
from .models import TubeWellElectricityUsage

from django import forms
from .models import TubeWellElectricityUsage

class TubeWellElectricityUsageForm(forms.ModelForm):
    electricity_consumed = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )

    class Meta:
        model = TubeWellElectricityUsage
        exclude = ['created_at', 'updated_at']
        widgets = {
            'usage_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'meter_reading_start': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0'
            }),
            'meter_reading_end': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0'
            }),
            'tubewell': forms.Select(attrs={'class': 'form-control select2'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        meter_start = cleaned_data.get('meter_reading_start')
        meter_end = cleaned_data.get('meter_reading_end')
        electricity = cleaned_data.get('electricity_consumed')

        if meter_start is not None and meter_end is not None:
            if meter_end < meter_start:
                raise forms.ValidationError("End reading must be greater than or equal to start reading.")
            # Allow saving with meter readings, even if electricity_consumed is empty
            return cleaned_data

        if electricity is None or electricity <= 0:
            raise forms.ValidationError("Either valid meter readings or electricity consumed must be provided.")

        return cleaned_data

from django import forms
from .models import ComplaintResolution

class ComplaintResolutionForm(forms.ModelForm):
    class Meta:
        model = ComplaintResolution
        fields = ['description', 'after_image', 'customer_satisfaction']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'after_image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'customer_satisfaction': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'  # ✅ HTML required
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Django-level validation required
        self.fields['customer_satisfaction'].required = True
        # (Optional) Custom message if not selected
        self.fields['customer_satisfaction'].error_messages = {
            'required': 'Please select a customer satisfaction option.'
        }

from django import forms
from .models import HotspotEvent


from django import forms
from .models import HotspotEvent

class HotspotEventForm(forms.ModelForm):
    class Meta:
        model = HotspotEvent
        fields = [
            'hotspot',  # User selects hotspot
            'rain_start_time', 'rain_end_time',
            'urban_start_time', 'urban_end_time',
            'rainfall_intensity', 'remarks',
            'before_image', 'after_image',
            'created_at'  # include created_at in the form

        ]
        widgets = {
            'hotspot': forms.Select(attrs={'class': 'form-control'}),
            'rain_start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'rain_end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'urban_start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'urban_end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),

            'rainfall_intensity': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'before_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'after_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
                        'created_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),

        }


from django import forms
from .models import ComplaintFeedback

# forms.py
from django import forms
from .models import ComplaintFeedback

class ComplaintFeedbackForm(forms.ModelForm):
    class Meta:
        model = ComplaintFeedback
        fields = ['feedback_officer_name', 'complaint_feedback', 'happy']
        widgets = {
            'feedback_officer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter officer name'
            }),
            'complaint_feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter feedback'
            }),
            'happy': forms.Select(attrs={
                'class': 'form-select'
            })
        }


from django import forms
from .models import Street


class StreetForm(forms.ModelForm):
    class Meta:
        model = Street
        fields = [
            # --- Basic Info ---
            'street_name',
            'location',
            'uc_name',
            'nc_name',
            'start_latitude',
            'start_longitude',
            'mid_latitude',
            'mid_longitude',
            'end_latitude',
            'end_longitude',
            'no_of_houses',
            'no_of_shops',
            'total_length_km',


            # --- Sweeping Schedule ---
            'sweeping_days',
            'monday_sweeping_time_slots',
            'tuesday_sweeping_time_slots',
            'wednesday_sweeping_time_slots',
            'thursday_sweeping_time_slots',
            'friday_sweeping_time_slots',
            'saturday_sweeping_time_slots',
            'sunday_sweeping_time_slots',
            'sweeping_schedule',
            'sweeping_time_slots',

            # --- Solid Waste Schedule ---
            'solid_waste_days',
            'monday_solid_waste_time_slots',
            'tuesday_solid_waste_time_slots',
            'wednesday_solid_waste_time_slots',
            'thursday_solid_waste_time_slots',
            'friday_solid_waste_time_slots',
            'saturday_solid_waste_time_slots',
            'sunday_solid_waste_time_slots',
            'solid_waste_schedule',
            'solid_waste_time_slots',

            # --- Assignments ---
            'assign_employee',
            'assign_vehicle',
        ]

        widgets = {
            # --- Primary Fields ---
            'street_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter street name',
                'required': 'required',
            }),
            'location': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'uc_name': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required',
            }),
            'nc_name': forms.Select(attrs={'class': 'form-select'}),

            # --- Coordinates ---
            'start_latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Start latitude'}),
            'start_longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Start longitude'}),
            'mid_latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Mid latitude'}),
            'mid_longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Mid longitude'}),
            'end_latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'End latitude'}),
            'end_longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'End longitude'}),

            # --- Counts ---
            'no_of_houses': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of houses',
                'min': 0,
                'required': 'required',
            }),
            'no_of_shops': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of shops',
                'min': 0,
                'required': 'required',
            }),
            'total_length_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total length (km)',
                'min': 0,
                'step': '0.001',   
            }),

            # --- Sweeping Schedule ---
            'sweeping_days': forms.Select(choices=Street.DAYS_OF_WEEK, attrs={'class': 'form-select'}),
            'monday_sweeping_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'tuesday_sweeping_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'wednesday_sweeping_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'thursday_sweeping_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'friday_sweeping_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'saturday_sweeping_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'sunday_sweeping_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'sweeping_schedule': forms.CheckboxSelectMultiple(choices=Street.DAYS_OF_WEEK),
            'sweeping_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),

            # --- Solid Waste Schedule ---
            'solid_waste_days': forms.Select(choices=Street.DAYS_OF_WEEK, attrs={'class': 'form-select'}),
            'monday_solid_waste_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'tuesday_solid_waste_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'wednesday_solid_waste_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'thursday_solid_waste_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'friday_solid_waste_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'saturday_solid_waste_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'sunday_solid_waste_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),
            'solid_waste_schedule': forms.CheckboxSelectMultiple(choices=Street.DAYS_OF_WEEK),
            'solid_waste_time_slots': forms.CheckboxSelectMultiple(choices=Street.TIME_SLOTS),

            # --- Assignments ---
            'assign_employee': forms.CheckboxSelectMultiple(),
            'assign_vehicle': forms.CheckboxSelectMultiple(),
        }

         # 🔥 CHANGE LABEL HERE → "Zone"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].label = "Zone"   

    # ✅ Ensure required validation in backend (not just HTML)
        # ✅ Ensure required validation in backend (not just HTML)
    def clean(self):
        cleaned_data = super().clean()
        required_fields = ['street_name', 'location', 'uc_name', 'no_of_houses', 'no_of_shops']

        for field in required_fields:
            value = cleaned_data.get(field)

            # Allow 0, but not None or empty string
            if value is None or value == "":
                self.add_error(field, f"{field.replace('_', ' ').title()} is required.")

        return cleaned_data







# District Service Delivery forms
    
from django import forms
from .models import MajorRoad, TrunkSewerInspection, StormDrainInspection, PondingPointsInspection, Location

YES_NO_CHOICES = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]

# --- Major Road Form ---
class MajorRoadForm(forms.ModelForm):
    emp_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    remark = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    inspection_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    image_1 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    image_2 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = MajorRoad
        fields = '__all__'

        labels = {
            'location': 'Zone',   # 🔥 Label updated here
        }

        widgets = {
            'location': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'facility_name': forms.Select(attrs={'class': 'form-control', 'required': True}),

            'free_from_garbage_rubble': forms.Select(
                choices=YES_NO_CHOICES,
                attrs={'class': 'form-select', 'required': True}
            ),

            'dry_and_clean': forms.Select(
                choices=YES_NO_CHOICES,
                attrs={'class': 'form-select', 'required': True}
            ),
        }

# --- Trunk Sewer Form ---
class TrunkSewerInspectionForm(forms.ModelForm):
    emp_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    remark = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    inspection_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    image_1 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    image_2 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = TrunkSewerInspection
        fields = '__all__'

        labels = {
            'location': 'Zone',   # 🔥 Updated label
        }

        widgets = {
            'location': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'facility_name': forms.Select(attrs={'class': 'form-control', 'required': True}),

            'manhole_covered': forms.Select(choices=YES_NO_CHOICES, attrs={'class': 'form-select', 'required': True}),
            'manhole_free_from_damage': forms.Select(choices=YES_NO_CHOICES, attrs={'class': 'form-select', 'required': True}),
            'no_sediment_around_manhole': forms.Select(choices=YES_NO_CHOICES, attrs={'class': 'form-select', 'required': True}),
            'no_outflow_of_sewage_from_manhole': forms.Select(choices=YES_NO_CHOICES, attrs={'class': 'form-select', 'required': True}),
            'no_bad_odour_around_manhole': forms.Select(choices=YES_NO_CHOICES, attrs={'class': 'form-select', 'required': True}),
            'no_blockage_at_outflow_of_drain': forms.Select(choices=YES_NO_CHOICES, attrs={'class': 'form-select', 'required': True}),
            'fastflow_of_water_at_outflow_of_drain': forms.Select(choices=YES_NO_CHOICES, attrs={'class': 'form-select', 'required': True}),
        }


# --- Storm Drain Form ---
class StormDrainInspectionForm(forms.ModelForm):
    emp_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    remark = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    inspection_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    image_1 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    image_2 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = StormDrainInspection
        fields = '__all__'

        labels = {
            'location': 'Zone',   # 🔥 Updated label
        }

        widgets = {
            'location': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'facility_name': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'entry_clear': forms.Select(
                choices=YES_NO_CHOICES,
                attrs={'class': 'form-select', 'required': True}
            ),
            'exit_clear': forms.Select(
                choices=YES_NO_CHOICES,
                attrs={'class': 'form-select', 'required': True}
            ),
        }


# --- Ponding Points Form ---
class PondingPointsInspectionForm(forms.ModelForm):
    emp_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    remark = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    inspection_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    image_1 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    image_2 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PondingPointsInspection
        fields = '__all__'

        labels = {
            'location': 'Zone',   # 🔥 Label updated here
        }

        widgets = {
            'location': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'facility_name': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'any_attempt_by_government': forms.Select(
                choices=YES_NO_CHOICES,
                attrs={'class': 'form-select', 'required': True}
            ),
        }




# District Service Delivery forms


from django import forms
from .models import TubeWelldischarge

class TubeWellDischargeForm(forms.ModelForm):
    class Meta:
        model = TubeWelldischarge
        fields = [
            'tubewell',
            'updated_average_discharge',
            'updated_average_discharge_date',
        ]
        widgets = {
            'tubewell': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'data-placeholder': 'Search TubeWell...',
                }
            ),
            'updated_average_discharge': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter average discharge',
                }
            ),
            'updated_average_discharge_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
        }






from django import forms
from .models import (
    MajorRoad_inspection,
    TrunkSewer_inspection,
    StormDrain_inspection,
    PondingPoints_inspection
)


# ========== DSD.1 Major Roads ==========
class MajorRoadInspectionFormDSD(forms.ModelForm):
    class Meta:
        model = MajorRoad_inspection
        fields = '__all__'
        widgets = {
            'zone': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'facility_name': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'free_from_garbage_rubble': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'dry_and_clean': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'inspection_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'remark': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'emp_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'image_1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            'zone',
            'facility_name',
            'emp_name',
            'inspection_date',
            'free_from_garbage_rubble',
            'dry_and_clean',
        ]

        for field in required_fields:
            self.fields[field].required = True




# ========== DSD.2 Trunk Sewer ==========
class TrunkSewerInspectionFormDSD(forms.ModelForm):
    class Meta:
        model = TrunkSewer_inspection
        fields = '__all__'
        widgets = {
            'zone': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'facility_name': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'manhole_covered': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'manhole_free_from_damage': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'no_sediment_around_manhole': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'no_outflow_of_sewage_from_manhole': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'no_bad_odour_around_manhole': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'no_blockage_at_outflow_of_drain': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'fastflow_of_water_at_outflow_of_drain': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'inspection_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'remark': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'emp_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'image_1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            'zone',
            'facility_name',
            'emp_name',
            'inspection_date',
            'manhole_covered',
            'manhole_free_from_damage',
            'no_sediment_around_manhole',
            'no_outflow_of_sewage_from_manhole',
            'no_bad_odour_around_manhole',
            'no_blockage_at_outflow_of_drain',
            'fastflow_of_water_at_outflow_of_drain',
        ]

        for field in required_fields:
            self.fields[field].required = True



# ========== DSD.3 Storm Drain ==========
class StormDrainInspectionFormDSD(forms.ModelForm):
    class Meta:
        model = StormDrain_inspection
        fields = '__all__'
        widgets = {
            'zone': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'facility_name': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'entry_clear': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'exit_clear': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'inspection_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'remark': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'emp_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'image_1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            'zone',
            'facility_name',
            'emp_name',
            'inspection_date',
            'entry_clear',
            'exit_clear',
        ]

        for field in required_fields:
            self.fields[field].required = True




# ========== DSD.4 Ponding Points ==========
class PondingPointsInspectionFormDSD(forms.ModelForm):
    class Meta:
        model = PondingPoints_inspection
        fields = '__all__'
        widgets = {
            'zone': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'facility_name': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'any_attempt_by_government': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'inspection_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'remark': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'emp_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'image_1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image_2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            'zone',
            'facility_name',
            'emp_name',
            'inspection_date',
            'any_attempt_by_government',
        ]

        for field in required_fields:
            self.fields[field].required = True



from django import forms
from .models import ComplaintResponse

class ComplaintResponseForm(forms.ModelForm):
    class Meta:
        model = ComplaintResponse
        fields = ['officer_name', 'feedback']
        widgets = {
            'officer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Officer Name'
            }),
            'feedback': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'officer_name': 'Officer Name',
            'feedback': 'Response Status'
        }




from django import forms
from .models import Manhole_inspection, UC


class ManholeInspectionForm(forms.ModelForm):

    emp_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    remark = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    inspection_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    image_1 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    image_2 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Manhole_inspection
        fields = '__all__'

        labels = {
            'zone': 'Zone',
        }

        widgets = {
            'zone': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'facility_name': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'manhole_covered': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'any_demage_manhole_covered': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'level_with_road': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
        }

    # ✅ FULL EXCLUDE LIST
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exclude_names = [

            # Zone E
            "COMMERCIAL ZONE-E", "DUMPING SITE-E", "PANDU ROAD-E",
            "WORK SHOP-E", "TRANSFER STATION-E", "MALARIA OFFICE-E",
            "Ring Road Sector I-E", "PARKING YARD-E",
            "Ring Road Sector II-E", "DORA ROAD-E",
            "SHAHI KATHA", "CMU OFFICE-E",

            # Zone D
            "KANAL ROAD", "SPECIAL GANG 2-D", "SPECIAL GANG-D",
            "UNIVERSITY ROAD", "FLEET (WORKSHOP)-D",
            "COMPLAINT CELL-D", "MALARIYA STAFF-D",
            "NIGHT SHIFT-D", "KARKHANU ROAD", "WARSAK ROAD",

            # Zone C
            "BARA ROAD-C", "JAMRUD ROAD 1", "JAMRUD ROAD 2",
            "SPECIAL GANG 1-C", "SPECIAL GANG 2-C",
            "SPECIAL GANG 4-C", "KOHAT ROAD",
            "SPECIAL GANG 3-C", "RING ROAD 1-C",
            "NOTHIA OFFICE-C", "JAMRUD ROAD NIGHT SHIFT",
            "PARKING YARD-C", "DUMPING SITE-C",
            "GULSHAN IQBAL", "MALARIA OFFICE-C",
            "FLEET (WORKSHOP)-C", "UNIVERSITY TOWN-C",
            "SPECIAL GANG 5-C", "KANAL ROAD",
            "RING ROAD 2-C",

            # Zone B
            "WIRELESS ROOM-B", "MALARIA OFFICE-B",
            "PUBLIC REPRESENTATIVE & GOVT OFFICIAL",
            "SPECIAL GANG-B (EMERGENCY)",
            "SPECIAL GANG -2B (UC-11)",
            "DUMPING SITE-B", "NAIB OFFICE",
            "SPECIAL GANG-3B (UC-13)",
            "TRANSFER STATION-B",
            "SPECIAL GANG-6B (UC-17 & 18)",
            "SPECIAL GANG-4B (UC-15 & 19)",
            "CIRCULAR ROAD",
            "SPECIAL GANG-7B (UC-20 &22)",
            "SPECIAL GANG-8B (UC-21 & 30)",
            "COMMERICAL ZONE-B",
            "WATER SUPPLY STORE-B",
            "SPECIAL GANG-5B (UC-14 & 16)",
            "WATER RATE-B",
            "KOHATI COMPLAINT CELL-B",
            "WORK SHOP OFFICE-B",
            "SPECIAL GANG-1B (UC-09 & 12)",
            "SHAHI KATHA",
            "CMU OFFICE-B",
            "PARKING YARD-B",

            # Zone A
            "DUMPING SITE-A", "MALARIA OFFICE-A",
            "COMPLAINT CELL-A", "WATER SUPPLY STORE-A",
            "RING ROAD-A", "TRANSFER STATION-A",
            "PIPELINE TEAM-2", "PIPELINE TEAM-1",
            "CONTROL ROOM-A", "CMU OFFICE-A",
            "COMMERCIAL ZONE-A", "PARKING YARD-A",

            # Offices / Others
            "Not Available",
            "Zone E Office", "Zone D Office",
            "Zone C Office", "Zone B Office",
            "Zone A Office", "Headoffice",
        ]

        self.fields['facility_name'].queryset = UC.objects.exclude(
            uc_name__in=exclude_names
        )




from django import forms
from django.utils import timezone
from .models import VisitEvaluation
from .models import VisitSchedule


from django import forms
from django.utils import timezone
from .models import VisitEvaluation, VisitSchedule


class VisitEvaluationForm(forms.ModelForm):

    class Meta:
        model = VisitEvaluation
        fields = "__all__"

        widgets = {

            # ======================
            # Status
            # ======================
            "status": forms.HiddenInput(),

            # ======================
            # Foreign Key
            # ======================
            "visit_schedule": forms.Select(
                attrs={"class": "form-control"}
            ),

            # ======================
            # Numbers → NumberInput
            # ======================
            "total_containers": forms.NumberInput(attrs={"class": "form-control"}),
            "containers_not_lifted": forms.NumberInput(attrs={"class": "form-control"}),
            "containers_not_managed": forms.NumberInput(attrs={"class": "form-control"}),
            "total_moqas": forms.NumberInput(attrs={"class": "form-control"}),
            "moqas_not_cleaned": forms.NumberInput(attrs={"class": "form-control"}),

            "drains_scheduled": forms.NumberInput(attrs={"class": "form-control"}),
            "drains_clean": forms.NumberInput(attrs={"class": "form-control"}),
            "manholes_scheduled": forms.NumberInput(attrs={"class": "form-control"}),
            "manholes_clean": forms.NumberInput(attrs={"class": "form-control"}),

            "roads_scheduled": forms.NumberInput(attrs={"class": "form-control"}),
            "roads_clean": forms.NumberInput(attrs={"class": "form-control"}),
            "streets_scheduled": forms.NumberInput(attrs={"class": "form-control"}),
            "streets_clean": forms.NumberInput(attrs={"class": "form-control"}),

            "streets_scheduled_d2d": forms.NumberInput(attrs={"class": "form-control"}),
            "houses_scheduled_d2d": forms.NumberInput(attrs={"class": "form-control"}),
            "streets_verified_d2d": forms.NumberInput(attrs={"class": "form-control"}),

            "total_tubewells": forms.NumberInput(attrs={"class": "form-control"}),
            "tubewells_visited": forms.NumberInput(attrs={"class": "form-control"}),
            "tubewells_satisfactory": forms.NumberInput(attrs={"class": "form-control"}),

            "overall_total_score": forms.NumberInput(attrs={"class": "form-control"}),
            "overall_obtained_score": forms.NumberInput(attrs={"class": "form-control"}),

            # ======================
            # Scores
            # ======================
            "containers_total_score": forms.NumberInput(attrs={"class": "form-control"}),
            "containers_obtained_score": forms.NumberInput(attrs={"class": "form-control"}),

            "drains_total_score": forms.NumberInput(attrs={"class": "form-control"}),
            "drains_obtained_score": forms.NumberInput(attrs={"class": "form-control"}),

            "roads_total_score": forms.NumberInput(attrs={"class": "form-control"}),
            "roads_obtained_score": forms.NumberInput(attrs={"class": "form-control"}),

            "d2d_total_score": forms.NumberInput(attrs={"class": "form-control"}),
            "d2d_obtained_score": forms.NumberInput(attrs={"class": "form-control"}),

            "tubewell_total_score": forms.NumberInput(attrs={"class": "form-control"}),
            "tubewell_obtained_score": forms.NumberInput(attrs={"class": "form-control"}),

            # ======================
            # Images
            # ======================
            "containers_picture_1": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "containers_picture_2": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "containers_picture_3": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "containers_picture_4": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "containers_picture_5": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "containers_picture_6": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "containers_picture_7": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "containers_picture_8": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "containers_picture_9": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "containers_picture_10": forms.ClearableFileInput(attrs={"class": "form-control"}),


            "drains_picture_1": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "drains_picture_2": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "drains_picture_3": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "drains_picture_4": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "drains_picture_5": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "drains_picture_6": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "drains_picture_7": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "drains_picture_8": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "drains_picture_9": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "drains_picture_10": forms.ClearableFileInput(attrs={"class": "form-control"}),


            "roads_picture_1": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "roads_picture_2": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "roads_picture_3": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "roads_picture_4": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "roads_picture_5": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "roads_picture_6": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "roads_picture_7": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "roads_picture_8": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "roads_picture_9": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "roads_picture_10": forms.ClearableFileInput(attrs={"class": "form-control"}),


            "d2d_picture_1": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "d2d_picture_2": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "d2d_picture_3": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "d2d_picture_4": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "d2d_picture_5": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "d2d_picture_6": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "d2d_picture_7": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "d2d_picture_8": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "d2d_picture_9": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "d2d_picture_10": forms.ClearableFileInput(attrs={"class": "form-control"}),


            "tubewell_picture_1": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tubewell_picture_2": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tubewell_picture_3": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tubewell_picture_4": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tubewell_picture_5": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tubewell_picture_6": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tubewell_picture_7": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tubewell_picture_8": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tubewell_picture_9": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tubewell_picture_10": forms.ClearableFileInput(attrs={"class": "form-control"}),


            # ======================
            # Text
            # ======================
            "containers_remarks": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "drains_remarks": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "roads_remarks": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "d2d_remarks": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tubewell_remarks": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = timezone.now().date()
        instance = kwargs.get("instance", None)

        # ===============================
        # UPDATE → Hide visit_schedule
        # ===============================
        if instance:
            self.fields.pop("visit_schedule", None)

        else:
            valid_schedules = VisitSchedule.objects.filter(
                visit_date__lte=today
            )

            used_schedules = VisitEvaluation.objects.values_list(
                "visit_schedule_id", flat=True
            )

            self.fields["visit_schedule"].queryset = valid_schedules.exclude(
                id__in=used_schedules
            )

        # ===============================
        # Readonly Score Fields
        # ===============================
        readonly_fields = [
            "containers_total_score",
            "drains_total_score",
            "roads_total_score",
            "d2d_total_score",
            "tubewell_total_score",
            "overall_total_score",
        ]

        for field in readonly_fields:
            if field in self.fields:
                self.fields[field].disabled = True




from .models import Manhole


class ManholeForm(forms.ModelForm):

    class Meta:
        model = Manhole
        fields = [
            'uc',
            'shape',
            'cover_size',
            'cover_material',
            'status',
            'latitude',
            'longitude'
        ]

        widgets = {
            'uc': forms.Select(attrs={'class': 'form-control'}),
            'shape': forms.Select(attrs={'class': 'form-control'}),
            'cover_size': forms.TextInput(attrs={'class': 'form-control'}),            
            'cover_material': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exclude_names = [

            # Zone E
            "COMMERCIAL ZONE-E", "DUMPING SITE-E",
            "WORK SHOP-E", "TRANSFER STATION-E", "MALARIA OFFICE-E",
            "Ring Road Sector I-E", "PARKING YARD-E",
            "Ring Road Sector II-E", "DORA ROAD-E",
            "SHAHI KATHA", "CMU OFFICE-E",

            # Zone D
            "KANAL ROAD", "SPECIAL GANG 2-D", "SPECIAL GANG-D",
            "UNIVERSITY ROAD", "FLEET (WORKSHOP)-D",
            "COMPLAINT CELL-D", "MALARIYA STAFF-D",
            "NIGHT SHIFT-D", "KARKHANU ROAD", "WARSAK ROAD",

            # Zone C
            "JAMRUD ROAD 1", "JAMRUD ROAD 2",
            "SPECIAL GANG 1-C", "SPECIAL GANG 2-C",
            "SPECIAL GANG 4-C", "KOHAT ROAD",
            "SPECIAL GANG 3-C", "RING ROAD 1-C",
            "NOTHIA OFFICE-C", "JAMRUD ROAD NIGHT SHIFT",
            "PARKING YARD-C", "DUMPING SITE-C",
            "GULSHAN IQBAL", "MALARIA OFFICE-C",
            "FLEET (WORKSHOP)-C",
            "SPECIAL GANG 5-C", "KANAL ROAD",
            "RING ROAD 2-C",

            # Zone B
            "WIRELESS ROOM-B", "MALARIA OFFICE-B",
            "PUBLIC REPRESENTATIVE & GOVT OFFICIAL",
            "SPECIAL GANG-B (EMERGENCY)",
            "SPECIAL GANG -2B (UC-11)",
            "DUMPING SITE-B", "NAIB OFFICE",
            "SPECIAL GANG-3B (UC-13)",
            "TRANSFER STATION-B",
            "SPECIAL GANG-6B (UC-17 & 18)",
            "SPECIAL GANG-4B (UC-15 & 19)",
            "CIRCULAR ROAD",
            "SPECIAL GANG-7B (UC-20 &22)",
            "SPECIAL GANG-8B (UC-21 & 30)",
            "COMMERICAL ZONE-B",
            "WATER SUPPLY STORE-B",
            "SPECIAL GANG-5B (UC-14 & 16)",
            "WATER RATE-B",
            "KOHATI COMPLAINT CELL-B",
            "WORK SHOP OFFICE-B",
            "SPECIAL GANG-1B (UC-09 & 12)",
            "SHAHI KATHA",
            "CMU OFFICE-B",
            "PARKING YARD-B",

            # Zone A
            "DUMPING SITE-A", "MALARIA OFFICE-A",
            "COMPLAINT CELL-A", "WATER SUPPLY STORE-A",
            "RING ROAD-A", "TRANSFER STATION-A",
            "PIPELINE TEAM-2", "PIPELINE TEAM-1",
            "CONTROL ROOM-A", "CMU OFFICE-A",
            "COMMERCIAL ZONE-A", "PARKING YARD-A",

            # Offices / Others
            "Not Available",
            "Zone E Office", "Zone D Office",
            "Zone C Office", "Zone B Office",
            "Zone A Office", "Headoffice",
        ]

        self.fields['uc'].queryset = UC.objects.exclude(
            uc_name__in=exclude_names
        )                