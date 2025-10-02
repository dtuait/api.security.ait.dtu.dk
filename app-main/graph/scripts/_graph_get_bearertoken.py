import logging
import os
from datetime import timedelta

import requests
from django.db import OperationalError, ProgrammingError, transaction
from django.utils import timezone
from dotenv import load_dotenv

from ..models import ServiceToken


logger = logging.getLogger(__name__)


class _EphemeralServiceToken:
    """Fallback token object used when the ServiceToken table is unavailable."""

    def __init__(self, *, service: str):
        self.service = service
        self.pk = None
        self.access_token = ""
        self.expires_at = timezone.now() - timedelta(seconds=1)

    def is_expired(self, *, buffer_seconds: int = 0) -> bool:  # pragma: no cover - simple proxy
        buffer = timedelta(seconds=max(buffer_seconds, 0))
        return self.expires_at <= timezone.now() + buffer

    def save(self, *args, **kwargs):  # pragma: no cover - no-op persistence proxy
        return None


TOKEN_REFRESH_BUFFER_SECONDS = int(os.getenv("GRAPH_ACCESS_BEARER_TOKEN_REFRESH_BUFFER", "120") or 120)
DEFAULT_TOKEN_TTL_SECONDS = int(os.getenv("GRAPH_ACCESS_BEARER_TOKEN_TTL", "3600") or 3600)


def _generate_new_token():
    """Generate a new Microsoft Graph access token using client credentials."""

    # Ensure environment variables are loaded before attempting the request.
    env_path = os.getenv("APP_ENV_FILE", "/usr/src/project/.devcontainer/.env")
    load_dotenv(dotenv_path=env_path, override=False)

    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("GRAPH_CLIENT_ID")
    client_secret = os.getenv("GRAPH_CLIENT_SECRET")
    grant_type = os.getenv("GRAPH_GRANT_TYPE", "client_credentials")
    graph_resource = os.getenv("GRAPH_RESOURCE", "https://graph.microsoft.com").rstrip("/")

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": grant_type,
        "scope": f"{graph_resource}/.default",
    }

    try:
        response = requests.post(url, data=data, timeout=20)
        if response.status_code == 200:
            return response.json().get("access_token")

        url_v1 = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
        data_v1 = {
            "resource": graph_resource,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": grant_type,
        }
        resp_v1 = requests.post(url_v1, data=data_v1, timeout=20)
        if resp_v1.status_code == 200:
            return resp_v1.json().get("access_token")
    except Exception:
        return None

    return None


def _get_token_record():
    """Fetch the persisted Graph token row with a database lock."""

    try:
        with transaction.atomic():
            token_obj, _created = ServiceToken.objects.select_for_update().get_or_create(
                service=ServiceToken.Service.GRAPH,
                defaults={
                    "access_token": "",
                    "expires_at": timezone.now() - timedelta(seconds=1),
                },
            )
            return token_obj
    except (OperationalError, ProgrammingError) as exc:
        logger.warning(
            "ServiceToken table unavailable while fetching Graph token; "
            "operating without persistence. Error: %s",
            exc,
        )
        return _EphemeralServiceToken(service=ServiceToken.Service.GRAPH)


def _refresh_token(token_obj):
    """Refresh the database token when the stored value is expired."""

    new_token = _generate_new_token()
    if not new_token:
        return None

    token_obj.access_token = new_token
    token_obj.expires_at = timezone.now() + timedelta(seconds=DEFAULT_TOKEN_TTL_SECONDS)

    if getattr(token_obj, "pk", None) is not None:
        try:
            token_obj.save(update_fields=["access_token", "expires_at", "updated_at"])
        except (OperationalError, ProgrammingError) as exc:
            logger.warning(
                "Unable to persist refreshed Graph token; operating in-memory. Error: %s",
                exc,
            )

    return token_obj.access_token


def _get_bearertoken():
    """Return a valid Graph access token, refreshing if needed."""

    token_obj = _get_token_record()

    if token_obj.access_token and not token_obj.is_expired(buffer_seconds=TOKEN_REFRESH_BUFFER_SECONDS):
        return token_obj.access_token

    refreshed_token = _refresh_token(token_obj)
    if refreshed_token:
        return refreshed_token

    # Fall back to whatever is stored even if expired when refresh fails.
    return token_obj.access_token


def run():
    response = _get_bearertoken()
    print(response)


if __name__ == "__main__":
    run()

