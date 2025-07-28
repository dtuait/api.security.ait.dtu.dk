from django.http import JsonResponse
import requests
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class APIDocumentationView(APIView):

    @swagger_auto_schema(
        operation_description="Fetches detailed documentation for a specific API endpoint.",
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description="Token used for authentication.",
                required=True,
                default='<token>'
            ),
            openapi.Parameter(
                name='endpoint_name',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="The API endpoint path for which documentation is requested.",
                required=True,
                default='active-directory\\v1.0\\query'
            )
        ],
        responses={
            200: "Returns the detailed documentation for the specified endpoint",
            404: "Endpoint not found"
        }
    )
    def get(self, request, endpoint_name=None):

        if endpoint_name:
            # replace backslashes with forward slashes
            endpoint_name = endpoint_name.replace('\\', '/')
            # Fetch and return the documentation
            openapi_url = 'http://localhost:6081/myview/swagger/?format=openapi'
            response = requests.get(openapi_url)
            spec = response.json()
            paths = spec.get('paths', {})
            endpoint_info = paths.get(f'/{endpoint_name}')  # Ensure the endpoint name is prefixed with '/'

            if endpoint_info:
                return JsonResponse(endpoint_info)
            else:
                return JsonResponse({'error': 'Endpoint not found'}, status=404)
        else:
            return JsonResponse({'message': 'All documentation'})



from django.http import JsonResponse
import requests
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class APIEndpointsListView(APIView):

    @swagger_auto_schema(

        operation_description="Lists all available API endpoints from the OpenAPI specification.",
        responses={
            200: openapi.Response(
                description="A list of all available API endpoints",
                examples={
                    'application/json': {
                        "endpoints": [
                            "/active-directory/v1.0/query",
                            "/other-endpoint/v1.0/action"
                        ]
                    }
                }
            ),
            404: "OpenAPI specification not found"
        }
    )
    def get(self, request):
        openapi_url = 'http://localhost:6081/myview/swagger/?format=openapi'
        response = requests.get(openapi_url)
        if response.status_code != 200:
            return JsonResponse({'error': 'OpenAPI specification not found'}, status=404)

        spec = response.json()  # Assumes the OpenAPI specification is returned as JSON
        paths = spec.get('paths', {})

        # Extracting all endpoint paths
        endpoints = list(paths.keys())
        return JsonResponse({'endpoints': endpoints})