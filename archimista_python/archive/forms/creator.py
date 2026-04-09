from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Creator,
    CreatorName, CreatorLegalStatus, CreatorUrl, CreatorIdentifier, CreatorActivity, CreatorEditor,
    RelCreatorCreator, RelCreatorInstitution, RelCreatorSource, RelCreatorFond,
    Institution, Source, Fond, CreatorAssociationType, Term,
)
from archimista_python.archive.widgets import (
    InstitutionSelect2Widget, SourceSelect2Widget, FondSelect2Widget, CreatorSelect2Widget,
    auto_select_threshold,
)

# =============================================================================
# FORM PER CREATOR (ALLINEATI A RUBY)
# =============================================================================

class CreatorForm(forms.ModelForm):
    class Meta:
        model = Creator
        fields = [
            'creator_type', 'creator_corporate_type', 'residence', 'abstract',
            'history', 'note', 'published'
        ]
        widgets = {
            'creator_type': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '---'), ('P', 'Persona'), ('F', 'Famiglia'), ('E', 'Ente'),
            ]),
            'creator_corporate_type': forms.Select(attrs={'class': 'form-select'}),
            'residence': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'history': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'creator_type': 'Tipologia',
            'creator_corporate_type': 'Tipologia ente',
            'residence': 'Sede',
            'abstract': 'Abstract',
            'history': 'Profilo storico / Biografia',
            'note': 'Appunti di servizio',
            'published': 'Pubblicato',
        }

# Form per il nome preferito (separato dagli altri nomi)
class CreatorPreferredNameForm(forms.ModelForm):
    class Meta:
        model = CreatorName
        fields = ['name', 'first_name', 'last_name', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Form per altri nomi (senza preferred, name, creator_type)
class CreatorOtherNameForm(forms.ModelForm):
    qualifier_term = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = CreatorName
        fields = ['name', 'qualifier', 'qualifier_term', 'note']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.HiddenInput(),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        terms = Term.objects.filter(
            vocabulary__name='creator_names.qualifier'
        ).order_by('position')
        choices = [('', '-- Seleziona --')] + [(t.term_value, t.term_value) for t in terms]
        self.fields['qualifier_term'].choices = choices
        if self.instance and self.instance.qualifier:
            self.fields['qualifier_term'].initial = self.instance.qualifier

    def save(self, commit=True):
        if self.cleaned_data.get('qualifier_term'):
            self.instance.qualifier = self.cleaned_data['qualifier_term']
        return super().save(commit)

class CreatorLegalStatusForm(forms.ModelForm):
    class Meta:
        model = CreatorLegalStatus
        fields = ['legal_status', 'note']
        widgets = {
            'legal_status': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class CreatorUrlForm(forms.ModelForm):
    class Meta:
        model = CreatorUrl
        fields = ['url', 'note']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CreatorIdentifierForm(forms.ModelForm):
    class Meta:
        model = CreatorIdentifier
        fields = ['identifier', 'identifier_source', 'note']
        widgets = {
            'identifier': forms.TextInput(attrs={'class': 'form-control'}),
            'identifier_source': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CreatorActivityForm(forms.ModelForm):
    class Meta:
        model = CreatorActivity
        fields = ['activity', 'note']
        widgets = {
            'activity': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class CreatorEditorForm(forms.ModelForm):
    editing_type = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = CreatorEditor
        fields = ['name', 'qualifier', 'editing_type', 'edited_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.TextInput(attrs={'class': 'form-control'}),
            'edited_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from archimista_python.archive.models import Term
        terms = Term.objects.filter(
            vocabulary__name='editors.editing_type'
        ).order_by('position')
        choices = [('', '-- Seleziona --')] + [(t.term_value, t.term_value) for t in terms]
        self.fields['editing_type'].choices = choices

class RelCreatorCreatorForm(forms.ModelForm):
    class Meta:
        model = RelCreatorCreator
        fields = ['related_creator', 'association_type']
        widgets = {
            'related_creator': CreatorSelect2Widget(),
            'association_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'related_creator', threshold=20)

class RelCreatorInstitutionForm(forms.ModelForm):
    class Meta:
        model = RelCreatorInstitution
        fields = ['institution']
        widgets = {
            'institution': InstitutionSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'institution', threshold=30)

class RelCreatorSourceForm(forms.ModelForm):
    class Meta:
        model = RelCreatorSource
        fields = ['source']
        widgets = {
            'source': SourceSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'source', threshold=30)

class RelCreatorFondForm(forms.ModelForm):
    class Meta:
        model = RelCreatorFond
        fields = ['fond']
        widgets = {
            'fond': FondSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'fond', threshold=20)

# Formset per Creator
CreatorLegalStatusFormSet = inlineformset_factory(
    Creator, CreatorLegalStatus, form=CreatorLegalStatusForm,
    extra=0, can_delete=True
)
CreatorOtherNameFormSet = inlineformset_factory(
    Creator, CreatorName, form=CreatorOtherNameForm,
    extra=0, can_delete=True,
    fields=['name', 'qualifier', 'note']
)
CreatorUrlFormSet = inlineformset_factory(Creator, CreatorUrl, form=CreatorUrlForm, extra=0, can_delete=True)
CreatorIdentifierFormSet = inlineformset_factory(Creator, CreatorIdentifier, form=CreatorIdentifierForm, extra=0, can_delete=True)
CreatorActivityFormSet = inlineformset_factory(Creator, CreatorActivity, form=CreatorActivityForm, extra=0, can_delete=True)
CreatorEditorFormSet = inlineformset_factory(Creator, CreatorEditor, form=CreatorEditorForm, extra=0, can_delete=True)
RelCreatorCreatorFormSet = inlineformset_factory(Creator, RelCreatorCreator, form=RelCreatorCreatorForm, fk_name='creator', extra=0, can_delete=True)
RelCreatorInstitutionFormSet = inlineformset_factory(Creator, RelCreatorInstitution, form=RelCreatorInstitutionForm, fk_name='creator', extra=0, can_delete=True)
RelCreatorSourceFormSet = inlineformset_factory(Creator, RelCreatorSource, form=RelCreatorSourceForm, fk_name='creator', extra=0, can_delete=True)
RelCreatorFondFormSet = inlineformset_factory(Creator, RelCreatorFond, form=RelCreatorFondForm, fk_name='creator', extra=0, can_delete=True)
