from django import forms
from .models import Post, Comment


class NewCommentForm(forms.ModelForm):
    comment = forms.CharField(label='', max_length=255, widget=forms.Textarea(
        attrs={'rows': '3', 'placeholder': 'Enter a comment...'}))

    class Meta:
        model = Comment
        fields = ['comment']
