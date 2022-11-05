from django.contrib import admin
from .models import Post, Comment, Like

# adding admin functionality based on provided models
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
