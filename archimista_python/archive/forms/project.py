from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Project, ProjectUrl, ProjectManager, ProjectStakeholder, RelProjectFond,
    Term, Fond
)
from archimista_python.archive.widgets import FondSelect2Widget, auto_select_threshold
from datetime import datetime

class ProjectForm(forms.ModelForm):
    # Campi a scelta con vocabolari controllati
    project_type_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="Tipologia d'intervento",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --"
    )
    status_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="Status",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --"
    )
    
    # Campi anno come select (come Ruby)
    start_year = forms.ChoiceField(
        required=False,
        label="Anno d'inizio",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    end_year = forms.ChoiceField(
        required=False,
        label="Anno di fine",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Project
        fields = [
            'name', 'project_type_term', 'project_type', 'published',
            'start_year', 'end_year', 'status_term', 'status',
            'description', 'note'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_type': forms.HiddenInput(),
            'status': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control x-long-content'}),
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control short-content'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Denominazione',
            'published': 'Pubblicato',
            'description': 'Descrizione',
            'note': 'Annotazioni',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Imposta i queryset per i campi a scelta
        self.fields['project_type_term'].queryset = Term.objects.filter(
            vocabulary__name='projects.project_type'
        ).order_by('position')
        self.fields['status_term'].queryset = Term.objects.filter(
            vocabulary__name='projects.status'
        ).order_by('position')
        
        # Opzioni anni (1970 a oggi+5 come Ruby)
        current_year = datetime.now().year
        years = [(str(y), str(y)) for y in range(1970, current_year + 6)]
        self.fields['start_year'].choices = years
        self.fields['end_year'].choices = years
        
        # Valori predefiniti se nuovi
        if not self.instance.pk:
            self.initial['start_year'] = str(current_year)
            self.initial['end_year'] = str(current_year)
            self.initial['published'] = True
        else:
            if self.instance.start_year:
                self.initial['start_year'] = str(self.instance.start_year)
            if self.instance.end_year:
                self.initial['end_year'] = str(self.instance.end_year)

        # Sincronizzazione campi term
        if self.instance.pk:
            if not self.instance.project_type_term and self.instance.project_type:
                term = Term.objects.filter(vocabulary__name='projects.project_type', term_value=self.instance.project_type).first()
                if term:
                    self.initial['project_type_term'] = term
            
            if not self.instance.status_term and self.instance.status:
                term = Term.objects.filter(vocabulary__name='projects.status', position=self.instance.status).first()
                if term:
                    self.initial['status_term'] = term

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('project_type_term'):
            instance.project_type = self.cleaned_data['project_type_term'].term_value
        
        if self.cleaned_data.get('status_term'):
            try:
                instance.status = int(self.cleaned_data['status_term'].position)
            except:
                instance.status = 0
                
        if commit:
            instance.save()
        return instance

class ProjectUrlForm(forms.ModelForm):
    class Meta:
        model = ProjectUrl
        fields = ['url', 'note', 'position']
        widgets = {
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.HiddenInput(),
        }

class ProjectManagerForm(forms.ModelForm):
    qualifier_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="Qualificatore",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --"
    )
    
    class Meta:
        model = ProjectManager
        fields = ['name', 'qualifier_term', 'qualifier']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.HiddenInput(),
        }
        labels = {
            'name': 'Nome',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qualifier_term'].queryset = Term.objects.filter(
            vocabulary__name='project_managers.qualifier'
        ).order_by('position')
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('qualifier_term'):
            instance.qualifier = self.cleaned_data['qualifier_term'].term_value
        if commit:
            instance.save()
        return instance

class ProjectStakeholderForm(forms.ModelForm):
    qualifier_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label="Qualificatore",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --"
    )
    
    class Meta:
        model = ProjectStakeholder
        fields = ['name', 'qualifier_term', 'qualifier']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.HiddenInput(),
        }
        labels = {
            'name': 'Nome',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qualifier_term'].queryset = Term.objects.filter(
            vocabulary__name='project_stakeholders.qualifier'
        ).order_by('position')

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('qualifier_term'):
            instance.qualifier = self.cleaned_data['qualifier_term'].term_value
        if commit:
            instance.save()
        return instance

class RelProjectFondForm(forms.ModelForm):
    fond = forms.ModelChoiceField(
        queryset=Fond.objects.filter(parent__isnull=True).order_by('name'),
        widget=FondSelect2Widget(),
        label="Fondo"
    )

    class Meta:
        model = RelProjectFond
        fields = ['fond']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'fond', threshold=20)

# Formset
ProjectUrlFormSet = inlineformset_factory(Project, ProjectUrl, form=ProjectUrlForm, extra=1, can_delete=True)
ProjectManagerFormSet = inlineformset_factory(Project, ProjectManager, form=ProjectManagerForm, extra=1, can_delete=True)
ProjectStakeholderFormSet = inlineformset_factory(Project, ProjectStakeholder, form=ProjectStakeholderForm, extra=1, can_delete=True)
RelProjectFondFormSet = inlineformset_factory(Project, RelProjectFond, form=RelProjectFondForm, extra=1, can_delete=True)
