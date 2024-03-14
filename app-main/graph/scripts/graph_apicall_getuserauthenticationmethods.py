
import requests
from ._graph_get_bearertoken import _get_bearertoken



def get_user_authentication_methods(user_id):



    token = _get_bearertoken()
    api_endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}/authentication/methods"


    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_endpoint, headers=headers)

    return response, response.status_code




def run():
    user_id = '3358461b-2b36-4019-a2b7-2da92001cf7c'
    response, status_code = get_user_authentication_methods(user_id)
    print(response)



# if main 
if __name__ == "__main__":
    run()

