# # app_mod/management/commands/regenerate_tokens.py

# from django.core.management.base import BaseCommand
# from app_mod.models import CustomToken

# class Command(BaseCommand):
#     help = 'Regenerates all existing tokens'

#     def handle(self, *args, **kwargs):
#         for token in CustomToken.objects.all():
#             new_key = token.generate_key()  # Generate a new key
#             # Explicitly update the key without creating a new instance
#             CustomToken.objects.filter(pk=token.pk).update(key=new_key)
#             self.stdout.write(self.style.SUCCESS(f'Regenerated token for user {token.user}'))



from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app_mod.models import CustomToken

class Command(BaseCommand):
    help = 'Regenerates all existing tokens'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            # Check if the user already has a token
            if not CustomToken.objects.filter(user=user).exists():
                continue  # Skip to the next user if no token exists

            # Delete existing token for the user
            CustomToken.objects.filter(user=user).delete()

            # Create a new token for the user
            new_token = CustomToken.objects.create(user=user)

            self.stdout.write(self.style.SUCCESS(f'Regenerated token for user {user.username}'))
