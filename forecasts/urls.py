from django.urls import path
from . import views

app_name='forecasts'

urlpatterns=[
    path('forecasts/', views.forecasts, name='forecasts'),
    path('forecasts-api/', views.forecasts_api, name='demand-management-api'),
    path('forecasts-excel-report/', views.generate_forecast_report, name='forecasts-excel-report'),
]
