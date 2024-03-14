
import requests
from ._graph_get_bearertoken import _get_bearertoken
# from ._graph_get_user_authentication_methods import get_user_authentication_methods


def delete_authentication_method(authentication_method_id):

    token = _get_bearertoken()

    headers = {
        'Authorization': f'Bearer {token}'
    }




    # before you delete make sure that it is not the password method. By checking if @odata.type not contains password




    api_endpoint = f"https://graph.microsoft.com/v1.0/users/{authentication_method_id}/authentication/methods"
    # https://graph.microsoft.com/v1.0/users/157181b5-5931-4849-b7fd-c80ebf17bd11/authentication/methods

    response = requests.delete(api_endpoint, headers=headers)

    return response, response.status_code




def run():
    authentication_method_id = '23234e09-d1d7-468b-aa33-2121d59338bb'
    response, status_code = delete_authentication_method(authentication_method_id)
    print(response)



# if main 
if __name__ == "__main__":
    run()

