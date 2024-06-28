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

 

def index(request):
    projects = Project.objects.all()  # Obtém todos os projetos
    developers = User.objects.filter(is_developer=True)  # Supõe que há um campo 'is_developer' no modelo User
    
    context = {
        'projects': projects,
        'developers': developers
    }
    return render(request, 'index.html', context)  # Ajuste o caminho do template conforme necessário
