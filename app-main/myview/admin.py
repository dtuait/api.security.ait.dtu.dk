from django.contrib import admin
from .models import UserProfile, Endpoint, EndpointPermission, AccessRequest, AccessRequestStatus
# from .models import (UserProfile, AccessControlType, Endpoint, AccessRequest, EndpointPermission, EndpointAccessControl)


# # Register your models here.
# admin.site.register(UserProfile)
# admin.site.register(AccessControlType)
admin.site.register(Endpoint) # shows list of endpoints
# admin.site.register(AccessRequest)
admin.site.register(EndpointPermission)
# admin.site.register(EndpointAccessControl)

class EndpointPermissionInline(admin.TabularInline):
    model = EndpointPermission
    extra = 1  # Specifies the number of blank forms the inline formset should display. Adjust as needed.



class UserProfileAdmin(admin.ModelAdmin):
    inlines = [EndpointPermissionInline,]
    list_display = ('user', 'id')  # Adjust list_display as needed for your use case

admin.site.register(UserProfile, UserProfileAdmin)



class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'endpoint', 'status', 'request_date')
    list_filter = ('status', 'request_date')
    search_fields = ('user_profile__user__username', 'endpoint__path')
    actions = ['approve_request', 'deny_request']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # This is the case when obj is already created i.e. it's an edit
            return 'user_profile', 'endpoint'
        else:
            return []

    def approve_request(self, request, queryset):
        """
        Custom admin action to approve selected requests.
        """
        queryset.update(status=AccessRequestStatus.GRANTED)

    approve_request.short_description = "Approve selected access requests"

    def deny_request(self, request, queryset):
        """
        Custom admin action to deny selected requests.
        """
        queryset.update(status=AccessRequestStatus.DENIED)

    deny_request.short_description = "Deny selected access requests"


    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'approve_request' in actions:
            del actions['approve_request']
        if 'deny_request' in actions:
            del actions['deny_request']
        # Add any other custom actions you wish to remove here
        return actions

admin.site.register(AccessRequest, AccessRequestAdmin)
# class AccessRequestInline(admin.TabularInline):
#     model = AccessRequest
#     extra = 1  # Determines the number of empty forms the formset displays.
#     # fields = ['organizational_unit', 'status']
#     # autocomplete_fields = ['organizational_unit']  # Use autocomplete for organizational_unit field if there are many instances.

# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user',)
#     inlines = [AccessRequestInline]
#     search_fields = ('user__username',)  # Enable search by user's username.




    # def get_ous(self, obj):
    #     return ", ".join([ou.canonical_name for ou in obj.ous.all()])
    # get_ous.short_description = 'Organizational Units'

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
