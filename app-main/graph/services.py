# azure/services.py
from .scripts.graph_apicall_runhuntingquery import run_hunting_query
from .scripts.graph_apicall_getuser import get_user
from .scripts.graph_apicall_listuserauthenticationmethods import list_user_authentication_methods
from .scripts.graph_apicall_deletemfa import delete_authentication_method

def execute_hunting_query(query):
    response, status_code = run_hunting_query(query)
    return response.json(), status_code

def execute_get_user(user):
    response, status_code = get_user(user)
    return response.json(), status_code


def execute_list_user_authentication_methods(user_id):
    response, status_code = list_user_authentication_methods(user_id)
    return response.json(), status_code


def execute_delete_user_authentication_method(azure_user_principal_id ,authentication_method_id):
    response, status_code = delete_authentication_method(azure_user_principal_id, authentication_method_id)
    # Response is empty and status code is 204
    return response, status_code