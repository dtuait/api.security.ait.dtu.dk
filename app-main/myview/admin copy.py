from django.contrib import admin
from django.http import HttpRequest
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import transaction
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

        def save_model(self, request, obj, form, change):




            # Get the selected objects for the 'relationships' field
            selected_relationships = form.cleaned_data.get('relationships', [])

            # Now 'selected_relationships' is a list of the selected objects
            for relationship in selected_relationships:
                # You can access the fields of each selected object
                print(relationship.some_field)
            # Use a transaction to ensure that all database operations are completed
            with transaction.atomic():
                # Save the endpoint first
                super().save_model(request, obj, form, change)
                # This will force the transaction to commit here
                


            # Call the method to delete unused groups
            self.delete_unused_groups()

            # for each group in ad_groups, sync the members
            from .models import ADGroupAssociation

            # Sync members for each group in ad_groups
            ad_groups = form.cleaned_data.get('ad_groups', [])
            for group in ad_groups:
                ADGroupAssociation.sync_ad_group_members(group)

            with transaction.atomic():
                # Save the endpoint first
                super().save_model(request, obj, form, change)
                # This will force the transaction to commit here

            


        def delete_unused_groups(self):


            
            used_ad_groups = ADGroupAssociation.objects.exclude(endpoints__isnull=True)

            # Delete groups no longer linked to any Endpoint
            # This assumes there is a reverse relation `endpoints` from ADGroupAssociation to Endpoint
            unused_ad_groups = ADGroupAssociation.objects.filter(endpoints__isnull=True)
            unused_ad_groups.delete()
            pass


            


        def formfield_for_manytomany(self, db_field, request, **kwargs):
            if db_field.name == "ad_groups":
                return self._custom_field_logic(db_field, request, ADGroupAssociation, **kwargs)
            elif db_field.name == "ad_organizational_units":
                return self._custom_field_logic(db_field, request, ADOrganizationalUnitAssociation, **kwargs)
            return super().formfield_for_manytomany(db_field, request, **kwargs)

        def _custom_field_logic(self, db_field, request, model_class, **kwargs):
            selected_items = request.session.get(f'ajax_change_form_update_form_{db_field.name}', [])
            associated_items = model_class.objects.filter(endpoints__isnull=False).distinct()

            # get or create ADGroupAssociation object if not exist 
            # class ADGroupAssociation(BaseModel):
                # cn = models.CharField(max_length=255, verbose_name="Common Name") # selected_items[0]['cn'][0] >> 'MEK-SN-Test'                               
                # canonical_name = models.CharField(max_length=1024) # selected_items[0]['canonicalName'][0] >> 'win.dtu.dk/Institutter/CME/Distribution group/MEK-SN-Test'
                # # distinguished_name = models.CharField(max_length=1024) # selected_items[0]['distinguishedName'][0] >> 'CN=MEK-SN-Test,OU=Distribution group,OU=CME,OU=Institutter,DC=win,DC=dtu,DC=dk'
                # members = models.ManyToManyField(User, related_name='ad_group_members')
            
            for item in selected_items:
                ad_group_assoc, created = ADGroupAssociation.objects.get_or_create(
                    cn=item['cn'][0],
                    canonical_name=item['canonicalName'][0],
                    defaults={'distinguished_name': item['distinguishedName'][0]}
                )
            
            



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
        
        # def save_model(self, request, obj, form, change):
        #     super().save_model(request, obj, form, change)
        #     # After saving the form, delete the groups that are no longer associated
        #     obj.delete_unused_groups()

        
        # def save_related(self, request, form, formsets, change):
        #     # super().save_related(request, form, formsets, change)
        #     # # After saving the form and related objects, sync the group members
        #     # if 'members' in form.changed_data:
        #     #     form.instance.sync_ad_group_members()
        #     pass


except ImportError:
    print("Endpoint model is not available for registration in the admin site.")
    pass
