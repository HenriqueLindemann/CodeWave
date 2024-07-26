from django import forms
from .models import Project, Task, ProgrammingLanguage, TaskApplication

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'category']

class TaskForm(forms.ModelForm):
    programming_languages = forms.ModelMultipleChoiceField(
        queryset=ProgrammingLanguage.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'due_date', 'initial_value', 'programming_languages', 'application_status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'application_status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('id', None)
        self.fields.pop('project', None)
        self.fields['application_status'].label = "Application Status"
        self.fields['application_status'].help_text = "Choose whether this task is open or closed for applications"

TaskFormSet = forms.inlineformset_factory(
    Project, Task, form=TaskForm,
    extra=1, can_delete=True,
    fields=['title', 'description', 'status', 'due_date', 'initial_value', 'programming_languages', 'application_status']
)

class TaskApplicationForm(forms.ModelForm):
    class Meta:
        model = TaskApplication
        fields = ['proposed_value']

    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop('task', None)
        self.developer = kwargs.pop('developer', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.task = self.task
        instance.developer = self.developer
        if commit:
            instance.save()
        return instance

class TaskApplicationForm(forms.ModelForm):
    class Meta:
        model = TaskApplication
        fields = ['proposed_value']
        widgets = {
            'proposed_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task', None)
        super().__init__(*args, **kwargs)
        if task:
            self.fields['proposed_value'].initial = task.initial_value