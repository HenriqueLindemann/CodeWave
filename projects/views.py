from django.shortcuts import get_object_or_404, render, redirect
from .models import Project, Task, TaskApplication, ProgrammingLanguage
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, TaskFormSet


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
def search_projects(request):
    projects = Project.objects.all()

    if request.method == 'POST':
        search_title = request.POST.get('searchInput', '')
        search_category = request.POST.get('categorySelect', '')

        request.session['search_title'] = search_title
        request.session['search_category'] = search_category

        return redirect('projects:results_search_projects')

    return render(request, 'search_projects.html', {'projects': projects})

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