
import logging
from typing import Optional, Tuple

import requests

from ._graph_get_bearertoken import _get_bearertoken


logger = logging.getLogger(__name__)


def _build_graph_endpoint(user_principal_name: str, select_parameters: Optional[str]) -> str:
    if select_parameters:
        return f"https://graph.microsoft.com/v1.0/users/{user_principal_name}?{select_parameters}"
    return f"https://graph.microsoft.com/v1.0/users/{user_principal_name}"


def _error_response(message: str, *, code: str = "RequestError", status: int = 503):
    return {"error": {"code": code, "message": message}}, status


def get_user(*, user_principal_name, select_parameters=None) -> Tuple[dict, int]:
    """Retrieve a user from Microsoft Graph.

    Network failures and JSON decoding issues are handled gracefully, returning a
    structured error response instead of raising to the caller.
    """

    # Microsoft api documentation
    # https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=http

    token = _get_bearertoken()
    if not token:
        logger.warning(
            "Unable to acquire Microsoft Graph token while requesting user %s",
            user_principal_name,
        )
        return _error_response("Failed to acquire access token", code="AuthTokenUnavailable", status=503)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    api_endpoint = _build_graph_endpoint(user_principal_name, select_parameters)

    try:
        response = requests.get(api_endpoint, headers=headers, timeout=20)
    except requests.exceptions.RequestException as exc:
        logger.warning(
            "Microsoft Graph request for %s failed: %s",
            user_principal_name,
            exc,
        )
        return _error_response(str(exc), status=503)

    try:
        data = response.json()
    except ValueError:
        logger.warning(
            "Received non-JSON response from Microsoft Graph for %s (status %s)",
            user_principal_name,
            response.status_code,
        )
        data = {"raw": response.text}

    return data, response.status_code




def run():
    user_principal_name = 'adm-vicre@dtu.dk'                    # will return status 200
    # user_principal_name = 'adm-vicre-not-a-real-user@dtu.dk'    # will return status 404
    response, status_code = get_user(user_principal_name=user_principal_name, select_parameters='$select=onPremisesImmutableId,userPrincipalName')
    print(response.get('onPremisesImmutableId'))



# if main 
if __name__ == "__main__":
    run()

