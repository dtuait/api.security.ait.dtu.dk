from django.contrib import admin
from .models import OrganizationalUnit, UserProfile, AccessRequest, Endpoint, EndpointPermission

# Registering the OrganizationalUnit model for the admin site.
@admin.register(OrganizationalUnit)
class OrganizationalUnitAdmin(admin.ModelAdmin):
    list_display = ('distinguished_name', 'canonical_name')
    search_fields = ('canonical_name',)

class AccessRequestInline(admin.TabularInline):
    model = AccessRequest
    extra = 1
    fields = ['organizational_unit', 'status']
    autocomplete_fields = ['organizational_unit']

# Registering the UserProfile model for the admin site.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_ous')
    inlines = [AccessRequestInline]

    def get_ous(self, obj):
        return ", ".join([ou.canonical_name for ou in obj.ous.all()])
    get_ous.short_description = 'Organizational Units'

# Registering the AccessRequest model for the admin site.
# Since AccessRequest is used as an inline for UserProfile, you might not need to register it separately.
# However, if you want it to be directly accessible from the admin, you can uncomment the following:
# admin.site.register(AccessRequest)

# Registering the Endpoint model for the admin site.
@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    list_display = ('path', 'method', 'display_organizational_units')
    search_fields = ('path', 'method')
    filter_horizontal = ('organizational_units',)

    def display_organizational_units(self, obj):
        return ", ".join([ou.canonical_name for ou in obj.organizational_units.all()])
    display_organizational_units.short_description = 'Organizational Units'

# Registering the EndpointPermission model for the admin site.
@admin.register(EndpointPermission)
class EndpointPermissionAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'endpoint', 'can_access', 'display_datetime_created')
    list_filter = ('can_access',)
    search_fields = ('user_profile__user__username', 'endpoint__path')

    def display_datetime_created(self, obj):
        return obj.datetime_created.strftime("%Y-%m-%d %H:%M:%S")
    display_datetime_created.short_description = 'Created At'

