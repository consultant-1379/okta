from django.urls import path
from . import views

app_name='demandmanagement'

urlpatterns=[
    path('demand-management/', views.demand_management, name='demandmanagement'),
    path('demand-management-api/', views.demand_management_api, name='demand-management-api'),
    path('demand-management-excel-report/', views.generate_demand_management_report, name='demand-management-excel-report'),
]
