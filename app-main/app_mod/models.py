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


