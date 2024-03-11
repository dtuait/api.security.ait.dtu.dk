# from django.contrib import admin
# from .models import OrganizationalUnit, UserProfile, AccessRequest, Endpoint, EndpointPermission

# class AccessRequestInline(admin.TabularInline):
#     model = AccessRequest
#     extra = 1  # Determines the number of empty forms the formset displays.
#     fields = ['organizational_unit', 'status']
#     autocomplete_fields = ['organizational_unit']  # Use autocomplete for organizational_unit field if there are many instances.

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'get_ous')
#     inlines = [AccessRequestInline]
#     search_fields = ('user__username',)  # Enable search by user's username.

#     def get_ous(self, obj):
#         return ", ".join([ou.canonical_name for ou in obj.ous.all()])
#     get_ous.short_description = 'Organizational Units'

# # Existing admin registrations...

# @admin.register(Endpoint)
# class EndpointAdmin(admin.ModelAdmin):
#     list_display = ('path', 'method', 'display_organizational_units')
#     search_fields = ('path', 'method')
#     filter_horizontal = ('organizational_units',)

#     def display_organizational_units(self, obj):
#         return ", ".join([ou.canonical_name for ou in obj.organizational_units.all()])
#     display_organizational_units.short_description = 'Organizational Units'

# @admin.register(EndpointPermission)
# class EndpointPermissionAdmin(admin.ModelAdmin):
#     list_display = ('user_profile', 'endpoint', 'can_access', 'display_datetime_created')
#     list_filter = ('can_access',)
#     search_fields = ('user_profile__user__username', 'endpoint__path')
#     autocomplete_fields = ['user_profile', 'endpoint']  # Enables search rather than dropdown

#     def display_datetime_created(self, obj):
#         return obj.datetime_created.strftime("%Y-%m-%d %H:%M:%S")
#     display_datetime_created.short_description = 'Created At'


# # Registering the OrganizationalUnit model for the admin site.
# # @admin.register(OrganizationalUnit)
# # class OrganizationalUnit(models.Model):
# #     distinguished_name = models.TextField(unique=True)
# #     canonical_name = models.TextField(unique=True, default="")

# #     class Meta:
# #         ordering = ['canonical_name']  # Add default ordering here

# #     def __str__(self):
# #         return self.canonical_name
    


# # Registering the OrganizationalUnit model for the admin site.
# @admin.register(OrganizationalUnit)
# class OrganizationalUnitAdmin(admin.ModelAdmin):
#     list_display = ('distinguished_name', 'canonical_name')
#     search_fields = ('canonical_name',)