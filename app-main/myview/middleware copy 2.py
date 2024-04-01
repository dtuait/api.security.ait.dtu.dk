from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin
from .models import Endpoint
from rest_framework.authentication import SessionAuthentication, TokenAuthentication




from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from django.utils.deprecation import MiddlewareMixin
import re
from django.core.exceptions import ObjectDoesNotExist
import logging
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model, login
from django.conf import settings
from django.http import Http404


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
        self.whitelist_paths = [
            '/favicon.ico',
            '/login/', 
            '/logout/',
            '/auth/callback/',
        ]
        super().__init__(get_response)

    def normalize_path(self, path):
        """Normalize the request path to ensure consistent matching."""
        # Strip query parameters
        path = path.split('?')[0]
        # Ensure a consistent use of trailing slash
        if not path.endswith('/'):
            path += '/'
        return path
    
    def __call__(self, request):
        # Normalize the request path
        normalized_path = self.normalize_path(request.path)
        token = request.META.get('HTTP_AUTHORIZATION')

        if normalized_path == '/favicon.ico/':
            return self.get_response(request)


        # Check for DEBUG mode to bypass regular authentication
        if settings.DEBUG and not token:
            User = get_user_model()  # Get the user model


            # This is too prevent starting a new session, which deletes session variables.
            if normalized_path.startswith('/myview/ajax'):
                return self.get_response(request)

            
            # Check if the user is already authenticated and bypass login logic if so
            #if request.user.is_authenticated and normalized_path != '/admin/login/':
             #   return self.get_response(request)
            
            # Specific logic for admin login page
            if normalized_path.startswith('/admin'):
                
                if request.user.is_authenticated and request.user.username != 'admin':
                    logout(request)

                if not request.user.is_authenticated:

                    try:
                        admin_user = User.objects.get(username='admin')
                    except User.DoesNotExist:
                        raise Http404("Admin user does not exist")
                    
                    admin_user.backend = 'django.contrib.auth.backends.ModelBackend'  # Specify the backend
                    login(request, admin_user)

                
                response = self.get_response(request)

                return response
        

            # # Specific logic for admin login page
            # if normalized_path.startswith('/admin'):
            #     admin_user, _ = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True})
            #     # Assuming 'admin' user exists with necessary permissions
            #     admin_user.backend = 'django.contrib.auth.backends.ModelBackend'  # Specify the backend
            #     login(request, admin_user)  # Log in as admin user
            #     return redirect('/admin/')  # Redirect to the admin index page to avoid loop
            
            # For other paths, mock or create the user "adm-vicre"
            else:
                if request.user.is_authenticated and request.user.username != 'adm-vicre':
                    logout(request)
                try:
                    user = User.objects.get(username='adm-vicre')
                except User.DoesNotExist:
                    raise Http404("User does not exist")
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)  # Set the mocked user as the authenticated user on the request
                return self.get_response(request)  # Proceed with the request



        # # Check if the request path is in the whitelist
        # if any(re.match("^" + re.escape(whitelist_path), normalized_path) for whitelist_path in self.whitelist_paths):
        #     return self.get_response(request)
        # Initialize a variable to track if the path is in the whitelist
        path_is_whitelisted = False

        # Iterate through each path in the whitelist
        for whitelist_path in self.whitelist_paths:
            # Use re.match to see if the start of the normalized path matches the whitelist path
            # re.escape is used to escape any special characters in whitelist_path so they are treated as literals
            if re.match("^" + re.escape(whitelist_path), normalized_path):
                # If a match is found, set path_is_whitelisted to True and break out of the loop
                path_is_whitelisted = True
                break  # We found a match, no need to check further paths

        # After checking all paths, if the path is in the whitelist
        if path_is_whitelisted:
            # Allow the request to proceed to the view
            return self.get_response(request)
        

        # Token authentication
        if token:
            try:
                # Attempt to retrieve user by token
                user = Token.objects.get(key=token).user
                request.user = user
            except ObjectDoesNotExist:
                if token != 'Token <token>':
                    logger = logging.getLogger(__name__)
                    logger.info(f'Invalid token access attempt. Path: {request.path}, Token: {token[:10]}')
                    return HttpResponseForbidden('Invalid token.')

        # Proceed with the request if the user is authenticated (either by token or session)
        if request.user.is_authenticated:
            try:
                # Retrieve the endpoint object based on the path and method. 
                # Adjust 'normalized_path' and 'request.method' as necessary based on your routing.
                # endpoint = Endpoint.objects.get(path=normalized_path, method=request.method.upper())
                endpoints = Endpoint.objects.all()
                # foreach print endpoint
                for endpoint in endpoints:
                    print(endpoint)
                    print(f'requested path: {request.method.lower()} {normalized_path}')
                    print(f'testing path: {endpoint.path}')
                    # >> get /active-directory/query
                    # >> get /graph/get-user/{user}
                    # >> get /graph/list/{user_id__or__user_principalname}/authentication-methods
                    # >> delete /graph/users/{user_id__or__user_principalname}/authentication-methods/{microsoft_authenticator_method_id}
                    # print(f'{request.method.lower()} {normalized_path}') >> /v1.0/graph/get-user/vicre@dtu.dk/ get /v1.0/graph/get-user/vicre@dtu.dk/
                    # HOW DO I COMPARE THEM TO SEE IF THEY MATCH?

                # Check if the user is a member of any AD group that has access to this endpoint.
                # This checks across all AD groups the user belongs to if any of them are linked to the endpoint.
                # user_ad_groups = request.user.ad_groups.all()
                # if not endpoint.ad_groups.filter(pk__in=user_ad_groups).exists():
                #     # User is authenticated but not authorized to access the endpoint
                #     return HttpResponseForbidden("You do not have access to this endpoint.")
            
            except Endpoint.DoesNotExist:
                # If the endpoint is not found, it may be a public endpoint or an error in endpoint configuration.
                # Decide on how to handle such cases. For example, you can allow the request to proceed,
                # log a warning, or block access as a security measure.
                pass

            # Continue with the request processing if access is granted
            response = self.get_response(request)
            return response
        else:
            return redirect('/login/')
