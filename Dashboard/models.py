from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
from django.utils.translation import gettext_lazy as _

class Location(models.Model):
    location_name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = '(2.1) Locations'

    def __str__(self):
        return self.location_name


class UC(models.Model):
    uc_name = models.CharField(max_length=50)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  
    coordinates = models.TextField(null=True, blank=True)


    class Meta:
        verbose_name_plural = '(2.2) UCs'

    def __str__(self):
        return self.uc_name


class NC(models.Model):
    nc_name = models.CharField(max_length=50)
    uc_name = models.ForeignKey(UC, on_delete=models.CASCADE)  

    class Meta:
        verbose_name_plural = '(2.3) NCs'

    def __str__(self):
        return self.nc_name


class Street(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    TIME_SLOTS = [
        ('6_7', '6:00 AM - 7:00 AM'),
        ('7_8', '7:00 AM - 8:00 AM'),
        ('8_9', '8:00 AM - 9:00 AM'),
        ('9_10', '9:00 AM - 10:00 AM'),
        ('10_11', '10:00 AM - 11:00 AM'),
        ('11_12', '11:00 AM - 12:00 PM'),
        ('12_1', '12:00 PM - 1:00 PM'),
    ]



    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    uc_name = models.ForeignKey(UC, on_delete=models.CASCADE, null=True, blank=True)
    street_name = models.CharField(max_length=50)
    nc_name = models.ForeignKey(NC, on_delete=models.CASCADE, null=True, blank=True)

    # Coordinates
    start_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    start_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    mid_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    mid_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    end_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Basic stats
    no_of_houses = models.IntegerField(null=True, blank=True)
    no_of_shops = models.IntegerField(null=True, blank=True)
    total_length_km = models.DecimalField(
        max_digits=8,        # enough for large distances
        decimal_places=3,    # up to meters precision (0.001 km = 1 meter)
        null=True,
        blank=True
    )



    sweeping_days = models.CharField(
    max_length=50,
    choices=DAYS_OF_WEEK,
    blank=True,
    null=True,
    help_text='Select the day(s) for sweeping schedule'
    )

    monday_sweeping_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select sweeping time slots for Monday')
    tuesday_sweeping_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select sweeping time slots for Tuesday')
    wednesday_sweeping_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select sweeping time slots for Wednesday')
    thursday_sweeping_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select sweeping time slots for Thursday')
    friday_sweeping_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select sweeping time slots for Friday')
    saturday_sweeping_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select sweeping time slots for Saturday')
    sunday_sweeping_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select sweeping time slots for Sunday')

    solid_waste_days = models.CharField(
        max_length=50,
        choices=DAYS_OF_WEEK,
        blank=True,
        null=True,
        help_text='Select the day(s) for solid waste schedule'
    )

    monday_solid_waste_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select solid waste time slots for Monday')
    tuesday_solid_waste_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select solid waste time slots for Tuesday')
    wednesday_solid_waste_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select solid waste time slots for Wednesday')
    thursday_solid_waste_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select solid waste time slots for Thursday')
    friday_solid_waste_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select solid waste time slots for Friday')
    saturday_solid_waste_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select solid waste time slots for Saturday')
    sunday_solid_waste_time_slots = models.JSONField(default=list, blank=True, null=True, help_text='Select solid waste time slots for Sunday')


    # Sweeping schedule and time
    sweeping_schedule = models.JSONField(default=list, blank=True, null=True, help_text="Select sweeping days")
    sweeping_time_slots = models.JSONField(default=list, blank=True, null=True, help_text="Select sweeping time slots")

    # Solid waste schedule and time
    solid_waste_schedule = models.JSONField(default=list, blank=True, null=True, help_text="Select solid waste collection days")
    solid_waste_time_slots = models.JSONField(default=list, blank=True, null=True, help_text="Select solid waste collection time slots")


    assign_employee = models.ManyToManyField(
    'Employee',
    blank=True,  # allows no employees to be selected
    related_name='assigned_streets',
    help_text="Select one or more employees assigned to this street"
    )

    assign_vehicle = models.ManyToManyField(
        'Vehicle',
        blank=True,  # allows no vehicles to be selected
        related_name='assigned_streets',
        help_text="Select one or more vehicles assigned to this street"
    )


    class Meta:
        verbose_name_plural = "(3.4.6) Street"

    def __str__(self):
        return self.street_name






class DailyStreetCollection(models.Model):
    street = models.ForeignKey(Street, on_delete=models.CASCADE, related_name='collections')
    collection_date = models.DateField(null=False, blank=False) 
    collected_houses = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Number of houses collected today"
    )
    collected_shops = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Number of shops collected today"
    )
    remarks = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = '(3.4.7) Daily Street Collection'
        ordering = ['-collection_date']
        unique_together = ('street', 'collection_date')

    def __str__(self):
        return f"{self.street.street_name} - {self.collection_date}"



class DailyStreetSweeping(models.Model):
    SWEEPING_TYPE_CHOICES = (
        ('manual', 'Manual'),
        ('mechanical', 'Mechanical'),
    )

    street = models.ForeignKey(
        Street,
        on_delete=models.CASCADE,
        related_name='daily_sweeping'
    )
    sweeping_date = models.DateField()

    sweeping_done = models.BooleanField(default=False)

    sweeping_type = models.CharField(
        max_length=20,
        choices=SWEEPING_TYPE_CHOICES,
        null=True,
        blank=True
    )

    sweeping_length_km = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Total sweeping length in kilometers"
    )

    remarks = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = '(3.4.8) Daily Street Sweeping'
        unique_together = ('street', 'sweeping_date')
        ordering = ['-sweeping_date']

    def __str__(self):
        return f"{self.street.street_name} - {self.sweeping_date}"


class Department(models.Model):
    department_name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = '(2.4) Departments'

    def __str__(self):
        return self.department_name



class Designation(models.Model):
    designation_name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = '(2.6) Designations'

    def __str__(self):
        return self.designation_name  



class ComplaintSource(models.Model):
    source_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = '(3.3.1) Complaint Sources'

    def __str__(self):
        return self.source_name



class ComplaintType(models.Model):
    type_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = '(3.3.2) Complaint Types'

    def __str__(self):
        return self.type_name   


class ComplaintSubType(models.Model):
    complaint_type = models.ForeignKey(ComplaintType, on_delete=models.SET_NULL, null=True)
    type_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = '(999) Complaint Types'

    def __str__(self):
        return self.type_name          


class Post(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank and null

    def __str__(self):
        return self.name or "Unnamed Post"  # Handle blank names

    class Meta:
        verbose_name_plural = '(3.2.1) Posts'


class PostDetail(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='details')
    media_channel = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.post.name} - {self.media_channel}"

    class Meta:
        verbose_name_plural = '(3.2.2) Post Details'



class Status(models.Model):
    status = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.status}"

    class Meta:
        verbose_name_plural = '(2.5) Status'  # Correct plural name

def employee_image_path(instance, filename):
    """
    Save images as:
    employee_profiles/{location_name}/{uc_name}/{employee_id}.{ext}
    """
    ext = filename.split('.')[-1]
    filename = f"{instance.employee_id}.{ext}"

    # --- Folder structure ---
    location_name = "UnknownLocation"
    uc_name = "UnknownUC"

    if instance.uc:
        uc_name = instance.uc.uc_name.replace(' ', '_')
        if instance.uc.location:
            location_name = instance.uc.location.location_name.replace(' ', '_')
    elif instance.location:
        location_name = instance.location.location_name.replace(' ', '_')

    return os.path.join('employee_profiles', location_name, uc_name, filename)


class Employee(models.Model):
    employee_id = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank
    father_name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    uc = models.ForeignKey(UC, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    designation = models.CharField(max_length=150, blank=True, null=True)  # Allow blank
    department = models.CharField(max_length=150, blank=True, null=True)  # Allow blank
    cnic = models.CharField(max_length=15, verbose_name='CNIC', null=True, blank=True)  # Optional

    acting_role = models.CharField(max_length=150, blank=True, null=True)  # Allow blank
    status = models.ForeignKey(Status, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    profile_image = models.ImageField(
        upload_to=employee_image_path,
        blank=True,
        null=True,
        verbose_name="Profile Image"
    )

    def __str__(self):
        return f"{self.name} - {self.employee_id} - {self.designation} - {self.acting_role} "

    class Meta:
        verbose_name_plural = '(1.1) Employees List'


class EmployeeAttendance(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)  # Allow blank
    uc = models.ForeignKey(UC, on_delete=models.CASCADE, null=True, blank=True)  # Allow blank
    employee_name = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)  # Allow blank
    attendance_date = models.DateField(null=True, blank=True, default=None)  # Allow blank
    absent = models.BooleanField(null=True, blank=True, default=None)  # Allow blank
    present = models.BooleanField(null=True, blank=True, default=None)  # Allow blank
    leave = models.BooleanField(null=True, blank=True, default=None)  # Allow blank
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance on {self.attendance_date} at {self.location}"

    class Meta:
        verbose_name_plural = '(6.1.1) Employee Attendances'


STATE_CHOICE = [
    ('-----', '-----'), 
    ('Primary', 'Primary'),  
    ('Secondary', 'Secondary'),  
]


STATUS_CHOICE = [
    ('Active', 'Active'),
    ('Transfer', 'Transfer'),
    ('Scrap', 'Scrap'),
]

class Vehicle(models.Model): 
    vehicle_id = models.CharField(max_length=100, db_index=True) 
    vehicle_name = models.CharField(max_length=150)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    vehicle_type = models.CharField(max_length=50, choices=STATE_CHOICE, default='')
    category = models.CharField(max_length=150, null=True, blank=True)

    driver_name = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={'designation': 'Driver'},
        related_name='vehicles'
    )

    # ✅ Added Status Field (Dropdown)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICE,
        null=True,
        blank=True,
        default=None,
        verbose_name="Vehicle Status"
    )
    

    class Meta:
        verbose_name_plural = '(1.2) Vehicles List'

    def __str__(self):
        name = self.vehicle_name or "Unnamed Vehicle"
        vtype = self.vehicle_type or "Unknown Type"
        vid = self.vehicle_id or "No ID"
        return f"{name} - {vtype} ({vid})"


from django.db import models
from .models import Location, Vehicle

