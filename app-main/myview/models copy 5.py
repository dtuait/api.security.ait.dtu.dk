from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from active_directory.scripts.active_directory_query import active_directory_query
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class BaseModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class LimiterType(models.Model):
    """
    This model represents a type of limiter.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')
    
    # Content type and object ID for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'model__in': ['iplimiter', 'adorganizationalunitlimiter']})
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    # object_id = models.PositiveIntegerField(null=True, blank=True)
    # content_object = GenericForeignKey('content_type', 'object_id')
    
    def __str__(self):
        return self.name


class IPLimiter(BaseModel):
    """
    This model represents a type of limiter.
    """
    is_a_limiter = True
    ip_address = models.CharField(max_length=15)
    description = models.TextField(blank=True, default='')
    ad_groups = models.ManyToManyField('ADGroupAssociation', related_name='ip_limiters', blank=True)
    limiter_type = GenericRelation(LimiterType)

    class Meta:
        verbose_name = "IP Limiter"
        verbose_name_plural = "IP Limiters"

class ADOrganizationalUnitLimiter(BaseModel):
    """
    This model represents a type of limiter.
    """
    is_a_limiter = True
    canonical_name = models.CharField(max_length=1024)
    distinguished_name = models.CharField(max_length=1024)
    ad_groups = models.ManyToManyField('ADGroupAssociation', related_name='ad_organizational_unit_limiters', blank=True)
    limiter_type = GenericRelation(LimiterType)
    
    class Meta:
        verbose_name = "AD Organizational Unit Limiter"
        verbose_name_plural = "AD Organizational Unit Limiters"

# This model is used to associate AD groups with Django users
class ADGroupAssociation(BaseModel):
    """
    This model represents an association between an AD group and a Django user.
    """
    cn = models.CharField(max_length=255, verbose_name="Common Name")
    canonical_name = models.CharField(max_length=1024)
    distinguished_name = models.CharField(max_length=1024)
    members = models.ManyToManyField(User, related_name='ad_group_members')
    def __str__(self):
        return self.cn

    def sync_user_ad_groups(username):
        from active_directory.services import execute_active_directory_query
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.get(username=username)

        base_dn = "DC=win,DC=dtu,DC=dk"
        search_filter = f"(sAMAccountName={username})"
        search_attributes = ['memberOf']
        result = execute_active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

        if result and 'memberOf' in result[0]:
            ad_groups = set(result[0]['memberOf'])
        else:
            ad_groups = set()

        current_associations = set(user.ad_group_members.values_list('distinguished_name', flat=True))
        groups_to_add = ad_groups - current_associations
        groups_to_remove = current_associations - ad_groups

        # Add new group associations
        for group_dn in groups_to_add:
            group, created = ADGroupAssociation.objects.get_or_create(distinguished_name=group_dn)
            group.members.add(user)

        # Remove outdated group associations
        for group_dn in groups_to_remove:
            group = ADGroupAssociation.objects.get(distinguished_name=group_dn)
            group.members.remove(user)

        # Remove all groups not associated with any endpoint
        for group in ADGroupAssociation.objects.all():
            if not group.endpoints.exists():
                group.delete()

        user.save()
        user.refresh_from_db()
                 
    @staticmethod
    def delete_unused_groups():
        unused_ad_groups = ADGroupAssociation.objects.filter(endpoints__isnull=True)
        unused_ad_groups.delete()

    # This function gets all AD groups and syncs them with the database
    def sync_ad_groups(self):
        base_dn = "DC=win,DC=dtu,DC=dk"
        search_filter = "(objectClass=group)"
        search_attributes = ['cn', 'canonicalName', 'distinguishedName']

        try:
            ad_groups = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

            # Extract the associations into a dictionary
            associations = {}
            for group in ADGroupAssociation.objects.prefetch_related('endpoints'):
                associations[group.cn] = [endpoint.id for endpoint in group.endpoints.all()]

            ADGroupAssociation.objects.all().delete()

            with transaction.atomic():

                new_groups = []

                for group in ad_groups:
                    cn = group['cn'][0] if group['cn'][0] else ''
                    canonical_name = group['canonicalName'][0] if group['canonicalName'][0] else ''
                    distinguished_name = group['distinguishedName'][0] if group['distinguishedName'][0] else ''
   
                    # Prepare new group for creation
                    new_group = ADGroupAssociation(cn=cn, canonical_name=canonical_name, distinguished_name=distinguished_name)
                    new_groups.append(new_group)

                # Bulk create new groups and bulk update existing groups
                ADGroupAssociation.objects.bulk_create(new_groups)

                # Reapply the associations
                for group in ADGroupAssociation.objects.filter(cn__in=associations.keys()):
                    group.endpoints.set(Endpoint.objects.filter(id__in=associations[group.cn]))


            return True
        except Exception as e:
            print(f"An error occurred during sync ad groups operation: {e}")
            return False
  
    def escape_ldap_filter_chars(self, s):
        escape_chars = {
            '\\': r'\5c',
            '*': r'\2a',
            '(': r'\28',
            ')': r'\29',
            '\0': r'\00',
            '/': r'\2f',
        }
        for char, escaped_char in escape_chars.items():
            s = s.replace(char, escaped_char)
        return s
    

    def create_new_users_if_not_exists(self, users):
            try:
                User = get_user_model()
                new_users = []  # To collect new users                
                

                for user in users:
                    dn = user['distinguishedName'][0] if user['distinguishedName'] else ''
                    username = user['sAMAccountName'][0].lower() if user['sAMAccountName'] else ''
                    first_name = user['givenName'][0] if user['givenName'] else ''
                    last_name = user['sn'][0] if user['sn'] else ''

                    if dn and username:
                        # Check if the user exists in Django, and if not, create a new user instance
                        if not User.objects.filter(username=username).exists():
                            username_part = username.rsplit('-', 1)[-1]
                            email = f'{username_part}@dtu.dk'
                            is_superuser = username in ['adm-jaholm']
                            is_staff = is_superuser  # Typically, superusers are also staff
                            new_user = User(username=username, email=email, first_name=first_name, last_name=last_name, is_superuser=is_superuser, is_staff=is_staff)
                            new_users.append(new_user)
                User.objects.bulk_create(new_users)

                


            except Exception as error:
                print(f"An unexpected error occurred: {error}")


    def sync_ad_group_members(self):
            # print("Syncing AD group members...")
            base_dn = "DC=win,DC=dtu,DC=dk"
            search_filter = "(&(objectClass=user)(memberOf={}))".format(self.escape_ldap_filter_chars(self.distinguished_name))
            # search_attributes = ['distinguishedName', 'sAMAccountName']  # Include 'sAMAccountName' here
            search_attributes = ['distinguishedName', 'sAMAccountName', 'givenName', 'sn']

            try:
                # Perform the search on LDAP
                current_members = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

                

                # # filter out all users that does not startwith adm- or contians -adm-
                # current_members = [user for user in current_members if user['sAMAccountName'][0].lower().startswith('adm-') or '-adm-' in user['sAMAccountName'][0].lower()]
                
                self.create_new_users_if_not_exists(current_members)

                # remove all members from the group
                self.members.clear()

                # Fetch the current members of the group
                for user in current_members:
                    username = user['sAMAccountName'][0].lower()
                    user_instance = User.objects.filter(username=username).first()
                    if user_instance:
                        self.members.add(user_instance)
                

                

                # print("Syncing AD group members finished")


            except Exception as e:
                print(f"An error occurred during the LDAP operation: {e}")


    
    def add_member(self, user, admin_user):
        self.members.add(user)
        self.added_manually_by = admin_user
        self.save()



class Endpoint(BaseModel):
    path = models.CharField(max_length=255, unique=True)
    method = models.CharField(max_length=6, blank=True, default='')
    ad_groups = models.ManyToManyField('ADGroupAssociation', related_name='endpoints', blank=True)
    limiter_type = models.ForeignKey(LimiterType, on_delete=models.CASCADE, null=True, blank=True)
    # limiter_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    no_limit = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.method} {self.path}" if self.method else self.path

    def validate_and_get_ad_groups_for_user_access(self, user, endpoint_path):
        # Fetch the endpoint instance based on the provided path.
        try:
            endpoint = Endpoint.objects.get(path=endpoint_path)
        except Endpoint.DoesNotExist:
            return False, None  # No access since the endpoint does not exist.

        # Check if the user is in any group that is associated with the endpoint.
        user_groups = user.ad_group_members.all()
        access_granting_groups = []
        for group in user_groups:
            if endpoint.ad_groups.filter(pk=group.pk).exists():
                access_granting_groups.append(group)

        if access_granting_groups:
            return True, access_granting_groups  # Return True and the groups that grant access
        else:
            return False, None  # No access granted


