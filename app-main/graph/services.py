# azure/services.py
from .scripts.graph_apicall_runhuntingquery import run_hunting_query
from .scripts.graph_apicall_getuser import get_user

def execute_hunting_query(query):
    response, status_code = run_hunting_query(query)
    return response.json(), status_code

def execute_get_user(user):
    response, status_code = get_user(user)
    return response.json(), status_code
