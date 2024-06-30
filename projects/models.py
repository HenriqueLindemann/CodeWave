from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

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

    def get_unique_languages(self):
        # Utiliza um QuerySet para coletar todos os objetos ProgrammingLanguage associados às tasks deste projeto
        # Distinct garante que cada linguagem seja listada apenas uma vez
        return ProgrammingLanguage.objects.filter(
            tasks__project=self
        ).distinct().order_by('name')
    
class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

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
    programming_languages = models.ManyToManyField(ProgrammingLanguage, related_name='tasks', blank=True)


    def __str__(self):
        return self.title