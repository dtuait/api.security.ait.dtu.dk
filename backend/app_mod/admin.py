# app_mod/admin.py

from django.contrib import admin
from rest_framework.authtoken.models import Token





# # If you have a custom token model, you can register it here as well
try: 


    from .models import CustomToken

    # Check if the Token model is registered before trying to unregister it
    if admin.site.is_registered(Token):
        admin.site.unregister(Token)

    @admin.register(CustomToken)
    class CustomTokenAdmin(admin.ModelAdmin):
        list_display = ('key', 'user', 'created')
        fields = ('user',)
        ordering = ('-created',)
        raw_id_fields = ('user',)
        autocomplete_fields = ['user']

        def get_queryset(self, request):
            qs = super().get_queryset(request).select_related('user')
            return qs

except ImportError:
    print("Endpoint model is not available for registration in the admin site.")
    pass