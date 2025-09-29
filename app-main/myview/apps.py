
from django.apps import AppConfig
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

class MyviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myview'


    def ready(self):
        # Best-effort background sync of AD groups at startup and after migrations
        try:
            from django.db.models.signals import post_migrate
            from .models import ADGroupAssociation

            # Ensure initial sync on app startup (cached/throttled)
            try:
                ADGroupAssociation.ensure_groups_synced_cached()
            except Exception:
                logger.exception("Initial cached AD group sync in AppConfig.ready() failed")

            # Ensure sync after migrations to reflect new schema
            def _post_migrate_sync(sender, **kwargs):
                try:
                    ADGroupAssociation.ensure_groups_synced_cached()
                except Exception:
                    logger.exception("Post-migrate cached AD group sync failed")

            post_migrate.connect(_post_migrate_sync, sender=self, dispatch_uid="myview_post_migrate_sync")
        except Exception:
            logger.exception("Failed to register AD group sync hooks in AppConfig.ready()")

        # # Ensure server is running in development mode before running the script.
        # from django.conf import settings
        # call_command('runscript', 'utils.cronjob_update_endpoints')
        # # if settings.DEBUG:
        # #     try:
                
        # #         # call_command('runscript', 'utils.create_new_database')
        # #         pass
        # #     except:
        # #         pass  # Handle any expected exceptions or log errors as needed
