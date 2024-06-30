from django.shortcuts import get_object_or_404, render
from .models import Project
from django.contrib.auth.decorators import login_required

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()  # Acessa todas as tarefas relacionadas ao projeto
    return render(request, 'project_detail.html', {'project': project, 'tasks': tasks})
