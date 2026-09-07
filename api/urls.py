from django.urls import path
from .views import ApiStatusCheck, dshbMonthWiseData
from . import views
app_name = "api"

urlpatterns = [
    path("ApiStatusCheck", ApiStatusCheck),
    path("dshbMonthWiseData", dshbMonthWiseData),

    path("revenue/dashboard/", views.revenuedashboard, name="dashboard"),

]
