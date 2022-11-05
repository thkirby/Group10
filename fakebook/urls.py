"""fakebook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from users.views import ActiveProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('', auth_views.LoginView.as_view(template_name='feed/landing.html', redirect_authenticated_user=True), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html', redirect_authenticated_user=True), name='login'),
    path('profile/', ActiveProfileView.as_view(), name='profile'),
    path('profile/edit_profile/', user_views.edit_profile, name='edit_profile'),
    path('users/<slug>/', user_views.profile_view, name='profile_view'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('', include('feed.urls')),
    path('users/', user_views.users_list, name='users_list'),
    path('friends/', user_views.friend_list, name='friend_list'),
    path('users/friend-request/send/<int:id>/', user_views.send_friend_request, name='send_friend_request'),
    path('users/friend-request/cancel/<int:id>/', user_views.cancel_friend_request, name='cancel_friend_request'),
    path('users/friend-request/accept/<int:id>/', user_views.accept_friend_request, name='accept_friend_request'),
    path('users/friend-request/delete/<int:id>/', user_views.delete_friend_request, name='delete_friend_request'),
    path('users/friend/delete/<int:id>/', user_views.delete_friend, name='delete_friend'),
    path('search_users/', user_views.search_users, name='search_users'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
