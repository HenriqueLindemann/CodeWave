from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from accounts.models import User
from accounts.forms import UserCreationForm, Autenticacao
import time
from django.utils.translation import activate
current_dir = 'core/Templates/'

@login_required 
def index(request):
    return HttpResponseRedirect("/dashboard/")

class MyLoginView(LoginView):
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:index')
    
    def form_invalid(self, form):
        messages.error(self.request,'Erro: Nome de usuário incorreto ou senha inválida')
        return self.render_to_response(self.get_context_data(form=form))


def change_language(request, language_code):
    # Activate the new language
    activate(language_code)

    # Redirect back to the referring page or home
    return redirect(request.META.get('HTTP_REFERER', '/'))

class UserCreate(CreateView):
    model = User
    template_name = 'login/register.html'  # Confirme se o caminho do template está correto
    form_class = UserCreationForm
    success_url = reverse_lazy('index')  # Certifique-se de que a URL 'index' está corretamente configurada

    def form_valid(self, form):
        valid = super(UserCreate, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        if new_user:
            login(self.request, new_user)
        return valid

    def get_context_data(self, **kwargs):
        context = super(UserCreate, self).get_context_data(**kwargs)
        context['form'] = self.get_form()  # Isso garante que o formulário seja passado como 'form'
        return context
