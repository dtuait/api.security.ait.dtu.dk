# app_mod/management/commands/regenerate_tokens.py

from django.core.management.base import BaseCommand
from app_mod.models import CustomToken

class Command(BaseCommand):
    help = 'Regenerates all existing tokens'

    def handle(self, *args, **kwargs):
        for token in CustomToken.objects.all():
            new_key = token.generate_key()  # Generate a new key
            # Explicitly update the key without creating a new instance
            CustomToken.objects.filter(pk=token.pk).update(key=new_key)
            self.stdout.write(self.style.SUCCESS(f'Regenerated token for user {token.user}'))
