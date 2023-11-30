from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GraphHuntingViewSet

router = DefaultRouter()

# router.register(r'graph/security/runHuntingQuery', GraphHuntingViewSet, basename='hunting')

urlpatterns = [
    path('', include(router.urls)),
    path('graph/security/runHuntingQuery/', GraphHuntingViewSet.as_view({'post': 'run_hunting_query'})),
]