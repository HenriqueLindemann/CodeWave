# coding=utf-8
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView, TemplateView, UpdateView, FormView
)
from django.shortcuts import render, get_object_or_404

from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from .models import User, Skill
from projects.models import Project, Task
from .forms import *
from django.contrib.auth import get_user_model
#Emerson mexendo
from .forms import AddWaveForm


current_dir = 'accounts/Templates/' # Path for specific apps templates
app_name = 'accounts'

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/Templates/index.html'

@login_required
def user_profile(request):
    user = request.user
    owned_projects = Project.objects.filter(created_by=user)
    assigned_tasks = Task.objects.filter(assigned_to=user)

    assigned_tasks = user.assigned_tasks.all()
    
    context = {
        'user': user,
        'wave_balance': user.wave_balance,
        'owned_projects': owned_projects,
        'assigned_tasks': assigned_tasks,
    }
    
    return render(request, current_dir + 'user_profile.html', context)

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

def search_developer(request):
    skills = Skill.objects.all()

    if request.method == 'POST':
        search_name = request.POST.get('searchInput', '')
        search_skill = request.POST.get('filterSelect', '')
        request.session['search_name'] = search_name
        request.session['search_skill'] = search_skill

        return redirect('accounts:results_search_devs')

    return render(request, 'search_developer.html', {'skills': skills})

def results_search_devs(request):
    search_name = request.session.get('search_name', '')
    search_skill = request.session.get('search_skill', '')
    developers = User.objects.all()

    if search_name:
        developers = User.objects.filter(name__icontains=search_name)

    if search_skill:
        developers = developers.filter(skills__id=search_skill)

    return render(request, 'results_search_devs.html', {'developers': developers})

@login_required
def view_profile(request, user_id):
    User = get_user_model()
    profile_user = get_object_or_404(User, id=user_id)
    
    # Determina se o usuário atual tem permissão para ver informações sensíveis
    can_view_sensitive_info = request.user.is_staff or request.user == profile_user

    # Projetos que o usuário é dono
    owned_projects = Project.objects.filter(created_by=profile_user)

    # Projetos em que o usuário é responsável por desenvolver uma task
    projects_with_tasks = Project.objects.filter(tasks__assigned_to=profile_user).distinct()

    # Tasks que o usuário é responsável por desenvolver
    assigned_tasks = Task.objects.filter(assigned_to=profile_user)

    context = {
        'profile_user': profile_user,
        'can_view_sensitive_info': can_view_sensitive_info,
        'owned_projects': owned_projects,
        'projects_with_tasks': projects_with_tasks,
        'assigned_tasks': assigned_tasks,
    }

    # Se o usuário tem permissão, adiciona informações sensíveis ao contexto
    if can_view_sensitive_info:
        context['user_balance'] = profile_user.balance
        context['user_email'] = profile_user.email

    return render(request, 'view_profile.html', context)

#Emerson mexendo 
@login_required
def add_wave(request):
    if request.method == 'POST':
        form = AddWaveForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user = request.user
            
            # Adiciona o valor ao saldo do usuário
            user.wave_balance += amount
            user.save()

            messages.success(request, f'Você adicionou {amount} Wave à sua conta!')
            return redirect('accounts:user_profile')
        else:
            messages.error(request, 'Por favor, corrija o erro abaixo.')
    else:
        form = AddWaveForm()

    return render(request, 'add_wave.html', {'form': form})

