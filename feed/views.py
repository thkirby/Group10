from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.utils import timezone
from .forms import NewCommentForm, NewPostForm, SharePostForm
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import json
from .models import Post, Like, Comment


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
        return redirect('home')
