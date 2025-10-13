# azure/services.py
from .scripts.graph_apicall_runhuntingquery import run_hunting_query
from .scripts.graph_apicall_getuser import get_user
from .scripts.graph_apicall_getuserphoto import get_user_photo
from .scripts.graph_apicall_listuserauthenticationmethods import (
    list_user_authentication_methods,
)
from .scripts.graph_apicall_listusergroups import list_user_groups
from .scripts.graph_apicall_deletemfa import microsoft_authentication_method
from .scripts.graph_apicall_deletephone import phone_authentication_method
from .scripts.graph_apicall_deletesoftwaremfa import delete_software_mfa_method  # Import the new method


def execute_hunting_query(query):
    response, status_code = run_hunting_query(query)
    return response.json(), status_code

def execute_get_user(user_principal_name, select_parameters):
    data, status_code = get_user(user_principal_name=user_principal_name, select_parameters=select_parameters)
    return data, status_code


def execute_list_user_authentication_methods(user_id):
    response, status_code = list_user_authentication_methods(user_id)
    return response.json(), status_code


def execute_list_user_groups(user_principal_name):
    return list_user_groups(user_principal_name)


def execute_get_user_photo(user_principal_name):
    return get_user_photo(user_principal_name)


def execute_phone_authentication_method(azure_user_principal_id ,authentication_method_id):
    response, status_code = phone_authentication_method(azure_user_principal_id, authentication_method_id)
    # Response is empty and status code is 204
    return response, status_code


def execute_microsoft_authentication_method(azure_user_principal_id ,authentication_method_id):
    response, status_code = microsoft_authentication_method(azure_user_principal_id, authentication_method_id)
    # Response is empty and status code is 204
    return response, status_code

def execute_delete_software_mfa_method(azure_user_principal_id, authentication_method_id):
    response, status_code = delete_software_mfa_method(azure_user_principal_id, authentication_method_id)
    return response, status_code