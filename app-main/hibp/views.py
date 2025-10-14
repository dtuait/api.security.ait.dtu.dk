"""Views exposing the DTU-hosted Have I Been Pwned API behind our limiter stack."""

from __future__ import annotations

import logging
from typing import Any, Dict

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from utils.api import SecuredAPIView

from .services import HIBPClient, HIBPConfigurationError, HIBPRequestError

logger = logging.getLogger(__name__)


class BaseHIBPView(SecuredAPIView):
    """Common behaviour for all HIBP proxy endpoints."""

    hibp_path_template: str = ""
    require_api_key: bool = True
    expect_json: bool = True
    extra_headers: Dict[str, str] | None = None

    def _build_params(self, request) -> Dict[str, Any]:
        if not hasattr(request, "query_params"):
            return {}
        params: Dict[str, Any] = {}
        for key, value in request.query_params.items():
            if value is None or value == "":
                continue
            params[key] = value
        return params

    def _resolve_path(self, **kwargs: Any) -> str:
        if not self.hibp_path_template:
            raise RuntimeError("hibp_path_template must be configured on view")
        try:
            return self.hibp_path_template.format(**kwargs)
        except KeyError as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Missing URL kwarg for template substitution: {exc}") from exc

    def _proxy_request(self, request, **kwargs: Any) -> Response:
        params = self._build_params(request)
        path = self._resolve_path(**kwargs)

        try:
            service_response = HIBPClient.get(
                path,
                params=params,
                headers=self.extra_headers,
                require_api_key=self.require_api_key,
            )
        except HIBPConfigurationError as exc:
            logger.error("HIBP configuration error: %s", exc)
            return Response(
                {"detail": "HIBP backend is not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except HIBPRequestError as exc:
            logger.warning("HIBP upstream failure path=%s error=%s", path, exc)
            return Response(
                {"detail": "Unable to contact Have I Been Pwned service."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        response = service_response.response
        data: Any

        if self.expect_json:
            try:
                data = response.json()
            except ValueError:
                data = {"detail": response.text or ""}
            return Response(data, status=response.status_code)

        data = response.text
        content_type = response.headers.get("Content-Type", "text/plain")
        return HttpResponse(data, status=response.status_code, content_type=content_type)

    def get(self, request, *args: Any, **kwargs: Any) -> Response:  # type: ignore[override]
        return self._proxy_request(request, **kwargs)


class SubscriptionDomainsView(BaseHIBPView):
    hibp_path_template = "api/v3/subscribeddomains"


class SubscriptionStatusView(BaseHIBPView):
    hibp_path_template = "api/v3/subscription/status"


class BreachedDomainView(BaseHIBPView):
    hibp_path_template = "api/v3/breacheddomain/{domain}"


class DataClassesView(BaseHIBPView):
    hibp_path_template = "api/v3/dataclasses"


class BreachedAccountView(BaseHIBPView):
    hibp_path_template = "api/v3/breachedaccount/{account}"


class AllBreachesView(BaseHIBPView):
    hibp_path_template = "api/v3/breaches"


class SingleBreachView(BaseHIBPView):
    hibp_path_template = "api/v3/breach/{name}"


class PasteAccountView(BaseHIBPView):
    hibp_path_template = "api/v3/pasteaccount/{account}"


class StealerLogsByEmailDomainView(BaseHIBPView):
    hibp_path_template = "api/v3/stealerlogsbyemaildomain/{domain}"


class StealerLogsByEmailView(BaseHIBPView):
    hibp_path_template = "api/v3/stealerlogsbyemail/{account}"


class StealerLogsByWebsiteDomainView(BaseHIBPView):
    hibp_path_template = "api/v3/stealerlogsbywebsitedomain/{domain}"


class PwnedPasswordsRangeView(BaseHIBPView):
    hibp_path_template = "range/{prefix}"
    require_api_key = False
    expect_json = False
    extra_headers = {"Accept": "text/plain"}
