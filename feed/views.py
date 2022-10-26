from django.shortcuts import render
from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewPostForm
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from .models import Post, Like


class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'feed/landing.html')


class PostListView(ListView):
    model = Post
    template_name = 'feed/post_list.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            liked = [i for i in Post.objects.all() if Like.objects.filter(user=self.request.user, post=i)]
            context['liked_post'] = liked
        return context


class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feed/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        liked = [i for i in Post.objects.filter(user_name=user) if Like.objects.filter(user=self.request.user, post=i)]
        context['liked_post'] = liked
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(user_name=user).order_by('-date_posted')


class CreatePost(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if request.method == "POST":
            form = NewPostForm(request.POST, request.FILES)
            if form.is_valid():
                data = form.save(commit=False)
                data.user_name = user
                data.save()
                messages.success(request, f'Posted Successfully')
                return redirect('home')
        else:
            form = NewPostForm()
        return render(request, 'feed/create_post.html', {'post_form': form})
