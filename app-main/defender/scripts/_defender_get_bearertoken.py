import os
from datetime import timedelta

import requests
from django.db import transaction
from django.utils import timezone
from dotenv import load_dotenv

from graph.models import ServiceToken


TOKEN_REFRESH_BUFFER_SECONDS = int(os.getenv("DEFENDER_ACCESS_BEARER_TOKEN_REFRESH_BUFFER", "120") or 120)
DEFAULT_TOKEN_TTL_SECONDS = int(os.getenv("DEFENDER_ACCESS_BEARER_TOKEN_TTL", "3600") or 3600)


def _generate_new_token():
    env_path = os.getenv("APP_ENV_FILE", "/usr/src/project/.devcontainer/.env")
    load_dotenv(dotenv_path=env_path, override=False)

    url = f"https://login.microsoftonline.com/{os.getenv('AZURE_TENANT_ID')}/oauth2/token"

    data = {
        "resource": os.getenv("DEFENDER_RESOURCE"),
        "client_id": os.getenv("DEFENDER_CLIENT_ID"),
        "client_secret": os.getenv("DEFENDER_CLIENT_SECRET"),
        "grant_type": os.getenv("DEFENDER_GRANT_TYPE"),
    }

    try:
        response = requests.post(url, data=data, timeout=20)
        if response.status_code == 200:
            return response.json().get("access_token")
    except Exception:
        return None

    return None


def _get_token_record():
    with transaction.atomic():
        token_obj, _created = ServiceToken.objects.select_for_update().get_or_create(
            service=ServiceToken.Service.DEFENDER,
            defaults={
                "access_token": "",
                "expires_at": timezone.now() - timedelta(seconds=1),
            },
        )
        return token_obj


def _refresh_token(token_obj):
    new_token = _generate_new_token()
    if not new_token:
        return None

    token_obj.access_token = new_token
    token_obj.expires_at = timezone.now() + timedelta(seconds=DEFAULT_TOKEN_TTL_SECONDS)
    token_obj.save(update_fields=["access_token", "expires_at", "updated_at"])
    return token_obj.access_token


def _get_bearertoken():
    token_obj = _get_token_record()

    if token_obj.access_token and not token_obj.is_expired(buffer_seconds=TOKEN_REFRESH_BUFFER_SECONDS):
        return token_obj.access_token

    refreshed_token = _refresh_token(token_obj)
    if refreshed_token:
        return refreshed_token

    return token_obj.access_token


def run():
    response = _get_bearertoken()
    print(response)


if __name__ == "__main__":
    run()
