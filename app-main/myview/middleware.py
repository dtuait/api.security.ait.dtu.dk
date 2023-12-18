from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from utils.get_computer_ou import get_computer_ou
from .models import UserProfile
from dotenv import load_dotenv
import os
from django.http import HttpResponseForbidden
from .models import EndpointAccess



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



class OUAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply this middleware for the specified endpoint.
        if request.path.startswith('/sccm/computer/v1-0-1/') and request.method == "GET":
            # Extract computer_name from the path and token from the headers.
            computer_name = request.path.split('/')[-1]
            token = request.headers.get('Authorization', '').replace('Token ', '')

            # Check if computer is under a permitted OU.
            if not self._is_computer_in_permitted_ou(token, computer_name):
                return JsonResponse({"error": "Unauthorized access"}, status=403)

        return self.get_response(request)

    def _is_computer_in_permitted_ou(self, token, computer_name):
            
            dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
            load_dotenv(dotenv_path)

            ad_username = os.getenv("ACTIVE_DIRECTORY_USERNAME")
            ad_password = os.getenv("ACTIVE_DIRECTORY_PASSWORD")
            ad_server = os.getenv("ACTIVE_DIRECTORY_SERVER")
            
            # Connect to AD and get the OU of the computer
            computer_ou = get_computer_ou(computer_name, ad_server, ad_username, ad_password)

            if not computer_ou:
                return False  # Can't find the computer in AD or there was an error.

            try:
                # Get the user associated with the token
                user_token = Token.objects.get(key=token)
                user_profile = UserProfile.objects.get(user=user_token.user)

                # Check if the computer's OU is in the user's permitted OUs
                permitted_ous = user_profile.ous.all()
                for ou in permitted_ous:
                    if computer_ou.endswith(ou.name):
                        return True
                    
            except (Token.DoesNotExist, UserProfile.DoesNotExist):
                return False  # Token or User not found

            return False




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
