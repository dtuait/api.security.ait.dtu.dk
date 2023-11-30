from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SCCMComputerViewSet_1_0_0, SCCMComputerViewSet_1_0_1

router = DefaultRouter()
# router.register(r'items', ItemViewSet)
# router.register(r'sccm', SCCMViewSet, basename='sccm')


urlpatterns = [
    path('', include(router.urls)),
    path('sccm/computer/v1-0-0/<str:computer_name>/', SCCMComputerViewSet_1_0_0.as_view({'get': 'retrieve'})),
    path('sccm/computer/v1-0-1/<str:computer_name>/', SCCMComputerViewSet_1_0_1.as_view({'get': 'retrieve'})),
    # path('sccm/v2/<str:computer_name>/', SCCMViewSet.as_view({'get': 'retrieve'})),
]

