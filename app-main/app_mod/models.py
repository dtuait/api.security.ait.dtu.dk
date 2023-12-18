# app_mod/models.py

# from django.db import models
# from rest_framework.authtoken.models import Token
# import binascii
# import os
# from django.contrib.auth.models import User


# class CustomToken(Token):
#     extended_key = models.CharField("Extended Key", max_length=128, db_index=True, unique=True)


#     class Meta:
#         verbose_name = "Custom Token"
#         verbose_name_plural = "Custom Tokens"
    
#     def generate_key(self):
#         # Generate a longer and more complex token
#         return binascii.hexlify(os.urandom(64)).decode()  # This creates a 128-character token

#     def save(self, *args, **kwargs):
#         if not self.key:
#             self.key = self.generate_key()
#         return super().save(*args, **kwargs)


from django.db import models
from rest_framework.authtoken.models import Token
import binascii
import os
from django.contrib.auth.models import User


# Ensure you have the correct length set for your token key field.
class CustomToken(Token):
    # key = models.CharField("Key", max_length=128, primary_key=True)
    # extended_key = models.CharField("Extended Key", max_length=128, db_index=True, unique=True)

    class Meta:
        verbose_name = "Custom Token"
        verbose_name_plural = "Custom Tokens"
    
    def generate_key(self):
        # Generate a longer and more complex token
        return binascii.hexlify(os.urandom(128)).decode()[:255]  # This creates a 255-character token

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

# Now, outside of your CustomToken class definition, you can alter the field like this:
CustomToken._meta.get_field('key').max_length = 255




# class OrganizationalUnit(models.Model):
#     name = models.TextField(unique=True)  # The full OU string, e.g. "OU=AIT,OU=ITAdmUsers,OU=Delegations..."

#     # String representation for easier debugging.
#     def __str__(self):
#         return self.name

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     ous = models.ManyToManyField(OrganizationalUnit)

#     def __str__(self):
#         return self.user.username