class VehicleAttendance(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    vehicle_name = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    attendance_date = models.DateField(null=True, blank=True, default=None)
    
    # Functional and Non-Functional statuses (mutually exclusive)
    functional = models.BooleanField(default=True)  # Assume vehicles are functional by default
    non_functional = models.BooleanField(default=False)  # Non-functional is false by default

    # Options for functional vehicles
    parked = models.BooleanField(null=True, blank=True)
    field_operation = models.BooleanField(null=True, blank=True)
    
    # Options for non-functional vehicles
    minor_repair = models.BooleanField(null=True, blank=True)
    major_repair = models.BooleanField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle_name} - {self.attendance_date}"

    class Meta:
        unique_together = ('vehicle_name', 'attendance_date')
        verbose_name = "Vehicle Attendance"
        verbose_name_plural = "(6.1.2) Vehicle Attendances"



from django.db import models
from django.utils import timezone

class VehiclePE(models.Model):
    # Define choices for vehicle type
    STATE_CHOICE00 = [
        ('-----', '-----'), 
        ('Primary', 'Primary'),  
        ('Secondary', 'Secondary'),  
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    vehicle_name = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=50, choices=STATE_CHOICE00, default='')

    attendance_date = models.DateField(null=True, blank=True, default=None)
    TRIP_CHOICES = [(i, str(i)) for i in range(0, 11)]
    vehicle_trips = models.IntegerField(choices=TRIP_CHOICES, default=0)
    fuel_issued = models.DecimalField(max_digits=10, decimal_places=2)  # Fuel issued in liters
    engine_oil = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,    
        blank=True     
    )

    hydraulic_oil = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    odometer_start = models.PositiveIntegerField(null=True, blank=True)  # Starting odometer value
    odometer_end = models.PositiveIntegerField(null=True, blank=True)  # Ending odometer value
    manual_running_km = models.PositiveIntegerField(null=True, blank=True, help_text="Use this field if odometer is not available")
    running_km = models.PositiveIntegerField(editable=False, default=0)  # Automatically calculated or manually entered

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Handle empty strings for odometer fields and convert to None
        self.odometer_start = self.odometer_start if isinstance(self.odometer_start, int) else None
        self.odometer_end = self.odometer_end if isinstance(self.odometer_end, int) else None
        self.manual_running_km = self.manual_running_km if isinstance(self.manual_running_km, int) else None

        # Calculate running kilometers based on odometer values
        if self.odometer_start is not None and self.odometer_end is not None:
            if self.odometer_end >= self.odometer_start:
                self.running_km = self.odometer_end - self.odometer_start
            else:
                self.running_km = 0  # Optional: handle cases where end < start
        elif self.manual_running_km is not None:
            self.running_km = self.manual_running_km
        else:
            self.running_km = 0  # Default to 0 if neither odometer nor manual km is provided

        super().save(*args, **kwargs)  # 


    def __str__(self):
        return f"{self.vehicle_name} - {self.attendance_date}"

    class Meta:
        verbose_name_plural = "(6.1.4) Vehicle Attendances Performance"





class Tracker(models.Model):
    vehicle_id = models.CharField(max_length=100, db_index=True) 
    vehicle_name = models.CharField(max_length=150)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    vehicle_type = models.CharField(max_length=50, choices=STATE_CHOICE, default='')


    def __str__(self):
        return self.vehicle_name  

    class Meta:
        verbose_name_plural = '(1.3) Tracker List'


