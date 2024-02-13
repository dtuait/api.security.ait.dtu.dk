from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .services import generate_custom_api_token
from django.urls import get_resolver
from rest_framework.test import APIClient
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_302_FOUND


# This script checks if all endpoints in your Django REST API require authentication.
# Including /
class AuthenticationRequiredTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_endpoints_require_authentication(self):
        urlconf = get_resolver(None)
        all_url_patterns = urlconf.url_patterns  # get all URL patterns

        # List of endpoints to ignore
        ignore_these_endpoints = ['', 'admin/', "login/", "logout/"]

        for url_pattern1 in all_url_patterns:
            if str(url_pattern1.pattern) in ignore_these_endpoints:
                continue

            if hasattr(url_pattern1, 'url_patterns'):  # Check if this pattern is an include
                for url_pattern2 in url_pattern1.url_patterns:
                    if str(url_pattern2.pattern) in ignore_these_endpoints:
                        continue
                    full_url_pattern = f"{url_pattern1.pattern}{url_pattern2.pattern}"
                    self.check_url_requires_auth(full_url_pattern)
            else:
                self.check_url_requires_auth(str(url_pattern1.pattern))

    def check_url_requires_auth(self, url_pattern):
        # Replace dynamic URL parts with example values
        url = self.replace_dynamic_url_parts(url_pattern)
        response = self.client.get("http://localhost:6081/" + url, format='json')
        
        if response.status_code == HTTP_302_FOUND:
            # check if the rederited url requires authentication
            self.assertIn('/login/', response.url)
        else:
            # Assert that authentication is required
            self.assertIn(response.status_code, [HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN], msg=f"URL {url} does not require authentication")


    def replace_dynamic_url_parts(self, url_pattern):
        # Replace dynamic segments in the URL pattern with example values

        # For each dynamic endpoint you should create a unittest here.

        url = url_pattern.replace('<str:computer_name>/', 'example/')
        url = url.replace('<int:id>/', '1/')
        # Add more replacements here as needed
        # Ensure the resulting URL is valid for a GET request; you might need to add a base path
        return "" + url  # Assuming all URLs are under '/api/', adjust if your application is different

# Note: This script assumes your API is prefixed with '/api/'. Adjust the `replace_dynamic_url_parts` method as necessary.