from django import forms
from .models import Comment


class NewCommentForm(forms.ModelForm):
    comment = forms.CharField(label='', max_length=255, widget=forms.Textarea(
        attrs={'rows': '3', 'placeholder': 'Enter a comment...'}))

    class Meta:
        model = Comment
        fields = ['comment']


class SharePostForm(forms.Form):
    description = forms.CharField(label='', widget=forms.Textarea(attrs={
        'rows': '4', 'placeholder': 'Type something...'}))
