from django.contrib import admin
from .models import OrganizationalUnit, UserProfile, AccessRequest

# Registering the OrganizationalUnit model for the admin site.
@admin.register(OrganizationalUnit)
class OrganizationalUnitAdmin(admin.ModelAdmin):
    list_display = ('distinguished_name', 'canonical_name')  # Assuming you have these fields
    search_fields = ('canonical_name',)  # Users will be able to search by the canonical name

class AccessRequestInline(admin.TabularInline):
    model = AccessRequest
    extra = 1
    fields = ['organizational_unit', 'status']
    autocomplete_fields = ['organizational_unit']  # This enables a search box for the 'organizational_unit' field

# Registering the UserProfile model for the admin site.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_ous')
    inlines = [AccessRequestInline]

    def get_ous(self, obj):
        return ", ".join([ou.canonical_name for ou in obj.ous.all()])
    get_ous.short_description = 'Organizational Units'