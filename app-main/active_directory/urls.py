from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ADComputerViewSet, ADInactiveComputersViewset

# router = DefaultRouter()
# router.register(r'items', ItemViewSet)
# router.register(r'sccm', SCCMViewSet, basename='sccm')


urlpatterns = [
    # path('', include(router.urls)),


    path('computer/v1-0-0/<str:computer_name>/', ADComputerViewSet.as_view({'get': 'retrieve'})),

    # this endpoint returns a list of computers that thats has not been logged in for x days - default 30 days    
    path('computer/v1-0-0/inactive-computers', ADInactiveComputersViewset.as_view({'get': 'retrieve'})),

    # path('sccm/v2/<str:computer_name>/', SCCMViewSet.as_view({'get': 'retrieve'})),
    
]

