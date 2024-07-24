# coding=utf-8

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django import forms
from .models import User
from django.utils.translation import gettext as _
from django.contrib.auth.models import Group


class UserAdminCreationForm(UserCreationForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True,
                                   help_text="Select one Group")

    class Meta:
        model = User
        fields = ['username', 'email', 'group']

    def save(self, commit=True):
        instance = super(UserAdminCreationForm, self).save(commit=False)
        if commit:
            instance.save()
            group.user_set.add(instance)
        return instance


class Profile_Form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class UserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label=_("Repeat the password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_("Repeat the same password for verification.")
    )

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'is_developer', 'is_client', 'skills','bio')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_developer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_client': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'skills': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),  

        }


    # def save(self, commit=True):
    #     instance = super(UserCreationForm, self).save(commit=False)
    #     group = Group.objects.get(name=self.cleaned_data['group'])
    #     if group:
    #         if str(self.cleaned_data['group']) == 'Developer':
    #             instance.avatar = '/static/img/avatars/developer.png'
    #     if commit:
    #         instance.save()
    #         group.user_set.add(instance)
    #     return instance

class UserProfileEditForm(UserChangeForm):
    password = None  # Desabilita a edição de senha neste formulário

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'bio', 'is_developer', 'is_client', 'skills')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_developer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_client': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'skills': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['email'].help_text = None


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'name', 'is_active', 'is_staff']

class Autenticacao(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}))
    password = forms.CharField(label=_("Senha"),
                               widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}))
    


