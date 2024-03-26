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
        path = request.path

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
        if token:
            try:
                request.user = Token.objects.get(key=token).user
            except ObjectDoesNotExist:
                logger = logging.getLogger(__name__)
                logger.info(f'Invalid token access attempt. Path: {path}, Token: {token[:10]}')
                return HttpResponseForbidden('Invalid token.')

        if request.user.is_authenticated:
            return self.get_response(request)

        return HttpResponseRedirect('/login/')

