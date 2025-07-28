from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActiveDirectoryQueryViewSet, ActiveDirectoryQueryAssistantViewSet

urlpatterns = [
    path('active-directory/v1.0/query', ActiveDirectoryQueryViewSet.as_view({'get': 'query'})),
    path('active-directory/v1.0/query-assistant', ActiveDirectoryQueryAssistantViewSet.as_view({'post': 'create'})),
]

