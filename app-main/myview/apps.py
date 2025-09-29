
from django.apps import AppConfig
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError
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

            def _tables_ready():
                """Check whether our key tables exist before attempting sync."""
                try:
                    with connection.cursor() as cursor:
                        tables = connection.introspection.table_names(cursor)
                except (ProgrammingError, OperationalError):
                    return False
                return 'myview_adgroupassociation' in tables

            # Ensure initial sync on app startup (cached/throttled)
            if _tables_ready():
                try:
                    ADGroupAssociation.ensure_groups_synced_cached()
                except Exception:
                    logger.exception("Initial cached AD group sync in AppConfig.ready() failed")
            else:
                logger.info("Skipping initial AD group sync until migrations are applied")

            # Ensure sync after migrations to reflect new schema
            def _post_migrate_sync(sender, **kwargs):
                try:
                    if not _tables_ready():
                        logger.info("Skipping post-migrate AD group sync; tables not ready")
                        return

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
