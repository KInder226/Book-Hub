from django import forms
from .models import Book, ReadingProgress


class BookForm(forms.ModelForm):
    """Форма добавления/редактирования книги"""
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'description', 'cover', 'genres', 'pages', 'published_year']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'genres': forms.CheckboxSelectMultiple(),
            'pages': forms.NumberInput(attrs={'class': 'form-control'}),
            'published_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ReadingProgressForm(forms.ModelForm):
    """Форма обновления прогресса чтения"""
    class Meta:
        model = ReadingProgress
        fields = ['current_chapter', 'pages_read', 'is_completed', 'notes']
        widgets = {
            'current_chapter': forms.NumberInput(attrs={'class': 'form-control'}),
            'pages_read': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

