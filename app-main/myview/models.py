from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver


class BaseModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    endpoints = models.ManyToManyField(
        'Endpoint',
        through='AccessRequest',
        through_fields=('user_profile', 'endpoint'),
        related_name='user_profiles'
    )

    def has_endpoint_access(self, path, method):
        endpoint_qs = Endpoint.objects.filter(path=path)
        if method:
            endpoint_qs = endpoint_qs.filter(method=method)
        return EndpointPermission.objects.filter(
            user_profile=self,
            endpoint__in=endpoint_qs,
            can_access=True
        ).exists()

    def __str__(self):
        return self.user.username





class AccessControlType(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Endpoint(BaseModel):
    path = models.CharField(max_length=255, unique=True)
    method = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return f"{self.method if self.method else ''} {self.path}"



###### these classes depends on eachother ######
class AccessRequestStatus(models.TextChoices):
    PENDING = 'P',  _('Pending')
    GRANTED = 'G',  _('Granted')
    DENIED =  'D',  _('Denied')


class AccessRequest(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1,
        choices=AccessRequestStatus.choices,
        default=AccessRequestStatus.PENDING
    )
    request_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_profile', 'endpoint')

    def __str__(self):
        return f"{self.user_profile.user.username}'s access to {self.endpoint.path} is {self.get_status_display()}"  
    
    def save(self, *args, **kwargs):
        # Check if this is an existing instance and not a new one
        if self.pk:
            old_instance = AccessRequest.objects.get(pk=self.pk)
            # Check if status changed from Granted to something else
            if old_instance.status == AccessRequestStatus.GRANTED and self.status != AccessRequestStatus.GRANTED:
                # Revoke access by updating EndpointPermission
                EndpointPermission.objects.filter(user_profile=self.user_profile, endpoint=self.endpoint).update(can_access=False)
            elif self.status == AccessRequestStatus.GRANTED:
                # Ensure access is granted
                EndpointPermission.objects.update_or_create(
                    user_profile=self.user_profile,
                    endpoint=self.endpoint,
                    defaults={'can_access': True}
                )
        super().save(*args, **kwargs)
###### these classes depends on eachother ######


class EndpointPermission(BaseModel):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
    can_access = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user_profile', 'endpoint')
        verbose_name = 'Endpoint Permission'
        verbose_name_plural = 'Endpoint Permissions'

    def __str__(self):
        access_status = 'can access' if self.can_access else 'cannot access'
        return f"{self.user_profile.user.username} {access_status} {self.endpoint.path}"


class EndpointAccessControl(BaseModel):
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
    access_control = models.ForeignKey(AccessControlType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('endpoint', 'access_control')



@receiver(pre_delete, sender=Endpoint)
def endpoint_pre_delete_handler(sender, instance, **kwargs):
    # Automatically deny access requests associated with the endpoint being deleted
    AccessRequest.objects.filter(endpoint=instance, status=AccessRequestStatus.PENDING).update(status=AccessRequestStatus.DENIED)




@receiver(post_save, sender=AccessRequest)
def update_endpoint_permission(sender, instance, **kwargs):
    """
    Signal to update EndpointPermission when an AccessRequest is saved.
    """
    if instance.status == AccessRequestStatus.GRANTED:
        # If access is granted, ensure the user has permission.
        EndpointPermission.objects.update_or_create(
            user_profile=instance.user_profile,
            endpoint=instance.endpoint,
            defaults={'can_access': True}
        )
    elif instance.status in [AccessRequestStatus.PENDING, AccessRequestStatus.DENIED]:
        # If access is not granted, ensure the user does not have permission.
        EndpointPermission.objects.filter(
            user_profile=instance.user_profile,
            endpoint=instance.endpoint
        ).update(can_access=False)












# class OrganizationalUnit(BaseModel):
#     distinguished_name = models.TextField(unique=True)  # The full OU string
#     canonical_name = models.TextField(unique=True, default="")  # The canonical name of the OU

#     def __str__(self):
#         return self.canonical_name

#     class Meta(BaseModel.Meta):  # Make sure to inherit from BaseModel.Meta if it defines any meta options
#         ordering = ['canonical_name']  # This sets the default ordering for queries on this model



# class EndpointOrganizationalUnit(BaseModel):
#     endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
#     organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('endpoint', 'organizational_unit')


