from django.urls import path
from django.conf.urls import url,include

from . import views

app_name='resourceaccommodator'

urlpatterns=[
    path('resource-accommodator/', views.resource_accommodator, name='resource-accommodator'),
    path('resourceaccommodator/cloud-calculator', views.cloud_calculator, name='cloud-calculator'),
    path('get-orderable-item-api/', views.get_orderable_item_api, name='get-orderable-item-api'),
    path('get-all-orderable-items-api', views.get_all_orderable_items_api, name='get-all-orderable-items-api'),
    path('get-all-orderable-items-dtt-api', views.get_all_orderable_items_dtt_api, name='get-all-orderable-items-dtt-api'),
    path('test', views.test, name='test'),
]

