from django.contrib import admin
from .models import OrganizationalUnit, UserProfile, EndpointAccess
from django.db.models import Q
from django import forms






@admin.register(EndpointAccess)
class EndpointAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'endpoint', 'can_access')  # Displaying the fields in the list view.
    list_filter = ('user', 'can_access')  # Adding filters for the 'user' and 'can_access' fields.
    search_fields = ('user__username', 'endpoint')  # Adding a search bar for the 'user__username' and 'endpoint' fields.
















@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', )

    # ... your existing methods ...

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "ous":
            kwargs["queryset"] = OrganizationalUnit.objects.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    filter_horizontal = ('ous',)  # This makes it easier to manage many-to-many relationships in the admin interface.


# # Registering the UserProfile model for the admin site.
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', )

#     def get_ous(self, obj):
#         """Display the OUs associated with the user profile in a comma-separated string."""
#         return ", ".join([ou.name for ou in obj.ous.all()])
#     get_ous.short_description = 'Organizational Units'

#     filter_horizontal = ('ous',)  # This makes it easier to manage many-to-many relationships in the admin interface.








@admin.register(OrganizationalUnit)
class OrganizationalUnitAdmin(admin.ModelAdmin):
    list_display = ('datetime_created', 'datetime_modified', 'distinguished_name', 'canonical_name')
    search_fields = ('canonical_name',)

    def get_search_results(self, request, queryset, search_term):
        """
        Override the 'get_search_results' to implement an exact match search.
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            # Filter by exact match (case-insensitive)
            queryset = queryset.filter(canonical_name__exact=search_term)
        return queryset, use_distinct

# # Registering the OrganizationalUnit model for the admin site.
# @admin.register(OrganizationalUnit)
# class OrganizationalUnitAdmin(admin.ModelAdmin):
#     list_display = ('datetime_created', 'datetime_modified', 'distinguished_name', 'canonical_name')
#     search_fields = ('canonical_name',)
#     def get_search_results(self, request, queryset, search_term):
#         queryset, use_distinct = super().get_search_results(request, queryset, search_term)
#         if search_term:
#             queryset = queryset.filter(canonical_name=search_term)
#         return queryset, use_distinct



