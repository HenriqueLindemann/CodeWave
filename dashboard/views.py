from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from accounts.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import activate
from projects.models import Project
from accounts.models import User
import logging
import requests
import re
import pdb
import json
import os

current_dir = 'dashboard/Templates/' # Path for specific apps templates
app_name = 'dashboard'

@login_required
def change_language(request, language_code):
    # Activate the new language
    activate(language_code)

    # Redirect back to the referring page or home
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def index(request):
    projects = Project.objects.all().order_by('-date_created')  # Obtém todos os projetos, mais recentes primeiro
    developers = User.objects.filter(is_developer=True)  # Obtém todos os desenvolvedores
    
    context = {
        'projects': projects,
        'developers': developers
    }

    # Se o usuário for um cliente (is_client)
    if hasattr(request.user, 'is_client') and request.user.is_client:
        # Obtém os projetos criados pelo usuário atual
        user_projects = Project.objects.filter(created_by=request.user).order_by('-date_created')
        
        # print(f"Projetos do usuário {request.user.username}: {user_projects}") #depuração

        context['user_projects'] = user_projects
    

    return render(request, 'index.html', context)
