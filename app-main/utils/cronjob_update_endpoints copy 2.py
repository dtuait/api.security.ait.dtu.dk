from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg import openapi
from django.urls import get_resolver
from myview.models import Endpoint  # Update 'myview' with the actual name of your app

def updateEndpoints():
    # Instantiate the schema generator
    generator = OpenAPISchemaGenerator(
        info=openapi.Info(
            title="API",
            default_version='v1',
            description="Description of your API",
            terms_of_service="https://www.example.com/terms/",
            contact=openapi.Contact(email="contact@example.com"),
            license=openapi.License(name="BSD License"),
        ),
        url='',  # Set this to your production URL if necessary
        patterns=get_resolver().url_patterns,  # Using the default URL patterns
    )

    schema = generator.get_schema(request=None, public=True)

    # Create a set of all endpoint paths in the Django model
    existing_endpoints = set(Endpoint.objects.values_list('path', flat=True))

    # Ensure the special 'any' path and method exists
    # Endpoint.objects.get_or_create(path='any', method='any')

    # Loop through the paths in the schema
    for path, path_data in schema['paths'].items():
        for method in path_data.keys():
            # Normalize method to uppercase
            common_http_methods = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
            method = method.lower()
            method = path_data.operations[0][0] if path_data.operations[0][0] in common_http_methods else None
            # Check if the endpoint (with method) already exists
            endpoint, created = Endpoint.objects.get_or_create(
                path=path,
                method=method,
                defaults={'path': path, 'method': method}
            )
            if created:
                print(f"Added new endpoint: {method} {path}")
            else:
                # Remove the endpoint from the set of existing endpoints if it still exists in the schema
                existing_endpoints.discard(path)

    # Delete any endpoints that were not found in the schema
    Endpoint.objects.filter(path__in=existing_endpoints).delete()

    print("Completed updating endpoints.")


def run():
    updateEndpoints()

# if main 
if __name__ == "__main__":
    run()