class TrackerAttendance(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    vehicle_name = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    attendance_date = models.DateField(null=True, blank=True, default=None)

    functional = models.BooleanField(default=True) 
    non_functional = models.BooleanField(default=False)  
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance on {self.attendance_date} at {self.vehicle_name}"

    class Meta:
        verbose_name_plural = '(6.1.3) Tracker Attendances'



class Vehiclerepair(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    Vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)  # Removed duplicate
    Vehicle_repair_description = models.CharField(max_length=150)
    cost = models.IntegerField(default=0, null=True, blank=True)
    remarks = models.CharField(max_length=150)
    image = models.ImageField(upload_to='repair_Vehicle/', null=True, blank=True) 
    date = models.DateField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '(6.2.1) Vehicle Repair' 

    def __str__(self):
        return f"Vehicle on {self.date} at {self.location} from {self.Vehicle}"  # More informative




class TubeWell(models.Model):
    STATE_CHOICE_T = [
    ('-----', '-----'), 
    ('yes', 'Yes'),  
    ('No', 'No'),  
]
    tubewell_id = models.CharField(max_length=50)
    tubewell_name = models.CharField(max_length=50)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    uc = models.ForeignKey(UC, on_delete=models.CASCADE)
    scada = models.CharField(max_length=50, choices=STATE_CHOICE_T, default='No')
    flow_meter = models.CharField(max_length=50, choices=STATE_CHOICE_T, default='No')
    pesco_id = models.CharField(max_length=255, null=True, blank=True)
    motor_hours_power = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    tubewell_no_connection = models.CharField(max_length=50)
    average_discharge = models.CharField(max_length=50)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
   

    class Meta:
        verbose_name_plural = '(1.4) TubeWells List'

    def __str__(self):
        return f"{self.tubewell_name} (ID: {self.tubewell_id})"



class TubeWelldischarge(models.Model):
    tubewell = models.ForeignKey(TubeWell, on_delete=models.CASCADE)
    updated_average_discharge = models.CharField(max_length=255, null=True, blank=True)
    updated_average_discharge_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Updated Average Discharge'

    def __str__(self):
        return f"{self.tubewell.tubewell_name} - {self.updated_average_discharge_date}"


class TubeWellAttendance(models.Model):
    tubewell = models.ForeignKey(TubeWell, on_delete=models.CASCADE, related_name='attendances') 
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    uc = models.ForeignKey(UC, on_delete=models.CASCADE)
    functional = models.BooleanField(default=True)  
    non_functional = models.BooleanField(default=False)
    non_operational = models.BooleanField(default=False)
    run_hour = models.CharField(max_length=50, default='0')
    electricity_consume = models.CharField(max_length=50, default='0')
    water_produce = models.CharField(max_length=50, default='0')
    remarks = models.CharField(max_length=50)
    meter_reading_start = models.CharField(max_length=50, default='0')
    meter_reading_end = models.CharField(max_length=50, default='0')
    attendance_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '(6.1.5) TubeWell Attendances'

    def __str__(self):
        return f"TubeWell: {self.tubewell.tubewell_name} on {self.attendance_date}"
    


    
class WaterSupply(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True, default=None)
    new_water_supply_connection_registered = models.IntegerField(null=True, blank=True, default=1)
    water_quality_tests_conducted = models.IntegerField(null=True, blank=True)
    functional_filtration_plants = models.IntegerField(null=True, blank=True)  # Added for filtration plants
    non_functional_filtration_plants = models.IntegerField(null=True, blank=True)  # Added for filtration plants
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '(6.2.3) New Water Connection'

    def __str__(self):
        return f"Water Supply on {self.date} at {self.location}" 



STATE_CHOICE5 = [
    ('-----', '-----'), 
    ('safe', 'safe'),  
    ('unsafe', 'unsafe'),  

]

STATE_CHOICE6 = [
    ('-----', '-----'), 
    ('At source', 'At source'),  
    ('Consumer Tap', 'Consumer Tap'),  

]

class Watertest(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    uc = models.ForeignKey(UC, on_delete=models.CASCADE, null=True, blank=True)
    tubewell = models.ForeignKey(TubeWell, on_delete=models.CASCADE, null=True, blank=True)  # Removed duplicate
    location_type = models.CharField(max_length=50, choices=STATE_CHOICE6, default='Consumer Tap')
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ph = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    electrical_conductivity_uc_cm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dissolved_oxygen_mg_l = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tss_mg_l = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    turbidity_ntu = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tds_mg_l = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    resistivity_ojm_cm = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salinity_mg_l = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coliform = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)   
    output = models.CharField(max_length=50, choices=STATE_CHOICE5, default='unsafe')  # Changed to None
    longitude = models.FloatField(null=True, blank=True)  
    latitude = models.FloatField(null=True, blank=True)  
    date = models.DateField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '(6.2.4) Water Quality Tests'  # Consistency in naming

    def __str__(self):
        return f"Water Supply on {self.date} at {self.location} from {self.tubewell}"  # More informative




class Filter(models.Model):
    filter_id = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank

            # New fields
    remarks = models.TextField(blank=True, null=True)  # Optional remarks
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')


    def __str__(self):
        return f"{self.name} - {self.filter_id}"

    class Meta:
        verbose_name_plural = '(1.5) Filter List'


class FilterAttendance(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    filter_name = models.ForeignKey(Filter, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    attendance_date = models.DateField(null=True, blank=True, default=None)  # Allow blank
    functional = models.BooleanField(null=True, blank=True, default=None)  # Allow blank
    non_functional = models.BooleanField(null=True, blank=True, default=None)  # Allow blank
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance on {self.attendance_date} at {self.location}"

    class Meta:
        verbose_name_plural = '(6.1.6) Filter Attendances'



class Tubewellrepair(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    uc = models.ForeignKey(UC, on_delete=models.CASCADE, null=True, blank=True)
    tubewell = models.ForeignKey(TubeWell, on_delete=models.CASCADE, null=True, blank=True)  # Removed duplicate
    tubewell_repair_description = models.CharField(max_length=150)
    cost = models.IntegerField(default=0, null=True, blank=True)
    remarks = models.CharField(max_length=150)
    image = models.ImageField(upload_to='repair_tubewell/', null=True, blank=True) 
    date = models.DateField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '(6.2.2) Tubewell Repair' 

    def __str__(self):
        return f"Tubewell on {self.date} at {self.location} from {self.tubewell}"  # More informative





class official(models.Model):
    employee_id = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank
    father_name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    designation = models.CharField(max_length=50, blank=True, null=True)  # Allow blank
    department = models.CharField(max_length=50, blank=True, null=True)  # Allow blank

    def __str__(self):
        return f"{self.name} - {self.employee_id}"

    class Meta:
        verbose_name_plural = '(3.1.1) Filed Visite Management Staff'



from django.db import models
from django.utils import timezone

class FieldVisitReport(models.Model):
    date = models.DateField(default=timezone.now)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='field_visit_reports')
    name_of_official = models.ForeignKey(official, on_delete=models.CASCADE, blank=True, null=True)
    visit_area = models.CharField(max_length=255)
    brief_report = models.TextField()
    image = models.ImageField(upload_to='field_visits/', null=True, blank=True)  # New image field
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    visited_zone_name = models.ForeignKey(
        Location,
        blank=True,       
        null=True,        
        related_name='visited_reports',
        on_delete=models.SET_NULL  
    )


    def __str__(self):
        return f"Visit by {self.name_of_official} on {self.date} at {self.location}"

    class Meta:
        verbose_name_plural = '(6.2.5) Field Visit Reports'




STATE_CHOICE2 = [
    ('1', '1'), 
]
class PostAttendance(models.Model):
    post_type = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    post_detail = models.ForeignKey(PostDetail, on_delete=models.CASCADE, blank=True, null=True)
    no_of_post = models.CharField(max_length=50, choices=STATE_CHOICE2, default='')
    resource_link = models.URLField(max_length=200, blank=True, null=True)
    post_date = models.DateField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)


    
    def __str__(self):
        # Safely handle NoneType attributes
        post_type_name = self.post_type.name if self.post_type else "Unknown Post Type"
        post_detail_media_channel = self.post_detail.media_channel if self.post_detail else "No Details"
        return f"Attendance on {self.post_date} for {post_type_name} - {post_detail_media_channel}"

    class Meta:
        verbose_name_plural = '(6.1.8) Post Attendances'









class Revenue(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    recovery_day_water_supply = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recovery_day_solid_waste_management = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bill_paid_day_water_supply = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bill_paid_day_solid_waste_management = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_paid_month_water_supply = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_paid_month_solid_waste_management = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bills_paid_month_water_supply = models.PositiveIntegerField(null=True, blank=True)
    bills_paid_month_solid_waste_management = models.PositiveIntegerField(null=True, blank=True)
    recovery_of_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recovery_of_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    disconnection_of_defaulters = models.PositiveIntegerField(null=True, blank=True) 
    billed_amount_total = models.DecimalField(
            max_digits=10, 
            decimal_places=2, 
            default=0
        )   
    number_of_bills_paid = models.PositiveIntegerField(null=True, blank=True)
    date = models.DateField(null=True, blank=True, default=None)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '(6.2.7) Revenue Management'

    def __str__(self):
        return f"Revenue data for {self.location}"







from django.db import models

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ]

    
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    uc = models.ForeignKey(UC, on_delete=models.SET_NULL, null=True)
    complaint_source = models.ForeignKey(ComplaintSource, on_delete=models.SET_NULL, null=True)
    Pcp_compalin_no = models.CharField(max_length=25, verbose_name='PCP Complaint No', null=True, blank=True)  # Optional
    Eak_compalin_no = models.CharField(max_length=25, verbose_name='EAK Complaint No', null=True, blank=True)  # Optional
    Ebaldia_compalin_no = models.CharField(max_length=25, verbose_name='E-Baldia Complaint No', null=True, blank=True)  # Optional

    complaint_type = models.ForeignKey(ComplaintType, on_delete=models.SET_NULL, null=True)
    SubType = models.ForeignKey(ComplaintSubType, on_delete=models.SET_NULL, null=True, blank=True)

    complaint_detail = models.TextField()
    title = models.CharField(max_length=100, verbose_name='Tile Complaint', null=True, blank=True)  # Optional


    type_choices = [
        ('Long Term', 'Long Term'),
        ('Short Term', 'Short Term'),
    ]
    type = models.CharField(max_length=10, choices=type_choices, verbose_name='Type', null=True, blank=True)  # Optional

    date = models.DateField(default=None)  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
  
    first_name = models.CharField(max_length=100, verbose_name='First Name', null=False, blank=True)
    last_name = models.CharField(max_length=100, verbose_name='Last Name', null=False, blank=True)
    bill_number = models.CharField(max_length=100, verbose_name='Bill#', null=True, blank=True)  # Optional
    area = models.CharField(max_length=100, verbose_name='Area', null=False, blank=True)
    address = models.TextField(verbose_name='Address', null=False, blank=True)
    tehsil = models.CharField(max_length=100, verbose_name='Tehsil', null=True, blank=True)  # Optional
    cnic = models.CharField(max_length=15, verbose_name='CNIC', null=True, blank=True)  # Optional
    cell_number = models.CharField(max_length=15, verbose_name='Cell#', null=False, blank=True)

    gender_choices = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = models.CharField(max_length=10, choices=gender_choices, verbose_name='Gender', null=True, blank=True)  # Optional

    consumer_type_choices = [
        ('domestic', 'Domestic'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
    ]
    consumer_type = models.CharField(max_length=20, choices=consumer_type_choices, verbose_name='Consumer Type', null=True, blank=True)  # Optional

    phone_number = models.CharField(max_length=15, verbose_name='Phone#', null=True, blank=True)  # Optional
    before_image = models.ImageField(
        upload_to='complaints/before_images/', 
        null=True, 
        blank=True,
        verbose_name="Before Image"
    )
    class Meta:
        verbose_name_plural = '(6.2.6) Complaints'

    def __str__(self):
        return f"{self.complaint_type} - {self.location} ({self.created_at.strftime('%Y-%m-%d')})"



from django.db import models

class ComplaintResolution(models.Model):
    complaint = models.OneToOneField(
        'Complaint',
        on_delete=models.CASCADE,
        related_name='resolution',
        verbose_name='Complaint'
    )
    description = models.TextField(
        verbose_name='Resolution Description',
        null=True,
        blank=True
    )

    customer_satisfaction_choices = [
    ('yes', 'Yes'),
    ('no', 'No'),
    ('call_no_response', 'Call No Response'),

    ]

    customer_satisfaction = models.CharField(
    max_length=20,
    choices=customer_satisfaction_choices,
    verbose_name='Customer Satisfaction',
    null=True,
    blank=True,
    default=None,  # ✅ Empty by default
)
    after_image = models.ImageField(
        upload_to='complaints/after_images/',
        null=True,
        blank=True,
        verbose_name='After Image'
    )

    class Meta:
        verbose_name_plural = "Complaint Resolutions"

    def __str__(self):
        return f"Resolution for Complaint #{self.complaint.id}"





class ComplaintFeedback(models.Model):
    complaint = models.ForeignKey(
        'Complaint',
        on_delete=models.CASCADE,
        related_name='feedbacks',  # note plural
        verbose_name='Complaint'
    )
    feedback_officer_name = models.CharField(
        max_length=100,
        verbose_name='Feedback Officer Name'
    )
    complaint_feedback = models.TextField(
        verbose_name='Complaint Feedback',
        null=True,
        blank=True
    )
    happy = models.BooleanField(
        choices=[(True, 'Yes'), (False, 'No')],
        verbose_name='Happy'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name_plural = "Complaint Feedbacks"
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback for Complaint #{self.complaint.id} by {self.feedback_officer_name}"


from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class ComplaintActionLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('resolved', 'Resolved'),
    ]
    
    complaint = models.ForeignKey('Complaint', on_delete=models.CASCADE, related_name='actions')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Performed By")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = " 999Complaint Actions"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.complaint} - {self.action} by {self.user}"



@receiver(post_save, sender='Dashboard.Complaint')  
def create_complaint_log(sender, instance, created, **kwargs):
    if created:  
        ComplaintActionLog.objects.create(
            complaint=instance,
            action='created'
        )









class Sanitation(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True, default=None) 
    
    container_lifted = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Container Lifted (Tons)")
    moqas_cleared = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Moqas Cleared (Tons)")
    primary_vehicle_trips = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Primary Vehicle Trips")
    primary_waste_collection_tons = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Primary Waste Collection (Tons)")
    
    waste_locally_dumped_tons = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Waste Locally Dumped (Tons)")
    waste_dumped_at_lfs_tons = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Waste Dumped at LFS (Tons)")
    
    lfs_trips_no = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="LFS Trips (No)")
    local_dumping_trips_no = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Local Dumping Trips (No)")
    
    fuel_top_up_liters = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Fuel Top-Up (Liters)")
    
    door_to_door_solid_waste_collection_no = models.IntegerField(null=True, blank=True, verbose_name="Door-to-Door Collection (No of Houses)")
    
    replacement_of_manhole_covers = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Replacement of Manhole Covers (No)")
    cleaning_de_siltation_of_manholes = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Cleaning/De-Siltation of Manholes (No)")
    cleaning_de_siltation_of_drain_sewars_km = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Cleaning/De-Siltation of Drain Sewers (KM)")
    
    fumigation_sprays_no = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Fumigation Sprays (No)")
    ir_spray_no = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="IR Spray (No)")
    
    rate_killing_no = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Rate Killing (No)")
    dog_catching_no = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Dog Catching (No)")
   
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    class Meta:
        verbose_name_plural = '(6.3.1) Sanitation'

    def __str__(self):
        return f"Sanitation on {self.date} at {self.location}"



class Activity(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True)  # Allow blank and null

    def __str__(self):
        return self.name or "Unnamed Activity"  # Handle blank names

    class Meta:
        verbose_name_plural = '(3.5.1) CLC Activities'


class CLCStaff(models.Model):  
    employee_id = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank
    father_name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    designation = models.CharField(max_length=50, blank=True, null=True)  # Allow blank

    def __str__(self):
        return self.name or "Unnamed Staff"

    class Meta:
        verbose_name_plural = '(3.1.2) CLC Staff'



class CLC(models.Model):
    date = models.DateField(default=timezone.now)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    uc = models.ForeignKey('UC', on_delete=models.CASCADE, blank=True, null=True)
    nc = models.ForeignKey('NC', on_delete=models.CASCADE, blank=True, null=True)
    no_of_participants = models.CharField(max_length=100, blank=True, null=True)  # Allow blank and null
    IEC_material_distribution = models.CharField(max_length=100, blank=True, null=True)  # Allow blank and null


    name_of_official = models.ForeignKey(CLCStaff, on_delete=models.CASCADE, blank=True, null=True)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='clc_images/', null=True, blank=True)
    brief_report = models.TextField()

    def clean(self):
        # Validate the image field
        if self.image:
            # Check the file size
            max_size_kb = 6144  # 6 MB in KB
            if self.image.size > max_size_kb * 1024:
                raise ValidationError(
                    _("Image file size must not exceed %(size)d KB."),
                    params={'size': max_size_kb},
                )
            
            # Check the file format
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(self.image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(
                    _("Unsupported file format. Please upload an image with one of the following extensions: %(exts)s."),
                    params={'exts': ', '.join(valid_extensions)},
                )

    def __str__(self):
        return f"Visit by {self.name_of_official} on {self.date} at {self.location}"

    class Meta:
        verbose_name_plural = '(6.2.8) CLC Reports'


class Typeofpoint(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = ' Types of point'

    def __str__(self):
        return self.name  
    

class Category(models.Model):
    category = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = '(3.4.1) Category'

    def __str__(self):
        return self.category     
    
class Capacity(models.Model):
    capacity = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = '(3.4.2) Capacity'

    def __str__(self):
        return self.capacity      
    
    
class LiftingFrequency(models.Model):
    frequency = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = '(3.4.3) Frequency'

    def __str__(self):
        return self.frequency    
    
class LiftingSchedule(models.Model):
    from_time = models.TimeField(help_text="Select the start time.")
    to_time = models.TimeField(help_text="Select the end time.")



    class Meta:
        verbose_name_plural = '(3.4.4) Lifting Schedule'
    def __str__(self):
        return f" {self.from_time} - {self.to_time}"    

class DayFrequency(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = '(3.4.5) Day Frequency'

    def __str__(self):
        return self.name 



#not workin 

class Container(models.Model):
    TYPE_CHOICES = [
        ('container', 'Container'),
        ('moqa', 'Moqa'),
    ]

    
    container_id = models.CharField(max_length=100, unique=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    uc = models.ForeignKey(UC, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    capacity = models.ForeignKey(Capacity, on_delete=models.CASCADE)
    lifting_schedule = models.ForeignKey(LiftingSchedule, on_delete=models.CASCADE)
    lifting_frequency = models.ForeignKey(LiftingFrequency, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    class Meta:
        verbose_name_plural = ' Container and Moqas'

    def __str__(self):
        return f" - {self.type}"    
    

class ContainerStatus(models.Model):
    LIFTED_STATUS_CHOICES = [
        (True, 'Lifted'),
        (False, 'Unlifted'),
    ]

    container = models.ForeignKey(Container, on_delete=models.CASCADE)  # Links to the existing Container model
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  # Links to Location
    uc = models.ForeignKey(UC, on_delete=models.CASCADE)  # Links to UC
    lifted_status = models.BooleanField(choices=LIFTED_STATUS_CHOICES, default=False)
    status_date = models.DateTimeField(default=timezone.now)  # Optional: To track when the status was updated

    class Meta:
        verbose_name_plural = 'Container Statuses'

    def __str__(self):
        return f"Container: {self.container}, Lifted: {self.get_lifted_status_display()}"

    def get_lifted_status_display(self):
        return "Lifted" if self.lifted_status else "Unlifted"
    

#not workin 






class Bin(models.Model):

    TYPE_CHOICES = [
        ('container', 'Container'),
        ('moqa', 'Moqa'),
    ]
    bin_id = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=100, choices=TYPE_CHOICES)
    name_container = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    
    uc = models.ForeignKey(UC, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    nc = models.ForeignKey(NC, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    street = models.ForeignKey(Street, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    capacity = models.ForeignKey(Capacity, on_delete=models.CASCADE)
    lifting_schedule = models.ForeignKey(LiftingSchedule, on_delete=models.CASCADE, blank=True, null=True)
    lifting_frequency = models.ForeignKey(LiftingFrequency, on_delete=models.CASCADE)
    days = models.ManyToManyField(DayFrequency, blank=True)  # Allow blank
    first_lifting_time = models.TimeField(blank=True, null=True)
    second_lifting_time = models.TimeField(blank=True, null=True)
    third_lifting_time = models.TimeField(blank=True, null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    def __str__(self):
        return f"{self.name} - {self.bin_id}"

    class Meta:
        verbose_name_plural = '(1.6) BIN List'



class BinAttendance(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    uc = models.ForeignKey(UC, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    bin_name = models.ForeignKey(Bin, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    attendance_date = models.DateField(null=True, blank=True, default=None)  # Allow blank
    lifted = models.BooleanField(null=True, blank=True, default=None)  # Allow blank
    unlifted = models.BooleanField(null=True, blank=True, default=None)  # Allow blank
 
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance on {self.attendance_date} at {self.location}"

    class Meta:
        verbose_name_plural = '(6.1.7) Bin Attendances'




class Binfoam(models.Model):
    TYPE_CHOICES1 = [
                ('0', '0'),

        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    uc = models.ForeignKey(UC, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    bin_name = models.ForeignKey(Bin, on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    liftingfrequency = models.CharField(max_length=100, choices=TYPE_CHOICES1)
    firstliftingtime = models.TimeField(blank=True, null=True)
    secondliftingtime = models.TimeField(blank=True, null=True)
    thirdliftingtime = models.TimeField(blank=True, null=True)

    attendance_date = models.DateField(null=True, blank=True, default=None)  # Allow blank
 
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance on {self.attendance_date} at {self.location}"

    class Meta:
        verbose_name_plural = '(6.2.9) Bin lifting Data Store'





class VehiclePerformance(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    vehicle_name = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True, default=timezone.now)
    TRIP_CHOICES = [(i, str(i)) for i in range(1, 11)]
    vehicle_trips = models.IntegerField(choices=TRIP_CHOICES, default=1)
    fuel_issued = models.DecimalField(max_digits=10, decimal_places=2)  # Fuel issued in liters
    odometer_start = models.PositiveIntegerField(null=True, blank=True)  # Starting odometer value, optional
    odometer_end = models.PositiveIntegerField(null=True, blank=True)  
    manual_running_km = models.PositiveIntegerField(null=True, blank=True, help_text="Use this field if odometer is not available")
    running_km = models.PositiveIntegerField(editable=False)  # Automatically calculated or manually entered

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Check if odometer values are provided, and calculate running kilometers
        if self.odometer_start is not None and self.odometer_end is not None and self.odometer_end >= self.odometer_start:
            self.running_km = self.odometer_end - self.odometer_start
        elif self.manual_running_km is not None:
            self.running_km = self.manual_running_km
        else:
            self.running_km = 0  # Default to 0 if neither odometer nor manual km is provided
        super(VehiclePerformance, self).save(*args, **kwargs)

    def __str__(self):
        return f"Performance on {self.date} for {self.vehicle_name}"

    class Meta:
        verbose_name_plural = 'Vehicle Performances'







class locationmap(models.Model):
    
    name = models.CharField(max_length=100) 
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
   
    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = 'locationmap'



from django.urls import reverse
from django.utils.html import format_html

class KMZUpload(models.Model):
    file = models.FileField(upload_to='kmz_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    kml_file = models.FileField(upload_to='kml/', null=True, blank=True)  # ✅ Add this


    def visualization_link(self):
        if self.id:  # Ensure the object is saved before generating the link
            url = reverse('kmz_visualization', args=[self.id])
            return format_html('<a href="{}" target="_blank">View on Map</a>', url)
        return "Save the object to view the link"

    visualization_link.short_description = "Visualization"
    visualization_link.allow_tags = True




class Management_Staff(models.Model):  
    employee_id = models.CharField(max_length=30)
    name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank
    father_name = models.CharField(max_length=100, blank=True, null=True)  # Allow blank
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=True, null=True)  # Allow blank
    designation = models.CharField(max_length=150, blank=True, null=True)  # Allow blank

    def __str__(self):
        return f"{self.name} - {self.father_name} - {self.designation}"

    class Meta:
        verbose_name_plural = '(3.1.3) Management Staff'



class perfoma_tube(models.Model):
    name_of_official = models.ForeignKey(Management_Staff, on_delete=models.CASCADE, blank=True, null=True)

    tube_well_id = models.CharField(max_length=50, unique=True, verbose_name="Tube Well ID", blank=True, null=True)
    tube_well_functional = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Tube Well is Functional", blank=True, null=True)
    operator_present = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Tube Well Operator Present", blank=True, null=True)
    supervisor_present = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Tube Well Supervisor Present and Attendance Maintained", blank=True, null=True)
    bookkeeping_updated = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Bookkeeping/Log Records Updated", blank=True, null=True)
    filtration_plant_functional = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Filtration Plant Functional", blank=True, null=True)
    scada_system_functional = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="SCADA System Installed & Functional", blank=True, null=True)
    water_quality_device_functional = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Water Quality Device Installed & Functional", blank=True, null=True)
    operator_in_uniform = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Tube Well Operator in Duty Uniform", blank=True, null=True)
    mechanical_fault = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Mechanical & Electrification Fault in Tube Well", blank=True, null=True)
    pipe_leakage = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Pipe Leak at Tube Well or Network", blank=True, null=True)
    maintenance_record_maintained = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Maintenance Record Maintained", blank=True, null=True)
    registered_connection = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Registered Connection on Tube Well", blank=True, null=True)
    illegal_connection = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Illegal Connection from Tube Well", blank=True, null=True)
    complaints_redressal = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Complaints/Redressal", blank=True, null=True)
    
    location = models.CharField(max_length=100, verbose_name="Location of Containers/Bins/Moqa", blank=True, null=True)
    bins_clean = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Containers/Bins/Moqa are Clean and in Good Condition", blank=True, null=True)
    surroundings_clean = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Surroundings of Containers/Bins are Clean", blank=True, null=True)
    spillage_observed = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Spillage or Overflow Observed (Document Time of Occurrence)", blank=True, null=True)
    waste_lifted_timely = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Waste Lifted in a Timely Manner", blank=True, null=True)
    staff_uniform = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Staff in Duty Uniform", blank=True, null=True)
    street_littering = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Street Littering", blank=True, null=True)
    area_sweeping = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Sweeping in the Area", blank=True, null=True)
    swm_consumer_billed = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="SWM Consumer Billed", blank=True, null=True)
    vehicle_condition = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="SWM Collection Vehicle Condition", blank=True, null=True)
    vehicle_trip_record = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Vehicle Trip Record Maintained", blank=True, null=True)
    pending_complaints = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="SWM Pending Complaint", blank=True, null=True)
    staff_attendance = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Staff Attendance", blank=True, null=True)

    drain_location = models.CharField(max_length=100, verbose_name="Drain Location (Specific to Urban Areas Prone to Blockages)", blank=True, null=True)
    drain_desiltation = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Drain Desiltation", blank=True, null=True)
    manhole_covers = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Manholes Have Proper Covers (Report Missing/Damaged Covers)", blank=True, null=True)
    sludge_lifting_timely = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Timely Lifting of Sludge", blank=True, null=True)
    manhole_desiltation = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Desiltation of Manholes", blank=True, null=True)
    dewats_status = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="DEWATS Status", blank=True, null=True)
    staff_attendance = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Staff Attendance", blank=True, null=True)

    Staff_present_specify_numbers_for_absentees= models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Staff present", blank=True, null=True)
    Staff_wearing_proper_uniform_and_safety_equipment = models.CharField(max_length=3, choices=[("Yes", "Yes"), ("No", "No")], verbose_name="Staff wearing proper uniform", blank=True, null=True)




    Total_vehicle_in_the_yard = models.CharField(max_length=50, unique=True, verbose_name="Total vehicle", blank=True, null=True)
    Layout_of_vehicles = models.CharField(max_length=50, unique=True, verbose_name="Layout of vehicles", blank=True, null=True)
    Layout_and_safety_of_store = models.CharField(max_length=50, unique=True, verbose_name="Total vehicle", blank=True, null=True)
    vehicle_condition = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Vehicle Condition (Neat & Clean)", blank=True, null=True
    )
    firefighting_equipment = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Firefighting Equipment", blank=True, null=True
    )
    presence_of_security_guard = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Presence of Security Guard and Other Staff", blank=True, null=True
    )
    functionality_bio_attendance = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Functionality of Bio Time Attendance Devices", blank=True, null=True
    )
    cctv_cameras = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="CCTV Cameras", blank=True, null=True
    )
    availability_oil_spare_parts = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Availability of Oil and Replaced Spare Parts", blank=True, null=True
    )
    fuel_register_records = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Fuel Register, Used Oil, Log Books, and Other Records", blank=True, null=True
    )
    general_cleanliness = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="General Cleanliness of Vehicles", blank=True, null=True
    )
    odometer_temp_fuel_gauge = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Odometer, Temp Gauge, and Fuel Gauge of Vehicles", blank=True, null=True
    )
    sheet_provided = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Sheet Provided for Vehicle Covering Solid Waste in Vehicle", blank=True, null=True
    )
    parking_sheds = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Parking Sheds", blank=True, null=True
    )
    basic_maintenance_tools = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Basic Maintenance Tools (Tyre Inflation Pump, Puncture Machine, etc.)", blank=True, null=True
    )
    washing_pit = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Washing Pit", blank=True, null=True
    )



    waste_in_out_record = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Waste In-Out Record Maintained", blank=True, null=True
    )
    vehicles_in_out_record = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Vehicles In-Out Record", blank=True, null=True
    )
    scavengers_activity = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Scavengers Activity", blank=True, null=True
    )
    backlog = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Backlog", blank=True, null=True
    )
    maintenance_route = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Maintenance Route", blank=True, null=True
    )
    fumigation_spray_arrangements = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Fumigation & Spray Arrangements", blank=True, null=True
    )
    boundary_wall_control = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Boundary Wall for Control", blank=True, null=True
    )
    leachate_collection = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Leachate Collection", blank=True, null=True
    )
    buffer_zone_plantation = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Buffer Zone Plantation", blank=True, null=True
    )
    staff_attendance_2 = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Staff Attendance", blank=True, null=True
    )
    loading_arrangements = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Loading Arrangements", blank=True, null=True
    )
    staff_working_station = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Staff Working Station", blank=True, null=True
    )



    fuel_sops_followed = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Fuel SOPs Followed (Check for Any Anomalies)", blank=True, null=True
    )
    fuel_card_swiped = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Fuel Card Swiped at Refueling", blank=True, null=True
    )
    driver_signature_fuel_register = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Driver Signature in Fuel Register", blank=True, null=True
    )
    fuel_liters_recorded = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Fuel Liters Recorded in Vehicle Trip Sheet", blank=True, null=True
    )
    staff_on_duty_attendance = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Staff on Duty Attendance", blank=True, null=True
    )


    random_check_households_bills = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Random Check, Households Received Their Bills", blank=True, null=True
    )
    random_check_shops_bills = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Random Check, Shops and Commercial Units Received Bills", blank=True, null=True
    )
    uc_area_work_quality = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Overall UC/Area Work Quality is Satisfactory", blank=True, null=True
    )
    field_staff_duty_hours = models.CharField(
        max_length=3,
        choices=[("Yes", "Yes"), ("No", "No")],
        verbose_name="Field Staff Following Duty Hours", blank=True, null=True
    )
    suggestions_recommendations = models.TextField(
        blank=True,
        null=True,
        verbose_name="Suggestions or Recommendations (if any)"
    )

    date = models.DateField(null=True, blank=True, default=None) 

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)












