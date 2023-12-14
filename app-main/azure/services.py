# azure/services.py
from .scripts.graph_apicall_runhuntingquery import run_hunting_query

def execute_hunting_query(query):
    response, status_code = run_hunting_query(query)
    return response.json(), status_code