from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .services import generate_custom_api_token
from django.urls import get_resolver
from rest_framework.test import APIClient
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_302_FOUND
# class TestSwaggerView(TestCase):
#     """
#     This test suite verifies that the Swagger UI endpoint is properly secured by requiring users to be logged in.
#     It tests two scenarios:
#     1. An unauthenticated request, which should be redirected to the login page.
#     2. An authenticated request, which should grant access to the endpoint.
#     """
    
#     def setUp(self):
#         # Set up a test client, create a test user, and determine the URL for the Swagger UI endpoint.
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.url = reverse('schema-swagger-ui')  # Ensure this name matches the actual view name in your URLs configuration.

#     def test_requires_login(self):
#         """
#         Test that accessing the Swagger UI endpoint without being authenticated redirects to the login page.
#         This ensures that unauthenticated users cannot access the endpoint directly.
#         """
#         response = self.client.get(self.url)
#         # Check that the response redirects to the login page, with the intended redirect URL as a parameter.
#         self.assertRedirects(response, '/login/?next=/my-view/swagger/', fetch_redirect_response=False)

#     def test_authenticated_access(self):
#         """
#         Test that a logged-in user can access the Swagger UI endpoint without being redirected.
#         This confirms that authentication is correctly configured to allow access to authenticated users.
#         """
#         # Log in with the test user credentials.
#         self.client.login(username='testuser', password='12345')
#         # Make a request to the endpoint as the authenticated user.
#         response = self.client.get(self.url)
#         # Verify that the response status code is 200 OK, indicating successful access.
#         self.assertEqual(response.status_code, 200)




# class TestCustomSwaggerView(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.url = reverse('custom-swagger-ui')  # replace 'custom_swagger' with the actual name of the view

#     def test_requires_login(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)  # Check for redirect (login required)

#     def test_authenticated_access(self):
#         self.client.login(username='testuser', password='12345')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)  # Check for successful access




# class TestFrontpagePageView(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.url = reverse('frontpage')  # replace 'frontpage' with the actual name of the view

#     def test_requires_login(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)  # Check for redirect (login required)

#     def test_authenticated_access(self):
#         self.client.login(username='testuser', password='12345')
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)  # Check for successful access        

# CIRKER IKKE 
# class TestTokenViews(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(username='testuser', password='12345')
#         self.client.force_authenticate(user=self.user)
#         self.generate_token_url = reverse('generate_api_token')  # replace with the actual name of the view
#         self.regenerate_token_url = reverse('regenerate_api_token')  # replace with the actual name of the view

#     def test_generate_api_token(self):
#         response = self.client.post(self.generate_token_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue('token' in response.json())

#     def test_regenerate_api_token(self):
#         # First, generate a token
        
#         generate_custom_api_token(request=None, username=self.user.username)
#         response = self.client.post(self.regenerate_token_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue('token' in response.json())
        


# class AuthenticationRequiredTestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()

#     def display_all_urls(self, url_patterns, prefix=''):
#         """Display all URLs and their names."""
#         for url_pattern in url_patterns:
#             if hasattr(url_pattern, 'url_patterns'):
#                 # This is an included URLconf, iterate over its URL patterns
#                 yield from self.display_all_urls(url_pattern.url_patterns, prefix + str(url_pattern.pattern))
#             else:
#                 # This is a URL pattern
#                 yield prefix + str(url_pattern.pattern), url_pattern.name

#     def test_endpoints_require_authentication(self):
#         urlconf = get_resolver(None)
#         all_url_patterns = urlconf.url_patterns  # get all URL patterns

#         for pattern, name in self.display_all_urls(all_url_patterns):
#             print(pattern, name)


# class AuthenticationRequiredTestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()

#     def test_endpoints_require_authentication(self):
#         urlconf = get_resolver(None)
#         all_url_patterns = urlconf.url_patterns  # get all URL patterns

#         # Create a list
#         ignore_these_endpoints = ['','admin/',"login/","logout/"]

#         for url_pattern1 in all_url_patterns:
#             # if url_pattern.pattern is in ignore_these_endpoints: then continue
#             if str(url_pattern1.pattern) in ignore_these_endpoints:
#                 continue

#             for url_pattern2 in url_pattern1.url_patterns:

#                 ignore_these_endpoints2 = ['']
#                 if str(url_pattern2.pattern) in ignore_these_endpoints2:
#                     continue
#                 print(url_pattern1.pattern, end="")
#                 print(url_pattern2.pattern)





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
        url = url_pattern.replace('<str:computer_name>/', 'example/')
        url = url.replace('<int:id>/', '1/')
        # Add more replacements here as needed
        # Ensure the resulting URL is valid for a GET request; you might need to add a base path
        return "" + url  # Assuming all URLs are under '/api/', adjust if your application is different

# Note: This script assumes your API is prefixed with '/api/'. Adjust the `replace_dynamic_url_parts` method as necessary.