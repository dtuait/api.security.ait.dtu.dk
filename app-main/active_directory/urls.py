from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActiveDirectoryQueryViewSet

urlpatterns = [
    path('v1.0/active-directory/query', ActiveDirectoryQueryViewSet.as_view({'get': 'query'})),    
]

