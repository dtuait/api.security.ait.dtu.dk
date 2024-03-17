
import requests
from ._graph_get_bearertoken import _get_bearertoken
# from ._graph_get_user_authentication_methods import get_user_authentication_methods


def delete_authentication_method(azure_user_principal_id ,authentication_method_id):

    token = _get_bearertoken()

    headers = {
        'Authorization': f'Bearer {token}'
    }




    # before you delete make sure that it is not the password method. By checking if @odata.type not contains password




    # api_endpoint = f"https://graph.microsoft.com/v1.0/users/{authentication_method_id}/authentication/methods"
    api_endpoint = f"https://graph.microsoft.com/v1.0/users/{azure_user_principal_id}/authentication/microsoftAuthenticatorMethods/{authentication_method_id}"
    # https://graph.microsoft.com/v1.0/users/157181b5-5931-4849-b7fd-c80ebf17bd11/authentication/methods

    response = requests.delete(api_endpoint, headers=headers)

    return response, response.status_code




def run():
    azure_user_principal_id = '3358461b-2b36-4019-a2b7-2da92001cf7c'
    authentication_method_id = 'f18a98ad-7fc4-4294-8814-4fbdea4ef13b'
    response, status_code = delete_authentication_method(azure_user_principal_id, authentication_method_id)
    # print(response)
    print(status_code)



# if main 
if __name__ == "__main__":
    run()

