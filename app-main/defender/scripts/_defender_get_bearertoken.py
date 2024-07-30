from dotenv import load_dotenv, set_key
import requests
import time
import os


def update_env_file(env_path, key, new_value):
    # Read the existing content
    with open(env_path, 'r') as file:
        lines = file.readlines()

    # Update the specific key with new value
    with open(env_path, 'w') as file:
        for line in lines:
            if line.startswith(key):
                key_name, _ = line.split('=', 1)
                file.write(f'{key_name}={new_value}\n')
            else:
                file.write(line)


# Function to generate a new token
def _generate_new_token():
    # Replace this with your actual logic to generate a new token

    url = 'https://login.microsoftonline.com/' + os.getenv("AZURE_TENANT_ID") + '/oauth2/token'

    data = {
        'resource': os.getenv("DEFENDER_RESOURCE"),
        'client_id': os.getenv("DEFENDER_CLIENT_ID"),
        'client_secret': os.getenv("DEFENDER_CLIENT_SECRET"),
        'grant_type': os.getenv("DEFENDER_GRANT_TYPE")
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return None






def _get_bearertoken():
    

    # Load environment variables from .env file
    env_path = '/usr/src/project/.devcontainer/.env'
    load_dotenv(dotenv_path=env_path)

    # Get the expiration time from the environment variables
    expires_on = int(os.getenv("DEFENDER_ACCESS_BEARER_TOKEN_EXPIRES_ON"))

    # Get the current time as a Unix timestamp
    current_time = int(time.time())

    # Check if the token is expired
    if current_time > expires_on:
        # Generate a new token
        new_token = _generate_new_token()

        # Update the .env file with the new token and expiration time
        # Replace 3600 with the actual lifetime of the token in seconds
        try:
            update_env_file(env_path, 'DEFENDER_ACCESS_BEARER_TOKEN', new_token)
            update_env_file(env_path, 'DEFENDER_ACCESS_BEARER_TOKEN_EXPIRES_ON', str(current_time + 3600))
            # Reload the environment variables
            load_dotenv(dotenv_path=env_path, override=True)
        except Exception as e:
            print("An error occurred while updating the .env file:", str(e))

    # Use the token to perform the hunting query
    token = os.getenv("DEFENDER_ACCESS_BEARER_TOKEN")
    return token



def run():


    response = _get_bearertoken()
    print(response)



# if main 
if __name__ == "__main__":
    run()
