from django import forms
from .models import Project, Task, ProgrammingLanguage, TaskApplication
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


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
        fields = ['title', 'description', 'due_date', 'initial_value', 'programming_languages']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('id', None)
        self.fields.pop('project', None)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status = 'open'
        instance.application_status = 'open'
        if commit:
            instance.save()
        return instance

TaskFormSet = forms.inlineformset_factory(
    Project, Task, form=TaskForm,
    extra=1, can_delete=True,
    fields=['title', 'description', 'due_date', 'initial_value', 'programming_languages']
)

class FinalDeliveryForm(forms.Form):
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        label='Comentários',
        help_text='Inclua o link do repositório e quaisquer informações relevantes sobre a entrega.'
    )
    
    class Meta:
        fields = ['comments']

class TaskApplicationForm(forms.ModelForm):
    class Meta:
        model = TaskApplication
        fields = ['proposed_value', 'comment']
        widgets = {
            'proposed_value': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0.01'  # Adiciona validação no lado do cliente
            }),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        task = kwargs.pop('task', None)
        super().__init__(*args, **kwargs)
        if task:
            self.fields['proposed_value'].initial = task.initial_value

        # Adiciona validação no lado do servidor
        self.fields['proposed_value'].validators.append(MinValueValidator(0.01))

    def clean_proposed_value(self):
        value = self.cleaned_data['proposed_value']
        if value <= 0:
            raise forms.ValidationError(_("The proposed value must be greater than zero."))
        return value
    
class TaskReviewForm(forms.Form):
    REVIEW_CHOICES = [
        ('approved', 'Aprovar'),
        ('rejected', 'Rejeitar'),
    ]
    review_status = forms.ChoiceField(choices=REVIEW_CHOICES, widget=forms.RadioSelect, label="Status da Revisão")
    feedback = forms.CharField(widget=forms.Textarea, label="Feedback")