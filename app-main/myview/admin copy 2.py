from django.contrib import admin








# Attempt to import the ADGroup model
try:
    from .models import ADGroupAssociation

    # @admin.register(ADGroupAssociation)
    # class ADGroupAssociationAdmin(admin.ModelAdmin):
    #     list_display = ('cn', 'canonical_name', 'distinguished_name', 'datetime_created', 'datetime_modified')
    #     filter_horizontal = ('members',)
    #     search_fields = ('cn', 'canonical_name', 'distinguished_name')
    #     list_filter = ('group_no_longer_exist_in_ad',)
    #     readonly_fields = ('cn', 'canonical_name', 'distinguished_name')

    #     def get_queryset(self, request):
    #         qs = super().get_queryset(request)
    #         # return qs.prefetch_related('users')
    #         return qs.prefetch_related('members')

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

        def get_queryset(self, request):
            qs = super().get_queryset(request)
            return qs.prefetch_related('ad_groups')

except ImportError:
    print("Endpoint model is not available for registration in the admin site.")
    pass
