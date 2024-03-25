from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from utils.active_directory_query import active_directory_query
from django.db import transaction
from django.db.utils import IntegrityError

class BaseModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# The ADGroup model now has a ManyToManyField to Django's User model to represent the association between a user and an AD group.
class ADGroupAssociation(BaseModel):
    cn = models.CharField(max_length=255, verbose_name="Common Name")
    canonical_name = models.CharField(max_length=255)
    distinguished_name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='ad_groups')
    # group_no_longer_exist_in_ad = models.BooleanField(default=False) # now you can keep the group and freeze it, but not use it



    def sync_ad_groups(self):
        base_dn = "DC=win,DC=dtu,DC=dk"
        search_filter = "(objectClass=group)"
        search_attributes = ['cn', 'canonicalName', 'distinguishedName']

        try:
            ad_groups = active_directory_query(base_dn, search_filter, search_attributes)

            with transaction.atomic():
                # Fetch existing groups to identify new and to-be-deleted groups
                existing_groups = {group.distinguished_name: group for group in ADGroupAssociation.objects.all()}
                ad_group_dns = set()

                new_groups = []
                updated_groups = []

                for group in ad_groups:
                    cn = group.get('cn', '')
                    canonical_name = group.get('canonicalName', '')
                    distinguished_name = group.get('distinguishedName', '')

                    # Track DNs of groups found in AD
                    ad_group_dns.add(distinguished_name)

                    if distinguished_name in existing_groups:
                        # Prepare existing group for update
                        existing_group = existing_groups[distinguished_name]
                        existing_group.cn = cn
                        existing_group.canonical_name = canonical_name
                        updated_groups.append(existing_group)
                        updated_groups.append(existing_group)
                    else:
                        # Prepare new group for creation
                        new_group = ADGroupAssociation(cn=cn, canonical_name=canonical_name, distinguished_name=distinguished_name)
                        new_groups.append(new_group)

                # Bulk create new groups and bulk update existing groups
                ADGroupAssociation.objects.bulk_create(new_groups)
                ADGroupAssociation.objects.bulk_update(updated_groups, ['cn', 'canonical_name'])

                # Delete groups that are no longer in AD
                groups_to_delete = set(existing_groups.keys()) - ad_group_dns
                ADGroupAssociation.objects.filter(distinguished_name__in=groups_to_delete).delete()

        except Exception as e:
            print(f"An error occurred during sync ad groups operation: {e}")


  
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
                    dn = user.get('distinguishedName')
                    username = user.get('sAMAccountName', '').lower()  # Get 'sAMAccountName' from the current query
                    first_name = user.get('givenName', '')
                    last_name = user.get('sn', '')

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

    # def create_new_cas_user(username):
    #     try:
    #         User = get_user_model()
    #         # Convert the username to lowercase as a common practice
    #         username = username.lower()
            
    #         # Check if the user already exists
    #         if not User.objects.filter(username=username).exists():
    #             # Assume some default values for email, first_name, and last_name
    #             # You can modify these or extend the function to accept more parameters
    #             email = f'{username}@example.com'
    #             first_name = 'Default'
    #             last_name = 'User'
                
    #             # Determine if the user should have admin rights
    #             # This is just an example; adjust the logic to fit your needs
    #             is_superuser = username in ['adm-vicre', 'adm-jaholm']
    #             is_staff = is_superuser
                
    #             # Create the new user
    #             new_user = User.objects.create_user(
    #                 username=username, 
    #                 email=email, 
    #                 first_name=first_name, 
    #                 last_name=last_name, 
    #                 is_superuser=is_superuser, 
    #                 is_staff=is_staff
    #             )
                
    #             print(f"User {username} was successfully created.")
    #         else:
    #             print(f"User {username} already exists.")
                
    #     except IntegrityError as error:
    #         # This exception is raised if the user creation violates a database constraint
    #         print(f"Could not create user {username} due to a database integrity error: {error}")
    #     except Exception as error:
    #         # Catch any other unexpected errors
    #         print(f"An unexpected error occurred: {error}")


    def sync_ad_group_members(self):
            print("Syncing AD group members...")
            base_dn = "DC=win,DC=dtu,DC=dk"
            search_filter = "(&(objectClass=user)(memberOf={}))".format(self.escape_ldap_filter_chars(self.distinguished_name))
            # search_attributes = ['distinguishedName', 'sAMAccountName']  # Include 'sAMAccountName' here
            search_attributes = ['distinguishedName', 'sAMAccountName', 'givenName', 'sn']

            try:
                # Perform the search on LDAP
                current_members = active_directory_query(base_dn, search_filter, search_attributes)

                self.create_new_users_if_not_exists(current_members)

                print("Syncing AD group members finished")


            except Exception as e:
                print(f"An error occurred during the LDAP operation: {e}")

    def __str__(self):
        return self.canonical_name

    
    def add_member(self, user, admin_user):
        self.members.add(user)
        self.added_manually_by = admin_user
        self.save()