class Street_cleaning(models.Model):
     
    loction = models.ForeignKey(Location, on_delete=models.CASCADE) 
    uc_name = models.ForeignKey(UC, on_delete=models.CASCADE) 
    nc_name = models.ForeignKey(NC, on_delete=models.CASCADE)  
    street_name = models.ForeignKey(Street, on_delete=models.CASCADE)
    day_frequency = models.ManyToManyField(DayFrequency, blank=True)
    
    Cleaning_frequency = models.ForeignKey(LiftingFrequency, on_delete=models.CASCADE)
    employee_assign_for_cleaning = models.ManyToManyField(Employee, blank=True)  # Allow blank
    bin_assign = models.ManyToManyField(Bin, blank=True)
    vehicle_assign_for_cleaning = models.ManyToManyField(Vehicle, blank=True)  # Allow blank



    class Meta:
        verbose_name_plural = 'Street Cleaning'

    def __str__(self):
        return str(self.street_name)  







from django.contrib.auth.models import User
from django.db import models


class UserActivityLog(models.Model):
    ACTION_CHOICES = [
        ('ADD', 'Add'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_logs")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=255)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} on {self.model_name}"

    class Meta:
        verbose_name = "User Activity Log"
        verbose_name_plural = "(5.1.1) User Activity Logs"




from django.db import models
from django.contrib.auth.models import User

class Log(models.Model):  # Changed model name from UserActivityLog to Log
    ACTION_CHOICES = [
        ('ADD', 'Add'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('ACCESS', 'Access'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    action_category = models.CharField(max_length=50, choices=ACTION_CHOICES, default='ACCESS')
    method = models.CharField(max_length=10)  # e.g., GET, POST
    path = models.CharField(max_length=500)  # URL path
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "All Activity Log"
        verbose_name_plural = "(5.1.2) All Activity Logs"

        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.user} performed {self.action} via {self.method}"



class ViewName(models.Model):
    VIEW_NAME_CHOICES = [
        ('attendance_summary', 'attendance_summary'),
        ('vehicle_attendance_summary', 'vehicle_attendance_summary'),
        ('tubewell_attendance_summary', 'tubewell_attendance_summary'),
        ('field_visit_summary', 'field_visit_summary'),
        ('sanitation_summary_view', 'sanitation_summary_view'),
        ('clc_summary', 'clc_summary'),
        ('complaint_summary_view', 'complaint_summary_view'),
        ('media_summary', 'media_summary'),
        ('revenue_summary_view', 'revenue_summary_view'),
        ('bin_summary_view', 'bin_summary_view'),
        ('----', '----'),
        ('attendance_report', 'attendance_report'),
        ('vehicle_attendance_report', 'vehicle_attendance_report'),
        ('daily_sanitation_report', 'daily_sanitation_report'),
        ('tubewell_attendance', 'tubewell_attendance'),
        ('daily_post_attendance', 'daily_post_attendance'),
        ('complaint_management_report', 'complaint_management_report'),
        ('revenue_management_report', 'revenue_management_report'),
        ('field_visit_report', 'field_visit_report'),
        ('clc_report', 'clc_report'),
        ('water_supply_report', 'water_supply_report'),
        ('bin_attendance_report', 'bin_attendance_report'),
        ('filter_attendance_report', 'filter_attendance_report'),
        ('vehicle_pe_attendance', 'vehicle_pe_attendance'),
        ('tracker_attendance_report', 'tracker_attendance_report'),
        ('water_quality_report', 'water_quality_report'),
        ('----', '----'),
        ('attendance_report_generator', 'attendance_report_generator'),
        ('report_vehicle','report_vehicle'),
        ('attendance_summary_pdf', 'attendance_summary_pdf'),
         ('tubewell_repair_view', 'tubewell_repair_view'),
         ('vehicle_repair_view', 'vehicle_repair_view'),
         ('tubewell_attendance_report', 'tubewell_attendance_report'),
         ('attendance_summary_excel', 'attendance_summary_excel'),
         ('generate_clc_report', 'generate_clc_report'),
         ('complaint_report_generator', 'complaint_report_generator'),
         ('revenue_report_generator', 'revenue_report_generator'),
         ('binfoam_view', 'binfoam_view'),
         ('generate_field_visit_report', 'generate_field_visit_report'),

         ('bin_list_view', 'bin_list_view'),
        ('total_attendance_report', 'total_attendance_report'),
        ('report_tubwell_2', 'report_tubwell_2'),
        ('report_post_attendance', 'report_post_attendance'),
        ('sanitation_data', 'sanitation_data'),

         ('department_attendance_report', 'department_attendance_report'),
         ('daily_fuel_report', 'daily_fuel_report'),
         ('bin_report_view', 'bin_report_view'),
         ('document_list', 'document_list'),
         ('vehicle_pe_monthly_report', 'vehicle_pe_monthly_report'),
         ('add_water_produce', 'add_water_produce'),
         ('add_electricity_usage', 'add_electricity_usage'),
         ('tubewell_monthly_summary', 'tubewell_monthly_summary'),
         ('adp_list', 'adp_list'),
        ('hotspot_list', 'hotspot_list'),
         ('hotspot_event_view', 'hotspot_event_view'),
         ('hotspot_history', 'hotspot_history'),
         ('flood_report', 'flood_report'),
         ('complaint_management_view', 'complaint_management_view'),
         ('ComplaintFeedbackCreateView', 'ComplaintFeedbackCreateView'),
         ('ComplaintFeedbackListView', 'ComplaintFeedbackListView'),
         ('adp_scheme_list', 'adp_scheme_list'),
         ('adp_scheme_detail', 'adp_scheme_detail'),
        ('daily_collection_entry', 'daily_collection_entry'),
        ('accumulative_street_report', 'accumulative_street_report'),
        ('street_collection_dashboard', 'street_collection_dashboard'),
        ('street_detail_view', 'street_detail_view'),
          ('water_quality_dashboard', 'water_quality_dashboard'),
        ('water_test_report', 'water_test_report'),


        ('ponding_points_report', 'ponding_points_report'),
        ('storm_drain_report', 'storm_drain_report'),
        ('trunk_sewer_report', 'trunk_sewer_report'),
        ('major_road_report', 'major_road_report'),
        ('ponding_points_delete', 'ponding_points_delete'),
        ('ponding_points_update', 'ponding_points_update'),
        ('ponding_points_create', 'ponding_points_create'),
        ('ponding_points_list', 'ponding_points_list'),
        ('storm_drain_delete', 'storm_drain_delete'),
        ('storm_drain_update', 'storm_drain_update'),
        ('storm_drain_create', 'storm_drain_create'),
        ('storm_drain_list', 'storm_drain_list'),

        ('trunk_sewer_delete', 'trunk_sewer_delete'),
        ('trunk_sewer_update', 'trunk_sewer_update'),
        ('trunk_sewer_create', 'trunk_sewer_create'),
        ('trunk_sewer_list', 'trunk_sewer_list'),
        ('major_road_delete', 'major_road_delete'),
        ('major_road_update', 'major_road_update'),
        ('major_road_create', 'major_road_create'),
        ('major_road_list', 'major_road_list')
                  







    ]
    
    name = models.CharField(max_length=100, choices=VIEW_NAME_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()
    

    class Meta:
        verbose_name_plural = '(4.1.1) ViewName'


class UserViewPermission(models.Model):
    user = models.ManyToManyField(User)
    view_name = models.ManyToManyField(ViewName)  
    can_view = models.BooleanField(default=False)

    def __str__(self):
        # Get all usernames
        user_names = ", ".join(user.username for user in self.user.all())
        view_names = ", ".join(view.name for view in self.view_name.all())
        return f"{user_names} - {view_names} - {'Can View' if self.can_view else 'Cannot View'}"

    class Meta:
        verbose_name_plural = '(4.1.2) UserViewPermission'



class LocationPermission(models.Model):
    user = models.ManyToManyField(User)
    locations = models.ManyToManyField(Location)
    can_view = models.BooleanField(default=False)

    def __str__(self):
        user_names = ", ".join(user.username for user in self.user.all())
        return f"{user_names} Permissions for Locations"

    class Meta:
        verbose_name = 'Location Permission'
        verbose_name_plural = '(4.1.3) Location Permissions'



class UcPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Uc = models.ManyToManyField(UC)
    can_view = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'UC Permission'
        verbose_name_plural = '(4.1.4) UC Permissions'



class DepartmentPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Department = models.ManyToManyField(Department)
    can_view = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'Department Permission'
        verbose_name_plural = '(4.1.5) Department Permissions'


        


class officialFPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Official = models.ManyToManyField(official)
    can_view = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'Field Visit Permission'
        verbose_name_plural = '(4.1.6) Field Visit Permissions'        




class officialCPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Official = models.ManyToManyField(CLCStaff)
    can_view = models.BooleanField(default=False)


    class Meta:
        verbose_name = 'Field Visit Permission'
        verbose_name_plural = '(4.1.7) CLC Visit Permissions'   


from django.db import models

class Document(models.Model):
    # File name (string field)
    file_name = models.CharField(max_length=255)
    
    # Uploaded file (file field)
    uploaded_file = models.FileField(upload_to='uploads/')

    # Optionally, you can define a method to get the file extension
    def file_extension(self):
        return self.uploaded_file.name.split('.')[-1].lower()

    # String representation of the model
    def __str__(self):
        return self.file_name



class ADP(models.Model):
    # File name (string field)
    file_name = models.CharField(max_length=255)
    
    # Uploaded file (file field)
    uploaded_file = models.FileField(upload_to='uploads/')

    # Optionally, you can define a method to get the file extension
    def file_extension(self):
        return self.uploaded_file.name.split('.')[-1].lower()

    # String representation of the model
    def __str__(self):
        return self.file_name



from django.db import models
from django.utils import timezone

class Fuel(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(null=True, blank=True)  # No need for default=None

    lfs_trips_no = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="LFS Trips (No)"
    )

    fuel_top_up_liters = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Fuel Top-Up (Liters)"
    )

    primary_trips = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True, verbose_name="Primary Trips (No)"
    )

    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    class Meta:
        verbose_name_plural = '(6.3.2) Fuel/Trips'

    def __str__(self):
        return f"Fuel Record on {self.date} at {self.location if self.location else 'Unknown Location'}"


class TubeWellwaterdepth(models.Model):
    tubewell = models.ForeignKey(TubeWell, on_delete=models.CASCADE) 
    water_table_depth = models.CharField(null=True, blank=True)  
    water_table_measurment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Water Depth'

    def _str_(self):
        return f"TubeWell: {self.tubewell.tubewell_name} on {self.water_table_measurment_date}"


class TubeWellWaterProduce(models.Model):
    tubewell = models.ForeignKey(TubeWell, on_delete=models.CASCADE, related_name='waterproduce') 
    run_hour = models.CharField(max_length=50, default='0')
    water_produce = models.CharField(max_length=50, default='0')
    remarks = models.CharField(max_length=50, blank=True, null=True)

    water_meter_reading_start = models.CharField(max_length=50, default='0')
    water_meter_reading_end = models.CharField(max_length=50, default='0')
    water_produce_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'TubeWell water produce'

    def __str__(self):
        return f"TubeWell: {self.tubewell.tubewell_name} on {self.water_produce_date}"
    

from django.db import models
from django.utils import timezone

class TubeWellElectricityUsage(models.Model):
    tubewell = models.ForeignKey('TubeWell', on_delete=models.CASCADE, related_name='electricity_usage')

    meter_reading_start = models.DecimalField(max_digits=10, decimal_places=2)
    meter_reading_end = models.DecimalField(max_digits=10, decimal_places=2)
    electricity_consumed = models.DecimalField(max_digits=10, decimal_places=2)

    remarks = models.CharField(max_length=255, blank=True, null=True)
    usage_date = models.DateField(default=timezone.now)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'TubeWell electricity usage'


    def __str__(self):
        return f"Electricity Usage: {self.tubewell.tubewell_name} on {self.usage_date}"


from django.db import models
from django.utils import timezone


class Hotspot(models.Model):
    name = models.CharField(max_length=50)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    uc = models.ForeignKey(UC, on_delete=models.SET_NULL, null=True)
    supervisor_name = models.CharField(max_length=50)
    supervisor_phone_number = models.CharField(
        max_length=15,
        verbose_name='Phone#',
        null=True,
        blank=True
    )  # Optional

    officer_name = models.CharField(max_length=50)
    officer_phone_number = models.CharField(
        max_length=15,
        verbose_name='Phone#',
        null=True,
        blank=True
    )  # Optional

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '7.1 WSSP Urban Flooding HotSpots'

    def __str__(self):
        return f"{self.name}"




class HotspotEvent(models.Model):
    RAINFALL_INTENSITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    hotspot = models.ForeignKey(
        'Hotspot',
        on_delete=models.CASCADE,
        related_name='events'
    )
    rain_start_time = models.TimeField(null=True, blank=True)
    rain_end_time = models.TimeField(null=True, blank=True)
    urban_start_time = models.TimeField(null=True, blank=True)
    urban_end_time = models.TimeField(null=True, blank=True)

    rainfall_intensity = models.CharField(
        max_length=10,
        choices=RAINFALL_INTENSITY_CHOICES,
        default='low'
    )
    remarks = models.TextField(null=True, blank=True)

    before_image = models.ImageField(
        upload_to='hotspot_events/before/',
        null=True,
        blank=True
    )
    after_image = models.ImageField(
        upload_to='hotspot_events/after/',
        null=True,
        blank=True
    )

    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = '7.2 Hotspot Events'

    def __str__(self):
        return f"Event at {self.hotspot.name} ({self.created_at.date()})"


from django.db import models


class AdpScheme(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    name = models.CharField(max_length=255, verbose_name="Name")
    aa_cost = models.CharField(max_length=255, verbose_name="AA Cost / Administrative Approval")
    release = models.CharField(max_length=255, verbose_name="Release Amount")
    exp = models.CharField(max_length=255, verbose_name="Expenditure")
    start_date = models.DateField(null=True, blank=True, verbose_name="Start Date")
    end_date = models.DateField(null=True, blank=True, verbose_name="End Date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ADP Scheme"
        verbose_name_plural = "ADP Schemes"
        ordering = ("-start_date", "code")

    def __str__(self):
        return f"{self.code} — {self.name}"


class FinancialProgress(models.Model):
    scheme = models.ForeignKey(
        AdpScheme,
        on_delete=models.CASCADE,
        related_name='financial_progress'
    )
    progress = models.CharField(max_length=255, verbose_name="Financial Progress")
    date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Financial Progress"
        verbose_name_plural = "Financial Progress Records"

    def __str__(self):
        return f"{self.scheme} — Financial Progress"


class PhysicalProgress(models.Model):
    scheme = models.ForeignKey(
        AdpScheme,
        on_delete=models.CASCADE,
        related_name='physical_progress'
    )
    progress = models.CharField(max_length=255, verbose_name="Physical Progress")
    date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Physical Progress"
        verbose_name_plural = "Physical Progress Records"

    def __str__(self):
        return f"{self.scheme} — Physical Progress"



class Schemestatus(models.Model):
    scheme = models.ForeignKey(
        AdpScheme,
        on_delete=models.CASCADE,
        related_name='scheme_status'
    )
    status = models.CharField(max_length=255, verbose_name="Scheme Status")
    date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Scheme Status"

    def __str__(self):
        return f"{self.scheme} — Scheme Status"




from datetime import date


# OLD Extra Data
class MajorRoad(models.Model):
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    FACILITY_CHOICES = [
    ('Circular Road (Bhana Marai Chowk Hashtnagri)', 'Circular Road (Bhana Marai Chowk Hashtnagri)'),
    ('GT Road', 'GT Road'),
    ('Depo Road (Near Dalazak Road)', 'Depo Road (Near Dalazak Road)'),
    ('GT Road – Faqir Abad Thana', 'GT Road – Faqir Abad Thana'),
    ('Gunj Gate Phandu Road – Jameel Chowk', 'Gunj Gate Phandu Road – Jameel Chowk'),
    ('Gulbahar BRT Station 07 – Outer Circular Road', 'Gulbahar BRT Station 07 – Outer Circular Road'),
    ('Anam Sanam Chowk Ring Road (Via Ishrat Cinema Road)', 'Anam Sanam Chowk Ring Road (Via Ishrat Cinema Road)'),
    ('Dilazak Road (Bacha Khan Chowk – Ring Road)', 'Dilazak Road (Bacha Khan Chowk – Ring Road)'),
    ('Main Charsadda Road (Shah Alam Pul Naguman Chowk)', 'Main Charsadda Road (Shah Alam Pul Naguman Chowk)'),
    ('Bara Road (Mall Road – Pishtakhara)', 'Bara Road (Mall Road – Pishtakhara)'),
    ('Jamrud Road', 'Jamrud Road'),
    ('Abdara Road (Opp. Jawad Tower)', 'Abdara Road (Opp. Jawad Tower)'),
    ('Old Bara Road (Mehbob Masjid – Airport Boundary)', 'Old Bara Road (Mehbob Masjid – Airport Boundary)'),
    ('Zoo / Palosi Road (Opp. Speen Jumat)', 'Zoo / Palosi Road (Opp. Speen Jumat)'),
    ('University Road (Near Rular Academy Town)', 'University Road (Near Rular Academy Town)'),
    ('Circular Road (Near Town III Office)', 'Circular Road (Near Town III Office)'),
    ('Inqilab Road (Kohat Road Qamar Din Garhi)', 'Inqilab Road (Kohat Road Qamar Din Garhi)'),
    ('(Ring Road) C', '(Ring Road) C'),
    ('(Ring Road) E', '(Ring Road) E'),


]


    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='major_roads')
    facility_name = models.CharField(
        max_length=100,
        choices=FACILITY_CHOICES,
        default='Circular Road (Bhana Marai Chowk Hashtnagri)',
    )



    free_from_garbage_rubble = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    dry_and_clean = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')

    remark = models.TextField(null=True, blank=True)
    emp_name = models.CharField(max_length=100, null=True, blank=True)

    inspection_date = models.DateField(default=date.today)

    # ✅ Image upload fields (optional)
    image_1 = models.ImageField(
        upload_to='major_roads_inspections/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='major_roads_inspections/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "DSD.1 Major Roads"

    def __str__(self):
        return f"{self.facility_name} ({self.location})"


from django.db import models
from datetime import date

class TrunkSewerInspection(models.Model):
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    FACILITY_CHOICES = [
        ('Shahi Katta Drain', 'Shahi Katta Drain'),
        ('NullahMuhammad Zai', 'NullahMuhammad Zai'),
        ('Airport TehkalPayan Drain', 'Airport TehkalPayan Drain'),
    ]

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='trunk_sewer_inspections'
    )

    facility_name = models.CharField(
        max_length=100,
        choices=FACILITY_CHOICES,
        default='Shahi Katta Drain',
    )

    manhole_covered = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    manhole_free_from_damage = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    no_sediment_around_manhole = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    no_outflow_of_sewage_from_manhole = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    no_bad_odour_around_manhole = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    no_blockage_at_outflow_of_drain = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    fastflow_of_water_at_outflow_of_drain = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')

    # ✅ Image upload fields (optional)
    image_1 = models.ImageField(
        upload_to='trunk_sewer_inspections/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='trunk_sewer_inspections/',
        null=True,
        blank=True
    )

    remark = models.TextField(null=True, blank=True)
    emp_name = models.CharField(max_length=100, null=True, blank=True)

    inspection_date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "DSD.2 Trunk Sewer Inspections"

    def __str__(self):
        return f"{self.facility_name} ({self.location})"


class StormDrainInspection(models.Model):
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]


    FACILITY_CHOICES = [
        ('GT Road Drain (GT Road, City)', 'GT Road Drain (GT Road, City)'),
        ('Kohat Road Drain (Near Govt. Technical College, Kohat Road)', 'Kohat Road Drain (Near Govt. Technical College, Kohat Road)'),
            ('University Road TehkalBalaDrain (University Road, TehkalBala)', 'University Road TehkalBalaDrain (University Road, TehkalBala)'),

    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='storm_drain_inspections')
    facility_name = models.CharField(
        max_length=100,
        choices=FACILITY_CHOICES,
        default='GT Road Drain (GT Road, City)',
    )

    entry_clear = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    exit_clear = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')

    remark = models.TextField(null=True, blank=True)
    emp_name = models.CharField(max_length=100, null=True, blank=True)

    inspection_date = models.DateField(default=date.today)

    # ✅ Image upload fields (optional)
    image_1 = models.ImageField(
        upload_to='strom_drain_inspections/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='strom_drain_inspections/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "DSD.3 Storm Drain Inspections"

    def __str__(self):
        return f"{self.facility_name} ({self.location})"


class PondingPointsInspection(models.Model):
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

    FACILITY_CHOICES = [
    ('WSSP (Kabootar Chowk)', 'WSSP (Kabootar Chowk)'),
    ('WSSP (Children Hospital)', 'WSSP (Children Hospital)'),
    ('WSSP (Hashtnagri Chowk A)', 'WSSP (Hashtnagri Chowk A)'),
    ('WSSP (Hashtnagri Chowk B)', 'WSSP (Hashtnagri Chowk B)'),

    ('WSSP (Charsadda Road)', 'WSSP (Charsadda Road)'),
    ('WSSP (Bacha Khan Chowk)', 'WSSP (Bacha Khan Chowk)'),
    ('WSSP (Gulbahar Police Station)', 'WSSP (Gulbahar Police Station)'),
    ('WSSP (Kohati Gate)', 'WSSP (Kohati Gate)'),
    ('WSSP (Jamil Chowk)', 'WSSP (Jamil Chowk)'),
    ('WSSP (Ring Road Park)', 'WSSP (Ring Road Park)'),
    ('WSSP (Nothia Bazar)', 'WSSP (Nothia Bazar)'),
    ('WSSP (Usmania Restaurant, University Road)', 'WSSP (Usmania Restaurant, University Road)'),
    ('WSSP (Maqbool Ice Cream, University Road)', 'WSSP (Maqbool Ice Cream, University Road)'),
    ('WSSP (PCS Laboratory Road, University Road)', 'WSSP (PCS Laboratory Road, University Road)'),
    ('WSSP (Hotel Grand, University Road)', 'WSSP (Hotel Grand, University Road)'),
    ('WSSP (FATA Secretariat)', 'WSSP (FATA Secretariat)'),
    ('WSSP (Chungi Chowk)', 'WSSP (Chungi Chowk)'),
]


    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='ponding_points_inspections')
    facility_name = models.CharField(
        max_length=100,
        choices=FACILITY_CHOICES,
        default='WSSP (Kabootar Chowk)',
    )

    any_attempt_by_government = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')

    remark = models.TextField(null=True, blank=True)
    emp_name = models.CharField(max_length=100, null=True, blank=True)

    inspection_date = models.DateField(default=date.today)

    # ✅ Image upload fields (optional)
    image_1 = models.ImageField(
        upload_to='ponding_point_inspections/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='pomding_point_inspections/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "DSD.4 Ponding Points Inspections"

    def __str__(self):
        return f"{self.facility_name} ({self.location})"


# OLD Extra Data








# New DSD Code


class MajorRoad_Add(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    road = models.CharField(max_length=150)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = 'DSD MajorRoad_Add'

    def __str__(self):
        return self.road


class TrunkSewer_Add(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    trunksewer = models.CharField(max_length=150)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = 'DSD TrunkSewer_Add'

    def __str__(self):
        return self.trunksewer


class StormDrain_Add(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    stormdrain = models.CharField(max_length=150)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)  
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = 'DSD StormDrain_Add'

    def __str__(self):
        return self.stormdrain        


class PondingPoints_Add(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    pondingpoints = models.CharField(max_length=150)
    location = models.ForeignKey(Location, on_delete=models.CASCADE) 
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        null=True,
        blank=True
    ) 

    class Meta:
        verbose_name_plural = 'DSD PondingPoints_Add'

    def __str__(self):
        return self.pondingpoints
    


class MajorRoad_inspection(models.Model):
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]

   

    zone = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='major_roads_inspection_new')
    facility_name = models.ForeignKey(MajorRoad_Add, on_delete=models.CASCADE, related_name='major_roads_inspection_new')



    free_from_garbage_rubble = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    dry_and_clean = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')

    remark = models.TextField(null=True, blank=True)
    emp_name = models.CharField(max_length=100, null=True, blank=True)

    inspection_date = models.DateField(default=date.today)

    # ✅ Image upload fields (optional)
    image_1 = models.ImageField(
        upload_to='major_roads_inspections/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='major_roads_inspections/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "DSD.1 Major Roads - Inspections"

    def __str__(self):
        return f"{self.facility_name} ({self.zone})"


class TrunkSewer_inspection(models.Model):
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]


    zone = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='trunk_sewer_inspections_new'
    )

    facility_name = models.ForeignKey(TrunkSewer_Add, on_delete=models.CASCADE, related_name='trunk_sewer_inspection_new')


    manhole_covered = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    manhole_free_from_damage = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    no_sediment_around_manhole = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    no_outflow_of_sewage_from_manhole = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    no_bad_odour_around_manhole = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    no_blockage_at_outflow_of_drain = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    fastflow_of_water_at_outflow_of_drain = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')

    # ✅ Image upload fields (optional)
    image_1 = models.ImageField(
        upload_to='trunk_sewer_inspections/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='trunk_sewer_inspections/',
        null=True,
        blank=True
    )

    remark = models.TextField(null=True, blank=True)
    emp_name = models.CharField(max_length=100, null=True, blank=True)

    inspection_date = models.DateField(default=date.today)

    class Meta:
        verbose_name_plural = "DSD.2 Trunk Sewer - Inspections"

    def __str__(self):
        return f"{self.facility_name} ({self.zone})"


class StormDrain_inspection(models.Model):
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]


    zone = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='storm_drain_inspections_new')
    facility_name = models.ForeignKey(StormDrain_Add, on_delete=models.CASCADE, related_name='storm_drain_inspections_new')


    entry_clear = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    exit_clear = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')

    remark = models.TextField(null=True, blank=True)
    emp_name = models.CharField(max_length=100, null=True, blank=True)

    inspection_date = models.DateField(default=date.today)

    # ✅ Image upload fields (optional)
    image_1 = models.ImageField(
        upload_to='strom_drain_inspections/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='strom_drain_inspections/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "DSD.3 Storm Drain - Inspections"

    def __str__(self):
        return f"{self.facility_name} ({self.zone})"


class PondingPoints_inspection(models.Model):
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]



    zone = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='ponding_points_inspections_new')
    facility_name = models.ForeignKey(PondingPoints_Add, on_delete=models.CASCADE, related_name='ponding_points_inspections_new')


    any_attempt_by_government = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')

    remark = models.TextField(null=True, blank=True)
    emp_name = models.CharField(max_length=100, null=True, blank=True)

    inspection_date = models.DateField(default=date.today)

    # ✅ Image upload fields (optional)
    image_1 = models.ImageField(
        upload_to='ponding_point_inspections/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='pomding_point_inspections/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "DSD.4 Ponding Points - Inspections"

    def __str__(self):
        return f"{self.facility_name} ({self.zone})"




class ComplaintResponse(models.Model):

    FEEDBACK_STATUS_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('neutral', 'Neutral'),
        ('not_responded', 'Call Not Responded'),
    ]

    complaint = models.ForeignKey(
        'Complaint',
        on_delete=models.CASCADE,
        related_name='responses', 
        verbose_name='Complaint'
    )

    officer_name = models.CharField(
        max_length=100,
        verbose_name='Officer Name'
    )

    feedback = models.CharField(
        max_length=20,
        choices=FEEDBACK_STATUS_CHOICES,
        verbose_name='Status'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )

    class Meta:
        verbose_name = "Complaint Response"
        verbose_name_plural = "Complaint Responses"
        ordering = ['-created_at']

    def __str__(self):
        return f"Response for Complaint #{self.complaint.id} by {self.officer_name}"



