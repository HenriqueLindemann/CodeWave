from django import forms
from .models import Project, Task, ProgrammingLanguage, TaskApplication

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = "Título do Projeto"
        self.fields['description'].label = "Descrição"
        self.fields['category'].label = "Categoria"
        
        # Adicione placeholder e help_text
        self.fields['title'].widget.attrs['placeholder'] = "Digite o título do projeto"
        self.fields['description'].widget.attrs['placeholder'] = "Descreva o projeto"
        self.fields['category'].widget.attrs['placeholder'] = "Digite a categoria do projeto"
        
        self.fields['description'].help_text = "Forneça uma descrição detalhada do projeto"
        self.fields['category'].help_text = "Exemplo: Desenvolvimento Web, Mobile, IA, etc."

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError("O título deve ter pelo menos 5 caracteres.")
        return title

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if len(category) < 2:
            raise forms.ValidationError("A categoria deve ter pelo menos 2 caracteres.")
        return category
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
        fields = ['proposed_value', 'comment']
        widgets = {
            'proposed_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task', None)
        super().__init__(*args, **kwargs)
        if task:
            self.fields['proposed_value'].initial = task.initial_value