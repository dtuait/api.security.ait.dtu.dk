# from django.db import models
# from django.contrib.auth.models import User
# from django.utils.translation import gettext_lazy as _

# class BaseModel(models.Model):
#     datetime_created = models.DateTimeField(auto_now_add=True)
#     datetime_modified = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True

# class UserGroup(BaseModel):
#     name = models.CharField(max_length=255, unique=True)

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


