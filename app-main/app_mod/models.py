# app_mod/models.py

from django.db import models
from rest_framework.authtoken.models import Token
import binascii
import os

class CustomToken(Token):

    class Meta:
        verbose_name = "MyToken"
        verbose_name_plural = "MyTokens"
    
    def generate_key(self):
        # Generate a longer and more complex token
        return binascii.hexlify(os.urandom(64)).decode()  # This creates a 128-character token

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)




# # models.py
# from django.db import models
# from rest_framework.authtoken.models import Token

# class CustomToken(Token):
#     key = models.CharField("Key", max_length=128, db_index=True, unique=True)

#     class Meta:
#         verbose_name = "Token"
#         verbose_name_plural = "Tokens"


# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth.models import User
# import binascii
# import os

# class CustomToken(models.Model):
#     key = models.CharField(_("Key"), max_length=128, null=False, blank=True, primary_key=True)
#     user = models.ForeignKey(
#         User, related_name='custom_auth_token',
#         on_delete=models.CASCADE, verbose_name=_("User")
#     )
#     created = models.DateTimeField(_("Created"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Token")
#         verbose_name_plural = _("Tokens")

#     def save(self, *args, **kwargs):
#         if not self.key:
#             self.key = self.generate_key()
#         return super().save(*args, **kwargs)

#     def generate_key(self):
#         return binascii.hexlify(os.urandom(64)).decode()  # generates a 128 character key

#     def __str__(self):
#         return self.key

