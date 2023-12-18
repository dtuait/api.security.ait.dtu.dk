from django.contrib.auth.models import User
from django.db import models
from django.db import models
from django.contrib.auth.models import User

class OrganizationalUnit(models.Model):
    name = models.TextField(unique=True)  # The full OU string, e.g. "OU=AIT,OU=ITAdmUsers,OU=Delegations..."

    # String representation for easier debugging.
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ous = models.ManyToManyField(OrganizationalUnit)

    def __str__(self):
        return self.user.username


class EndpointAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=100)
    can_access = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.endpoint}"