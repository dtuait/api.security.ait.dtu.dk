"""Signal handlers keeping HIBP endpoints aligned with limiter configuration."""

from __future__ import annotations

import logging
from functools import lru_cache

from django.apps import apps
from django.db import OperationalError, ProgrammingError
from django.db.models.signals import post_save
from django.db.utils import ConnectionDoesNotExist
from django.dispatch import receiver

from .constants import HIBP_ENDPOINT_PATHS

logger = logging.getLogger(__name__)


def normalize_endpoint_path(path: str) -> str:
    if not path:
        return "/"
    normalized = "/" + path.lstrip("/")
    if len(normalized) > 1 and normalized.endswith("/"):
        normalized = normalized.rstrip("/")
    return normalized


_NORMALISED_HIBP_PATHS = {normalize_endpoint_path(path) for path in HIBP_ENDPOINT_PATHS}


@lru_cache(maxsize=1)
def _get_ou_limiter_type_id() -> int | None:
    try:
        LimiterType = apps.get_model("myview", "LimiterType")
    except LookupError:  # pragma: no cover - defensive
        logger.info("LimiterType model unavailable; cannot resolve AD OU limiter type")
        return None

    try:
        limiter_type = (
            LimiterType.objects.filter(content_type__model="adorganizationalunitlimiter")
            .only("pk")
            .first()
        )
    except (OperationalError, ProgrammingError, ConnectionDoesNotExist):
        logger.info("Database not ready to resolve AD OU limiter type for HIBP")
        return None
    except Exception:  # pragma: no cover - defensive
        logger.exception("Unexpected failure while resolving AD OU limiter type for HIBP")
        return None

    return limiter_type.pk if limiter_type else None


def _paths_match(candidate: str) -> bool:
    normalised = normalize_endpoint_path(candidate)
    return normalised in _NORMALISED_HIBP_PATHS


try:
    Endpoint = apps.get_model("myview", "Endpoint")
except LookupError:  # pragma: no cover - defensive
    Endpoint = None  # type: ignore


if Endpoint is not None:

    @receiver(post_save, sender=Endpoint, dispatch_uid="hibp_assign_ou_limiter")
    def ensure_hibp_limiter(sender, instance, **kwargs):  # type: ignore[override]
        if not instance or not getattr(instance, "path", None):
            return

        if not _paths_match(instance.path):
            return

        limiter_type_id = _get_ou_limiter_type_id()
        if limiter_type_id is None:
            logger.debug("HIBP limiter assignment skipped; limiter type id unavailable")
            return

        updates = {}
        if instance.limiter_type_id != limiter_type_id:
            updates["limiter_type_id"] = limiter_type_id
        if instance.no_limit:
            updates["no_limit"] = False

        if not updates:
            return

        try:
            sender.objects.filter(pk=instance.pk).update(**updates)
            logger.debug(
                "Aligned HIBP endpoint pk=%s path=%s with AD OU limiter", instance.pk, instance.path
            )
        except (OperationalError, ProgrammingError, ConnectionDoesNotExist):
            logger.info("Database not ready to update HIBP endpoint limiter")
        except Exception:  # pragma: no cover - defensive
            logger.exception("Failed to align limiter for HIBP endpoint path=%s", instance.path)
