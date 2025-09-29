from django.apps import AppConfig
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError
import logging


logger = logging.getLogger(__name__)


class MyviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myview'

    def ready(self):
        self._register_ad_group_sync()
        self._register_endpoint_refresh()
        self._refresh_api_endpoints()

    def _register_ad_group_sync(self):
        """Ensure AD groups are synced at startup and after migrations."""

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

            post_migrate.connect(
                _post_migrate_sync,
                sender=self,
                dispatch_uid="myview_post_migrate_sync",
            )
        except Exception:
            logger.exception("Failed to register AD group sync hooks in AppConfig.ready()")

    def _register_endpoint_refresh(self):
        """Register a post-migrate hook to refresh API endpoints automatically."""

        try:
            from django.db.models.signals import post_migrate

            def _post_migrate_refresh(sender, **kwargs):
                self._refresh_api_endpoints()

            post_migrate.connect(
                _post_migrate_refresh,
                sender=self,
                dispatch_uid="myview_post_migrate_endpoint_refresh",
            )
        except Exception:
            logger.exception("Failed to register endpoint refresh hook")

    def _refresh_api_endpoints(self):
        """Populate the Endpoint table from the current OpenAPI schema."""

        try:
            from utils.cronjob_update_endpoints import updateEndpoints
        except Exception:
            logger.exception("Unable to import endpoint updater")
            return

        from django.apps import apps as django_apps
        from django.db import connection
        from django.db.utils import OperationalError, ProgrammingError

        try:
            Endpoint = django_apps.get_model("myview", "Endpoint")
        except LookupError:
            logger.info("Endpoint model not available; skipping endpoint refresh")
            return

        # Ensure the table exists before attempting to update.
        try:
            with connection.cursor():
                table_names = set(connection.introspection.table_names())
            if Endpoint._meta.db_table not in table_names:
                return
        except (OperationalError, ProgrammingError):
            logger.info("Skipping endpoint refresh; database not ready")
            return
        except Exception:
            logger.exception("Failed while checking Endpoint table availability")
            return

        try:
            updateEndpoints()
        except Exception:
            logger.exception("Automatic endpoint refresh failed")
