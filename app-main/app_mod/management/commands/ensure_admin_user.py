import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a Django admin account from environment variables."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_ADMIN_USERNAME")
        password = os.getenv("DJANGO_ADMIN_PASSWORD")
        email = os.getenv("DJANGO_ADMIN_EMAIL")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_ADMIN_USERNAME or DJANGO_ADMIN_PASSWORD not set; skipping admin bootstrap."
                )
            )
            return

        if not email:
            email = f"{username}@example.com"

        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        updated = False

        if created:
            updated = True

        if not user.is_staff:
            user.is_staff = True
            updated = True

        if not user.is_superuser:
            user.is_superuser = True
            updated = True

        if not user.check_password(password):
            user.set_password(password)
            updated = True

        if not user.email and email:
            user.email = email
            updated = True

        if updated:
            user.save()
            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(f"{action} admin user '{username}' from environment variables.")
            )
        else:
            self.stdout.write(f"Admin user '{username}' already up to date; no changes applied.")
