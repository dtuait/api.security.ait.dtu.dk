from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GraphViewSet

router = DefaultRouter()

# router.register(r'graph/security/runHuntingQuery', GraphHuntingViewSet, basename='hunting')

urlpatterns = [
    path('', include(router.urls)),
    path('graph/security/run-hunting-query', GraphViewSet.as_view({'post': 'run_hunting_query'})),
]