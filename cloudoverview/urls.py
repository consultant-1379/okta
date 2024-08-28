from django.urls import path

from . import views

app_name='cloudoverview'

urlpatterns=[
    path('cloud-overview/', views.cloud_overview, name='cloud-overview'),
    path('create-potential-cloud/', views.PotentialCloudCreateView.as_view(), name='create-potential-cloud'), 
    path('get-potential-cloud-api/', views.get_potential_cloud_api, name='get-potential-cloud-api'), 
    path('delete-potential-cloud/', views.delete_potential_cloud, name='delete-potential-cloud'),
    path('edit-potential-cloud/', views.edit_potential_cloud, name='edit-potential-cloud'),
    path('edit-potential-cloud-modal/', views.get_edit_potential_cloud_modal, name='edit-potential-cloud-modal'),
]
