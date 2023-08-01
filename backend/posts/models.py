from django.db import models
    
class dbposts(models.Model):
    id  = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    text = models.CharField(max_length=100)
    comment_cnt = models.IntegerField()
    created_at = models.DateTimeField()

    def __str__(self):
        return self.text
    
class dbquestions(models.Model):
    id = models.AutoField(primary_key=True)
    # user_id = models.CharField(max_length=100)
    post_id = models.IntegerField()
    text = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.text

class dbreplies(models.Model):
    id = models.AutoField(primary_key=True)
    # user_id = models.CharField(max_length=100)
    question_id = models.IntegerField()
    text = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    def __str__(self):
        return self.text
