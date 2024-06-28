from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, related_name='projects', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Task(models.Model):
    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, default='open')  # Exemplos: open, in_progress, completed
    assigned_to = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    proposed_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Valor proposto pelo cliente
    is_accepted = models.BooleanField(null=True, blank=True)  # Status da aceitação da proposta pelo dev
    application_status = models.CharField(max_length=50, default='pending')  # Exemplos: pending, reviewed, accepted, rejected

    def __str__(self):
        return self.title
