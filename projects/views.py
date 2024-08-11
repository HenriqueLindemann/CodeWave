from django.shortcuts import get_object_or_404, render, redirect
from .models import Project, Task, TaskApplication, ProgrammingLanguage
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, TaskFormSet, FinalDeliveryForm
from .forms import TaskApplicationForm, TaskForm, TaskReviewForm
from django.forms import inlineformset_factory  
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.http import JsonResponse


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
    user = request.user
    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        task_formset = TaskFormSet(request.POST)
        
        if project_form.is_valid() and task_formset.is_valid():
            tasks = task_formset.save(commit=False)

            # Soma o custo total das tasks usando o campo 'initial_value'
            total_cost = sum(task.initial_value for task in tasks)
            
            # Verifica se o usuário tem Waves suficientes
            if user.wave_balance < total_cost:
                messages.error(request, 'Você não tem Waves suficientes para criar este projeto.')
                return redirect('projects:create_project')

            with transaction.atomic():
                # Desconta o saldo do usuário
                user.wave_balance -= total_cost
                user.save()

                # Cria o projeto
                project = project_form.save(commit=False)
                project.created_by = request.user
                project.save()

                # Cria as tasks associadas ao projeto
                for task in tasks:
                    task.project = project
                    task.save()

                # Salva as relações many-to-many (programming_languages)
                task_formset.save_m2m()
                
                messages.success(request, f'Projeto criado com sucesso! {total_cost} Waves foram descontados do seu saldo.')
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

def results_search_projects(request):
    search_title = request.session.get('search_title', '')
    search_category = request.session.get('search_category', '')
    projects = Project.objects.all()
    
    if search_title:
        projects = projects.filter(title__icontains=search_title)

    if search_category:
        projects = projects.filter(category__icontains=search_category)


    return render(request, 'results_search_projects.html', {'projects': projects})

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
        
        with transaction.atomic():  # transação para garantir a consistência dos dados
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

                #envia email se for aceito
                # accept_email(application.developer.email, application.task.project.title)
                
                messages.success(request, "Application accepted. The task has been assigned, other applications have been rejected, and the task is now closed for new applications.")
            
            elif action == 'reject':
                application.status = 'rejected'
                application.save()
                messages.success(request, "Application rejected.")
                
                #Envia email se for rejeitado
                # reject_email(application.developer.email, application.task.project.title)

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

@login_required
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    # Verificar se o usuário é o dono do projeto
    if request.user != project.created_by:
        messages.error(request, _("You don't have permission to edit this task."))
        return redirect('projects:project_detail', pk=project.id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save(commit=False)

            # Debugging prints to check values
            print(f"Original Value: {task.initial_value}")
            print(f"New Value: {updated_task.initial_value}")

            # Calcular a diferença de custo entre o valor anterior e o novo valor da tarefa
            difference = updated_task.initial_value - task.initial_value
            print(f"Difference: {difference}")

            # Verificar se o saldo é suficiente para cobrir o custo adicional, se houver
            if difference > 0 and request.user.wave_balance < difference:
                messages.error(request, 'Você não tem Waves suficientes para atualizar esta tarefa.')
                return redirect('projects:project_detail', pk=project.id)

            with transaction.atomic():
                # Descontar a diferença do saldo do usuário, se necessário
                if difference > 0:
                    request.user.wave_balance -= difference
                    request.user.save()

                # Atualizar a tarefa com os novos valores
                updated_task.save()
                form.save_m2m()  # Salva as relações many-to-many (programming_languages)

                if difference > 0:
                    messages.success(request, f'Tarefa atualizada com sucesso! {difference} Waves foram descontados do seu saldo.')
                else:
                    messages.success(request, 'Tarefa atualizada com sucesso.')
                    
                return redirect('projects:project_detail', pk=project.id)
        else:
            print("Form is not valid:", form.errors)
    else:
        form = TaskForm(instance=task)

    context = {
        'form': form,
        'task': task,
        'project': project,
        'can_be_deleted': task.can_be_deleted(),
    }
    return render(request, 'edit_task.html', context)


def add_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Verificar se o usuário é o dono do projeto
    if request.user != project.created_by:
        messages.error(request, _("You don't have permission to add tasks to this project."))
        return redirect('projects:project_detail', pk=project.id)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)

            # Verificar se o usuário tem Waves suficientes para adicionar a tarefa
            initial_value = task.initial_value

            if request.user.wave_balance < initial_value:
                messages.error(request, 'Você não tem Waves suficientes para adicionar esta tarefa.')
                return redirect('projects:project_detail', pk=project.id)

            with transaction.atomic():
                # Desconta o saldo do usuário
                request.user.wave_balance -= initial_value
                request.user.save()

                # Associa a tarefa ao projeto e salva
                task.project = project
                task.save()
                
                # Salva as relações many-to-many (programming_languages)
                form.save_m2m()

                messages.success(request, f'Tarefa adicionada com sucesso! {initial_value} Waves foram descontados do seu saldo.')
                return redirect('projects:project_detail', pk=project.id)
    else:
        form = TaskForm()

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'add_task.html', context)

