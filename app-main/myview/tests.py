from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .services import generate_custom_api_token


class TestSwaggerView(TestCase):
    """
    This test suite verifies that the Swagger UI endpoint is properly secured by requiring users to be logged in.
    It tests two scenarios:
    1. An unauthenticated request, which should be redirected to the login page.
    2. An authenticated request, which should grant access to the endpoint.
    """
    
    def setUp(self):
        # Set up a test client, create a test user, and determine the URL for the Swagger UI endpoint.
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.url = reverse('schema-swagger-ui')  # Ensure this name matches the actual view name in your URLs configuration.

    def test_requires_login(self):
        """
        Test that accessing the Swagger UI endpoint without being authenticated redirects to the login page.
        This ensures that unauthenticated users cannot access the endpoint directly.
        """
        response = self.client.get(self.url)
        # Check that the response redirects to the login page, with the intended redirect URL as a parameter.
        self.assertRedirects(response, '/login/?next=/my-view/swagger/', fetch_redirect_response=False)

    def test_authenticated_access(self):
        """
        Test that a logged-in user can access the Swagger UI endpoint without being redirected.
        This confirms that authentication is correctly configured to allow access to authenticated users.
        """
        # Log in with the test user credentials.
        self.client.login(username='testuser', password='12345')
        # Make a request to the endpoint as the authenticated user.
        response = self.client.get(self.url)
        # Verify that the response status code is 200 OK, indicating successful access.
        self.assertEqual(response.status_code, 200)




class TestCustomSwaggerView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.url = reverse('custom-swagger-ui')  # replace 'custom_swagger' with the actual name of the view

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Check for redirect (login required)

    def test_authenticated_access(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # Check for successful access




class TestFrontpagePageView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.url = reverse('frontpage')  # replace 'frontpage' with the actual name of the view

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Check for redirect (login required)

    def test_authenticated_access(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # Check for successful access        


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