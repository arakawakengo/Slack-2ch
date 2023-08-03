from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Workspace(models.Model):
    w_id = models.AutoField(primary_key=True)
    workspace_id = models.CharField(max_length=20, unique=True)
    workspace_name = models.CharField(max_length=20)
    workspace_token = models.CharField(max_length=100)

    def __str__(self):
        return str(self.workspace_name)

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
    
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='users'
    )
    
    user_id = models.CharField(max_length=20)
    username = models.CharField(max_length=20, unique=True)
    channel_id = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    image_url = models.CharField(max_length=200)
    is_owner = models.BooleanField()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "workspace"],
                name="user_unique"
            ),
        ]
    