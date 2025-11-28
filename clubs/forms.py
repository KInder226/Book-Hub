from django import forms
from .models import Club, ClubInvitation


class ClubForm(forms.ModelForm):
    """Форма создания/редактирования клуба"""
    class Meta:
        model = Club
        fields = ['name', 'description', 'cover', 'is_private']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'is_private': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClubInvitationForm(forms.ModelForm):
    """Форма приглашения участника"""
    class Meta:
        model = ClubInvitation
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
        }

