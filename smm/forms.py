from django import forms
from .models import Post
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class PostForm(forms.Form):
    post_title = forms.CharField(label='Post title', required=False)
    post_body = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PostFormModel(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('post_title', 'post_body')


class PostFormModel1(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_title', 'branches', 'post_body', 'image', 'videofile']