from django.contrib import admin
from .models import OrganizationalUnit, UserProfile

# Registering the OrganizationalUnit model for the admin site.
@admin.register(OrganizationalUnit)
class OrganizationalUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Displaying the 'name' field in the list view.
    search_fields = ('name',)  # Adding a search bar for the 'name' field.

# Registering the UserProfile model for the admin site.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_ous')

    def get_ous(self, obj):
        """Display the OUs associated with the user profile in a comma-separated string."""
        return ", ".join([ou.name for ou in obj.ous.all()])
    get_ous.short_description = 'Organizational Units'

    filter_horizontal = ('ous',)  # This makes it easier to manage many-to-many relationships in the admin interface.
