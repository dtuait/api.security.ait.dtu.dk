
import requests
from ._graph_get_bearertoken import _get_bearertoken
# from ._graph_get_user_authentication_methods import get_user_authentication_methods


def phone_authentication_method(azure_user_principal_id ,authentication_method_id):

    token = _get_bearertoken()

    headers = {
        'Authorization': f'Bearer {token}'
    }




    # before you delete make sure that it is not the password method. By checking if @odata.type not contains password




    
    # https://graph.microsoft.com/v1.0/users/vicre-test01@dtudk.onmicrosoft.com/authentication/microsoftAuthenticatorMethods/123e4441-eadf-4950-883d-fea123988824
    api_endpoint = f"https://graph.microsoft.com/v1.0/users/{azure_user_principal_id}/authentication/phoneMethods/{authentication_method_id}"
    

    response = requests.delete(api_endpoint, headers=headers)

    # response.status_code = 204
     
    # 204 means successfully deleted
    return response, response.status_code




def run():
    azure_user_principal_id = '3358461b-2b36-4019-a2b7-2da92001cf7c'
    authentication_method_id = 'f18a98ad-7fc4-4294-8814-4fbdea4ef13b'
    response, status_code = phone_authentication_method(azure_user_principal_id, authentication_method_id)
    print(status_code)



# if main 
if __name__ == "__main__":
    run()

