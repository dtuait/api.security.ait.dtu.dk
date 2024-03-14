from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HuntingQueryViewSet, DeleteMfaViewSet, UnlockMfaViewSet, GetUserViewSet, GetUserAuthenticationMethodsViewSet

# router = DefaultRouter()

# router.register(r'graph/security/runHuntingQuery', GraphHuntingViewSet, basename='hunting')

urlpatterns = [
    path('v1.0/graph/security/run-hunting-query', HuntingQueryViewSet.as_view({'post': 'run_hunting_query'})),
    path('v1.0/graph/get-user/<str:user>', GetUserViewSet.as_view({'get': 'get_user'})),
    path('v1.0/graph/get-user-authentication-methods/<str:user_id>', GetUserAuthenticationMethodsViewSet.as_view({'get': 'get_user_authentication_methods'})),
    path('v1.0/graph/delete-mfa/<str:user>', DeleteMfaViewSet.as_view({'delete': 'delete_mfa'})),

    

]

