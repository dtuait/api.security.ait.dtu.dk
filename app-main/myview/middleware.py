from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from .models import EndpointPermission, Endpoint

class AccessControlMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize the list of paths to exclude from checks
        self.excluded_paths = [
            '/admin',  # Exclude all Django admin paths
            '/accounts/login/',  # Exclude login page
            # Add any other paths you want to exclude
            '/myview',
            '/login/',
            # '/myview/swagger/',
        ]
        super().__init__(get_response)

    def __call__(self, request):
        path = request.path
        method = request.method.lower()

        # Check if the path is in the excluded paths
        if any(path.startswith(excluded_path) for excluded_path in self.excluded_paths):
            return self.get_response(request)

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return HttpResponseForbidden('You must be logged in to access this endpoint')

        # Special handling for root users and 'any' endpoint
        if request.user.is_superuser:
            return self.get_response(request)
        
        
        # Check access in EndpointPermission
        try:
            endpoint = Endpoint.objects.get(path=path, method=method)
            permission = EndpointPermission.objects.get(user_profile=request.user.userprofile, endpoint=endpoint)
            if not permission.can_access:
                return HttpResponseForbidden('You do not have access to this endpoint')
        except (Endpoint.DoesNotExist, EndpointPermission.DoesNotExist):
            return HttpResponseForbidden('Endpoint not found or access not defined')

        return self.get_response(request)















































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
