from django.db.models import Max
from django.db.models.functions import Coalesce
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, FriendRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from feed.forms import NewPostForm, SharePostForm
from feed.models import Post, Like
from django.views.generic import ListView
import random

# grabbing django user model
User = get_user_model()


# list created for logged-in users to see other user profiles on the site
# friends of user are excluded from this list
@login_required
def users_list(request):
    users = Profile.objects.exclude(user=request.user)
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    sent_to = []
    friends = []
    for user in users:
        friend = user.friends.all()
        for f in friend:
            if f in friends:
                friend = friend.exclude(user=f.user)
        friends += friend
    my_friends = request.user.profile.friends.all()
    for i in my_friends:
        if i in friends:
            friends.remove(i)
    if request.user.profile in friends:
        friends.remove(request.user.profile)
    random_list = random.sample(list(users), min(len(list(users)), 10))
    for r in random_list:
        if r in friends:
            random_list.remove(r)
    friends += random_list
    for i in my_friends:
        if i in friends:
            friends.remove(i)
    for se in sent_friend_requests:
        sent_to.append(se.to_user)

    context = {
        'users': friends,
        'sent': sent_to
    }
    return render(request, "users/users_list.html", context)


# user's friends list
def friend_list(request):
    p = request.user.profile
    friends = p.friends.all()
    context = {
        'friends': friends
    }
    return render(request, "users/friend_list.html", context)


# User sending a friend request to another user
@login_required
def send_friend_request(request, id):
    user = get_object_or_404(User, id=id)
    frequest, created = FriendRequest.objects.get_or_create(
        from_user=request.user,
        to_user=user)
    return redirect(request.META['HTTP_REFERER'])


# User canceling a friend request sent to another user
@login_required
def cancel_friend_request(request, id):
    user = get_object_or_404(User, id=id)
    frequest = FriendRequest.objects.filter(
        from_user=request.user,
        to_user=user).first()
    frequest.delete()
    return redirect(request.META['HTTP_REFERER'])


# User accepting a friend request sent to them
@login_required
def accept_friend_request(request, id):
    from_user = get_object_or_404(User, id=id)
    frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
    user1 = frequest.to_user
    user2 = from_user
    user1.profile.friends.add(user2.profile)
    user2.profile.friends.add(user1.profile)
    if (FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()):
        request_rev = FriendRequest.objects.filter(from_user=request.user, to_user=from_user).first()
        request_rev.delete()
    frequest.delete()
    return redirect(request.META['HTTP_REFERER'])


# User rejecting a friend request sent to them
@login_required
def delete_friend_request(request, id):
    from_user = get_object_or_404(User, id=id)
    frequest = FriendRequest.objects.filter(from_user=from_user, to_user=request.user).first()
    frequest.delete()
    return redirect(request.META['HTTP_REFERER'])


# User removing a friend from their friend's list
def delete_friend(request, id):
    user_profile = request.user.profile
    friend_profile = get_object_or_404(Profile, id=id)
    user_profile.friends.remove(friend_profile)
    friend_profile.friends.remove(user_profile)
    return redirect(request.META['HTTP_REFERER'])


# User can query for other users
@login_required
def search_users(request):
    query = request.GET.get('q')
    object_list = User.objects.filter(username__icontains=query)
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    p = request.user.profile
    friends = p.friends.all()

    sent_to = []

    for se in sent_friend_requests:
        sent_to.append(se.to_user)
    context = {
        'users': object_list,
        'sent': sent_to,
        'friends': friends
    }
    return render(request, "users/search_users.html", context)


# registration using forms created in forms.py
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You can now log in')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


