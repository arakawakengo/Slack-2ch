from django.db import models
from authentication.models import CustomUser, Workspace
from django.utils import timezone

    
class Posts(models.Model):
    id  = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='users_posts'
    )
    text = models.CharField(max_length=100)
    category = models.CharField(max_length=10)
    comment_cnt = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text
    
class Questions(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(
        Posts,
        on_delete=models.CASCADE,
        related_name='posts_questions'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='users_questions'
    )
    text = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    
    

    def __str__(self):
        return self.text

class Replies(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='users_replies'
    )
    question = models.ForeignKey(
        Questions,
        on_delete=models.CASCADE,
        related_name='questions_replies',
    )
    text = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text

class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=10)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["category_name", "workspace"],
                name="category_unique"
            )
        ]