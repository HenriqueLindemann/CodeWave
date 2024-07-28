from django.shortcuts import get_object_or_404, render, redirect
from .models import Project, Task, TaskApplication, ProgrammingLanguage
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, TaskFormSet
from .forms import TaskApplicationForm, TaskForm
from django.forms import inlineformset_factory  
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.prefetch_related(
            Prefetch(
                'tasks',
                queryset=Task.objects.prefetch_related(
                    'programming_languages',
                    Prefetch(
                        'applications',
                        queryset=TaskApplication.objects.select_related('developer'),
                        to_attr='prefetched_applications'
                    )
                )
            )
        ),
        id=pk
    )
    
    is_project_owner = project.created_by == request.user

    # Debug print
    for task in project.tasks.all():
        print(f"Task: {task.title}, Application Status: {task.application_status}")

    return render(request, 'project_detail.html', {
        'project': project,
        'is_project_owner': is_project_owner
    })

@login_required
def create_project(request):
    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        task_formset = TaskFormSet(request.POST)
        
        if project_form.is_valid() and task_formset.is_valid():
            project = project_form.save(commit=False)
            project.created_by = request.user
            project.save()
            
            tasks = task_formset.save(commit=False)
            for task in tasks:
                task.project = project
                task.save()
            task_formset.save_m2m()  # Salva as relações many-to-many
            
            return redirect('projects:project_detail', pk=project.pk)
    else:
        project_form = ProjectForm()
        task_formset = TaskFormSet()
    
    return render(request, 'create_project.html', {
        'project_form': project_form,
        'task_formset': task_formset,
    })

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projeto atualizado com sucesso.')
            return redirect('projects:project_detail', pk=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'edit_project.html', {
        'form': form,
        'project': project
    })

@login_required
def search_projects(request):
    projects = Project.objects.all()
    categories = set(project.category for project in projects)

    if request.method == 'POST':
        search_title = request.POST.get('searchInput', '')
        search_category = request.POST.get('categorySelect', '')

        request.session['search_title'] = search_title
        request.session['search_category'] = search_category

        return redirect('projects:results_search_projects')

    return render(request, 'search_projects.html', {'projects': projects, 'categories': categories})

@login_required
def results_search_projects(request):
    search_title = request.session.get('search_title', '')
    search_category = request.session.get('search_category', '')
    projects = Project.objects.all()
    
    if search_title:
        projects = projects.filter(title__icontains=search_title)

    if search_category:
        projects = projects.filter(category__icontains=search_category)


    return render(request, 'results_search_projects.html', {'projects': projects})

@login_required
def search_tasks(request):
    projects = Project.objects.all()
    programming_languages = ProgrammingLanguage.objects.all()  # Mudamos o nome da variável
    application_statuses = dict(Task.APPLICATION_STATUS_CHOICES)

    if request.method == 'POST':
        search_title = request.POST.get('searchInput', '')
        search_project = request.POST.get('projectSelect', '')
        search_language = request.POST.get('languageSelect', '')
        search_app_status = request.POST.get('applicationStatusSelect', '')

        request.session['search_title'] = search_title
        request.session['search_project'] = search_project
        request.session['search_language'] = search_language
        request.session['search_app_status'] = search_app_status

        return redirect('projects:results_search_tasks')

    context = {
        'projects': projects,
        'programming_languages': programming_languages,  # Mudamos o nome da chave no contexto
        'application_statuses': application_statuses,
    }
    return render(request, 'search_tasks.html', context)

@login_required
def results_search_tasks(request):
    search_title = request.session.get('search_title', '')
    search_project = request.session.get('search_project', '')
    search_language = request.session.get('search_language', '')
    search_app_status = request.session.get('search_app_status', '')

    tasks = Task.search(
        title=search_title,
        project=search_project,
        language=search_language,
        app_status=search_app_status
    )

    context = {
        'tasks': tasks,
        'search_title': search_title,
        'search_project': search_project,
        'search_language': search_language,
        'search_app_status': search_app_status,
    }
    return render(request, 'results_search_tasks.html', context)

