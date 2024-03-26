from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from .models import Endpoint
from rest_framework.authentication import SessionAuthentication, TokenAuthentication




from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ObjectDoesNotExist
import logging



from django.shortcuts import redirect

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class AccessControlMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize the list of paths to exclude from checks
        self.excluded_paths = [
            # '/admin',  # Exclude all Django admin paths
            # '/myview',
            # '/login-redirector/'       
            # '/auth',
            # '/login',
            # '/logout',
            # '/auth/callback', 
            '/favicon.ico',
        ]

        


        self.login_paths = [
            {
                'path': '/login/', 
                'method': 'get'
            },
            {
                'path': '/logout/',
                'method': None
            },
            {
                'path': '/auth/callback/',
                'method': None
            }
        ]



        super().__init__(get_response)

    def __call__(self, request):

        
        path    = request.path
        method  = request.method.lower()     


        # Check if the path is excluded from checks
        if any(path.startswith(excluded_path) for excluded_path in self.excluded_paths):
            return self.get_response(request)
        
        
        # overwrites the request.user with the user from the token
        token = request.META.get('HTTP_AUTHORIZATION')
        token_short = None
        if token:
            try:
                request.user = (Token.objects.get(key=token)).user
                token_short = token[:10] if token else None
            except ObjectDoesNotExist:
                ip = get_client_ip(request)
                token_short = token[:20] if token else None
                logger = logging.getLogger(__name__)
                logger.info(f'Invalid token from IP: {ip}, token: {token_short}')
                # return HttpResponseForbidden('Invalid token')
                
        # print(f'running middleware for path: {path} and method: {method} and from user {request.user.username} and token: {token_short}...')


        # Allow the user to access the login page
        if any(path == login_path['path'] and (login_path['method'] == method or login_path['method'] == None) for login_path in self.login_paths):
            if path  == '/login/':
                from app.views import msal_login
                msal_login(request)
                return None
            elif (path == '/auth/callback/'):
                return redirect('/auth/callback/')
            return HttpResponseForbidden('Unknow login path')



        # if the user is not authenticated, then redirect to login
        if not request.user.is_authenticated:
            return redirect('/login/')
        
        # if the user is authenticated and the token is None, then redirect to login
        # also check if the user is not a superuser
        if not request.user.username.startswith('adm-'):
            if not request.user.is_superuser:
                from django.contrib.auth import logout
                logout(request)
                return HttpResponseForbidden('Error in token, please login again')

    
            
        # TEMP - skal erstattes med endpoint access control.
        # This is the final entry
        if request.user.is_authenticated:
            if request.user.username.startswith('adm-') or request.user.is_superuser:
                return self.get_response(request)
        
        # # Check access in EndpointPermission
        # try:
        #     endpoint = Endpoint.objects.get(path=path, method=method)
        #     permission = EndpointPermission.objects.get(user_profile=request.user.userprofile, endpoint=endpoint)
        #     if not permission.can_access:
        #         return HttpResponseForbidden('You do not have access to this endpoint')
        # except (Endpoint.DoesNotExist, EndpointPermission.DoesNotExist):
        #     return HttpResponseForbidden('Endpoint not found or access not defined')

        # if not request.user.is_authenticated and not token_user:
        #     return HttpResponseForbidden('You must be logged in to access this endpoint')

        # # Special handling for root users and 'any' endpoint
        # if request.user.is_superuser:
        #     return self.get_response(request)
                

        

        # If none of the above, forbid access
        return HttpResponseForbidden('You must be logged in to access this endpoint')


def is_authenticated(request):
    pass
        
    
        






























# class AccessControlMiddleware(MiddlewareMixin):
#     def __init__(self, get_response):
#         self.get_response = get_response
#         self.token_auth = TokenAuthentication()
#         self.excluded_paths = [
#             '/admin',
#             '/accounts/login/',
#             '/myview',
#             '/login/',
#             '/logout/',
#             # Add any other paths to exclude as needed
#         ]
#         super().__init__(get_response)

#     def __call__(self, request):
#         path = request.path

#         # Exclude paths that don't require authentication
#         if any(path.startswith(excluded_path) for excluded_path in self.excluded_paths):
#             return self.get_response(request)

#         # Try to authenticate using token first
#         auth = get_authorization_header(request).split()
#         if auth and len(auth) == 2 and auth[0].lower() == b'token':
#             user_auth_tuple = self.token_auth.authenticate(request)
#             if user_auth_tuple is not None:
#                 # Token is valid, set user and continue
#                 request.user, request.auth = user_auth_tuple
#                 return self.get_response(request)

#         # If token auth failed, check if user is authenticated via session
#         if request.user.is_authenticated:
#             return self.get_response(request)

#         # Handle root/superuser access
#         if request.user.is_superuser:
#             return self.get_response(request)

#         # If none of the above, forbid access
#         return HttpResponseForbidden('You must be logged in to access this endpoint')


























# from django.http import HttpResponseForbidden
# from django.utils.deprecation import MiddlewareMixin
# from .models import EndpointPermission, Endpoint

