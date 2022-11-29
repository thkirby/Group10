from django.contrib import admin
from django.urls import path
from .views import Index, CreatePost, PostDetailView, SharePostView, PostEditView, ListThreads, CreateThread, \
    ThreadView, CreateMessage, DeleteNotificaiton
from . import views

# url patterns to handle redirection and linking between pages
urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('post/new/', CreatePost.as_view(), name='create-post'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/delete/<int:pk>/', views.post_delete, name='post-delete'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/comment/delete/<int:pk>/', views.comment_delete, name='comment-delete'),
    path('like/', views.like, name='post-like'),
    path('share/<int:pk>/', SharePostView.as_view(), name='share-post'),
    path('inbox/', ListThreads.as_view(), name='inbox'),
    path('inbox/create-thread/', CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>/', ThreadView.as_view(), name='message-thread'),
    path('inbox/<int:pk>/create-message', CreateMessage.as_view(), name='create-message'),
    path('notification/delete/', DeleteNotificaiton.as_view(), name='delete-notification'),
]