from django.db import models

class Disbursement(models.Model):
    date = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    disbursement_amount_water_supply = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    disbursement_amount_solid_waste_management = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'location')
        indexes = [
            models.Index(fields=['date', 'location']),
        ]

    def __str__(self):
        return f"{self.date} - {self.location}"




class Manhole_inspection(models.Model):
    YES_NO_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]



    zone = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='manhole_inspections_new')
    facility_name = models.ForeignKey(UC, on_delete=models.CASCADE, related_name='manhole_points_inspections_new')


    manhole_covered = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    any_demage_manhole_covered = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')
    level_with_road = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='No')

    remark = models.TextField(null=True, blank=True)
    emp_name = models.CharField(max_length=100, null=True, blank=True)

    inspection_date = models.DateField(default=date.today)

    # ✅ Image upload fields (optional)
    image_1 = models.ImageField(
        upload_to='manhole_inspections/',
        null=True,
        blank=True
    )
    image_2 = models.ImageField(
        upload_to='manhole_inspections/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name_plural = "DSD.5 Manhole - Inspections"

    def __str__(self):
        return f"{self.facility_name} ({self.zone})"




class VisitSchedule(models.Model):

    visit_date = models.DateField()

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="visit_schedules"
    )

    locations = models.ManyToManyField(
        Location,
        related_name="visit_schedules",
        blank=True
    )

    ucs = models.ManyToManyField(
        UC,
        related_name="visit_schedules",
        blank=True
    )

    visit_roads = models.TextField(
        blank=True,
        null=True,
        help_text="Enter road names separated by commas"
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Visit Schedule"
        verbose_name_plural = "(3.1) Visit Schedules"
        ordering = ["-visit_date"]

    def __str__(self):
        return f"{self.employee.name} - {self.visit_date}"    



from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class VisitEvaluation(models.Model):

    STATUS_CHOICES = [
    ("draft", "Draft"),
    ("completed", "Completed"),
]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )
    
    visit_schedule = models.OneToOneField(
        VisitSchedule,
        on_delete=models.CASCADE,
        related_name="evaluation"
    )


    # ==============================
    # 1. Containers / Moqas
    # ==============================
    total_containers = models.IntegerField(default=0)
    containers_not_lifted = models.IntegerField(default=0)
    containers_not_managed = models.IntegerField(default=0)
    total_moqas = models.IntegerField(default=0)
    moqas_not_cleaned = models.IntegerField(default=0)

    containers_total_score = models.IntegerField(default=4)
    containers_obtained_score = models.IntegerField(default=0,validators=[MinValueValidator(1),MaxValueValidator(4)])
    containers_picture_1 = models.ImageField(upload_to='visit/', blank=True, null=True)    
    containers_picture_2 = models.ImageField(upload_to='visit/', blank=True, null=True)
    containers_picture_3 = models.ImageField(upload_to='visit/', blank=True, null=True)
    containers_picture_4 = models.ImageField(upload_to='visit/', blank=True, null=True)
    containers_picture_5 = models.ImageField(upload_to='visit/', blank=True, null=True)
    containers_picture_6 = models.ImageField(upload_to='visit/', blank=True, null=True)
    containers_picture_7 = models.ImageField(upload_to='visit/', blank=True, null=True)
    containers_picture_8 = models.ImageField(upload_to='visit/', blank=True, null=True)
    containers_picture_9 = models.ImageField(upload_to='visit/', blank=True, null=True)
    containers_picture_10 = models.ImageField(upload_to='visit/', blank=True, null=True)

    containers_remarks = models.TextField(blank=True, null=True)

    # ==============================
    # 2. Drains & Manholes Cleaning
    # ==============================
    drains_scheduled = models.IntegerField(default=0)
    drains_clean = models.IntegerField(default=0)
    manholes_scheduled = models.IntegerField(default=0)
    manholes_clean = models.IntegerField(default=0)

    drains_total_score = models.IntegerField(default=4)
    drains_obtained_score = models.IntegerField(default=0,validators=[MinValueValidator(1),MaxValueValidator(4)])
    drains_picture_1 = models.ImageField(upload_to='visit/', blank=True, null=True)
    drains_picture_2 = models.ImageField(upload_to='visit/', blank=True, null=True)
    drains_picture_3 = models.ImageField(upload_to='visit/', blank=True, null=True)
    drains_picture_4 = models.ImageField(upload_to='visit/', blank=True, null=True)
    drains_picture_5 = models.ImageField(upload_to='visit/', blank=True, null=True)
    drains_picture_6 = models.ImageField(upload_to='visit/', blank=True, null=True)
    drains_picture_7 = models.ImageField(upload_to='visit/', blank=True, null=True)
    drains_picture_8 = models.ImageField(upload_to='visit/', blank=True, null=True)
    drains_picture_9 = models.ImageField(upload_to='visit/', blank=True, null=True)
    drains_picture_10 = models.ImageField(upload_to='visit/', blank=True, null=True)

    drains_remarks = models.TextField(blank=True, null=True)

    # ==============================
    # 3. Roads / Streets Sweeping
    # ==============================
    roads_scheduled = models.IntegerField(default=0)
    roads_clean = models.IntegerField(default=0)
    streets_scheduled = models.IntegerField(default=0)
    streets_clean = models.IntegerField(default=0)

    roads_total_score = models.IntegerField(default=4)
    roads_obtained_score = models.IntegerField(default=0,validators=[MinValueValidator(1),MaxValueValidator(4)])
    roads_picture_1 = models.ImageField(upload_to='visit/', blank=True, null=True)
    roads_picture_2 = models.ImageField(upload_to='visit/', blank=True, null=True)
    roads_picture_3 = models.ImageField(upload_to='visit/', blank=True, null=True)
    roads_picture_4 = models.ImageField(upload_to='visit/', blank=True, null=True)
    roads_picture_5 = models.ImageField(upload_to='visit/', blank=True, null=True)
    roads_picture_6 = models.ImageField(upload_to='visit/', blank=True, null=True)
    roads_picture_7 = models.ImageField(upload_to='visit/', blank=True, null=True)
    roads_picture_8 = models.ImageField(upload_to='visit/', blank=True, null=True)
    roads_picture_9 = models.ImageField(upload_to='visit/', blank=True, null=True)
    roads_picture_10 = models.ImageField(upload_to='visit/', blank=True, null=True)

    roads_remarks = models.TextField(blank=True, null=True)

    # ==============================
    # 4. Door to Door Collection
    # ==============================
    streets_scheduled_d2d = models.IntegerField(default=0)
    houses_scheduled_d2d = models.IntegerField(default=0)
    streets_verified_d2d = models.IntegerField(default=0)

    d2d_total_score = models.IntegerField(default=4)
    d2d_obtained_score = models.IntegerField(default=0,validators=[MinValueValidator(1),MaxValueValidator(4)])
    d2d_picture_1 = models.ImageField(upload_to='visit/', blank=True, null=True)
    d2d_picture_2 = models.ImageField(upload_to='visit/', blank=True, null=True)
    d2d_picture_3 = models.ImageField(upload_to='visit/', blank=True, null=True)
    d2d_picture_4 = models.ImageField(upload_to='visit/', blank=True, null=True)
    d2d_picture_5 = models.ImageField(upload_to='visit/', blank=True, null=True)
    d2d_picture_6 = models.ImageField(upload_to='visit/', blank=True, null=True)
    d2d_picture_7 = models.ImageField(upload_to='visit/', blank=True, null=True)
    d2d_picture_8 = models.ImageField(upload_to='visit/', blank=True, null=True)
    d2d_picture_9 = models.ImageField(upload_to='visit/', blank=True, null=True)
    d2d_picture_10 = models.ImageField(upload_to='visit/', blank=True, null=True)

    d2d_remarks = models.TextField(blank=True, null=True)

    # ==============================
    # 5. Tube Wells
    # ==============================
    total_tubewells = models.IntegerField(default=0)
    tubewells_visited = models.IntegerField(default=0)
    tubewells_satisfactory = models.IntegerField(default=0)

    record = models.BooleanField(default=False)
    uniform = models.BooleanField(default=False)
    functional_time = models.BooleanField(default=False)
    leaks = models.BooleanField(default=False)

    tubewell_total_score = models.IntegerField(default=4)
    tubewell_obtained_score = models.IntegerField(default=0,validators=[MinValueValidator(1),MaxValueValidator(4)])
    tubewell_picture_1 = models.ImageField(upload_to='visit/', blank=True, null=True)
    tubewell_picture_2 = models.ImageField(upload_to='visit/', blank=True, null=True)
    tubewell_picture_3 = models.ImageField(upload_to='visit/', blank=True, null=True)
    tubewell_picture_4 = models.ImageField(upload_to='visit/', blank=True, null=True)
    tubewell_picture_5 = models.ImageField(upload_to='visit/', blank=True, null=True)
    tubewell_picture_6 = models.ImageField(upload_to='visit/', blank=True, null=True)
    tubewell_picture_7 = models.ImageField(upload_to='visit/', blank=True, null=True)
    tubewell_picture_8 = models.ImageField(upload_to='visit/', blank=True, null=True)
    tubewell_picture_9 = models.ImageField(upload_to='visit/', blank=True, null=True)
    tubewell_picture_10 = models.ImageField(upload_to='visit/', blank=True, null=True)


    tubewell_remarks = models.TextField(blank=True, null=True)

    # ==============================
    # Overall
    # ==============================
    overall_total_score = models.IntegerField(default=20)
    overall_obtained_score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation - {self.visit_schedule}"




class ManholeShape(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ManholeCoverSize(models.Model):
    size = models.CharField(max_length=50)

    def __str__(self):
        return self.size


class ManholeCoverMaterial(models.Model):
    material = models.CharField(max_length=50)

    def __str__(self):
        return self.material


class Manhole(models.Model):

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('covered', 'Covered'),
    ]


    uc = models.ForeignKey(UC, on_delete=models.CASCADE, blank=True, null=True)

    # 🔗 New Linked Fields
    shape = models.ForeignKey(ManholeShape, on_delete=models.SET_NULL, null=True, blank=True)
    cover_size = models.CharField(max_length=100, null=True, blank=True)  
    cover_material = models.ForeignKey(ManholeCoverMaterial, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    def __str__(self):
        return f"{self.uc} - {self.status}"

    class Meta:
        verbose_name_plural = '(1.6) Manhole'        