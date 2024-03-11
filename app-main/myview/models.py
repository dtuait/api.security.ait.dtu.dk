from django.contrib.auth.models import User
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _






class BaseModel(models.Model):
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



class OrganizationalUnit(BaseModel):
    distinguished_name = models.TextField(unique=True)  # The full OU string
    canonical_name = models.TextField(unique=True, default="")  # The canonical name of the OU
    # make a field that indicates if the user has access to the OU or if it is a applying for access to the OU sort of flag

    def __str__(self):
        return self.canonical_name


















# Define the possible access statuses as a choices enum
class AccessRequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    GRANTED = 'granted', 'Granted'
    DENIED = 'denied', 'Denied'

# This is the through model that connects UserProfile and OrganizationalUnit with additional information
class AccessRequest(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    organizational_unit = models.ForeignKey(OrganizationalUnit, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=AccessRequestStatus.choices,
        default=AccessRequestStatus.PENDING
    )
    request_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_profile', 'organizational_unit')

    def __str__(self):
        return f"{self.user_profile.user.username}'s access to {self.organizational_unit.canonical_name} is {self.status}"




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ous = models.ManyToManyField(OrganizationalUnit, through=AccessRequest)
    

    def __str__(self):
        return self.user.username








class EndpointAccess(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=100)
    can_access = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.endpoint}"
    
    