# Profile of currently logged-in user
class ActiveProfileView(LoginRequiredMixin, ListView):
    # get details of logged-in user profile
    def get(self, request, *args, **kwargs):
        active_profile = request.user.profile
        active_user = active_profile.user
        sent_friend_requests = FriendRequest.objects.filter(from_user=active_profile.user)
        rec_friend_requests = FriendRequest.objects.filter(to_user=active_profile.user)
        friends_list = active_profile.friends.all()
        form = NewPostForm()
        share_form = SharePostForm()
        liked = [i for i in Post.objects.all() if Like.objects.filter(user=active_profile.user, post=i)]
        button_status = 'none'
        post_filter = [active_profile]
        friend = active_profile.friends.all()

        # filtering user timeline posts for posts made by friends of user
        for f in friend:
            if f in post_filter:
                friend = friend.filter(user=f.user)
        post_filter += friend
        # pagination of posts on a page
        paginator = Paginator(Post.objects.filter(username__profile__in=post_filter)
                              .annotate(lr=Coalesce(Max('shared_date'), 'date_posted'))
                              .order_by('-lr'), 10)
        page = request.GET.get('page')
        posts = paginator.get_page(page)

        if active_profile not in request.user.profile.friends.all():
            button_status = 'not_friend'
            # if user profile sent a friend request
            if len(FriendRequest.objects.filter(from_user=request.user).filter(to_user=active_profile.user)) == 1:
                button_status = 'friend_request_sent'
            # if user profile recieved a friend request
            if len(FriendRequest.objects.filter(from_user=active_profile.user).filter(to_user=request.user)) == 1:
                button_status = 'friend_request_received'

        context = {
            'u': active_user,
            'button_status': button_status,
            'friends_list': friends_list,
            'sent_friend_requests': sent_friend_requests,
            'rec_friend_requests': rec_friend_requests,
            'is_liked': liked,
            'post_form': form,
            'share_form': share_form,
            'posts': posts,
        }
        return render(request, 'users/profile.html', context)

    # form for making a new post
    def post(self, request, *args, **kwargs):
        user = request.user
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.username = user
            data.save()
            return redirect('home')
        else:
            form = NewPostForm()
        return redirect('home')


# form for editing user profile
def edit_profile(request):
    # method for editing/updating profile
    if request.user.is_authenticated:
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, f'Your profile has been updated!')
                return redirect('profile')
        else:
            user_form = UserUpdateForm(instance=request.user)
            profile_form = ProfileUpdateForm(instance=request.user.profile)

        context = {
            'u_form': user_form,
            'p_form': profile_form,
        }
        return render(request, 'users/edit_profile.html', context)
    else:
        messages.warning(request, f'Please log in to access your profile')
        return redirect('login')


# profile page for user's without logged-in user functionality
def profile_view(request, slug):
    user_profile = Profile.objects.filter(slug=slug).first()
    user = user_profile.user
    if request.user.is_authenticated:
        sent_friend_requests = FriendRequest.objects.filter(from_user=user_profile.user)
        rec_friend_requests = FriendRequest.objects.filter(to_user=user_profile.user)
        friends = user_profile.friends.all()
        liked = [i for i in Post.objects.all() if Like.objects.filter(user=request.user, post=i)]
        button_status = 'none'
        post_filter = [user_profile]
        friend = user_profile.friends.all()

        # filtering user timeline posts for posts made by friends of user
        for f in friend:
            if f in post_filter:
                friend = friend.filter(user=f.user)
        post_filter += friend
        # pagination of posts on a page
        paginator = Paginator(
            Post.objects.filter(username__profile__in=post_filter).annotate(lr=Coalesce(Max('shared_date'), 'date_posted'))
            .order_by('-lr'), 10)
        page = request.GET.get('page')
        posts = paginator.get_page(page)


        if user_profile not in request.user.profile.friends.all():
            button_status = 'not_friend'

            # if current user has sent friend request to viewed profile
            if len(FriendRequest.objects.filter(
                    from_user=request.user).filter(to_user=user_profile.user)) == 1:
                button_status = 'friend_request_sent'
            # if current user has recieved a friend request to viewed profile
            if len(FriendRequest.objects.filter(
                    from_user=user_profile.user).filter(to_user=request.user)) == 1:
                button_status = 'friend_request_received'
        context = {
            'u': user,
            'button_status': button_status,
            'friends_list': friends,
            'sent_friend_requests': sent_friend_requests,
            'rec_friend_requests': rec_friend_requests,
            'is_liked': liked,
            'posts': posts,
        }
        return render(request, "users/profile_view.html", context)

    context = {
        'u': user,
    }

    return render(request, "users/profile_view.html", context)
