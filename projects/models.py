from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, related_name='created_projects', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_unique_languages(self):
        return ProgrammingLanguage.objects.filter(
            tasks__project=self
        ).distinct().order_by('name')

class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),  # Quando o cliente cria a task
        ('in_progress', 'In Progress'),  # Após o cliente aceitar a candidatura de um desenvolvedor
        ('under_review', 'Under Review'),  # Quando o desenvolvedor envia o trabalho para revisão
        ('completed', 'Completed'),  # Quando o cliente aprova e confirma a conclusão da tarefa
        ('rejected', 'Rejected'),  # Se o cliente rejeita o trabalho e requer alterações
        ('cancelled', 'Cancelled'),  # Se a tarefa for cancelada por qualquer motivo
    ]
    APPLICATION_STATUS_CHOICES = [
        ('open', 'Open for Applications'),
        ('closed', 'Closed for Applications'),
    ]

    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open')
    assigned_to = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    initial_value = models.DecimalField(max_digits=10, decimal_places=2)  # Valor proposto pelo cliente
    application_status = models.CharField(max_length=50, choices=APPLICATION_STATUS_CHOICES, default='open')
    programming_languages = models.ManyToManyField(ProgrammingLanguage, related_name='tasks', blank=True)

    def search_tasks(self, title='', project=None, language=None, app_status=''):
        queryset = Task.objects.all()
        
        if title:
            queryset = queryset.filter(title__icontains=title)
        
        if project:
            queryset = queryset.filter(project_id=project)
        
        if language:
            queryset = queryset.filter(programming_languages__id=language)
        
        if app_status:
            queryset = queryset.filter(application_status=app_status)
        
        return queryset.distinct()
    
    @classmethod
    def search(cls, title='', project=None, language=None, app_status=''):
        return cls().search_tasks(title, project, language, app_status)
    
    def __str__(self):
        return self.title

class TaskApplication(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    task = models.ForeignKey(Task, related_name='applications', on_delete=models.CASCADE)
    developer = models.ForeignKey(User, related_name='task_applications', on_delete=models.CASCADE)
    proposed_value = models.DecimalField(max_digits=10, decimal_places=2)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=APPLICATION_STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True, null=True)  

    def __str__(self):
        return f"{self.developer.username} - {self.task.title}"