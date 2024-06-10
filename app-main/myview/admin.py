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
        list_display = ('canonical_name', 'distinguished_name', 'member_count')  # Fields to display in the admin list view
        search_fields = ('canonical_name',)
        filter_horizontal = ('members',)  # Provides a more user-friendly widget for ManyToMany relations
        readonly_fields = ('canonical_name', 'distinguished_name', 'member_count')  # Fields that should be read-only in the admin
        list_per_page = 40

        def get_queryset(self, request):
            qs = super().get_queryset(request)
            return qs.prefetch_related('members')

        def has_delete_permission(self, request, obj=None):
            return True
        
        def has_add_permission(self, request, obj=None):
            return False
        
        def get_readonly_fields(self, request, obj=None):
            if obj:  # This is the case when obj is already created i.e. it's an edit
                return self.readonly_fields + ('members',)
            return self.readonly_fields
        
        def member_count(self, obj):
            return obj.members.count()
        member_count.short_description = 'Member Count'

except ImportError:
    print("ADGroup model is not available for registration in the admin site.")
    pass




try:
    from .models import LimiterType
    @admin.register(LimiterType)
    class LimiterTypeAdmin(admin.ModelAdmin):
        list_display = ('content_type',)
        search_fields = ('name',)
        def save_model(self, request, obj, form, change):
            obj.name = obj.content_type.model_class()._meta.verbose_name
            obj.description = obj.content_type.model_class().__doc__
            super().save_model(request, obj, form, change)


except ImportError:
    print("Limiter type model is not available for registration in the admin site.")
    pass








# Attempt to import the Endpoint model
try:
    from .models import Endpoint


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
        
        def has_add_permission(self, request):
            return False
        



except ImportError:
    print("Endpoint model is not available for registration in the admin site.")
    pass





















































try:
    from .models import ADOrganizationalUnitLimiter
    from django.db.models import Q

    from django.contrib import admin
    from django.db.models import Q
    from django.contrib.admin.widgets import FilteredSelectMultiple
    from django.db import models

    from django.contrib import admin
    from .models import ADOrganizationalUnitLimiter

    @admin.register(ADOrganizationalUnitLimiter)
    class ADOrganizationalUnitLimiterAdmin(admin.ModelAdmin):
        list_display = ('canonical_name', 'distinguished_name','member_count')
        search_fields = ('canonical_name', 'distinguished_name')
        filter_horizontal = ('ad_groups',)  
        list_per_page = 10  # Display 10 objects per page

        def has_delete_permission(self, request, obj=None):
            return False
        
        def has_add_permission(self, request, obj=None):
            return False
        
        def member_count(self, obj):
            return sum(group.members.count() for group in obj.ad_groups.all())  # Correctly counts the members in all ad_groups
        member_count.short_description = 'Member Count'
except ImportError:
    print("ADOU model is not available for registration in the admin site.")
    pass