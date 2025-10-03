import os
from datetime import datetime, timedelta, timezone

from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError, transaction


def _parse_expiry(value: str | None, *, default_ttl_seconds: int = 3600) -> datetime:
    """Parse an expiry env var as epoch or TTL, return aware datetime.

    Accepts either a Unix epoch (seconds) or a small integer interpreted as a TTL
    in seconds. Falls back to now + default TTL when input is missing/invalid.
    """

    now = datetime.now(timezone.utc)
    if not value:
        return now + timedelta(seconds=default_ttl_seconds)
    try:
        raw = int(str(value).strip())
    except (TypeError, ValueError):
        return now + timedelta(seconds=default_ttl_seconds)

    # Heuristic: treat large numbers as epoch seconds, small as TTL seconds
    if raw > 1_000_000_000:  # ~2001-09-09
        try:
            return datetime.fromtimestamp(raw, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return now + timedelta(seconds=default_ttl_seconds)
    return now + timedelta(seconds=max(raw, 0))


class GraphConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'graph'

    def ready(self) -> None:  # noqa: C901 (complexity not critical here)
        # Lazy import to avoid model initialization during app config import
        from .models import ServiceToken

        seeds = (
            (
                ServiceToken.Service.GRAPH,
                os.getenv("GRAPH_ACCESS_BEARER_TOKEN"),
                os.getenv("GRAPH_ACCESS_BEARER_TOKEN_EXPIRES_ON"),
            ),
            (
                ServiceToken.Service.DEFENDER,
                os.getenv("DEFENDER_ACCESS_BEARER_TOKEN"),
                os.getenv("DEFENDER_ACCESS_BEARER_TOKEN_EXPIRES_ON"),
            ),
        )

        for service, token, expires_raw in seeds:
            if not token:
                continue

            try:
                with transaction.atomic():
                    obj, _created = ServiceToken.objects.select_for_update().get_or_create(
                        service=service,
                        defaults={
                            "access_token": token,
                            "expires_at": _parse_expiry(expires_raw),
                        },
                    )
                    # Only set if the DB does not already have a token value
                    if not obj.access_token:
                        obj.access_token = token
                        obj.expires_at = _parse_expiry(expires_raw)
                        obj.save(update_fields=["access_token", "expires_at", "updated_at"])
            except (OperationalError, ProgrammingError):
                # Database not ready (e.g., before migrations) — skip silently
                return
