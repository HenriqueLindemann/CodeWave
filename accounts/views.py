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
from .models import User, Skill
from .forms import *


current_dir = 'accounts/Templates/' # Path for specific apps templates
app_name = 'accounts'

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/Templates/index.html'

@login_required
def user_profile(request):
    user = request.user
    return render(request, current_dir + 'user_profile.html', {'user': user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, instance=request.user)  # Passa a instância atual do usuário
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:user_profile')  
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserProfileEditForm(instance=request.user)  # Formulário pré-preenchido com os dados do usuário

    return render(request, current_dir + 'edit_profile.html', {'form': form})

@login_required
def search_developer(request):
    skills = Skill.objects.all()

    if request.method == 'POST':
        search_name = request.POST.get('searchInput', '')
        search_skill = request.POST.get('filterSelect', '')
        request.session['search_name'] = search_name
        request.session['search_skill'] = search_skill

        return redirect('accounts:results_search')

    return render(request, 'search_developer.html', {'skills': skills})

@login_required
def results_search(request):
    search_name = request.session.get('search_name', '')
    search_skill = request.session.get('search_skill', '')
    developers = User.objects.none()

    if search_name:
        developers = User.objects.filter(name__icontains=search_name)

    if search_skill:
        developers = developers.filter(skills__id=search_skill)

    return render(request, 'results_search.html', {'developers': developers})