@login_required
def apply_for_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.user == task.project.created_by:
        messages.error(request, "You can't apply for your own task.")
        return redirect('projects:project_detail', pk=task.project.id)
    
    # Verificar se já existe uma aplicação do usuário para esta tarefa
    existing_application = TaskApplication.objects.filter(
        task=task, 
        developer=request.user
    ).first()

    # Se a aplicação existente foi rejeitada, o usuário só pode visualizar
    if existing_application and existing_application.status == 'rejected':
        context = {
            'task': task,
            'application': existing_application,
            'is_rejected': True
        }
        return render(request, 'apply_for_task.html', context)

    # Verificar se a tarefa está aberta para candidaturas
    if task.status != 'open' or task.application_status != 'open':
        if existing_application:
            # Se o usuário já se candidatou, mostrar os detalhes da candidatura
            context = {
                'task': task,
                'application': existing_application,
                'is_closed': True
            }
            return render(request, 'apply_for_task.html', context)
        else:
            messages.error(request, "This task is not open for applications.")
            return redirect('projects:project_detail', pk=task.project.id)

    if request.method == 'POST':
        form = TaskApplicationForm(request.POST, instance=existing_application)
        if form.is_valid():
            application = form.save(commit=False)
            application.task = task
            application.developer = request.user
            application.status = 'pending'  # Resetar o status para pendente em caso de atualização
            application.save()
            if existing_application:
                messages.success(request, "Your application has been updated successfully.")
            else:
                messages.success(request, "Your application has been submitted successfully.")
            return redirect('projects:project_detail', pk=task.project.id)
    else:
        form = TaskApplicationForm(instance=existing_application)
    
    context = {
        'form': form,
        'task': task,
        'is_update': existing_application is not None
    }
    return render(request, 'apply_for_task.html', context)

@login_required
def review_application(request, application_id):
    application = get_object_or_404(TaskApplication, id=application_id)
    task = application.task
    project = task.project
    
    if request.user != project.created_by:
        messages.error(request, "You don't have permission to review this application.")
        return redirect('projects:project_detail', pk=project.id)
    
    if task.status != 'open' or task.application_status != 'open':
        messages.error(request, "This task is no longer open for applications.")
        return redirect('projects:project_detail', pk=project.id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        with transaction.atomic():  # Usamos uma transação para garantir a consistência dos dados
            if action == 'accept':
                # Aceita a aplicação atual
                application.status = 'accepted'
                task.assigned_to = application.developer
                task.status = 'in_progress'
                task.application_status = 'closed'  # Fecha a tarefa para novas candidaturas
                application.save()
                task.save()
                
                # Rejeita todas as outras aplicações para esta tarefa
                TaskApplication.objects.filter(task=task).exclude(id=application.id).update(status='rejected')

                #envia email
                accept_email(application.developer.email, application.task.project.title)
                
                messages.success(request, "Application accepted. The task has been assigned, other applications have been rejected, and the task is now closed for new applications.")
            elif action == 'reject':
                application.status = 'rejected'
                application.save()
                messages.success(request, "Application rejected.")
                reject_email(application.developer.email, application.task.project.title)
            else:
                messages.error(request, "Invalid action.")
                return redirect('projects:project_detail', pk=project.id)
        
        return redirect('projects:project_detail', pk=project.id)
    
    return render(request, 'review_application.html', {'application': application, 'task': task})

def accept_email(developer_email, project_title):
    subject = 'Você foi aceito no projeto!'
    message = f'Parabéns Desenvolvedor! Você foi aceito no projeto {project_title}.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [developer_email]
    
    send_mail(subject, message, email_from, recipient_list)

def reject_email(developer_email, project_title):
    subject = 'Você não foi aceito no projeto!'
    message = f'Infelizmente você não foi aceito no projeto {project_title}.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [developer_email]
    
    send_mail(subject, message, email_from, recipient_list)