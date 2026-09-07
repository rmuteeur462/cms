from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from .views import (
    home_view, 
    login_view, 
    attendance_report, 
    water_supply_report,
    tubewell_attendance, 
    LocationAutocomplete, 
    UCAutocomplete, 
    EmployeeAutocomplete, 
    TubeWellAutocomplete,
    vehicle_attendance_report,
    vehicle_attendance_summary,
    tubewell_attendance_summary,
    daily_post_attendance,
    complaint_management_report,
    get_post_details,
    attendance_report_generator,
    get_uc_by_location,
    daily_sanitation_report,
    sanitation_summary_view,
    field_visit_report,
    field_visit_summary,
    clc_report,
    clc_summary,
    water_quality_report,
    bin_attendance_report,
    bin_summary_view,
    tracker_attendance_report,
    attendance_summary_pdf,
    get_ucs,
    get_tubewells,
    tubewell_repair_view,
    PasswordUpdateView,
    password_change_done,
    bin_list_view,
    kmz_visualization,
    revenue_report_generator,
    update_revenue,
    update_bin_view,
    perfoma_tube_list

)



from .views import (
    StreetListView,
    StreetCreateView,
    StreetUpdateView,
    StreetDeleteView
)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, EmployeeAttendanceViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'attendances', EmployeeAttendanceViewSet, basename='attendance')