class Endpoint(BaseModel):
    path = models.CharField(max_length=255, unique=True)
    method = models.CharField(max_length=6, blank=True, default='')
    # A many-to-many relationship with ADGroup. This means an Endpoint can be associated with multiple ADGroups.
    ad_groups = models.ManyToManyField(ADGroupAssociation, related_name='endpoints')

    def __str__(self):
        return f"{self.method} {self.path}" if self.method else self.path























































# from django.db import models
# from django.contrib.auth.models import User
# from django.utils.translation import gettext_lazy as _

# class BaseModel(models.Model):
#     datetime_created = models.DateTimeField(auto_now_add=True)
#     datetime_modified = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True


# class ADGroup(BaseModel):
#     cn = models.CharField(max_length=255, verbose_name="Common Name")
#     canonical_name = models.CharField(max_length=255)
#     distinguished_name = models.CharField(max_length=255)
#     group_no_longer_exist_in_ad = models.BooleanField(default=False)

#     def __str__(self):
#         return self.canonical_name
    

# class Endpoint(BaseModel):
#     path = models.CharField(max_length=255, unique=True)
#     method = models.CharField(max_length=6, blank=True, default='')

#     def __str__(self):
#         return f"{self.method} {self.path}" if self.method else self.path




# class UserGroup(BaseModel):
#     name = models.CharField(max_length=255, unique=True)
#     users = models.ManyToManyField(User, related_name="user_groups")

#     def __str__(self):
#         return self.name



# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     groups = models.ManyToManyField(UserGroup, related_name='members')

#     def has_endpoint_access(self, path, method=None):
#         groups = self.groups.all()
#         endpoint_qs = Endpoint.objects.filter(path=path)
#         if method:
#             endpoint_qs = endpoint_qs.filter(method=method)
        
#         return EndpointPermission.objects.filter(
#             user_group__in=groups,
#             endpoint__in=endpoint_qs,
#             can_access=True
#         ).exists()

#     def __str__(self):
#         return self.user.username

# class Endpoint(BaseModel):
#     path = models.CharField(max_length=255, unique=True)
#     method = models.CharField(max_length=6, blank=True, default='')

#     def __str__(self):
#         return f"{self.method} {self.path}" if self.method else self.path

# class EndpointPermission(BaseModel):
#     user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
#     endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
#     can_access = models.BooleanField(default=False)

#     class Meta:
#         unique_together = ('user_group', 'endpoint')

#     def __str__(self):
#         access_status = 'can access' if self.can_access else 'cannot access'
#         return f"{self.user_group.name} {access_status} {self.endpoint.path}"

# class AccessControlType(BaseModel):
#     name = models.CharField(max_length=255, unique=True)
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return self.name

# class EndpointAccessControl(BaseModel):
#     endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
#     access_control = models.ForeignKey(AccessControlType, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('endpoint', 'access_control')




# @receiver(pre_delete, sender=Endpoint)
# def endpoint_pre_delete_handler(sender, instance, **kwargs):
#     """
#     Automatically deny access requests associated with the endpoint being deleted.
#     """
#     AccessRequest.objects.filter(endpoint=instance, status=AccessRequestStatus.PENDING).update(status=AccessRequestStatus.DENIED)




# @receiver(post_save, sender=AccessRequest)
# def update_endpoint_permission(sender, instance, created, **kwargs):
#     """
#     Signal to update or create EndpointPermission when an AccessRequest is saved.
#     This reflects the move to group-based access control.
#     """
#     if instance.status == AccessRequestStatus.GRANTED:
#         # If access is granted, ensure the group has permission.
#         EndpointPermission.objects.update_or_create(
#             user_group=instance.user_group,
#             endpoint=instance.endpoint,
#             defaults={'can_access': True}
#         )
#     else:
#         # If access is not granted (or revoked), ensure the group does not have permission.
#         # This step might require careful consideration depending on how you want to handle revocations
#         # for groups since it could affect multiple users. Here, we're opting to update, but you might
#         # choose a different logic based on your application's requirements.
#         EndpointPermission.objects.filter(
#             user_group=instance.user_group,
#             endpoint=instance.endpoint
#         ).update(can_access=False)













# class EndpointOrganizationalUnit(BaseModel):
#     endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
#     organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('endpoint', 'organizational_unit')


