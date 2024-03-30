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

        if normalized_path == '/favicon.ico/':
            return self.get_response(request)


        # Check for DEBUG mode to bypass regular authentication
        if settings.DEBUG:
            User = get_user_model()  # Get the user model

            # if request.user.is_authenticated logout user

            
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
        token = request.META.get('HTTP_AUTHORIZATION')
        user_token_is_valid = False
        user_temporarily_authenticated = False
        if token:
            try:
                # Attempt to retrieve user by token
                user = Token.objects.get(key=token).user
                # Temporarily set user to request
                request.user = user
                user_temporarily_authenticated = True
            except ObjectDoesNotExist:
                if token != 'Token <token>':
                    logger = logging.getLogger(__name__)
                    logger.info(f'Invalid token access attempt. Path: {request.path}, Token: {token[:10]}')
                    return HttpResponseForbidden('Invalid token.')

        # Proceed with the request if the user is authenticated (either by token or session)
        if request.user.is_authenticated:
            response = self.get_response(request)
            # If the user was temporarily authenticated for this request, consider revoking here
            if user_temporarily_authenticated:
                # Perform any necessary cleanup, e.g., logging out the user from the request
                # Note: This is symbolic as the request lifecycle ends here
                logout(request)
            return response
        else:
            return redirect('/login/')
