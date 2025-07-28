from django.http import JsonResponse
import requests
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_description="Fetches detailed documentation for a specific API endpoint from the OpenAPI specification. The endpoint name must match the path specified in the OpenAPI documentation.",
    manual_parameters=[
        openapi.Parameter(
            name='endpoint_name',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            description="The API endpoint path for which documentation is requested. Example: '/active-directory/v1.0/query'",
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Returns the detailed documentation for the specified endpoint",
            examples={
                'application/json': {
                    '/active-directory/v1.0/query': {
                        "get": {
                            "summary": "Query Active Directory",
                            "description": "Performs a query on Active Directory based on given search parameters.",
                            "parameters": [
                                {
                                    "name": "base_dn",
                                    "in": "query",
                                    "description": "Base DN for search",
                                    "required": True,
                                    "type": "string"
                                }
                            ],
                            "responses": {
                                "200": {
                                    "description": "Successful response"
                                }
                            }
                        }
                    }
                }
            }
        ),
        404: "Endpoint not found"
    }
)
@api_view(['GET'])
def get_api_documentation(request, endpoint_name):
    openapi_url = 'http://localhost:6081/myview/swagger/?format=openapi'
    response = requests.get(openapi_url)
    spec = response.json()  # Assumes the OpenAPI specification is returned as JSON

    paths = spec.get('paths', {})
    endpoint_info = paths.get(f'/{endpoint_name}')  # Ensure the endpoint name is prefixed with '/'

    if endpoint_info:
        return JsonResponse(endpoint_info)
    else:
        return JsonResponse({'error': 'Endpoint not found'}, status=404)