# class AccessControlMiddleware(MiddlewareMixin):
#     def __call__(self, request):
#         # Extract the request path and method
#         path = request.path
#         method = request.method.lower()

#         # Check if user is authenticated
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden('You must be logged in to access this endpoint')

#         # Special handling for root users and 'any' endpoint
#         if request.user.is_superuser and (path == 'any' or method == 'any'):
#             return self.get_response(request)

#         # Check access in EndpointPermission
#         try:
#             endpoint = Endpoint.objects.get(path=path, method=method)
#             permission = EndpointPermission.objects.get(user_profile=request.user.userprofile, endpoint=endpoint)
#             if not permission.can_access:
#                 return HttpResponseForbidden('You do not have access to this endpoint')
#         except (Endpoint.DoesNotExist, EndpointPermission.DoesNotExist):
#             return HttpResponseForbidden('Endpoint not found or access not defined')

#         return self.get_response(request)



















































# from django.http import JsonResponse
# from rest_framework.authtoken.models import Token
# from utils.get_computer_ou import get_computer_ou
# from .models import UserProfile
# from dotenv import load_dotenv
# import os
# from django.http import HttpResponseForbidden
# from django.core.cache import cache
# from django.http import HttpResponseForbidden
# from .models import UserProfile, EndpointPermission






# class EndpointAccessMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Attempt to retrieve user access info from cache
#         user_access_key = f"user_{request.user.id}_access"
#         user_access = cache.get(user_access_key)

#         if user_access is None:
#             user_profile, created = UserProfile.objects.get_or_create(user=request.user)
#             # Use select_related or prefetch_related as necessary here
            
#             # Check general endpoint access
#             if not user_profile.has_endpoint_access(request.path, request.method):
#                 return HttpResponseForbidden('Access denied')
            
#             # If the endpoint has custom access control (e.g., organizational units)
#             if self.has_custom_access_control(request, user_profile):
#                 return HttpResponseForbidden('Access denied')
            
#             # Cache the user's access for next time
#             cache.set(user_access_key, True, timeout=300)  # Adjust timeout as needed

#         response = self.get_response(request)
#         return response

#     def has_custom_access_control(self, request, user_profile):
#         # Implement checks for organizational units or other custom access controls
#         # Example: Check if user's organizational units match the endpoint's requirements
#         # Return True if access should be denied, False otherwise
#         pass






































# class MyPermissions:
    # define access to endpoints - if access is not defined, then no access is given.
        # - sccm/computer/v1-0-1/[{{computername}}]
            # - dast's token only have access to computers under
                # OU=SUS,OU=Institutter,DC=win,DC=dtu,DC=dk
                # OU=BYG,OU=Institutter,DC=win,DC=dtu,DC=dk

        # - azure/graph/security/run-hunting-query
            # this is a endpoint where only GA should have access


        # - active-directory/computer/[{{computername}}]
            # - dast's token only have access to computers under
                # OU=SUS,OU=Institutter,DC=win,DC=dtu,DC=dk
                # OU=BYG,OU=Institutter,DC=win,DC=dtu,DC=dk
        # - active-directory/user/[{{username}}]
            # - dast's token only have access to computers under
                # OU=SUS,OU=Institutter,DC=win,DC=dtu,DC=dk
                # OU=BYG,OU=Institutter,DC=win,DC=dtu,DC=dk

# If an endpoint can be limited to only access relevant groups of computers, users, etc. Then the endpoint can be distrubuted to none GA, users.

# Forexample defender endpoint should allow a user to able to isolate machines that is under his wing.
# Dag should be able to delegate who can login and isolate machines, in his fleet.
# defender/machineactions/isolate/{{computername}}
# defender/machineactions/unisolate/{{computername}}





















# class EndpointAccessMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.
#         response = self.process_view(request, None, None, None)
#         if response is not None:
#             return response

#         response = self.get_response(request)

#         # Code to be executed for each request/response after
#         # the view is called.
        
#         return response

#     def process_view(self, request, view_func, view_args, view_kwargs):
#         # check if endpoint (e.g., '/sccm/computer/v1-0-1/DTU-8CC0140FG8/') starts with '/sccm/'
#         endpoint = request.path
#         if endpoint.startswith('/sccm/'):
#             # If it starts with /sccm/, no need to check the database
#             return None

#         user = request.user

#         # Check if the endpoint exists in the database and if the user has access
#         try:
#             parts = endpoint.strip('/').split('/')
#             app_endpoint = parts[0] if parts else None

#             access = EndpointAccess.objects.get(user=user, endpoint=app_endpoint)
#             if not access.can_access:
#                 return HttpResponseForbidden("You do not have access to this endpoint")

#         except EndpointAccess.DoesNotExist:
#             # Handle case where the endpoint is not in the database
#             # You may want to return a Forbidden response or handle it differently
#             return HttpResponseForbidden("Endpoint not configured")

#         # If no response has been returned yet, continue processing the request
#         return None
