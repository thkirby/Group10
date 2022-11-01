from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Post(models.Model):
    shared_description = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    pic = models.ImageField(upload_to='social_pics', blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    shared_date = models.DateTimeField(blank=True, null=True)
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_username = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='+')

    class Meta:
        ordering = ['-date_posted', '-shared_date']

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='details', on_delete=models.CASCADE)
    username = models.ForeignKey(User, related_name='details', on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    comment_date = models.DateTimeField(default=timezone.now)


class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
