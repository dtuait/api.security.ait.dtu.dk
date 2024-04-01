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
                # delete session variable
                # del request.session['ajax_change_form_update_form_ad_groups']
                if selected_ad_groups:
                    # type(selected_ad_groups) >> <class 'list'>
                    # len(selected_ad_groups) >> 100
                    # selected_ad_groups[0]['distinguishedName'] >> CN=MEK-SN-Test,OU=Distribution group,OU=CME,OU=Institutter,DC=win,DC=dtu,DC=dk
                    # selected_ad_groups[0]['canonicalName'] >> win.dtu.dk/Institutter/CME/Distribution group/MEK-SN-Test
                    # selected_ad_groups[0]['cn'] >> MEK-SN-Test
                    # Extracting 'distinguishedName' from each group as it's a unique identifier in AD

                    # The model that i am trying to filter is as follows:
                    # class Endpoint(BaseModel):
                    #     path = models.CharField(max_length=255, unique=True)
                    #     method = models.CharField(max_length=6, blank=True, default='')
                    #     ad_groups = models.ManyToManyField('ADGroupAssociation', related_name='endpoints')
                    #     def __str__(self):
                    #         return f"{self.method} {self.path}" if self.method else self.path

                    # class ADGroupAssociation(BaseModel):
                    #     cn = models.CharField(max_length=255, verbose_name="Common Name")
                    #     canonical_name = models.CharField(max_length=1024)
                    #     distinguished_name = models.CharField(max_length=1024)
                    #     members = models.ManyToManyField(User, related_name='ad_groups')
                    #     def __str__(self):
                    #         return self.cn

                    # The model that i am trying to filter is as follows:
                    distinguishedNames = [group['distinguishedName'][0] for group in selected_ad_groups]
                    # len(distinguishedNames) >> 100
                    # distinguishedNames[0][0] >> 'CN=KI-BYG,OU=Security group,OU=KEMI,OU=Institutter,DC=win,DC=dtu,DC=dk'
                    # distinguishedNames[1][0] >> 'CN=KEMI-L-Bygningscenter-1448,OU=SecurityGroups,OU=KEMI,OU=DTUBasen,DC=win,DC=dtu,DC=dk'
                    #
                    # add all these ADGroupAssociation objects to the queryset that have the distinguishedName in the list distinguishedNames
                    # db_field.related_model.objects.filter(distinguished_name__in=distinguishedNames) >> <QuerySet []> Why is it empty?!
                    kwargs["queryset"] = db_field.related_model.objects.filter(distinguished_name__in=distinguishedNames)

                    # distinguishedNames[0][0] >> 
                    # SELECT distinguished_name FROM `myview_adgroupassociation` WHERE distinguished_name = 'CN=CME-ITAdm,OU=ITAdmSecurityGroups,OU=Delegations and Security,DC=win,DC=dtu,DC=dk';
                    # >> CN=CME-ITAdm,OU=ITAdmSecurityGroups,OU=Delegations and Security,DC=win,DC=dtu,DC=dk


                else:
                    kwargs["queryset"] = db_field.related_model.objects.all()[:100]
                return super().formfield_for_manytomany(db_field, request, **kwargs)

        def has_delete_permission(self, request, obj=None):
            return False

except ImportError:
    print("Endpoint model is not available for registration in the admin site.")
    pass


