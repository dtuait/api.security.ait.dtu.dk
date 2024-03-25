from django.contrib import admin








# Attempt to import the ADGroup model
try:
    from .models import ADGroupAssociation

    @admin.register(ADGroupAssociation)
    class ADGroupAssociationAdmin(admin.ModelAdmin):
        list_display = ('cn', 'canonical_name', 'distinguished_name', 'datetime_created', 'datetime_modified')
        filter_horizontal = ('members',)
        search_fields = ('cn', 'canonical_name', 'distinguished_name')
        readonly_fields = ('cn', 'canonical_name', 'distinguished_name')

        def get_queryset(self, request):
            qs = super().get_queryset(request)
            return qs.prefetch_related('members')

        def save_related(self, request, form, formsets, change):
            super().save_related(request, form, formsets, change)
            # After saving the form and related objects, sync the group members
            if 'members' in form.changed_data:
                form.instance.sync_ad_group_members()

  
except ImportError:
    print("ADGroup model is not available for registration in the admin site.")
    pass




# Attempt to import the Endpoint model
try:
    from .models import Endpoint

    @admin.register(Endpoint)
    class EndpointAdmin(admin.ModelAdmin):
        list_display = ('path', 'method', 'datetime_created', 'datetime_modified')
        search_fields = ('path', 'method')
        list_filter = ('method',)
        readonly_fields = ('datetime_created', 'datetime_modified', 'path', 'method')
        # Specify which fields should have an autocomplete widget
        autocomplete_fields = ['ad_groups']

        def get_queryset(self, request):
            # Prefetch ad_groups to optimize database queries
            qs = super().get_queryset(request).prefetch_related('ad_groups')
            return qs

        def formfield_for_manytomany(self, db_field, request, **kwargs):
            # If the field is 'ad_groups', limit the initial queryset to none
            if db_field.name == "ad_groups":
                kwargs["queryset"] = ADGroupAssociation.objects.none()
            return super().formfield_for_manytomany(db_field, request, **kwargs)


except ImportError:
    print("Endpoint model is not available for registration in the admin site.")
    pass







try:
    from .models import EndpointPermission

    @admin.register(EndpointPermission)
    class EndpointPermissionAdmin(admin.ModelAdmin):
        list_display = ('ad_group', 'endpoint', 'can_access')
        list_filter = ('can_access',)
        search_fields = ('ad_group__cn', 'endpoint__path')
        autocomplete_fields = ['ad_group']
        

except ImportError:
    print("EndpointPermission model is not available for registration in the admin site.")
    pass















# # Attempt to import the Endpoint model
# try:
#     from .models import Endpoint

#     @admin.register(Endpoint)
#     class EndpointAdmin(admin.ModelAdmin):
#         list_display = ('path', 'method', 'datetime_created', 'datetime_modified')
#         search_fields = ('path', 'method')
#         list_filter = ('method',)
#         filter_horizontal = ('ad_groups',)
#         readonly_fields = ('datetime_created', 'datetime_modified', 'path', 'method')

#         def get_queryset(self, request):
#             # Prefetch ad_groups to optimize database queries
#             qs = super().get_queryset(request).prefetch_related('ad_groups')
#             return qs


# except ImportError:
#     print("Endpoint model is not available for registration in the admin site.")
#     pass