urlpatterns = [
    path('api/', include(router.urls)),

    path('login/', views.login_view, name='login'),                      # Login page
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Logout and redirect to login
    path('splash/', views.splash_screen, name='splash'),                 # Splash screen after login
    path('home/', views.home_view, name='home'), 
    path('attendance-report/', attendance_report, name='attendance_report'),
    path('tubewell-attendance/', tubewell_attendance, name='tubewell_attendance'),
    path('attendance-summary/', views.attendance_summary, name='attendance_summary'),
    path('attendance/report/', attendance_report_generator, name='attendance_report_generator'),
    path('attendance_summary/pdf/', attendance_summary_pdf, name='attendance_summary_pdf'),
    path('filter-attendance-report/', views.filter_attendance_report, name='filter_attendance_report'),
    path('tracker-attendance/', tracker_attendance_report, name='tracker_attendance_report'),
    path('location-autocomplete/', LocationAutocomplete.as_view(), name='location-autocomplete'),
    path('uc-autocomplete/', UCAutocomplete.as_view(), name='uc-autocomplete'),
    path('employee-autocomplete/', EmployeeAutocomplete.as_view(), name='employee-autocomplete'),
    path('tubewell-autocomplete/', TubeWellAutocomplete.as_view(), name='tubewell-autocomplete'),
    path('vehicle-attendance/', vehicle_attendance_report, name='vehicle_attendance_report'),
    path('vehicle-attendance-summary/', vehicle_attendance_summary, name='vehicle_attendance_summary'),
    path('tubewell-attendance-summary/', tubewell_attendance_summary, name='tubewell_attendance_summary'),
    path('vehicle_pe_attendance/', views.vehicle_pe_attendance, name='vehicle_pe_attendance'),
    path('daily-post-attendance/', daily_post_attendance, name='daily_post_attendance'),
    path('complaints/', complaint_management_report, name='complaint_management_report'),
    path('complaints-view/', views.complaint_management_view, name='complaint_management_view'),

    path('complaint-summary/', views.complaint_summary_view, name='complaint_summary'),
    path('get_post_details/', get_post_details, name='get_post_details'),
    path('sanitation-report/', daily_sanitation_report, name='daily_sanitation_report'),
    path('sanitation-summary/', sanitation_summary_view, name='sanitation_summary'),
    path('field-visit-report/', field_visit_report, name='field_visit_report'),
    path('field-visit-summary/', field_visit_summary, name='field_visit_summary'),
    path('clc-report/', clc_report, name='clc_report'),
    path('clc-summary/', clc_summary, name='clc_summary'),
    path('water-supply-report/', water_supply_report, name='water_supply_report'),
    path('water-quality-report/', water_quality_report, name='water_quality_report'),
    path('bin-attendance/', bin_attendance_report, name='bin_attendance_report'),
    path('bin-summary/', bin_summary_view, name='bin_summary'),
    path('revenue/', views.revenue_management_report, name='revenue_management_report'),
    path('revenue-summary/', views.revenue_summary_view, name='revenue_summary'),
    path('media-summary/', views.media_summary, name='media_summary'),
    path('report_vehicle/', views.report_vehicle, name='report_vehicle'),
    path('get-ucs/', get_ucs, name='get_ucs'),
    path('get-tubewells/', get_tubewells, name='get_tubewells'),
    path('get-ucs-by-location/', get_uc_by_location, name='uc-list'), 
    path('ajax/load-officials/', views.load_officials, name='load_officials'),
    path('tubewell-repair/', tubewell_repair_view, name='tubewell_repair'),
    path('vehicle-repair/', views.vehicle_repair_view, name='vehicle_repair'),
    path('tubewell-attendance-report/', views.tubewell_attendance_report, name='tubewell_attendance_report'),
    path('attendance-summary-excel/', views.attendance_summary_excel, name='attendance_summary_excel'),
    path('password-change/', PasswordUpdateView.as_view(), name='password_change'),
    path('password-change/done/', password_change_done, name='password_change_done'),
    path('bins/', bin_list_view, name='bin_list'),
    path('map-all-bins/', views.map_all_bins, name='map_all_bins'),
    path('map/', views.location_map_view, name='location_map'),
    path('map/geojson/', views.location_map_geojson, name='location_map_geojson'),
    path('kmz-visualization/<int:kmz_id>/', kmz_visualization, name='kmz_visualization'),
    path('binfoam/', views.binfoam_view, name='binfoam_view'),
    path('report/post_attendance/', views.report_post_attendance, name='report_post_attendance'),
    path('complaint-report-generator/', views.complaint_report_generator, name='C_report_generator'),
    path('revenue-report/', revenue_report_generator, name='revenue_report_generator'),
    path('report_FV/', views.generate_field_visit_report, name='generate_field_visit_report'),
    path('generate-clc-report/', views.generate_clc_report, name='generate_clc_report'),
    path('fetch_uc_by_location/', views.fetch_uc_by_location, name='fetch_uc_by_location'),
    path('fetch_bin_by_location/', views.fetch_bin_by_location, name='fetch_bin_by_location'),
    path('fetch_bin_by_uc/', views.fetch_bin_by_uc, name='fetch_bin_by_uc'),
        path('fetch_clc_staff_by_location/', views.fetch_clc_staff_by_location, name='fetch_clc_staff_by_location'),
path('dropuc/', views.dropuc, name='dropuc'),  # Make sure this is correctly written
    path('update-revenue/<int:revenue_id>/', update_revenue, name='update_revenue'),
        path('clc_report/update/<int:report_id>/', views.update_clc_report, name='update_clc_report'),
    path('update-field-visit-report/<int:report_id>/', views.update_field_visit_report, name='update_field_visit_report'),
    path('bins/update/<int:pk>/', update_bin_view, name='update_bin'),  # New route for updates
    path('report-tubewell-2/', views.report_tubwell_2, name='report_tubwell_2'),
    path('add_perfoma_tube/', views.add_perfoma_tube, name='add_perfoma_tube'),
    path('list/', perfoma_tube_list, name='perfoma_tube_list'),
    path('bin-lifting-report/', views.bin_lifting_report, name='bin_lifting_report'),


path('street_cleaning_list/', views.street_cleaning_list, name='street_cleaning_list'),
    path('create/', views.street_cleaning_create, name='street_cleaning_create'),
    path('update/<int:pk>/', views.street_cleaning_update, name='street_cleaning_update'),
    path('detail/<int:pk>/', views.street_cleaning_detail, name='street_cleaning_detail'),

 path('get_ucs/', views.get_ucs, name='get_ucs'),
    path('get_ncs/', views.get_ncs, name='get_ncs'),

     path('get_employees/', views.get_employees, name='get_employees'),
    path('get_vehicles/', views.get_vehicles, name='get_vehicles'),
    path('get_bins/', views.get_bins, name='get_bins'),
        path('get_streets/', views.get_streets, name='get_streets'),
    path('total-attendance-report/', views.total_attendance_report, name='total_attendance_report'),
path('zreport/', views.report_summary, name='zreport'),
    path('sanitation-data/', views.sanitation_data, name='sanitation_data'),
    path('fetch-clc-staff/', views.fetch_clc_staff, name='fetch_clc_staff'),
    path('fetch-ucs-by-location/', views.fetch_ucs_by_location, name='fetch_ucs_by_location'),  # Add this line
    path('fetch-ncs-by-uc/', views.fetch_ncs_by_uc, name='fetch_ncs_by_uc'),  
    path('bin-report/', views.bin_report_view, name='bin_report_view'),
    path('documents/', views.document_list, name='document_list'),
    path('adp/', views.adp_list, name='adp_list'),

    path('daily-fuel-report/', views.daily_fuel_report, name='daily_fuel_report'),

    path('department-attendance/', views.department_attendance_report, name='department_attendance_report'),
    path('distance_fuel_report/', views.distance_and_fuel_report, name='distance_and_fuel_report'),
    path('map/tubewells/', views.map_all_tubewells, name='map_all_tubewells'),
    path('complaint-dashboard/', views.complaint_dashboard, name='complaint_dashboard'),
    path('water-depths/', views.water_depth_list, name='water_depth_list'),


    path('vehicle_m&e/', views.vehicle_pe_monthly_report, name='vehicle_pe_monthly_report'),
    path('add-water-produce/', views.add_water_produce, name='add_water_produce'),
    path('add-electricity-usage/', views.add_electricity_usage, name='add_electricity_usage'),
    path('tubewell-monthly-summary/', views.tubewell_monthly_summary, name='tubewell_monthly_summary'),
    path("api/get-previous-reading/", views.get_previous_reading, name="get_previous_reading"),
    path('update-water-produce/<int:produce_id>/', views.update_water_produce, name='update_water_produce'),
    path('complaints/pending/', views.pending_complaints_list, name='pending_complaints_list'),
    path('ajax/load-subtypes/', views.ajax_load_subtypes, name='ajax_load_subtypes'),
    path('hotspots/', views.hotspot_list, name='hotspot_list'),
    path('hotspots/map', views.hotspot_list_map, name='hotspot_list_map'),

    path('hotspots/events/', views.hotspot_event_view, name='hotspot_event_view'),
    path('hotspots/<int:hotspot_id>/history/', views.hotspot_history, name='hotspot_history'),
    path("flood-report/", views.flood_report, name="flood_report"),
        path('schemes/', views.adp_scheme_list, name='adp_scheme_list'),
    path('schemes/<int:pk>/', views.adp_scheme_detail, name='adp_scheme_detail'),
 path('feedback/', views.ComplaintFeedbackListView.as_view(), name='feedback_list'),
    path('feedback/create/', views.ComplaintFeedbackCreateView.as_view(), name='feedback_create'),
    path('feedback/<int:pk>/update/', views.ComplaintFeedbackUpdateView.as_view(), name='feedback_update'),
path('complaint/check/', views.complaint_check_api, name='complaint_check_api'),
    path('complaints/by-user/', views.complaints_by_user_view, name='complaints_by_user'),
    path('complaint-report/', views.complaint_report, name='complaint_report'),
    path('update-watertest/', views.update_watertest, name='update_watertest'),





    path('streets/', StreetListView.as_view(), name='street_list'),
    path('streets/add/', StreetCreateView.as_view(), name='street_add'),
    path('streets/<int:pk>/edit/', StreetUpdateView.as_view(), name='street_edit'),
    path('streets/<int:pk>/delete/', StreetDeleteView.as_view(), name='street_delete'),
    path('daily-collection/', views.daily_collection_entry, name='daily_collection_entry'),
    path('street/<int:pk>/', views.street_detail_view, name='street_detail'),
    path('dashboard/street-collection/', views.street_collection_dashboard, name='street_collection_dashboard'),
    path('accumulative-street/', views.accumulative_street_report, name='accumulative_street_report'),



    path('water-quality/dashboard/', views.water_quality_dashboard, name='water_quality_dashboard'),
    path('get-unsafe-tests/', views.get_unsafe_tests, name='get_unsafe_tests'),
    path('water-test-report/', views.water_test_report, name='water_test_report'),
# ================= Major Road =================
    path('major-road/', views.major_road_list, name='major_road_list_old'),
    path('major-road/add/', views.major_road_create, name='major_road_create'),
    path('major-road/<int:pk>/edit/', views.major_road_update, name='major_road_update'),
    path('major-road/<int:pk>/delete/', views.major_road_delete, name='major_road_delete'),

    # ================= Trunk Sewer =================
    path('trunk-sewer/', views.trunk_sewer_list, name='trunk_sewer_list'),
    path('trunk-sewer/add/', views.trunk_sewer_create, name='trunk_sewer_create'),
    path('trunk-sewer/<int:pk>/edit/', views.trunk_sewer_update, name='trunk_sewer_update'),
    path('trunk-sewer/<int:pk>/delete/', views.trunk_sewer_delete, name='trunk_sewer_delete'),

    # ================= Storm Drain =================
    path('storm-drain/', views.storm_drain_list, name='storm_drain_list'),
    path('storm-drain/add/', views.storm_drain_create, name='storm_drain_create'),
    path('storm-drain/<int:pk>/edit/', views.storm_drain_update, name='storm_drain_update'),
    path('storm-drain/<int:pk>/delete/', views.storm_drain_delete, name='storm_drain_delete'),

    # ================= Ponding Points =================
    path('ponding-points/', views.ponding_points_list, name='ponding_points_list'),
    path('ponding-points/add/', views.ponding_points_create, name='ponding_points_create'),
    path('ponding-points/<int:pk>/edit/', views.ponding_points_update, name='ponding_points_update'),
    path('ponding-points/<int:pk>/delete/', views.ponding_points_delete, name='ponding_points_delete'),

    path("reports/major-road/", views.major_road_report, name="major_road_report_old"),
    path("reports/trunk-sewer/", views.trunk_sewer_report, name="trunk_sewer_report_old"),
    path("reports/storm-drain/", views.storm_drain_report, name="storm_drain_report_old"),
    path("reports/ponding-points/", views.ponding_points_report, name="ponding_points_report_old"),


    path('discharge/', views.tubewell_discharge_list, name='tubewell_discharge_list'),
    path('discharge/add/', views.tubewell_discharge_create, name='tubewell_discharge_create'),
    path('discharge/edit/<int:pk>/', views.tubewell_discharge_update, name='tubewell_discharge_update'),
    path('discharge/delete/<int:pk>/', views.tubewell_discharge_delete, name='tubewell_discharge_delete'),


 # ---------- DSD-1 Major Roads ----------
    path('dsd1/', views.dsd1_majorroad_list, name='dsd1_majorroad_list'),
    path('dsd1/add/', views.dsd1_majorroad_add, name='dsd1_majorroad_add'),
    path('dsd1/edit/<int:pk>/', views.dsd1_majorroad_update, name='dsd1_majorroad_update'),
    path('dsd1/delete/<int:pk>/', views.dsd1_majorroad_delete, name='dsd1_majorroad_delete'),

    # ---------- DSD-2 Trunk Sewer ----------
    path('dsd2/', views.dsd2_trunk_list, name='dsd2_trunk_list'),
    path('dsd2/add/', views.dsd2_trunk_add, name='dsd2_trunk_add'),
    path('dsd2/edit/<int:pk>/', views.dsd2_trunk_update, name='dsd2_trunk_update'),
    path('dsd2/delete/<int:pk>/', views.dsd2_trunk_delete, name='dsd2_trunk_delete'),

    # ---------- DSD-3 Storm Drain ----------
    path('dsd3/', views.dsd3_storm_list, name='dsd3_storm_list'),
    path('dsd3/add/', views.dsd3_storm_add, name='dsd3_storm_add'),
    path('dsd3/edit/<int:pk>/', views.dsd3_storm_update, name='dsd3_storm_update'),
    path('dsd3/delete/<int:pk>/', views.dsd3_storm_delete, name='dsd3_storm_delete'),

    # ---------- DSD-4 Ponding ----------
    path('dsd4/', views.dsd4_ponding_list, name='dsd4_ponding_list'),
    path('dsd4/add/', views.dsd4_ponding_add, name='dsd4_ponding_add'),
    path('dsd4/edit/<int:pk>/', views.dsd4_ponding_update, name='dsd4_ponding_update'),
    path('dsd4/delete/<int:pk>/', views.dsd4_ponding_delete, name='dsd4_ponding_delete'),
    path('dsd/', views.dsd_dashboard, name='dsd_dashboard'),

    path('major-roads/', views.MajorRoadListView.as_view(), name='major_road_list'),
    path('trunk-sewers/', views.TrunkSewerListView.as_view(), name='trunk_sewer_list'),
    path('storm-drains/', views.StormDrainListView.as_view(), name='storm_drain_list'),
    path('ponding-list/', views.PondingPointsListView_new.as_view(), name='ponding_points_list'),


    path('major-roads/<int:pk>/inspections/', views.MajorRoadInspectionDetailView.as_view(), name='major_road_inspections'),
    path(
        'trunk-sewer/<int:pk>/inspections/',
        views.TrunkSewerInspectionDetailView.as_view(),
        name='trunk_sewer_inspection_detail'
    ),

    # Storm Drain Inspections
    path(
        'storm-drain/<int:pk>/inspections/',
        views.StormDrainInspectionDetailView.as_view(),
        name='storm_drain_inspection_detail'
    ),

    # Ponding Points Inspections
    path(
        'ponding-points/<int:pk>/inspections/',
        views.PondingPointsInspectionDetailView.as_view(),
        name='ponding_points_inspection_detail'
    ),
    path('reports/major-roads/', views.major_road_report, name='major_road_report'),
    path('reports/trunk-sewer/', views.trunk_sewer_report, name='trunk_sewer_report'),
    path('reports/storm-drain/', views.storm_drain_report, name='storm_drain_report'),
    path('reports/ponding-points/', views.ponding_points_report, name='ponding_points_report'),


    path('tubewell/horsepower-summary/', views.HorsePowerSummaryView, name='horsepower_summary'),

    path('complaints/resolved/', views.resolved_complaint_list, name='resolved_complaint_list'),
    path('complaints/<int:complaint_id>/response/', views.add_complaint_response, name='add_complaint_response'),
    path(
            'daily-sweeping/',
            views.daily_sweeping_entry,
            name='daily_sweeping_entry'
        ),

    path('complaint-response-report/', views.complaint_response_report, name='complaint_response_report'),


    path(
            "visit-schedules/",
            views.visit_schedule_view,
            name="visit_schedule_list"
        ),


         # ---------- DSD-5 Manhole ----------
    path('dsd5/', views.dsd5_manhole_list, name='dsd5_manhole_list'),
    path('dsd5/add/', views.dsd5_manhole_add, name='dsd5_manhole_add'),
    path('dsd5/edit/<int:pk>/', views.dsd5_manhole_update, name='dsd5_manhole_update'),
    path('dsd5/delete/<int:pk>/', views.dsd5_manhole_delete, name='dsd5_manhole_delete'),
    path("reports/manhole/", views.dsd5_manhole_report, name="dsd5_manhole_report"),


    path("visit-evaluations/", views.visit_evaluation_list, name="visit_evaluation_list"),
    path("visit-evaluations/create/", views.visit_evaluation_create, name="visit_evaluation_create"),
    path("visit-evaluations/update/<int:pk>/", views.visit_evaluation_update, name="visit_evaluation_update"),
    path("visit-evaluations/delete/<int:pk>/", views.visit_evaluation_delete, name="visit_evaluation_delete"),
    path(
    "visit-evaluation/<int:pk>/detail/",
    views.visit_evaluation_detail,
    name="visit_evaluation_detail"),


    path('manhole/', views.manhole_list, name='manhole_list'),
    path('manhole/create/', views.manhole_create, name='manhole_create'),
    path('manhole/update/<int:pk>/', views.manhole_update, name='manhole_update'),
    path('manhole/delete/<int:pk>/', views.manhole_delete, name='manhole_delete'),
    path('manhole/dashboard/', views.manhole_dashboard, name='manhole_dashboard'),

    path('monthly-report/', views.monthly_report, name='monthly_report'),
    path('daily-report/', views.daily_progress_report, name='daily_report'),
    path("manholes/data/",views.manhole_geojson, name="manhole_geojson"),
    path("manholes/map/", views.manhole_map_view, name="manhole_map"),

    path("dashboard/", include("api.urls")),

]