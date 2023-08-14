from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', default=0)

    

class Post(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.TextField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)

class Likes(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)