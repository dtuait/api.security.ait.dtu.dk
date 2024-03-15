
from django.apps import AppConfig
from django.core.management import call_command

class MyviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myview'


    def ready(self):
        # Ensure server is running in development mode before running the script.
        from django.conf import settings
        if settings.DEBUG:
            try:
                call_command('runscript', 'utils.cronjob_update_endpoints')
            except:
                pass  # Handle any expected exceptions or log errors as needed

    