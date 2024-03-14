# azure/services.py
from .scripts.graph_apicall_runhuntingquery import run_hunting_query
from .scripts.graph_apicall_getuser import get_user
from .scripts.graph_apicall_getuserauthenticationmethods import get_user_authentication_methods

def execute_hunting_query(query):
    response, status_code = run_hunting_query(query)
    return response.json(), status_code

def execute_get_user(user):
    response, status_code = get_user(user)
    return response.json(), status_code


def execute_get_user_authentication_methods(user_id):
    response, status_code = get_user_authentication_methods(user_id)
    return response.json(), status_code