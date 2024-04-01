from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from active_directory.scripts.active_directory_query import active_directory_query
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ADGroupAssociation(BaseModel):
    cn = models.CharField(max_length=255, verbose_name="Common Name")
    canonical_name = models.CharField(max_length=1024)
    distinguished_name = models.CharField(max_length=1024)
    members = models.ManyToManyField(User, related_name='ad_groups')
    def __str__(self):
        return self.cn

    # group_no_longer_exist_in_ad = models.BooleanField(default=False)








  # This function gets all AD groups and syncs them with the database
    def sync_ad_groups(self):
        base_dn = "DC=win,DC=dtu,DC=dk"
        search_filter = "(objectClass=group)"
        search_attributes = ['cn', 'canonicalName', 'distinguishedName']

        try:
            ad_groups = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

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
            print("Syncing AD group members...")
            base_dn = "DC=win,DC=dtu,DC=dk"
            search_filter = "(&(objectClass=user)(memberOf={}))".format(self.escape_ldap_filter_chars(self.distinguished_name))
            # search_attributes = ['distinguishedName', 'sAMAccountName']  # Include 'sAMAccountName' here
            search_attributes = ['distinguishedName', 'sAMAccountName', 'givenName', 'sn']

            try:
                # Perform the search on LDAP
                current_members = active_directory_query(base_dn=base_dn, search_filter=search_filter, search_attributes=search_attributes)

                # filter out all users that does not startwith adm- or contians -adm-
                current_members = [user for user in current_members if user['sAMAccountName'][0].lower().startswith('adm-') or '-adm-' in user['sAMAccountName'][0].lower()]
                
                self.create_new_users_if_not_exists(current_members)

                # remove all members from the group
                self.members.clear()

                # Fetch the current members of the group
                for user in current_members:
                    username = user['sAMAccountName'][0].lower()
                    user_instance = User.objects.filter(username=username).first()
                    if user_instance:
                        self.members.add(user_instance)
                

                

                print("Syncing AD group members finished")


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
    def __str__(self):
        return f"{self.method} {self.path}" if self.method else self.path


    def validate_and_get_ad_groups_for_user_access(self, user, endpoint_path):
        # Fetch the endpoint instance based on the provided path.
        try:
            endpoint = Endpoint.objects.get(path=endpoint_path)
        except Endpoint.DoesNotExist:
            return False, None  # No access since the endpoint does not exist.

        # Check if the user is in any group that is associated with the endpoint.
        user_groups = user.ad_groups.all()
        access_granting_groups = []
        for group in user_groups:
            if endpoint.ad_groups.filter(pk=group.pk).exists():
                access_granting_groups.append(group)

        if access_granting_groups:
            return True, access_granting_groups  # Return True and the groups that grant access
        else:
            return False, None  # No access granted

















class EndpointAccessRequestStatus(models.TextChoices):
    PENDING = 'P',  _('Pending')
    GRANTED = 'G',  _('Granted')
    DENIED =  'D',  _('Denied')





class EndpointAccessRequest(models.Model):
    ad_group = models.ForeignKey(ADGroupAssociation, on_delete=models.CASCADE)
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1,
        choices=EndpointAccessRequestStatus.choices,
        default=EndpointAccessRequestStatus.PENDING
    )
    request_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ad_group', 'endpoint')

    def __str__(self):
        return f"CODEHERE's access to {self.endpoint.path} is {self.get_status_display()}"  



class EndpointPermission(BaseModel):
    ad_group = models.ForeignKey(ADGroupAssociation, on_delete=models.CASCADE)
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
    can_access = models.BooleanField(default=False)

    class Meta:
        unique_together = ('ad_group', 'endpoint')
        verbose_name = 'Endpoint Permission'
        verbose_name_plural = 'Endpoint Permissions'

    def __str__(self):
        access_status = 'can access' if self.can_access else 'cannot access'
        # Assuming the ADGroupAssociation model has a 'cn' field for common name
        return f"{self.ad_group.cn} {access_status} {self.endpoint.path}"