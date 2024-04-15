from django.contrib import admin
from django.http import HttpRequest
from django.contrib.admin.widgets import FilteredSelectMultiple

from django.db import models

import logging

logger = logging.getLogger(__name__)



# Attempt to import the ADGroup model
try:
    from .models import ADGroupAssociation

    @admin.register(ADGroupAssociation)
    class ADGroupAssociationAdmin(admin.ModelAdmin):
        list_display = ('cn', 'canonical_name', 'distinguished_name')  # Fields to display in the admin list view
        search_fields = ('cn', 'canonical_name')  # Fields to include in the search box in the admin
        filter_horizontal = ('members',)  # Provides a more user-friendly widget for ManyToMany relations
        readonly_fields = ('cn', 'canonical_name', 'distinguished_name')  # Fields that should be read-only in the admin

        def get_queryset(self, request):
            qs = super().get_queryset(request)
            return qs.prefetch_related('members')

        def has_delete_permission(self, request, obj=None):
            return False

        # def save_related(self, request, form, formsets, change):
        #     # super().save_related(request, form, formsets, change)
        #     # # After saving the form and related objects, sync the group members
        #     # if 'members' in form.changed_data:
        #     #     form.instance.sync_ad_group_members()
        #     pass





except ImportError:
    print("ADGroup model is not available for registration in the admin site.")
    pass




# Attempt to import the Endpoint model
try:
    from .models import Endpoint

    @admin.register(Endpoint)
    class EndpointAdmin(admin.ModelAdmin):
        list_display = ('path', 'method')
        search_fields = ('path', 'method')
        filter_horizontal = ('ad_groups',)  # Provides a more user-friendly widget for ManyToMany relations
        readonly_fields = ('path', 'method')

        # Use custom formfield for ManyToMany field to include filter interface
        formfield_overrides = {
            models.ManyToManyField: {'widget': FilteredSelectMultiple("Ad groups", is_stacked=False)},
        }

        def formfield_for_manytomany(self, db_field, request, **kwargs):
            if db_field.name == "ad_groups":
                selected_ad_groups = request.session.get('ajax_change_form_update_form_ad_groups', [])

                associated_ad_groups = ADGroupAssociation.objects.filter(endpoints__isnull=False).distinct()

                # Initial queryset based on selected ad groups or all associated groups
                if selected_ad_groups:
                    distinguishedNames = [group['distinguishedName'][0] for group in selected_ad_groups]
                    initial_queryset = db_field.related_model.objects.filter(distinguished_name__in=distinguishedNames)
                else:

                    initial_queryset = db_field.related_model.objects.all()[:100]


                # Get IDs from both querysets
                initial_ids = set(initial_queryset.values_list('id', flat=True))
                associated_ids = set(associated_ad_groups.values_list('id', flat=True))

                # Combine IDs and filter for unique objects
                all_ids = initial_ids | associated_ids
                combined_queryset = db_field.related_model.objects.filter(id__in=all_ids).distinct()

                kwargs["queryset"] = combined_queryset

                return super().formfield_for_manytomany(db_field, request, **kwargs)

        def has_delete_permission(self, request, obj=None):
            return False

except ImportError:
    print("Endpoint model is not available for registration in the admin site.")
    pass


# try:
#     from .models import Resource

#     @admin.register(Resource)
#     class ResourceAdmin(admin.ModelAdmin):
#         list_display = ('resource_path',)
#         search_fields = ('resource_path',)
#         filter_horizontal = ('ad_groups',)  # Provides a more user-friendly widget for ManyToMany relations
#         readonly_fields = ('resource_path',)

#         # Use custom formfield for ManyToMany field to include filter interface
#         formfield_overrides = {
#             models.ManyToManyField: {'widget': FilteredSelectMultiple("Ad groups", is_stacked=False)},
#         }

#         def formfield_for_manytomany(self, db_field, request, **kwargs):
#             if db_field.name == "ad_group_members":
#                 selected_ad_groups = request.session.get('ajax_change_form_update_form_ad_groups', [])

#                 associated_ad_groups = ADGroupAssociation.objects.filter(resources__isnull=False).distinct()

#                 # Initial queryset based on selected ad groups or all associated groups
#                 if selected_ad_groups:
#                     distinguishedNames = [group['distinguishedName'][0] for group in selected_ad_groups]
#                     initial_queryset = db_field.related_model.objects.filter(distinguished_name__in=distinguishedNames)
#                 else:
#                     initial_queryset = db_field.related_model.objects.all()[:100]

#                 # Get IDs from both querysets
#                 initial_ids = set(initial_queryset.values_list('id', flat=True))
#                 associated_ids = set(associated_ad_groups.values_list('id', flat=True))

#                 # Combine IDs and filter for unique objects
#                 all_ids = initial_ids | associated_ids
#                 combined_queryset = db_field.related_model.objects.filter(id__in=all_ids).distinct()

#                 kwargs["queryset"] = combined_queryset

#                 return super().formfield_for_manytomany(db_field, request, **kwargs)

#         def has_delete_permission(self, request, obj=None):
#             return False

# except ImportError:
#     print("Resource model is not available for registration in the admin site.")
#     pass