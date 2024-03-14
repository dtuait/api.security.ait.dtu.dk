from dotenv import load_dotenv, set_key
import requests
import time
import os




# Function to generate a new token
def _generate_new_token():
    # Replace this with your actual logic to generate a new token

    url = 'https://login.microsoftonline.com/' + os.getenv("AZURE_TENENT_ID") + '/oauth2/token'

    data = {
        'resource': os.getenv("GRAPH_RESOURCE"),
        'client_id': os.getenv("GRAPH_CLIENT_ID"),
        'client_secret': os.getenv("GRAPH_CLIENT_SECRET"),
        'grant_type': os.getenv("GRAPH_GRANT_TYPE")
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return None






def _get_bearertoken():
    

    # Load environment variables from .env file
    env_path = '/usr/src/project/app-main/.env'
    load_dotenv(dotenv_path=env_path)

    # Get the expiration time from the environment variables
    expires_on = int(os.getenv("GRAPH_ACCESS_BEARER_TOKEN_EXPIRES_ON"))

    # Get the current time as a Unix timestamp
    current_time = int(time.time())

    # Check if the token is expired
    if current_time > expires_on:
        # Generate a new token
        new_token = _generate_new_token()

        # Update the .env file with the new token and expiration time
        # Replace 3600 with the actual lifetime of the token in seconds
        set_key(env_path, "GRAPH_ACCESS_BEARER_TOKEN", new_token)
        set_key(env_path, "GRAPH_ACCESS_BEARER_TOKEN_EXPIRES_ON", str(current_time + 3600))
        # Reload the environment variables
        load_dotenv(dotenv_path=env_path, override=True)

    # Use the token to perform the hunting query
    token = os.getenv("GRAPH_ACCESS_BEARER_TOKEN")
    return token



def run():
    # # Generate a new token
    # new_token = generate_new_token()
    # message = new_token
    # print(message)


    response = _get_bearertoken()
    print(response)



# if main 
if __name__ == "__main__":
    run()
