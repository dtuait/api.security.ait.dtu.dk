from django.shortcuts import render

# Create your views here.
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from urllib.parse import urlencode

API_BASE = "https://api.haveibeenpwned.cert.dk/v3/"
API_KEY = "YOUR_CERT_API_KEY"  # Replace this with your actual key

class BreachedAccountView(APIView):
    @swagger_auto_schema(
        operation_description="Check if an email account was breached.",
        manual_parameters=[
            openapi.Parameter("email", openapi.IN_PATH, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter("truncateResponse", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
            openapi.Parameter("includeUnverified", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
        ],
        tags=["pwnedproxy"]
    )
    def get(self, request, email):
        query = {k: v for k, v in request.query_params.items() if k in ["truncateResponse", "includeUnverified"]}
        url = f"{API_BASE}breachedaccount/{email}"
        if query:
            url += f"?{urlencode(query)}"
        headers = {"x-api-key": API_KEY}
        resp = requests.get(url, headers=headers)
        return Response(resp.json(), status=resp.status_code)

class BreachesView(APIView):
    @swagger_auto_schema(operation_description="Get all breaches.", tags=["pwnedproxy"])
    def get(self, request):
        headers = {"x-api-key": API_KEY}
        resp = requests.get(f"{API_BASE}breaches", headers=headers)
        return Response(resp.json(), status=resp.status_code)

class DataClassesView(APIView):
    @swagger_auto_schema(operation_description="Get all dataclasses.", tags=["pwnedproxy"])
    def get(self, request):
        headers = {"x-api-key": API_KEY}
        resp = requests.get(f"{API_BASE}dataclasses", headers=headers)
        return Response(resp.json(), status=resp.status_code)

class LatestBreachView(APIView):
    @swagger_auto_schema(operation_description="Get the latest breach.", tags=["pwnedproxy"])
    def get(self, request):
        headers = {"x-api-key": API_KEY}
        resp = requests.get(f"{API_BASE}latestbreach", headers=headers)
        return Response(resp.json(), status=resp.status_code)

class BreachDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Get details about a specific breach.",
        manual_parameters=[openapi.Parameter("name", openapi.IN_PATH, type=openapi.TYPE_STRING, required=True)],
        tags=["pwnedproxy"]
    )
    def get(self, request, name):
        headers = {"x-api-key": API_KEY}
        url = f"{API_BASE}breach/{name}"
        resp = requests.get(url, headers=headers)
        return Response(resp.json(), status=resp.status_code)

class PasteAccountView(APIView):
    @swagger_auto_schema(
        operation_description="Check if an account has been pasted.",
        manual_parameters=[openapi.Parameter("account", openapi.IN_PATH, type=openapi.TYPE_STRING, required=True)],
        tags=["pwnedproxy"]
    )
    def get(self, request, account):
        headers = {"x-api-key": API_KEY}
        url = f"{API_BASE}pasteaccount/{account}"
        resp = requests.get(url, headers=headers)
        return Response(resp.json(), status=resp.status_code)

class SubscriptionStatusView(APIView):
    @swagger_auto_schema(operation_description="Get subscription status.", tags=["pwnedproxy"])
    def get(self, request):
        headers = {"x-api-key": API_KEY}
        resp = requests.get(f"{API_BASE}subscription/status", headers=headers)
        return Response(resp.json(), status=resp.status_code)
