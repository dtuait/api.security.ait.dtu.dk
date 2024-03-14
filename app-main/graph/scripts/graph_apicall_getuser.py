
import requests
from ._graph_get_bearertoken import _get_bearertoken


def get_user(user):

    token = _get_bearertoken()

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    api_endpoint = f"https://graph.microsoft.com/v1.0/users/{user}"

    response = requests.get(api_endpoint, headers=headers)

    return response, response.status_code




def run():
    user = 'vicre-test01@dtudk.onmicrosoft.com'
    response, status_code = get_user(user)
    print(response)



# if main 
if __name__ == "__main__":
    run()

