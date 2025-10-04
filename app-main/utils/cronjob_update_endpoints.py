import logging

from django.apps import apps as django_apps
from django.db import DEFAULT_DB_ALIAS
from django.urls import get_resolver
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator


def updateEndpoints(*, using=None, logger: logging.Logger | None = None):
    log = logger or logging.getLogger(__name__)
    if using is None:
        using = DEFAULT_DB_ALIAS

    Endpoint = django_apps.get_model("myview", "Endpoint")
    if Endpoint is None:
        log.info("Endpoint model unavailable; skipping endpoint synchronisation")
        return

    manager = Endpoint.objects.db_manager(using)

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
    existing_endpoints = set(manager.values_list('path', flat=True))

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
            endpoint, created = manager.get_or_create(
                path=path,
                method=method,
                defaults={'path': path, 'method': method}
            )
            if created:
                log.info("Added new endpoint: %s %s", method, path)
            else:
                # Remove the endpoint from the set of existing endpoints if it still exists in the schema
                existing_endpoints.discard(path)

    # Delete any endpoints that were not found in the schema
    if existing_endpoints:
        manager.filter(path__in=existing_endpoints).delete()

    log.info("Completed updating endpoints.")


def run():
    updateEndpoints()

# if main 
if __name__ == "__main__":
    run()
