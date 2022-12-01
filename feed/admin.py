from django.contrib import admin
from .models import Post, Comment, Like, Messages, Thread, Notifications

# adding admin functionality based on provided models
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Messages)
admin.site.register(Thread)
admin.site.register(Notifications)
