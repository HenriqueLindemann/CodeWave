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
        fields = ['title', 'description', 'status', 'due_date', 'initial_value', 'programming_languages']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('id', None)
        self.fields.pop('project', None)

TaskFormSet = forms.inlineformset_factory(
    Project, Task, form=TaskForm,
    extra=1, can_delete=True,
    fields=['title', 'description', 'status', 'due_date', 'initial_value', 'programming_languages']
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