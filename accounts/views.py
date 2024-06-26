# coding=utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView, TemplateView, UpdateView, FormView
)
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from .models import User
from .forms import *


@login_required
def index(request):
    profile_form = Profile_Form(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)
    if request.method == 'POST':
        if request.POST.get('profile'):
            profile_form = Profile_Form(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile has been updated!')
            else:
                messages.error(request, 'Input Error')
        if request.POST.get('password'):
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Password has been changed!')
            else:
                messages.error(request, 'Input Error')
    context = {'profile_form': profile_form,
               'password_form': password_form}
    return render(request, 'accounts/Templates/index.html', context)


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/Templates/index.html'
