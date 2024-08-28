from django.urls import path
from django.conf.urls import url,include

from . import views

app_name='blog'

urlpatterns=[
    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('user-auth/', views.user_auth, name='user-auth'),
    path('user-auth/blog/success/', views.success, name='success'),
]