@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project = task.project

    # Verificar se o usuário é o dono do projeto
    if request.user != project.created_by:
        return JsonResponse({
            'success': False,
            'error': _("You don't have permission to delete this task.")
        })

    # Verificar se a tarefa pode ser excluída
    if not task.can_be_deleted():
        return JsonResponse({
            'success': False,
            'error': _("This task cannot be deleted in its current status.")
        })

    try:
        # Recuperar o valor da tarefa para adicionar de volta ao saldo do usuário
        task_value = task.initial_value

        with transaction.atomic():  # Garantir a consistência dos dados
            # Adicionar o valor da tarefa de volta ao saldo do usuário
            request.user.wave_balance += task_value
            request.user.save()

            # Deletar a tarefa
            task.delete()

            return JsonResponse({
                'success': True,
                'message': _("Task deleted successfully and value added back to your Waves balance.")
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
    
@login_required
def submit_final_delivery(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.user != task.assigned_to or task.status != 'in_progress':
        messages.error(request, 'Você não tem permissão para enviar a entrega final desta tarefa.')
        return redirect('task_detail', task_id=task.id)
    
    if request.method == 'POST':
        form = FinalDeliveryForm(request.POST)
        if form.is_valid():
            # Salvar os comentários na tarefa
            task.final_delivery_comments = form.cleaned_data['comments']
            task.status = 'under_review'
            task.save()
            
            messages.success(request, 'Entrega final enviada com sucesso!')
            return redirect('projects:project_detail', pk=task.project.id)
    else:
        form = FinalDeliveryForm()
    
    return render(request, 'submit_final_delivery.html', {'form': form, 'task': task})

@login_required
def review_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    # Verificar se o usuário é o dono do projeto
    if request.user != task.project.created_by:
        messages.error(request, "Você não tem permissão para revisar esta tarefa.")
        return redirect('projects:project_detail', pk=task.project.id)
    
    # Verificar se a tarefa está no status 'under_review'
    if task.status != 'under_review':
        messages.error(request, "Esta tarefa não está disponível para revisão.")
        return redirect('projects:project_detail', pk=task.project.id)

    if request.method == 'POST':
        form = TaskReviewForm(request.POST)
        if form.is_valid():
            review_status = form.cleaned_data['review_status']
            feedback = form.cleaned_data['feedback']
            
            if review_status == 'approved':
                task.status = 'completed'
                messages.success(request, "Tarefa aprovada com sucesso!")
            else:
                task.status = 'in_progress'
                messages.info(request, "Tarefa retornada para o desenvolvedor para ajustes.")
            
            task.feedback = feedback
            task.save()
            
            # Redirecionando para a página do projeto
            return redirect('projects:project_detail', pk=task.project.id)
    else:
        form = TaskReviewForm()

    context = {
        'task': task,
        'form': form,
        'final_delivery_comments': task.final_delivery_comments,
    }
    return render(request, 'review_task.html', context)