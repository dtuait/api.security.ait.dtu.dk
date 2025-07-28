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
    def get(self, request, endpoint_name=None):
        openapi_url = 'http://localhost:6081/myview/swagger/?format=openapi'
        
        if endpoint_name:
            if endpoint_name == 'ALL_ENDPOINTS':
                # Fetch the OpenAPI specification
                response = requests.get(openapi_url)
                if response.status_code != 200:
                    return JsonResponse({'error': 'OpenAPI specification not found'}, status=404)

                spec = response.json()  # Assumes the OpenAPI specification is returned as JSON
                paths = spec.get('paths', {})

                # Return all endpoint documentation
                return JsonResponse(paths)

            else:
                # Replace backslashes with forward slashes
                endpoint_name = endpoint_name.replace('\\', '/')
                # Fetch and return the documentation for the specific endpoint
                response = requests.get(openapi_url)
                if response.status_code != 200:
                    return JsonResponse({'error': 'OpenAPI specification not found'}, status=404)

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
        # This need to be a script
        openapi_url = 'http://localhost:6081/myview/swagger/?format=openapi'
        response = requests.get(openapi_url)
        if response.status_code != 200:
            return JsonResponse({'error': 'OpenAPI specification not found'}, status=404)

        spec = response.json()  # Assumes the OpenAPI specification is returned as JSON
        paths = spec.get('paths', {})

        # Extracting all endpoint paths
        endpoints = list(paths.keys())
        return JsonResponse({'endpoints': endpoints})