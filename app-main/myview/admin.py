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
        list_per_page = 10

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

try:
    from .models import ADOrganizationalUnitAssociation
    from django.db.models import Q


    class ADOrganizationalUnitAssociationAdmin(admin.ModelAdmin):
        list_display = ('distinguished_name',)
        search_fields = ('distinguished_name',)
        # list_filter = ('distinguished_name',)
        list_per_page = 10  # Display 10 objects per page

        def get_queryset(self, request):
            qs = super().get_queryset(request)
            return qs.prefetch_related('members')

        def get_search_results(self, request, queryset, search_term):
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)
            queryset = queryset.filter(Q(distinguished_name__startswith=search_term))
            return queryset, use_distinct

        def has_delete_permission(self, request, obj=None):
            return False








    # class ADOrganizationalUnitAssociationAdmin(admin.ModelAdmin):
    #     list_display = ('distinguished_name',)  # Fields to display in list view
    #     search_fields = ('distinguished_name',)  # Fields to search in search bar
    #     list_filter = ('distinguished_name',)  # Fields to filter by

    #     def get_queryset(self, request):
    #         qs = super().get_queryset(request)
    #         if request.path.endswith('/adorganizationalunitassociation/'):
    #             return qs.prefetch_related('members')[:100]
    #         return qs.prefetch_related('members')

    #     def get_search_results(self, request, queryset, search_term):
    #         queryset, use_distinct = super().get_search_results(request, queryset, search_term)
    #         queryset = queryset.filter(Q(distinguished_name__startswith=search_term))
    #         return queryset, use_distinct

    #     def has_delete_permission(self, request, obj=None):
    #         return False

    # class ADOrganizationalUnitAssociationAdmin(admin.ModelAdmin):
    #     list_display = ('distinguished_name',)  # Fields to display in list view
    #     search_fields = ('distinguished_name',)  # Fields to search in search bar
    #     list_filter = ('distinguished_name',)  # Fields to filter by

    #     def get_queryset(self, request):
    #         qs = super().get_queryset(request)
    #         return qs.prefetch_related('members')

    #     def get_search_results(self, request, queryset, search_term):
    #         queryset, use_distinct = super().get_search_results(request, queryset, search_term)
    #         queryset = queryset.filter(Q(distinguished_name__startswith=search_term))
    #         return queryset, use_distinct  # Removed slice

    #     def changelist_view(self, request, extra_context=None):
    #         response = super().changelist_view(request, extra_context)
    #         try:
    #             response.context_data['cl'].result_list = response.context_data['cl'].result_list[:3]
    #         except (AttributeError, KeyError):
    #             pass
    #         return response

    # def has_delete_permission(self, request, obj=None):
    #     return False

    admin.site.register(ADOrganizationalUnitAssociation, ADOrganizationalUnitAssociationAdmin)

except ImportError:
    print("ADOU model is not available for registration in the admin site.")
    pass






# Attempt to import the Endpoint model
try:
    from .models import Endpoint






    @admin.register(Endpoint)
    class EndpointAdmin(admin.ModelAdmin):
        list_display = ('path', 'method')
        search_fields = ('path', 'method')
        filter_horizontal = ('ad_groups', 'ad_organizational_units')  # Add 'ad_organizational_units' here
        readonly_fields = ('path', 'method')

        formfield_overrides = {
            models.ManyToManyField: {'widget': FilteredSelectMultiple("Relationships", is_stacked=False)},
        }

        def formfield_for_manytomany(self, db_field, request, **kwargs):
            if db_field.name == "ad_groups":
                return self._custom_field_logic(db_field, request, ADGroupAssociation, **kwargs)
            elif db_field.name == "ad_organizational_units":
                return self._custom_field_logic(db_field, request, ADOrganizationalUnitAssociation, **kwargs)
            return super().formfield_for_manytomany(db_field, request, **kwargs)

        def _custom_field_logic(self, db_field, request, model_class, **kwargs):
            selected_items = request.session.get(f'ajax_change_form_update_form_{db_field.name}', [])
            associated_items = model_class.objects.filter(endpoints__isnull=False).distinct()

            if selected_items:
                distinguished_names = [item['distinguishedName'][0] for item in selected_items]
                initial_queryset = db_field.related_model.objects.filter(distinguished_name__in=distinguished_names)
            else:
                initial_queryset = db_field.related_model.objects.all()[:100]

            initial_ids = set(initial_queryset.values_list('id', flat=True))
            associated_ids = set(associated_items.values_list('id', flat=True))
            all_ids = initial_ids | associated_ids
            combined_queryset = db_field.related_model.objects.filter(id__in=all_ids).distinct()

            kwargs["queryset"] = combined_queryset
            return super().formfield_for_manytomany(db_field, request, **kwargs)

        def has_delete_permission(self, request, obj=None):
            return False










    # @admin.register(Endpoint)
    # class EndpointAdmin(admin.ModelAdmin):
    #     list_display = ('path', 'method')
    #     search_fields = ('path', 'method')
    #     filter_horizontal = ('ad_groups',)  # Provides a more user-friendly widget for ManyToMany relations
    #     readonly_fields = ('path', 'method')

    #     # Use custom formfield for ManyToMany field to include filter interface
    #     formfield_overrides = {
    #         models.ManyToManyField: {'widget': FilteredSelectMultiple("Ad groups", is_stacked=False)},
    #     }

    #     def formfield_for_manytomany(self, db_field, request, **kwargs):
    #         if db_field.name == "ad_groups":
    #             selected_ad_groups = request.session.get('ajax_change_form_update_form_ad_groups', [])

    #             associated_ad_groups = ADGroupAssociation.objects.filter(endpoints__isnull=False).distinct()

    #             # Initial queryset based on selected ad groups or all associated groups
    #             if selected_ad_groups:
    #                 distinguishedNames = [group['distinguishedName'][0] for group in selected_ad_groups]
    #                 initial_queryset = db_field.related_model.objects.filter(distinguished_name__in=distinguishedNames)
    #             else:

    #                 initial_queryset = db_field.related_model.objects.all()[:100]


    #             # Get IDs from both querysets
    #             initial_ids = set(initial_queryset.values_list('id', flat=True))
    #             associated_ids = set(associated_ad_groups.values_list('id', flat=True))

    #             # Combine IDs and filter for unique objects
    #             all_ids = initial_ids | associated_ids
    #             combined_queryset = db_field.related_model.objects.filter(id__in=all_ids).distinct()

    #             kwargs["queryset"] = combined_queryset

    #             return super().formfield_for_manytomany(db_field, request, **kwargs)

    #     def has_delete_permission(self, request, obj=None):
    #         return False

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