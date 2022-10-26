from django.contrib import admin
from django.urls import path, include
from .views import Index, CreatePost, PostListView
from . import views


urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('post/new/', CreatePost.as_view(), name='create_post'),
    path('posts/', PostListView.as_view(), name='posts'),
]
