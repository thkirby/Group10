from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


# model and fields to Posts to be created and stored in the database
class Post(models.Model):
    shared_description = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    pic = models.ImageField(upload_to='social_pics', blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    shared_date = models.DateTimeField(blank=True, null=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_username = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='+')

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


# model and fields for comments to be created, stored, and linked to a post in the database
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='details', on_delete=models.CASCADE)
    username = models.ForeignKey(User, related_name='details', on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    comment_date = models.DateTimeField(default=timezone.now)


# model and fields to link likes of a user to a specific post in the database
class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
