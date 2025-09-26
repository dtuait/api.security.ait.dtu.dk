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
from django.core.exceptions import ValidationError

class BaseModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True





class IPLimiter(BaseModel):
    """This model represents a specific IP limiter."""
    ip_address = models.CharField(max_length=15)
    description = models.TextField(blank=True, default='')
    ad_groups = models.ManyToManyField('ADGroupAssociation', related_name='ip_limiters', blank=True)

    class Meta:
        verbose_name = "IP Limiter"
        verbose_name_plural = "IP Limiters"

class ADOrganizationalUnitLimiter(BaseModel):
    """This model represents an AD organizational unit limiter."""
    canonical_name = models.CharField(max_length=1024)
    distinguished_name = models.CharField(max_length=1024)
    ad_groups = models.ManyToManyField('ADGroupAssociation', related_name='ad_organizational_unit_limiters', blank=True)

    class Meta:
        verbose_name = "AD Organizational Unit Limiter"
        verbose_name_plural = "AD Organizational Unit Limiters"


    def save(self, *args, **kwargs):
        if not self.distinguished_name.startswith('OU=') or not self.distinguished_name.endswith(',DC=win,DC=dtu,DC=dk'):
            raise ValidationError("distinguished_name must start with 'OU=' and end with ',DC=win,DC=dtu,DC=dk'")
        if not self.canonical_name.startswith('win.dtu.dk/'):
            raise ValidationError("canonical_name must start with 'win.dtu.dk/'")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.canonical_name

# This model is used to associate AD groups with Django users
class ADGroupAssociation(BaseModel):
    """
    This model represents an association between an AD group and a Django user.
    """
    canonical_name = models.CharField(max_length=255, unique=True, null=False)
    distinguished_name = models.CharField(max_length=255, unique=True, null=False)
    members = models.ManyToManyField(User, related_name='ad_group_members')

    def __str__(self):
        return self.canonical_name
    
    def save(self, *args, **kwargs):
        if not self.distinguished_name.startswith('CN=') or not self.distinguished_name.endswith(',DC=win,DC=dtu,DC=dk'):
            raise ValidationError("distinguished_name must start with 'CN=' and end with ',DC=win,DC=dtu,DC=dk'")

        # if the canonical_name is empty or None, create it from the distinguished_name
        if not self.canonical_name:
            from myview.scripts.distinguished_to_canonical import distinguished_to_canonical
            self.canonical_name = distinguished_to_canonical(self.distinguished_name)
            # CN=AIT-ADM-employees-29619,OU=SecurityGroups,OU=AIT,OU=DTUBasen,DC=win,DC=dtu,DC=dk
            # >> win.dtu.dk/DTUBasen/AIT/SecurityGroups/AIT-ADM-employees-29619

        if not self.canonical_name.startswith('win.dtu.dk/'):
            raise ValidationError("canonical_name must start with 'win.dtu.dk/'")

        is_new = self._state.adding

        super().save(*args, **kwargs)

        if is_new:
            # Ensure that newly created associations immediately reflect the current
            # membership of the backing AD group inside Django.
            self.sync_ad_group_members()


    # This function should only sync with already existing groups in the django db.
    def sync_user_ad_groups(username, remove_groups_that_are_not_used_by_any_endpoint=False):
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
            if ADGroupAssociation.objects.filter(distinguished_name=group_dn).exists():
                group = ADGroupAssociation.objects.get(distinguished_name=group_dn)
                ADGroupAssociation.sync_ad_group_members(group)


        # Remove all groups not associated with any endpoint
        if remove_groups_that_are_not_used_by_any_endpoint:
            for group in ADGroupAssociation.objects.all():
                if not group.endpoints.exists():
                    group.delete()

        user.save()
        user.refresh_from_db()

    @staticmethod
    def delete_unused_groups():
        unused_ad_groups = ADGroupAssociation.objects.filter(endpoints__isnull=True)
        unused_ad_groups.delete()

  
    def _escape_ldap_filter_chars(self, s):
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
    


    # def user_is_synched_with_azure_ad(self, user):


    


    def _create_or_update_django_users_if_not_exists(self, users):
        for user in users:
            try:
                
                user_principal_name = user.get('userPrincipalName', [''])[0]
                sam_accountname = user.get('sAMAccountName', [''])[0]


                if not user_principal_name.endswith('@dtu.dk'):
                    raise ValueError(f"User {user_principal_name} does not end with @dtu.dk")
                
                # validate user
                from graph.services import execute_get_user
                user_data, status_code = execute_get_user(user_principal_name=user_principal_name, select_parameters='$select=onPremisesImmutableId')
                if status_code != 200:                    
                    raise ValueError(f"User {user_principal_name} not found")
                on_premises_immutable_id = user_data.get('onPremisesImmutableId', '')           
                from app.scripts.azure_user_is_synced_with_on_premise_users import azure_user_is_synced_with_on_premise_users
                if not azure_user_is_synced_with_on_premise_users(sam_accountname=sam_accountname, on_premises_immutable_id=on_premises_immutable_id):
                    raise ValueError(f"User {user_principal_name} is not synched with on-premise users")

                # Create new user if the user is synched with azure ad
                # Normalize the username to lowercase so that it matches the
                # representation used when linking users to AD groups later.
                username = sam_accountname.lower()
                first_name = user.get('givenName', [''])[0]
                last_name = user.get('sn', [''])[0]
                email = user_principal_name

                from app.scripts.create_or_update_django_user import create_or_update_django_user
                create_or_update_django_user(username=username, first_name=first_name, last_name=last_name, email=email, update_existing_user=False)

            except Exception as error:
                print(f"An unexpected error occurred: {error}")






    # This function syncs the members of the AD group with the database
    def sync_ad_group_members(self):
            
            base_dn = "DC=win,DC=dtu,DC=dk"
            search_filter = "(&(objectClass=user)(memberOf={}))".format(self._escape_ldap_filter_chars(self.distinguished_name))
            search_attributes = ['mS-DS-ConsistencyGuid', 'userPrincipalName', 'distinguishedName', 'sAMAccountName', 'givenName', 'sn']

            try:
                # Perform the search on LDAP
                current_members = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

                # This will only add users to django if those AD users are synched with Azure AD
                self._create_or_update_django_users_if_not_exists(current_members)

                # Remove all members from the group
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



class LimiterType(models.Model):
    """This model represents a type of limiter, associated only with the model type."""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, 
                                     limit_choices_to={'model__in': ['iplimiter', 'adorganizationalunitlimiter']})

    def __str__(self):
        return self.name
    




class Endpoint(BaseModel):
    path = models.CharField(max_length=255, unique=True)
    method = models.CharField(max_length=6, blank=True, default='')
    ad_groups = models.ManyToManyField('ADGroupAssociation', related_name='endpoints', blank=True)
    limiter_type = models.ForeignKey(LimiterType, on_delete=models.CASCADE, null=True, blank=True)
    no_limit = models.BooleanField(default=False, null=False, blank=False)
    

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






class ChatThread(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_threads')
    title = models.CharField(max_length=255, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)  # 'user' or 'assistant'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"