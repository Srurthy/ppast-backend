from django.db import models
from django.apps import apps
from django.contrib.auth.models import AbstractUser
# from apps.projects.models import Project, EnterpriseProjectRole

# Create your models here.
# from apps.projects.models import Project


class User(AbstractUser):
    is_enterprise_admin = models.BooleanField(default=False)
    is_enterprise_member = models.BooleanField(default=False)
    company_name = models.CharField(max_length=64, blank=True, null=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    postal_code = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    province = models.CharField(max_length=64, blank=True, null=True)
    created_by = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    user_projects = models.ManyToManyField('projects.Project', null=True, blank=True)


class EnterpriseMemberProfile(models.Model):
    enterprise_leader = models.ForeignKey(User, on_delete=models.CASCADE)
    project_charges = models.ManyToManyField('projects.EnterpriseProjectRole')

class UserType(models.Model):
    code = models.CharField(max_length=20)
    desc = models.CharField(max_length=32)

    def __str__(self):
        return self.code
