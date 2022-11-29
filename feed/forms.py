from django import forms
from .models import Comment, Post


# form for creating a new comment and its fields
class NewCommentForm(forms.ModelForm):
    comment = forms.CharField(label='', max_length=255, widget=forms.Textarea(
        attrs={'rows': '3', 'placeholder': 'Enter a comment...'}))

    class Meta:
        model = Comment
        fields = ['comment']


# form for creating a new post and its fields
class NewPostForm(forms.ModelForm):
    description = forms.CharField(label='', widget=forms.Textarea(
        attrs={'rows': '4', 'placeholder': 'Type something...'}))

    class Meta:
        model = Post
        fields = ['description', 'pic']


# form for sharing a post and its fields
class SharePostForm(forms.Form):
    description = forms.CharField(label='', widget=forms.Textarea(attrs={
                                'rows': '4', 'placeholder': 'Type something...'}))


class ThreadForm(forms.Form):
    username = forms.CharField(label='', max_length=100)


class MessageForm(forms.Form):
    textbody = forms.CharField(label='', max_length=255)
