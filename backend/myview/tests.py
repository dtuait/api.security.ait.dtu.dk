from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model




##################MIDDLEWARE##################
##################MIDDLEWARE##################
##################MIDDLEWARE##################
# class AccessControlTests(TestCase):
#     def setUp(self):
#         # Setup for the test
#         self.client = Client()
#         self.user = get_user_model().objects.create_user(username='user', password='password')

#     def test_redirect_unauthenticated_user(self):
#         # List of paths to test that are not in the whitelist
#         test_paths = [
#             '/protected/', 
#             '/some_path/',
#             '/another_path/'
#         ]

#         # Test unauthenticated access to non-whitelisted paths
#         for path in test_paths:
#             response = self.client.get(path)
#             self.assertRedirects(response, '/login/', status_code=302, target_status_code=200)

#     def test_access_whitelisted_paths(self):
#         # Whitelisted paths from the middleware
#         whitelist_paths = [
#             '/favicon.ico/', 
#             '/login/', 
#             '/logout/', 
#             '/auth/callback/', 
#             '/admin/', 
#             '/myview/'
#         ]

#         # Test access to whitelisted paths for unauthenticated users
#         for path in whitelist_paths:
#             response = self.client.get(path)
#             # Expected status code might vary if the route does not actually exist in your urls
#             self.assertIn(response.status_code, [200, 302])

#     def test_authenticated_access_to_protected_path(self):
#         # Authenticate the user
#         self.client.login(username='user', password='password')

#         # Path that requires authentication
#         path = '/protected/'
#         response = self.client.get(path)

#         # Assert that access is granted (status code 200)
#         self.assertEqual(response.status_code, 200)
##################MIDDLEWARE##################
##################MIDDLEWARE##################
##################MIDDLEWARE##################













































##################ADMIN PANEL (AJAX View)##################
##################ADMIN PANEL (AJAX View)##################
##################ADMIN PANEL (AJAX View)##################

##################ADMIN PANEL (AJAX View)##################
##################ADMIN PANEL (AJAX View)##################
##################ADMIN PANEL (AJAX View)##################
