from django import forms
from .models import Post, Comment, PostReport


class PostForm(forms.ModelForm):
    """Форма создания/редактирования поста"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'post_type', 'chapter', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'post_type': forms.Select(attrs={'class': 'form-control'}),
            'chapter': forms.NumberInput(attrs={'class': 'form-control'}),
            'tags': forms.CheckboxSelectMultiple(),
        }


class CommentForm(forms.ModelForm):
    """Форма добавления комментария"""
    class Meta:
        model = Comment
        fields = ['content', 'parent']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'parent': forms.HiddenInput(),
        }


class PostReportForm(forms.ModelForm):
    """Форма жалобы на пост"""
    class Meta:
        model = PostReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

