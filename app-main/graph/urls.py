from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HuntingQueryViewSet, DeleteMfaViewSet, UnlockMfaViewSet, GetUserViewSet, ListUserAuthenticationMethodsViewSet

# router = DefaultRouter()

# router.register(r'graph/security/runHuntingQuery', GraphHuntingViewSet, basename='hunting')

urlpatterns = [
    path('v1.0/graph/security/run-hunting-query', HuntingQueryViewSet.as_view({'post': 'run_hunting_query'})),
    path('v1.0/graph/get-user/<str:user>', GetUserViewSet.as_view({'get': 'get_user'})),
    # GET https://graph.microsoft.com/v1.0/users/sandeep@contoso.com/authentication/microsoftAuthenticatorMethods
    path('v1.0/graph/list/<str:user_id__or__user_principalname>/authentication-methods', ListUserAuthenticationMethodsViewSet.as_view({'get': 'list_user_authentication_methods'})),
    # v1.0/users/kim@contoso.com/authentication/microsoftAuthenticatorMethods/_jpuR-TGZtk6aQCLF3BQjA2
    path('v1.0/graph/users/<str:user_id__or__user_principalname>/authentication-methods/<str:microsoft_authenticator_method_id>', DeleteMfaViewSet.as_view({'delete': 'delete_mfa'})),
    

    

]

