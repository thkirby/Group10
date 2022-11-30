from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Max
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.utils import timezone
from .forms import NewCommentForm, NewPostForm, SharePostForm, ThreadForm, MessageForm
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import json
from .models import Post, Like, Comment, Thread, Messages, Notifications
from users.models import Profile, FriendRequest

User = get_user_model()


class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'feed/landing.html')


# user page for creating a new post
class CreatePost(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if request.method == "POST":
            form = NewPostForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                data.username = user
                data.save()
                messages.success(request, f'Posted Successfully')
                return redirect('home')
        else:
            form = NewPostForm()
        return render(request, 'feed/create_post.html', {'post_form': form})


# page to view a specific post
class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        user = request.user
        form = NewCommentForm()
        comments = Comment.objects.filter(post=post).order_by('-comment_date')
        is_liked = Like.objects.filter(user=user, post=post)

        context = {
            'post': post,
            'comments': comments,
            'is_liked': is_liked,
            'comment_form': form
        }
        return render(request, 'feed/post_detail.html', context)

    # form for creating a comment on a post
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = NewCommentForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.username = request.user
            data.post = post
            data.save()
            return redirect('post-detail', pk=pk)
        else:
            form = NewCommentForm()
        return redirect('post-detail', pk=pk)


# function for deleting a post
@login_required()
def post_delete(request, pk):
    post = Post.objects.get(pk=pk)
    if request.user == post.username:
        Post.objects.get(pk=pk).delete()

    return redirect('home')


# function for deleting a comment
@login_required()
def comment_delete(request, pk):
    comment = Comment.objects.get(pk=pk)
    if request.user == comment.username:
        Comment.objects.get(pk=pk).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# page for editing a user post
class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['description', 'pic']
    template_name = 'feed/post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})


# function for allowing a user to like a post and remove that like
@login_required
def like(request):
    post_id = request.GET.get("likeId", "")
    user = request.user
    post = Post.objects.get(pk=post_id)
    liked = False
    like = Like.objects.filter(user=user, post=post)
    if like:
        like.delete()
    else:
        liked = True
        Like.objects.create(user=user, post=post)
    resp = {
        'liked': liked
    }
    response = json.dumps(resp)
    return HttpResponse(response, content_type="application/json")


# User can share an already existing post made by another user
class SharePostView(View):
    def post(self, request, pk, *args, **kwargs):
        original_post = Post.objects.get(pk=pk)
        share_form = SharePostForm(request.POST)
        # form for sharing a post
        if share_form.is_valid():
            share_post = Post(shared_description=self.request.POST.get('description'),
                              description=original_post.description,
                              username=original_post.username,
                              date_posted=original_post.date_posted,
                              pic=original_post.pic,
                              shared_username=request.user,
                              shared_date=timezone.now())
            share_post.save()
        else:
            share_form = SharePostForm()
        return redirect(request.META['HTTP_REFERER'])


class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        thread = Thread.objects.get(pk=pk)
        if thread.reciever == request.user:
            reciever = thread.user
        else:
            reciever = thread.reciever
        text = Messages(
            thread=thread,
            sender_user=request.user,
            reciever_user=reciever,
            textbody=request.POST.get('textbody')
        )
        text.save()
        notification = Notifications.objects.create(
            type=1,
            sending_user=request.user,
            recieving_user=reciever,
            message=thread
        )
        return redirect('message-thread', pk=pk)


class ListThreads(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        threads = Thread.objects.filter(Q(user=request.user) | Q(reciever=request.user))
        try:
            notifications = Notifications.objects.get(recieving_user=request.user)
        except:
            notifications = None

        context = {
            'threads': threads,
            'notifications': notifications
        }
        return render(request, 'feed/inbox.html', context)


class CreateThread(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()
        context = {
            'form': form
        }
        return render(request, 'feed/create_thread.html', context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)
        username = request.POST.get('username')
        try:
            reciever = User.objects.get(username=username)
            if Thread.objects.filter(user=request.user, reciever=reciever).exists():
                thread = Thread.objects.filter(user=request.user, reciever=reciever).first()
                return redirect('message-thread', pk=thread.pk)
            elif Thread.objects.filter(user=reciever, reciever=request.user).exists():
                thread = Thread.objects.filter(user=reciever, reciever=request.user).first()
                return redirect('message-thread', pk=thread.pk)
            if form.is_valid():
                thread = Thread(user=request.user, reciever=reciever)
                thread.save()
                return redirect('message-thread', pk=thread.pk)
        except:
            redirect('create-thread')


class ThreadView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = Thread.objects.get(pk=pk)
        message_list = Messages.objects.filter(thread__pk__contains=pk)

        context = {
            'thread': thread,
            'form': form,
            'message_list': message_list,
        }

        return render(request, 'feed/message_thread.html', context)


def search_posts(request):
    query = request.GET.get('q')
    object_list = Post.objects.filter(description__contains=query)
    share_form = SharePostForm()

    context = {
        'posts': object_list,
        'share_form': share_form,
    }
    return render(request, "feed/search_posts.html", context)


def search(request):
    query = request.GET.get('q')
    object_list = Post.objects.filter(description__contains=query).annotate(lr=Coalesce(Max('shared_date'),
                                                                                        'date_posted')).order_by('-lr')
    user_list = User.objects.filter(username__icontains=query)
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    p = request.user.profile
    friends = p.friends.all()
    share_form = SharePostForm()
    sent_to = []

    for se in sent_friend_requests:
        sent_to.append(se.to_user)
    context = {
        'users': user_list,
        'sent': sent_to,
        'friends': friends,
        'posts': object_list,
        'share_form': share_form,
    }
    return render(request, "feed/search.html", context)


def post_page(request):
    paginator = Paginator(Post.objects.all()
                          .annotate(lr=Coalesce(Max('shared_date'), 'date_posted'))
                          .order_by('-lr'), 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    share_form = SharePostForm()

    context = {
        'posts': posts,
        'share_form': share_form,
    }
    return render(request, "feed/post_page.html", context)


class DeleteNotificaiton(View):
    def get(self, request, pk, *args, **kwargs):
        thread = Thread.objects.get(pk=pk)
        try:
            Notifications.objects.get(recieving_user=request.user).delete()
        except:
            pass

        return redirect('message-thread', pk=thread.pk)


def CreateThreadButton(request, id, ):
    user = get_object_or_404(User, id=id)
    reciever = user

    if Thread.objects.filter(user=request.user, reciever=reciever).exists():
        thread = Thread.objects.filter(user=request.user, reciever=reciever).first()
        return redirect('message-thread', pk=thread.pk)
    elif Thread.objects.filter(user=reciever, reciever=request.user).exists():
        thread = Thread.objects.filter(user=reciever, reciever=request.user).first()
        return redirect('message-thread', pk=thread.pk)
    else:
        thread = Thread.objects.create(user=request.user, reciever=reciever)
        return redirect('message-thread', pk=thread.pk)
