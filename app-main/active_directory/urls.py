from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActiveDirectoryQueryViewSet

urlpatterns = [
    path('active-directory/v1.0/query', ActiveDirectoryQueryViewSet.as_view({'get': 'query'})),    
]

