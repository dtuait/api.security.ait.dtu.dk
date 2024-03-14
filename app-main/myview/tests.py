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
    























from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile, Endpoint, AccessRequest, EndpointPermission, AccessRequestStatus
from django.utils import timezone

class EndpointAccessTests(TestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'user1password')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'user2password')
        
        # Create user profiles
        self.user_profile1 = UserProfile.objects.create(user=self.user1)
        self.user_profile2 = UserProfile.objects.create(user=self.user2)
        
        # Create endpoints
        self.endpoint1 = Endpoint.objects.create(path='/playbook/my-mfa-rejected-by-user/render-html', method='post')
        self.endpoint2 = Endpoint.objects.create(path='/active_directory/computer/v1-0-0/inactive-computers', method='get')
        # Add more endpoints as needed
        
        # Grant access to user1 for endpoint1
        self.access_request1 = AccessRequest.objects.create(user_profile=self.user_profile1, endpoint=self.endpoint1, status=AccessRequestStatus.GRANTED, request_date=timezone.now())
        
        # Grant access to user2 for endpoint2
        self.access_request2 = AccessRequest.objects.create(user_profile=self.user_profile2, endpoint=self.endpoint2, status=AccessRequestStatus.GRANTED, request_date=timezone.now())

    def test_user_access(self):
        # Test user1 has access to endpoint1
        self.assertTrue(self.user_profile1.has_endpoint_access(self.endpoint1.path, self.endpoint1.method))
        
        # Test user1 does not have access to endpoint2
        self.assertFalse(self.user_profile1.has_endpoint_access(self.endpoint2.path, self.endpoint2.method))
        
        # Test user2 has access to endpoint2
        self.assertTrue(self.user_profile2.has_endpoint_access(self.endpoint2.path, self.endpoint2.method))
        
        # Test user2 does not have access to endpoint1
        self.assertFalse(self.user_profile2.has_endpoint_access(self.endpoint1.path, self.endpoint1.method))

        # Add more tests as needed for additional endpoints and conditions






























# from django.test import TestCase, RequestFactory
# from django.http import HttpResponseForbidden
# from django.contrib.auth.models import User
# from myview.middleware import AccessControlMiddleware
# from myview.models import Endpoint, EndpointPermission, UserProfile
# from django.test.utils import override_settings
# from unittest.mock import MagicMock

# @override_settings(
#     MIDDLEWARE=['myview.middleware.AccessControlMiddleware',]
# )
# class AccessControlMiddlewareTest(TestCase):

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.middleware = AccessControlMiddleware(get_response=MagicMock(name="get_response"))
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.superuser = User.objects.create_superuser(username='superuser', password='12345')
#         self.endpoint = Endpoint.objects.create(path='/test_endpoint', method='get')
#         self.user_profile = UserProfile.objects.create(user=self.user)
#         EndpointPermission.objects.create(user_profile=self.user_profile, endpoint=self.endpoint, can_access=True)

#     def test_authenticated_access(self):
#         request = self.factory.get('/test_endpoint')
#         request.user = self.user
#         response = self.middleware(request)
#         self.assertNotEqual(response.status_code, 403, 'Authenticated user should have access')

#     def test_unauthenticated_access(self):
#         request = self.factory.get('/test_endpoint')
#         request.user = MagicMock(is_authenticated=False)
#         response = self.middleware(request)
#         self.assertEqual(response.status_code, 403, 'Unauthenticated user should not have access')

#     def test_superuser_access(self):
#         request = self.factory.get('/any')
#         request.user = self.superuser
#         response = self.middleware(request)
#         self.assertNotEqual(response.status_code, 403, 'Superuser should have access to any endpoint')

    # def test_excluded_path_access(self):
    #     request = self.factory.get('/admin')
    #     request.user = MagicMock(is_authenticated=True)
    #     response = self.middleware(request)
    #     self.assertNotIsInstance(response, HttpResponseForbidden, 'Access to excluded path should not be forbidden')

    # def test_no_permission_access(self):
    #     EndpointPermission.objects.filter(user_profile=self.user_profile, endpoint=self.endpoint).update(can_access=False)
    #     request = self.factory.get('/test_endpoint')
    #     request.user = self.user
    #     response = self.middleware(request)
    #     self.assertEqual(response.status_code, 403, 'User without permission should not have access')

    # def tearDown(self):
    #     User.objects.all().delete()
    #     Endpoint.objects.all().delete()
    #     EndpointPermission.objects.all().delete()