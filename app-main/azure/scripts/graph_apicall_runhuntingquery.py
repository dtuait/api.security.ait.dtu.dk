import pyodbc
import os
import json
import time
import requests
from dotenv import load_dotenv, set_key

# Function to generate a new token
def generate_new_token():
    # Replace this with your actual logic to generate a new token

    url = 'https://login.microsoftonline.com/' + os.getenv("AZURE_TENENT_ID") + '/oauth2/token'

    data = {
        'resource': os.getenv("GRAPH_RESOURCE"),
        'client_id': os.getenv("DEFENDER_CLIENT_ID"),
        'client_secret': os.getenv("DEFENDER_CLIENT_SECRET"),
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return None


# Load environment variables from .env file
load_dotenv()

def run_hunting_query(query):



    # Get the expiration time from the environment variables
    expires_on = int(os.getenv("GRAPH_ACCESS_BEARER_TOKEN_EXPIRES_ON"))

    # Get the current time as a Unix timestamp
    current_time = int(time.time())

    # Check if the token is expired
    if current_time > expires_on:
        # Generate a new token
        new_token = generate_new_token()

        # Update the .env file with the new token and expiration time
        # Replace 3600 with the actual lifetime of the token in seconds
        set_key("app-main/.env", "GRAPH_ACCESS_BEARER_TOKEN", new_token)
        set_key("app-main/.env", "GRAPH_ACCESS_BEARER_TOKEN_EXPIRES_ON", str(current_time + 3600))
        # Reload the environment variables
        load_dotenv(override=True)

    
    
    # Use the token to perform the hunting query
    token = os.getenv("GRAPH_ACCESS_BEARER_TOKEN")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


    # Define the API endpoint
    api_endpoint = "https://graph.microsoft.com/v1.0/security/runHuntingQuery"  # Replace with your actual endpoint

    # Make the request
    response = requests.post(api_endpoint, headers=headers, json={"Query": query})

    return response, response.status_code









def run():
    # # Generate a new token
    # new_token = generate_new_token()
    # message = new_token
    # print(message)

    kql = "// might contain sensitive data\nlet alertedEvent = datatable(compressedRec: string)\n['eAEtjkFPAjEQRv8K6RmabReF3ZNEohiMEEQP3up22Excps20S9IY/7tj5DjvvWS+b3XEMzwCAbsMXrXKVraeGTOrq6OZt2bRmrk2y4Wtbm8+1FStYlxjioMrL+4M0u9OJ+xgE+SYqrcEvGekDqMbrsEFO4Y7n0ftvyR52q+8Z0hJlGmsrpe6qbSxjbh7zEXwNlAPlCbPhfrPIvw1yzgRm3ABn7LzQH91GClz2fEBegwkfr0V/DAOA/2/fscuB54cAOPI6ucXbMZKOg==']\n| extend raw = todynamic(zlib_decompress_from_base64_string(compressedRec)) | evaluate bag_unpack(raw) | project-away compressedRec;\nalertedEvent"
    response = run_hunting_query(kql)
    print(response)



# if main 
if __name__ == "__main__":
    run()
