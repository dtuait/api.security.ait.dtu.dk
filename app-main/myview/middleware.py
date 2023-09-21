from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from utils.get_computer_ou import get_computer_ou
from .models import UserProfile
from dotenv import load_dotenv
import os




class OUAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply this middleware for the specified endpoint.
        if request.path.startswith('/sccm/computer/v1-0-0/') and request.method == "GET":
            # Extract computer_name from the path and token from the headers.
            computer_name = request.path.split('/')[-2]
            token = request.headers.get('Authorization', '').replace('Token ', '')

            # Check if computer is under a permitted OU.
            if not self.is_computer_in_permitted_ou(token, computer_name):
                return JsonResponse({"error": "Unauthorized access"}, status=403)

        return self.get_response(request)

    def is_computer_in_permitted_ou(self, token, computer_name):
            
            dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
            load_dotenv(dotenv_path)

            ad_username = os.getenv("ACTIVE_DIRECTORY_USERNAME")
            ad_password = os.getenv("ACTIVE_DIRECTORY_PASSWORD")
            ad_server = os.getenv("ACTIVE_DIRECTORY_SERVER")
            
            # Connect to AD and get the OU of the computer
            computer_ou = get_computer_ou(computer_name, ad_server, ad_username, ad_password)

            if not computer_ou:
                return False  # Can't find the computer in AD or there was an error.

            try:
                # Get the user associated with the token
                user_token = Token.objects.get(key=token)
                user_profile = UserProfile.objects.get(user=user_token.user)

                # Check if the computer's OU is in the user's permitted OUs
                permitted_ous = user_profile.ous.all()
                for ou in permitted_ous:
                    if computer_ou.endswith(ou.name):
                        return True
                    
            except (Token.DoesNotExist, UserProfile.DoesNotExist):
                return False  # Token or User not found

            return False
