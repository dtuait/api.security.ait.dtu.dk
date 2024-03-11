from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _




class BaseModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True







class AccessControlType(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name



# Ensure you reference the through models with the app name if needed
class Endpoint(BaseModel):
    path = models.CharField(max_length=255, unique=True)
    method = models.CharField(max_length=6, null=True, blank=True)
    access_controls = models.ManyToManyField(
        AccessControlType,
        through='myapp.EndpointAccessControl',  # Update 'myapp' to your actual app name
        related_name='endpoints',
        blank=True,
        verbose_name="Custom Access Controls"
    )

    def __str__(self):
        return f"{self.method if self.method else ''} {self.path}"

# EndpointPermission and other models remain unchanged...
class EndpointAccessControl(BaseModel):
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
    access_control = models.ForeignKey(AccessControlType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('endpoint', 'access_control')






# class BaseModel(models.Model):
#     datetime_created = models.DateTimeField(auto_now_add=True)
#     datetime_modified = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True

# class OrganizationalUnit(BaseModel):
#     distinguished_name = models.TextField(unique=True)  # The full OU string
#     canonical_name = models.TextField(unique=True, default="")  # The canonical name of the OU

#     def __str__(self):
#         return self.canonical_name

# class AccessRequestStatus(models.TextChoices):
#     PENDING = 'P', _('Pending')
#     GRANTED = 'G', _('Granted')
#     DENIED = 'D', _('Denied')


# class AccessControlType(BaseModel):
#     name = models.CharField(max_length=255, unique=True)
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return self.name

# # This is the correct and only definition of Endpoint that should exist
# class Endpoint(BaseModel):
#     path = models.CharField(max_length=255, unique=True)
#     method = models.CharField(max_length=6, null=True, blank=True)
#     access_controls = models.ManyToManyField(
#         AccessControlType,
#         through='EndpointAccessControl',
#         related_name='endpoints',
#         blank=True,
#         verbose_name="Custom Access Controls"
#     )

#     def __str__(self):
#         return f"{self.method if self.method else ''} {self.path}"

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     ous = models.ManyToManyField(
#         OrganizationalUnit,
#         through='AccessRequest',
#         through_fields=('user_profile', 'organizational_unit'),
#         related_name='user_profiles'
#     )

#     def has_endpoint_access(self, path, method=None):
#         endpoint_qs = Endpoint.objects.filter(path=path)
#         if method:
#             endpoint_qs = endpoint_qs.filter(method=method)
#         return EndpointPermission.objects.filter(
#             user_profile=self,
#             endpoint__in=endpoint_qs,
#             can_access=True
#         ).exists()

#     def __str__(self):
#         return self.user.username


# class EndpointPermission(BaseModel):
#     user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
#     endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
#     can_access = models.BooleanField(default=False)

#     class Meta:
#         unique_together = ('user_profile', 'endpoint')

#     def __str__(self):
#         access_status = 'can access' if self.can_access else 'cannot access'
#         return f"{self.user_profile.user.username} {access_status} {self.endpoint.path}"




# class EndpointAccessControl(BaseModel):
#     endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
#     access_control = models.ForeignKey(AccessControlType, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('endpoint', 'access_control')




