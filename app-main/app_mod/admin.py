# app_mod/admin.py

from django.contrib import admin
from rest_framework.authtoken.models import Token



# Check if the Token model is registered before trying to unregister it
if admin.site.is_registered(Token):
    admin.site.unregister(Token)

# # If you have a custom token model, you can register it here as well
from .models import CustomToken

@admin.register(CustomToken)
class CustomTokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created')
    fields = ('user',)
    ordering = ('-created',)