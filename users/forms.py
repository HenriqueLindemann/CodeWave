from django import forms
from .models import UserProfile, Skill, Tag
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone_number', 'rating', 'location', 'skills', 'tags']
        widgets = {
            'skills': forms.CheckboxSelectMultiple(),
            'tags': forms.CheckboxSelectMultiple(),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # Ajuste conforme necessário