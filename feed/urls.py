from django.contrib import admin
from django.urls import path, include
from .views import Index, CreatePost, PostDetailView, SharePostView
from . import views


urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('post/new/', CreatePost.as_view(), name='create-post'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/delete/<int:pk>', views.post_delete, name='post-delete'),
    path('post/comment/delete/<int:pk>', views.comment_delete, name='comment-delete'),
    path('like/', views.like, name='post-like'),
    path('share/', SharePostView.as_view(), name='share-post'),
]
