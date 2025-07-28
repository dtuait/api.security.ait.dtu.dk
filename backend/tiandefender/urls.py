# tiandefender/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
