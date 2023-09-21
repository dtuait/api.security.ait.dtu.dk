from django.contrib.auth.models import User
from django.db import models

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
    