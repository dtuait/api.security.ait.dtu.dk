from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SCCMViewSet

router = DefaultRouter()
# router.register(r'items', ItemViewSet)
# router.register(r'sccm', SCCMViewSet, basename='sccm')


urlpatterns = [
    path('', include(router.urls)),
    path('sccm/v1/<str:computer_name>/', SCCMViewSet.as_view({'get': 'retrieve'})),
    # path('sccm/v2/<str:computer_name>/', SCCMViewSet.as_view({'get': 'retrieve'})),
]

