from rest_framework.authtoken.models import Token
import binascii
import os
from django.contrib.auth.models import User

# Ensure you have the correct length set for your token key field.
class CustomToken(Token):

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
    
def set_my_token(self, token):
    if len(token) != 255:
        raise ValueError("Token must be 255 characters long")
    CustomToken.objects.update_or_create(user=self, defaults={'key': token})


# Now, outside of your CustomToken class definition, you can alter the field like this:
CustomToken._meta.get_field('key').max_length = 255
User.add_to_class('set_my_token', set_my_token)
