from django.urls import path

from . import views

app_name='cloudstats'

urlpatterns=[
    path('cloud-stats/', views.cloud_stats, name='cloud-stats'),
]
