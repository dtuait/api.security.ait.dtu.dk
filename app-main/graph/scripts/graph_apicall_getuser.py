
import requests, json
from ._graph_get_bearertoken import _get_bearertoken


def get_user(*, user_principal_name, select_parameters=None):

    # Microsoft api documentation
    # https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=http    

    token = _get_bearertoken()

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


    if select_parameters is not None:
        api_endpoint = f"https://graph.microsoft.com/v1.0/users/{user_principal_name}?{select_parameters}"
    else:
        api_endpoint = f"https://graph.microsoft.com/v1.0/users/{user_principal_name}"

    response = requests.get(api_endpoint, headers=headers)



    return json.loads(response.text), response.status_code




def run():
    user_principal_name = 'adm-vicre@dtu.dk'                    # will return status 200
    # user_principal_name = 'adm-vicre-not-a-real-user@dtu.dk'    # will return status 404
    response, status_code = get_user(user_principal_name=user_principal_name, select_parameters='$select=onPremisesImmutableId,userPrincipalName')
    print(response.get('onPremisesImmutableId'))



# if main 
if __name__ == "__main__":
    run()

