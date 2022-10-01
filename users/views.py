from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, FriendRequest
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm

User = get_user_model()


# registration using forms created in forms.py
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You can now login')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def profile(request):
    if request.user.is_authenticated:
        active_profile = request.user.profile
        active_user = active_profile.user
        sent_friend_requests = FriendRequest.objects.filter(from_user=active_profile.user)
        rec_friend_requests = FriendRequest.objects.filter(to_user=active_profile.user)

        friends = active_profile.friends.all()

        button_status = 'none'
        if active_profile not in request.user.profile.friends.all():
            button_status = 'not_friend'

            # if we have sent him a friend request
            if len(FriendRequest.objects.filter(
                    from_user=request.user).filter(to_user=active_profile.user)) == 1:
                button_status = 'friend_request_sent'

            if len(FriendRequest.objects.filter(
                    from_user=active_profile.user).filter(to_user=request.user)) == 1:
                button_status = 'friend_request_received'

        context = {
            'u': active_user,
            'button_status': button_status,
            'friends_list': friends,
            'sent_friend_requests': sent_friend_requests,
            'rec_friend_requests': rec_friend_requests,
        }

        return render(request, 'users/profile.html', context)
    else:
        messages.warning(request, f'Please login to access your profile')
        return redirect('login')


def profile_view(request, slug):
    user_profile = Profile.objects.filter(slug=slug).first()
    user = user_profile.user
    sent_friend_requests = FriendRequest.objects.filter(from_user=user_profile.user)
    rec_friend_requests = FriendRequest.objects.filter(to_user=user_profile.user)

    friends = user_profile.friends.all()

    button_status = 'none'
    if user_profile not in request.user.profile.friends.all():
        button_status = 'not_friend'

        # if we have sent him a friend request
        if len(FriendRequest.objects.filter(
                from_user=request.user).filter(to_user=user_profile.user)) == 1:
            button_status = 'friend_request_sent'

        if len(FriendRequest.objects.filter(
                from_user=user_profile.user).filter(to_user=request.user)) == 1:
            button_status = 'friend_request_received'

    context = {
        'u': user,
        'button_status': button_status,
        'friends_list': friends,
        'sent_friend_requests': sent_friend_requests,
        'rec_friend_requests': rec_friend_requests,
    }

    return render(request, "users/profile.html", context)