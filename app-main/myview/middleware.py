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

        # if /myview/ is requested, log in as the 'adm-vicre' user
        elif normalized_request_path.startswith('/myview/'):
            # If a user is already logged in but is not 'adm-vicre', log them out
            # if request.user.is_authenticated and request.user.username == 'adm-vicre':
            logout(request)

            # If no user is authenticated, log in as the 'adm-vicre' user
            if not request.user.is_authenticated:


                try:

                    user = User.objects.get(username='adm-vicre')
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)  # Log in as the 'adm-vicre' user

                except User.DoesNotExist:
                    raise Http404("User does not exist")


                
                                

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


    def get_user_authorized_endpoints(self, user_ad_groups):
        """Get endpoints authorized for user's AD groups from the database."""
        from myview.models import Endpoint
        if isinstance(user_ad_groups, list):  # Cached IDs only
            user_endpoints = Endpoint.objects.filter(ad_groups__id__in=user_ad_groups)
        else:  # QuerySet from fresh fetch
            user_endpoints = Endpoint.objects.filter(ad_groups__in=user_ad_groups)
        
        return list(user_endpoints.prefetch_related('ad_groups').distinct().values_list('path', flat=True))



    def is_user_authorized_for_endpoint(self, request, normalized_request_path):
        """Check if the user has access to the requested endpoint."""

        from django.core.cache import cache
        from django.conf import settings
        # Allow access to superuser
        if request.user.is_superuser:
            return True

        # Normalize the incoming request path
        normalized_request_path = self.normalize_path(request.path)

        # Define a unique cache key for each user
        cache_key = f"user_ad_groups_{request.user.id}"

        # Try to get cached data
        user_ad_groups = cache.get(cache_key)
        if user_ad_groups is None:
            # No cache found, sync and set the cache
            self.set_user_ad_groups_cache(request.user)
            user_ad_groups = request.user.ad_group_members.all()

        # Get user authorized endpoints from cache or query
        user_endpoints = self.get_user_authorized_endpoints(user_ad_groups)

        # Check if user is authorized with cached data
        for endpoint_path in user_endpoints:
            if self.compare_paths(endpoint_path, normalized_request_path):
                return True

        return False  # No matching endpoint found, access denied



    def set_user_ad_groups_cache(user):
        from myview.models import ADGroupAssociation
        from django.core.cache import cache
        from django.conf import settings

        # Skip if user.username is 'admin'
        if user.username != 'admin':
            # Define a unique cache key for each user
            cache_key = f"user_ad_groups_{user.id}"

            # Sync user AD groups
            ADGroupAssociation.sync_user_ad_groups(user.username)
            user_ad_groups = user.ad_group_members.all()

            # Cache for a specified time using AD_GROUP_CACHE_TIMEOUT from settings
            cache.set(cache_key, list(user_ad_groups.values_list('id', flat=True)), timeout=settings.AD_GROUP_CACHE_TIMEOUT)



    def is_user_authorized(self, user, normalized_request_path):
        """Check if the user is authorized for the endpoint."""
        ad_groups = user.ad_group_members.all()
        endpoints = Endpoint.objects.filter(ad_groups__in=ad_groups)
        for endpoint in endpoints:
            endpoint_path = self.normalize_path(endpoint.path)
            if self.compare_paths(endpoint_path, normalized_request_path):
                return True  # Access is granted
        return False
    

 








































    def __call__(self, request):
        # Normalize request path for consistent handling
        normalized_request_path = self.normalize_path(request.path)
        token = request.META.get('HTTP_AUTHORIZATION')

        # Directly proceed with favicon requests
        if normalized_request_path == '/favicon.ico/':
            return self.get_response(request)


        # DEBUG mode: Mock authentication for testing without actual credentials
        if settings.DEBUG and not token:
            self.handle_debug_mode(request, normalized_request_path)    
            # return self.get_response(request)

        # Authenticate user based on token, if provided
        if token and not token.startswith('Token <token>'):
            if not self.authenticate_by_token(request, token):
                return HttpResponseForbidden('Invalid token.')



        # Initialize a flag to indicate whether the user is authorized
        is_authorized = False

        # Handle whitelist paths to bypass access control
        if any(normalized_request_path.startswith(whitelist_path) for whitelist_path in self.whitelist_paths):

            # If the user is authenticated, update the cache
            if request.user.is_authenticated:
                from myview.middleware import AccessControlMiddleware
                from django.core.cache import cache

                # Define a unique cache key for each user
                cache_key = f"user_ad_groups_{request.user.id}"

                # Try to get cached data
                user_ad_groups = cache.get(cache_key)
                if user_ad_groups is None:
                    # No cache found, sync and set the cache
                    AccessControlMiddleware.set_user_ad_groups_cache(request.user)

            is_authorized = True
        elif request.user.is_authenticated:
            # Check for endpoint access
            if self.is_user_authorized_for_endpoint(request, normalized_request_path):
                is_authorized = True
            else:
                return HttpResponseForbidden('Access denied.')

        if is_authorized:
            return self.get_response(request)
        else:
            # For unauthenticated users, redirect to login
            return redirect('/login/')


