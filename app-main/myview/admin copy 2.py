from django.contrib import admin
from django.http import HttpRequest
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import transaction
from django.db import models
from myview.models import ADGroupAssociation
from django.contrib.contenttypes.admin import GenericTabularInline
import logging
from django.contrib.contenttypes.models import ContentType
from django import forms

logger = logging.getLogger(__name__)




try:
    from .models import IPLimiter



except ImportError:
    print("IPLimiter model is not available for registration in the admin site.")
    pass




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




# 






# Attempt to import the Endpoint model
try:
    from .models import Endpoint, IPLimiter


    # class ResourceLimiterInline(GenericTabularInline):
    #     model = Endpoint.limiter.through
    #     ct_field = "limiter_type"
    #     ct_fk_field = "limiter_id"

    @admin.register(IPLimiter)
    class IPLimiterAdmin(admin.ModelAdmin):
        list_display = ('ip_address', 'description')
        search_fields = ('ip_address',)

    class EndpointAdminForm(forms.ModelForm):
        class Meta:
            model = Endpoint
            fields = '__all__'

        limiter_content_type = forms.ModelChoiceField(
            queryset=ContentType.objects.filter(model__in=['iplimiter']),
            required=False,
            label="Type of Limiter"
        )
        limiter_object_id = forms.IntegerField(
            required=False,
            label="ID of Limiter"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance and self.instance.limiter:
                self.fields['limiter_content_type'].initial = self.instance.limiter_type
                self.fields['limiter_object_id'].initial = self.instance.limiter_id

        def save(self, commit=True):
            model = super().save(commit=False)
            model.limiter_type = self.cleaned_data['limiter_content_type']
            model.limiter_id = self.cleaned_data['limiter_object_id']
            if commit:
                model.save()
            return model

    @admin.register(Endpoint)
    class EndpointAdmin(admin.ModelAdmin):
        list_display = ('path', 'method')
        search_fields = ('path', 'method')
        filter_horizontal = ('ad_groups',) 
        readonly_fields = ('path', 'method')
        

        
        formfield_overrides = {
            models.ManyToManyField: {'widget': FilteredSelectMultiple("Relationships", is_stacked=False)},
        }

        def save_model(self, request, obj, form, change):

            # Sync members for each group in ad_groups
            ad_groups = form.cleaned_data.get('ad_groups', [])
            for group in ad_groups:
                ADGroupAssociation.sync_ad_group_members(group)
                # get or create the group
                try:
                    ad_group_assoc, created = ADGroupAssociation.objects.get_or_create(
                        cn=group.cn,
                        canonical_name=group.canonical_name,
                        defaults={'distinguished_name': group.distinguished_name}
                    )
                except Exception as e:
                    print(f"Error creating ADGroupAssociation: {e}")
                # print ad_group_assoc creted true or false
                print(created)
                # add the group to the endpoint
                obj.ad_groups.add(ad_group_assoc)

            # Save the object again to save the changes to ad_groups
            obj.save()
            
            ADGroupAssociation.delete_unused_groups()

        def formfield_for_manytomany(self, db_field, request, **kwargs):
            if db_field.name == "ad_groups":
                return self._custom_field_logic(db_field, request, ADGroupAssociation, **kwargs)
            # elif db_field.name == "ad_organizational_units":
            #     return self._custom_field_logic(db_field, request, ADOrganizationalUnitAssociation, **kwargs)
            return super().formfield_for_manytomany(db_field, request, **kwargs)

        def _custom_field_logic(self, db_field, request, model_class, **kwargs):
            selected_items = request.session.get(f'ajax_change_form_update_form_{db_field.name}', [])
            associated_items = model_class.objects.filter(endpoints__isnull=False).distinct()
            
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
        


except ImportError:
    print("Endpoint model is not available for registration in the admin site.")
    pass





















































try:
    from .models import ADOrganizationalUnitLimiter
    from django.db.models import Q


    class ADOrganizationalUnitLimiterAdmin(admin.ModelAdmin):
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


    admin.site.register(ADOrganizationalUnitLimiter, ADOrganizationalUnitLimiterAdmin)

except ImportError:
    print("ADOU model is not available for registration in the admin site.")
    pass