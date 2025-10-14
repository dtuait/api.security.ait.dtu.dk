from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
import requests

from hibp import signals
from hibp.services import HIBPServiceResponse
from hibp.views import DataClassesView, PwnedPasswordsRangeView
from myview.models import ADOrganizationalUnitLimiter, Endpoint, LimiterType


class HibpViewTests(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(username="tester", password="pass")

    def _create_response(self, status_code: int, body: bytes, content_type: str) -> requests.Response:
        response = requests.Response()
        response.status_code = status_code
        response._content = body
        response.headers["Content-Type"] = content_type
        response.url = "https://api.haveibeenpwned.cert.dk/test"
        return response

    def test_dataclasses_view_proxies_json_response(self) -> None:
        response = self._create_response(200, b"[\"EmailAddresses\"]", "application/json")
        service_response = HIBPServiceResponse(response=response)

        request = self.factory.get("/hibp/v3/dataclasses")
        force_authenticate(request, user=self.user)

        with patch("hibp.views.HIBPClient.get", return_value=service_response):
            drf_response = DataClassesView.as_view()(request)

        self.assertEqual(drf_response.status_code, 200)
        self.assertEqual(drf_response.data, ["EmailAddresses"])

    def test_pwned_passwords_range_view_returns_plain_text(self) -> None:
        response = self._create_response(200, b"5BAA6:10", "text/plain")
        service_response = HIBPServiceResponse(response=response)

        request = self.factory.get("/hibp/range/5BAA6")
        force_authenticate(request, user=self.user)

        with patch("hibp.views.HIBPClient.get", return_value=service_response):
            django_response = PwnedPasswordsRangeView.as_view()(request, prefix="5BAA6")

        self.assertEqual(django_response.status_code, 200)
        self.assertEqual(django_response.content, b"5BAA6:10")
        self.assertEqual(django_response["Content-Type"], "text/plain")


class HibpLimiterSignalTests(TestCase):
    def setUp(self) -> None:
        signals._get_ou_limiter_type_id.cache_clear()
        content_type = ContentType.objects.get_for_model(ADOrganizationalUnitLimiter)
        self.limiter_type, _ = LimiterType.objects.get_or_create(
            content_type=content_type,
            defaults={
                "name": "AD Organizational Unit Limiter",
                "description": "This model represents an AD organizational unit limiter.",
            },
        )

    def test_endpoint_save_assigns_ad_ou_limiter(self) -> None:
        endpoint = Endpoint.objects.create(path="/hibp/v3/dataclasses", method="get")
        endpoint.refresh_from_db()

        self.assertEqual(endpoint.limiter_type_id, self.limiter_type.pk)
        self.assertFalse(endpoint.no_limit)
