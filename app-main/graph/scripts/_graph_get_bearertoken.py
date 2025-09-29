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
    """Generate a new Microsoft Graph access token using client credentials.

    Uses the OAuth v2.0 token endpoint and the 
    "https://graph.microsoft.com/.default" scope, which leverages the app's
    configured application permissions.
    """

    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("GRAPH_CLIENT_ID")
    client_secret = os.getenv("GRAPH_CLIENT_SECRET")
    grant_type = os.getenv("GRAPH_GRANT_TYPE", "client_credentials")

    # Default to Graph resource if not provided
    graph_resource = os.getenv("GRAPH_RESOURCE", "https://graph.microsoft.com").rstrip("/")

    # OAuth v2 endpoint + scope-based permission
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": grant_type,
        "scope": f"{graph_resource}/.default",
    }

    try:
        response = requests.post(url, data=data, timeout=20)
        if response.status_code == 200:
            body = response.json()
            return body.get("access_token")
        else:
            # Fall back to v1 endpoint if tenant is still configured that way
            # or if admins only allowed v1 (rare, but keep compatibility)
            url_v1 = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
            data_v1 = {
                "resource": graph_resource,
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": grant_type,
            }
            resp_v1 = requests.post(url_v1, data=data_v1, timeout=20)
            if resp_v1.status_code == 200:
                return resp_v1.json().get("access_token")
            return None
    except Exception:
        return None






def _get_bearertoken():
    """Return a valid Graph access token, refreshing if needed.

    If the token is missing or expired, attempts to generate a new one and
    persists it to the devcontainer .env file for reuse.
    """

    # Load environment variables from .env file
    env_path = '/usr/src/project/.devcontainer/.env'
    load_dotenv(dotenv_path=env_path, override=True)

    # Get expiration time (default to 0 so we refresh if missing/invalid)
    try:
        expires_on = int(os.getenv("GRAPH_ACCESS_BEARER_TOKEN_EXPIRES_ON", "0") or "0")
    except ValueError:
        expires_on = 0

    current_time = int(time.time())

    # Proactively refresh 2 minutes before expiry
    if current_time >= (expires_on - 120):
        new_token = _generate_new_token()
        if new_token:
            try:
                update_env_file(env_path, 'GRAPH_ACCESS_BEARER_TOKEN', new_token)
                update_env_file(env_path, 'GRAPH_ACCESS_BEARER_TOKEN_EXPIRES_ON', str(current_time + 3600))
                # Reload env so subsequent calls in the same process see updates
                load_dotenv(dotenv_path=env_path, override=True)
            except Exception:
                # If persisting fails, still return the in-memory token
                return new_token
        else:
            # If we cannot refresh, fall back to whatever is present (may be empty)
            pass

    return os.getenv("GRAPH_ACCESS_BEARER_TOKEN", "")



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
