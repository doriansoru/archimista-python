"""
Form per Institution (Profili istituzionali).
Allineati a Ruby: app/views/institutions/_form.html.erb
"""

from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Institution,
    InstitutionEditor,
    Term,
)


# =============================================================================
# FORM PER INSTITUTION
# =============================================================================

class InstitutionForm(forms.ModelForm):
    """Form principale per istituzione — allineato a Ruby.
    
    Campi Ruby:
    - name (text_field, required) → "Denominazione"
    - description (text_area, textile) → "Descrizione"
    - note (text_area) → "Annotazioni"
    - institution_editors (formset) → "Compilatori"
    """
    class Meta:
        model = Institution
        fields = ['name', 'description', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'name': 'Denominazione',
            'description': 'Descrizione',
            'note': 'Annotazioni',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError('Questo campo è obbligatorio.')
        return name.strip()


# =============================================================================
# FORM PER INSTITUTION EDITOR (COMPILATORI)
# =============================================================================

class InstitutionEditorForm(forms.ModelForm):
    editing_type = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = InstitutionEditor
        fields = ['name', 'qualifier', 'editing_type', 'edited_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.TextInput(attrs={'class': 'form-control'}),
            'edited_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'name': 'Compilatore',
            'qualifier': 'Qualifica',
            'editing_type': 'Tipologia di intervento',
            'edited_at': 'Data intervento',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        terms = Term.objects.filter(
            vocabulary__name='editors.editing_type'
        ).order_by('position')
        choices = [('', '-- Seleziona --')] + [(t.term_value, t.term_value) for t in terms]
        self.fields['editing_type'].choices = choices


# Formset inline per compilatori
InstitutionEditorFormSet = inlineformset_factory(
    Institution, InstitutionEditor, form=InstitutionEditorForm,
    extra=0, can_delete=True
)
