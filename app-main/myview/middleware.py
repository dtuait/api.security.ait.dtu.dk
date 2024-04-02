from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponseRedirect, HttpResponseServerError, Http404
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, get_authorization_header
import logging
import re
from .models import Endpoint

def get_client_ip(request):
    """Utility function to extract client's IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class AccessControlMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths that do not require access control
        self.whitelist_paths = [
            '/favicon.ico',
            '/login/', 
            '/logout/',
            '/auth/callback/',
            '/admin/',
            '/myview/'
        ]
        super().__init__(get_response)

    def normalize_path(self, path):
        """Normalize the request path to ensure consistent matching."""
        # Strip query parameters and ensure trailing slash
        path = path.split('?')[0]
        if not path.endswith('/'):
            path += '/'
        return path
    
    def compare_paths(self, endpoint_path, request_path):
        """Compare endpoint path with placeholders against the actual request path."""
        print(f"Original endpoint path: {endpoint_path}")
        print(f"Original request path: {request_path}")
        
        # Replace placeholders in endpoint path with regex pattern
        pattern = re.sub(r'\{[^}]*\}', '[^/]+', endpoint_path)
        print(f"Pattern after placeholder replacement: {pattern}")
        
        # Add regex for start and optional trailing slash
        pattern = '^' + pattern + '/?$'
        print(f"Final regex pattern: {pattern}")
        
        # Compile the pattern
        compiled_pattern = re.compile(pattern)
        
        # Check if request path matches the pattern
        match = compiled_pattern.match(request_path) is not None
        print(f"Does the request path match the pattern? {'Yes' if match else 'No'}")
        
        return match


    def __call__(self, request):
        # Normalize request path for consistent handling
        normalized_request_path = self.normalize_path(request.path)
        token = request.META.get('HTTP_AUTHORIZATION')

        # Directly proceed with favicon requests
        if normalized_request_path == '/favicon.ico/':
            return self.get_response(request)

        # Handle whitelist paths to bypass access control
        if any(normalized_request_path.startswith(whitelist_path) for whitelist_path in self.whitelist_paths):

            # If debug is true, skip /admin, because it needs special handling
            if settings.DEBUG and normalized_request_path.startswith('/admin'):
                pass
            else:
                return self.get_response(request)

        # DEBUG mode: Mock authentication for testing without actual credentials
        if settings.DEBUG and not token:
            self.handle_debug_mode(request, normalized_request_path)
            return self.get_response(request)

        # Authenticate user based on token, if provided
        if token and not token.startswith('Token <token>'):
            if not self.authenticate_by_token(request, token):
                return HttpResponseForbidden('Invalid token.')


        # check for enpoint access
        if request.user.is_authenticated:

            # Check if the user has access to the requested endpoint

            if not self.authorize_request(request, normalized_request_path):
                return HttpResponseForbidden('You do not have access to this endpoint.')      
                
            # limit the user only access to ressouces 

            # Check if the user has access to the requested resource
            return self.get_response(request)

        # For unauthenticated users, redirect to login
        return redirect('/login/')

































            return self.get_response(request)

        # For unauthenticated users, redirect to login
        return redirect('/login/')

































    def handle_debug_mode(self, request, normalized_request_path):
        """Handles user authentication in DEBUG mode without actual credentials."""
        # Use Django's get_user_model to support custom user models
        User = get_user_model()

        # Prevent starting a new session for AJAX calls in '/myview/ajax', 
        # which could delete session variables.
        if normalized_request_path.startswith('/myview/ajax'):
            return  # Just return, let the main __call__ method continue execution

        # Logic for handling admin login page access
        if normalized_request_path.startswith('/admin'):
            # If a user is already logged in but is not the admin, log them out
            if request.user.is_authenticated and request.user.username != 'admin':
                logout(request)

            # If no user is authenticated, log in as the admin user
            if not request.user.is_authenticated:
                try:
                    admin_user = User.objects.get(username='admin')
                except User.DoesNotExist:
                    raise Http404("Admin user does not exist")

                admin_user.backend = 'django.contrib.auth.backends.ModelBackend'  # Specify the backend
                login(request, admin_user)  # Log in as admin user

            # After handling admin access, let the main __call__ method continue execution
            return




        # For other paths in debug mode, you might want to mock or auto-login a default user
        # This example auto-logs in a user named 'adm-vicre', similar to your other logic
        else:
            # Log out the current user if they are not 'adm-vicre'
            if request.user.is_authenticated and request.user.username != 'adm-vicre':
                logout(request)

            # Attempt to get or create the 'adm-vicre' user
            try:
                user = User.objects.get(username='adm-vicre')
            except User.DoesNotExist:
                raise Http404("User does not exist")

            # Set the backend and log in the 'adm-vicre' user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)  # Set the mocked user as the authenticated user on the request

    def authenticate_by_token(self, request, token):
        """Authenticate user based on provided token."""
        try:
            user = Token.objects.get(key=token).user
            request.user = user
            return True
        except ObjectDoesNotExist:
            logger = logging.getLogger(__name__)
            logger.info(f'Invalid token access attempt. Path: {request.path}, Token: {token[:10]}')
            return False

    def authorize_request(self, request, normalized_request_path):
        """Check if the user has access to the requested endpoint."""


        # allow access to superuser
        if request.user.is_superuser:
            return True

        # Validate access to mortal users

        ad_groups = request.user.ad_groups.all()
        endpoints = Endpoint.objects.filter(ad_groups__in=ad_groups)
        for endpoint in endpoints:
            endpoint_path = self.normalize_path(endpoint.path)
            if self.compare_paths(endpoint_path, normalized_request_path):
                return True  # Access is granted
        return False  # No matching endpoint found, access denied
