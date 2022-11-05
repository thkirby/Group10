from django.contrib import admin
from .models import Profile, FriendRequest

# adding admin functionality based on provided models
admin.site.register(Profile)
admin.site.register(FriendRequest)
