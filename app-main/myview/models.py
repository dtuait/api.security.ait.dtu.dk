from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class OrganizationalUnit(BaseModel):
    distinguished_name = models.TextField(unique=True)  # The full OU string
    canonical_name = models.TextField(unique=True, default="")  # The canonical name of the OU

    def __str__(self):
        return self.canonical_name

class AccessRequestStatus(models.TextChoices):
    PENDING = 'P', _('Pending')
    GRANTED = 'G', _('Granted')
    DENIED = 'D', _('Denied')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ous = models.ManyToManyField(
        OrganizationalUnit,
        through='AccessRequest',
        through_fields=('user_profile', 'organizational_unit'),
        related_name='user_profiles'
    )

    def has_endpoint_access(self, path, method=None):
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

class AccessRequest(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1,
        choices=AccessRequestStatus.choices,
        default=AccessRequestStatus.PENDING
    )
    request_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_profile', 'organizational_unit')

    def __str__(self):
        return f"{self.user_profile.user.username}'s access to {self.organizational_unit.canonical_name} is {self.get_status_display()}"

class Endpoint(BaseModel):
    path = models.CharField(max_length=255, unique=True)
    method = models.CharField(max_length=6, null=True, blank=True)
    organizational_units = models.ManyToManyField(
        OrganizationalUnit,
        related_name='endpoints',
        blank=True
    )

    def __str__(self):
        return f"{self.method if self.method else ''} {self.path}"

class EndpointPermission(BaseModel):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)
    can_access = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user_profile', 'endpoint')

    def __str__(self):
        access_status = 'can access' if self.can_access else 'cannot access'
        return f"{self.user_profile} {access_status} {self.endpoint}"
