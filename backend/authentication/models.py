from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group
import secrets

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        verbose_name= ('groups'),
        blank=True,
        help_text= (
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name= ('user permissions'),
        blank=True,
        help_text= ('Specific permissions for this user.'),
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )
    
    u_ID = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=20)
    workspace_id = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    channel_id = models.CharField(max_length=20)
    
    
class Workspace(models.Model):
    w_id = models.AutoField(primary_key=True)
    workspace_id = models.CharField(max_length=20)
    workspace_name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.workspace_name)