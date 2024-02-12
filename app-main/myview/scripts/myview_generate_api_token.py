from django.http import JsonResponse
from app_mod.models import CustomToken
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

def generate_custom_api_token(request=None, username=""):
    try:
        # Retrieve the user based on the username
        user = User.objects.get(username=username)

        # Check if the token already exists for the user and delete it
        existing_token = CustomToken.objects.filter(user=user)
        if existing_token.exists():
            existing_token.delete()

        # Create a new token for the user
        token = CustomToken.objects.create(user=user)

        # Return the token key directly for scripting purpose
        return token.key

    except ObjectDoesNotExist:
        # Handle the case where the user does not exist
        print('User not found')
        return None

    except Exception as e:
        # Handle any other exceptions
        print(f'Error: {str(e)}')
        return None

def run():
    # Test generate_custom_api_token for a user named 'vicre'
    custom_api_token = generate_custom_api_token(username='vicre')
    if custom_api_token:
        print(f"Generated Token: {custom_api_token}")
    else:
        print("No token generated.")

# if main 
if __name__ == "__main__":
    run()

    