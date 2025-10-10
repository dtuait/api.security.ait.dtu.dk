from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from rest_framework.authtoken.models import Token
import logging
import re
from urllib.parse import urlparse
import time
from .models import Endpoint, IPLimiter, ADOrganizationalUnitLimiter, APIRequestLog


logger = logging.getLogger(__name__)

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
            '/myview/',
            '/media/',
            '/healthz/',
        ]

        # Always allow the default /admin/ URL so that it can redirect to the
        # configured admin URL without being blocked by access control.
        default_admin_prefix = self._normalize_whitelist_prefix('admin/')
        if default_admin_prefix and default_admin_prefix not in self.whitelist_paths:
            self.whitelist_paths.append(default_admin_prefix)

        # Honour the configured admin URL path.
        custom_admin_prefix = self._normalize_whitelist_prefix(
            getattr(settings, 'ADMIN_URL_PATH', 'admin/')
        )
        if custom_admin_prefix and custom_admin_prefix not in self.whitelist_paths:
            self.whitelist_paths.append(custom_admin_prefix)

        self._extend_whitelist_with_static_paths()
        super().__init__(get_response)

    def normalize_path(self, path):
        """Normalize the request path to ensure consistent matching."""
        # Strip query parameters and ensure trailing slash
        path = path.split('?')[0]
        if not path.endswith('/'):
            path += '/'
        return path

    def _normalize_whitelist_prefix(self, url):
        """Ensure whitelist prefixes start and end with a slash."""
        if not url:
            return None

        parsed = urlparse(url)
        path = parsed.path if parsed.scheme else url

        if not path.startswith('/'):
            path = '/' + path
        if not path.endswith('/'):
            path += '/'

        return path

    def _extend_whitelist_with_static_paths(self):
        """Add STATIC_URL (and similar) prefixes to the whitelist."""
        static_candidates = {
            self._normalize_whitelist_prefix(getattr(settings, 'STATIC_URL', '')),
            self._normalize_whitelist_prefix(getattr(settings, 'STATICFILES_URL', '')),
        }

        for path in filter(None, static_candidates):
            if path not in self.whitelist_paths:
                self.whitelist_paths.append(path)
    
    def compare_paths(self, endpoint_path, request_path):
        """Compare endpoint path with placeholders against the actual request path."""
        # Replace placeholders in endpoint path with regex pattern
        pattern = re.sub(r'\{[^}]*\}', '[^/]+', endpoint_path)

        # Add regex for start and optional trailing slash
        pattern = '^' + pattern + '/?$'

        # Compile the pattern
        compiled_pattern = re.compile(pattern)

        # Check if request path matches the pattern
        match = compiled_pattern.match(request_path) is not None

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Endpoint path '%s' %s request path '%s'",
                endpoint_path,
                'matches' if match else 'does not match',
                request_path,
            )
        
        # if endpoint_path and request_path both stars with /openapi/v1.0/documentation/ then return True
        if endpoint_path.startswith('/openapi/v1.0/documentation/') and request_path.startswith('/openapi/v1.0/documentation/'):
            return True

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
                    from django.contrib.auth.backends import ModelBackend

                    # After getting or creating the user
                    user, created = User.objects.get_or_create(username='vicre')
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
            if request.user.is_authenticated and request.user.username != 'vicre':
                logout(request)

            # Attempt to get or create the 'adm-vicre' user
            try:
                user = User.objects.get(username='vicre')
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
        
        # return list(user_endpoints.prefetch_related('ad_groups').distinct().values_list('path', flat=True))
        return user_endpoints

    
    def is_user_authorized_for_resource(self, endpoint, request):
        if endpoint.no_limit:
            return True  # Access is granted because there is no limitation
        
        # This is ugly. But if the authenticated user is vicre, and the request containes vicre-test01@dtudk.onmicrosoft.com then return True
        if request.user.username == 'vicre' and 'vicre-test01@dtudk.onmicrosoft.com' in request.path:
            return True
        
        # This is ugly. But if the authenticated user is vicre, and the request containes itsecurity@dtu.dk then return True
        if request.user.username == 'vicre' and 'itsecurity@dtu.dk' in request.path:
            return True

        if endpoint.limiter_type is not None:
            content_type = endpoint.limiter_type.content_type
            model_class = content_type.model_class()  # Retrieves the model class based on the content type

            # Retrieve all instances of the model class to see if the user has access through any
            limiters = model_class.objects.all()
            user_groups = request.user.ad_group_members.all()

            # Handle each type of limiter differently
            if model_class == IPLimiter:
                return self.handle_iplimiter(limiters, user_groups, request)
            elif model_class == ADOrganizationalUnitLimiter:
                return self.handle_ado_ou_limiter(limiters, user_groups, request)
            else:
                print(f"No specific handling for {model_class.__name__}")
                return False  # If the limiter type is not recognized, access is denied

        return False  # Deny access if no limiter type is specified

    def handle_iplimiter(self, limiters, user_groups, request):
        for limiter in limiters:
            if limiter.ad_groups.filter(id__in=user_groups).exists():
                logger.debug("Authorised by IPLimiter for request %s", request.path)
                return False  # Grant access if user is part of any related AD group
        return False

    def _should_log_request(self, request):
        path = request.path or ''
        if path.startswith('/static/') or path.startswith('/media/'):
            return False
        if path == '/favicon.ico':
            return False
        return True

    def _log_request(self, request, response, action, duration_ms, token):
        if not self._should_log_request(request):
            return

        try:
            if token and isinstance(token, str):
                token_value = token.split()[-1] if ' ' in token else token
                token_value = token_value[:32]
            else:
                token_value = ''

            if token:
                auth_type = APIRequestLog.AUTH_TYPE_TOKEN
            elif getattr(request.user, 'is_authenticated', False):
                auth_type = APIRequestLog.AUTH_TYPE_SESSION
            else:
                auth_type = APIRequestLog.AUTH_TYPE_ANONYMOUS

            APIRequestLog.objects.create(
                user=request.user if getattr(request.user, 'is_authenticated', False) else None,
                method=request.method,
                path=request.path,
                query_string=request.META.get('QUERY_STRING', ''),
                status_code=getattr(response, 'status_code', None),
                duration_ms=duration_ms,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                auth_type=auth_type,
                auth_token=token_value,
                action=action,
            )
        except Exception:
            logger.warning('Failed to record API request log entry.', exc_info=True)

    def handle_ado_ou_limiter(self, limiters, user_groups, request):
        for limiter in limiters:
            if limiter.ad_groups.filter(id__in=user_groups).exists():
                            
                # Regex to find the user principal name in the URL
                regex = r"([^\/@]+@[^\/]+)"

                # Extract the user principal name from the request path
                match = re.search(regex, request.path)
                user_principal_name = match.group() if match else None

                if user_principal_name is None:
                    return False

                # Get the ADOrganizationalUnitLimiter instances associated with the ADGroupAssociation instances
                ad_organizational_unit_limiters = ADOrganizationalUnitLimiter.objects.filter(ad_groups__in=limiter.ad_groups.all()).distinct()

                for ado_ou_limiter in ad_organizational_unit_limiters:
                    # perform ldap query ado_ou_limiters
                    logger.debug(
                        "Checking AD OU limiter '%s' for principal '%s'",
                        ado_ou_limiter.distinguished_name,
                        user_principal_name,
                    )

                    # base_dn = "DC=win,DC=dtu,DC=dk"
                    base_dn = ado_ou_limiter.distinguished_name
                    search_filter = f"(userPrincipalName={user_principal_name})"                    
                    search_attributes = ['userPrincipalName']
                    from active_directory.services import execute_active_directory_query
                    result = execute_active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

                    if len(result) > 0:
                        # print("User is under the OU")
                        return True

                
                return False
            


        return False


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
        for endpoint in user_endpoints.prefetch_related('ad_groups').distinct():
            if self.compare_paths(endpoint.path, normalized_request_path):
                return True, endpoint

        return False, None  # No matching endpoint found, access denied



    def set_user_ad_groups_cache(self, user):
        from myview.models import ADGroupAssociation
        from django.core.cache import cache
        from django.conf import settings

        # Skip if user.username is 'admin'
        if user.username != 'admin':
            # Define a unique cache key for each user
            cache_key = f"user_ad_groups_{user.id}"

            # Sync user AD groups
            ADGroupAssociation.sync_user_ad_groups(username=user.username)
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
        start_time = time.monotonic()
        normalized_request_path = self.normalize_path(request.path)
        token = request.META.get('HTTP_AUTHORIZATION')
        action = 'init'
        response = None

        logger.debug(
            "AccessControl start path=%s method=%s authenticated=%s token_present=%s",
            request.path,
            request.method,
            getattr(request.user, 'is_authenticated', False),
            bool(token),
        )

        # Periodically refresh AD groups + memberships using cache for performance
        sync_started = time.monotonic()
        sync_attempted = False
        try:
            if getattr(settings, 'AD_GROUP_AUTO_SYNC_ENABLED', False):
                from myview.models import ADGroupAssociation
                block_sync = request.user.is_authenticated or bool(token)
                sync_triggered = ADGroupAssociation.ensure_groups_synced_cached(block=block_sync)
                sync_attempted = True
        except Exception:
            logger.warning('AccessControl AD group sync failed', exc_info=True)
        else:
            if sync_attempted:
                logger.debug(
                    'AccessControl AD group sync %s in %.1fms',
                    'ran inline' if block_sync and sync_triggered else (
                        'scheduled async' if (not block_sync and sync_triggered) else 'skipped (fresh cache)'
                    ),
                    (time.monotonic() - sync_started) * 1000,
                )

        if normalized_request_path == '/favicon.ico/':
            action = 'favicon'
            response = self.get_response(request)
        else:
            # DEBUG mode: Mock authentication for testing without actual credentials
            if settings.DEBUG and not token:
                self.handle_debug_mode(request, normalized_request_path)

            if token and not token.startswith('<token>'):
                if not self.authenticate_by_token(request, token):
                    action = 'invalid_token'
                    response = JsonResponse({'error': 'Invalid API token.'}, status=403)

            is_authorized = False

            if response is None:
                if any(normalized_request_path.startswith(whitelist_path) for whitelist_path in self.whitelist_paths):
                    action = 'whitelist'
                    if request.user.is_authenticated:
                        from myview.middleware import AccessControlMiddleware
                        from django.core.cache import cache

                        cache_key = f"user_ad_groups_{request.user.id}"
                        user_ad_groups = cache.get(cache_key)
                        if user_ad_groups is None:
                            AccessControlMiddleware.set_user_ad_groups_cache(self, request.user)
                    is_authorized = True
                elif request.user.is_authenticated:
                    is_user_authorized_for_endpoint, endpoint = self.is_user_authorized_for_endpoint(request, normalized_request_path)
                    if not is_user_authorized_for_endpoint:
                        action = 'endpoint_forbidden'
                        response = JsonResponse({'message': 'Access denied. You are not authorized to access this endpoint.'}, status=403)
                    else:
                        is_user_authorized_for_resource = self.is_user_authorized_for_resource(endpoint, request)
                        if is_user_authorized_for_endpoint and is_user_authorized_for_resource:
                            action = 'authorized'
                            is_authorized = True
                        else:
                            action = 'resource_forbidden'
                            response = JsonResponse({'message': 'Access denied. You are not authorized to access this ressource.'}, status=403)

            if response is None:
                if is_authorized:
                    response = self.get_response(request)
                else:
                    action = 'redirect_login'
                    response = redirect('/login/')

        duration_ms = (time.monotonic() - start_time) * 1000
        logger.info(
            "AccessControl done path=%s method=%s action=%s status=%s duration_ms=%.1f user=%s token_present=%s",
            request.path,
            request.method,
            action,
            getattr(response, 'status_code', 'unknown'),
            duration_ms,
            getattr(request.user, 'username', 'anonymous'),
            bool(token),
        )

        self._log_request(request, response, action, duration_ms, token)

        return response
