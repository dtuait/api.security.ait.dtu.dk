from django.contrib.auth.models import User
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone







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