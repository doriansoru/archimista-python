from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Custodian,
    CustodianName, CustodianIdentifier, CustodianContact, CustodianBuilding,
    CustodianOwner, CustodianUrl, CustodianEditor,
    RelCustodianSource, RelCustodianFond,
    Source, Fond, Term,
)
from archimista_python.archive.widgets import (
    SourceSelect2Widget, FondSelect2Widget,
    auto_select_threshold,
)

# =============================================================================
# FORM PER CUSTODIAN (ALLINEATI A RUBY)
# =============================================================================

class CustodianForm(forms.ModelForm):
    class Meta:
        model = Custodian
        fields = [
            'custodian_type', 'legal_status', 'contact_person',
            'history', 'administrative_structure', 'collecting_policies',
            'holdings', 'accessibility', 'services', 'published'
        ]
        widgets = {
            'custodian_type': forms.Select(attrs={'class': 'form-select'}),
            'legal_status': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '---'), ('P', 'Pubblico'), ('R', 'Privato'),
            ]),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'history': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'administrative_structure': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'collecting_policies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'holdings': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'accessibility': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'services': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'custodian_type': 'Macrotipologia',
            'legal_status': 'Condizione giuridica',
            'contact_person': 'Referente',
            'history': 'Cenni storico istituzionali',
            'administrative_structure': 'Struttura amministrativa',
            'collecting_policies': 'Politiche di gestione e di acquisizione',
            'holdings': 'Patrimonio',
            'accessibility': "Orari e indicazioni per l'accesso ai fondi",
            'services': 'Servizi',
            'published': 'Pubblicato',
        }


class CustodianPreferredNameForm(forms.ModelForm):
    """Form for the preferred name (single record, not a formset)."""
    class Meta:
        model = CustodianName
        fields = ['preferred', 'name', 'note']
        widgets = {
            'preferred': forms.HiddenInput(),
            'name': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set preferred=True always for this form
        if self.instance and not self.instance.pk:
            self.instance.preferred = True


class CustodianNameForm(forms.ModelForm):
    qualifier_term = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = CustodianName
        fields = ['preferred', 'name', 'qualifier', 'qualifier_term', 'note']
        widgets = {
            'preferred': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'name': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'qualifier': forms.HiddenInput(),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        terms = Term.objects.filter(
            vocabulary__name='custodian_names.qualifier'
        ).order_by('position')
        choices = [('', '-- Seleziona --')] + [(t.term_value, t.term_value) for t in terms]
        self.fields['qualifier_term'].choices = choices
        # Sync: if instance has qualifier, pre-select qualifier_term
        if self.instance and self.instance.qualifier:
            self.fields['qualifier_term'].initial = self.instance.qualifier

    def save(self, commit=True):
        # Sync qualifier_term → qualifier
        if self.cleaned_data.get('qualifier_term'):
            self.instance.qualifier = self.cleaned_data['qualifier_term']
        return super().save(commit)


class CustodianIdentifierForm(forms.ModelForm):
    class Meta:
        model = CustodianIdentifier
        fields = ['identifier', 'identifier_source', 'note']
        widgets = {
            'identifier': forms.TextInput(attrs={'class': 'form-control'}),
            'identifier_source': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class CustodianContactForm(forms.ModelForm):
    class Meta:
        model = CustodianContact
        fields = ['contact', 'contact_type', 'contact_note']
        widgets = {
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_type': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class CustodianBuildingForm(forms.ModelForm):
    class Meta:
        model = CustodianBuilding
        fields = ['custodian_building_type', 'name', 'description', 'address', 'postcode', 'city', 'state', 'country']
        widgets = {
            'custodian_building_type': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustodianOwnerForm(forms.ModelForm):
    class Meta:
        model = CustodianOwner
        fields = ['owner']
        widgets = {
            'owner': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustodianUrlForm(forms.ModelForm):
    class Meta:
        model = CustodianUrl
        fields = ['url', 'note', 'position']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class CustodianEditorForm(forms.ModelForm):
    editing_type = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = CustodianEditor
        fields = ['name', 'qualifier', 'editing_type', 'edited_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.TextInput(attrs={'class': 'form-control'}),
            'edited_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        terms = Term.objects.filter(
            vocabulary__name='editors.editing_type'
        ).order_by('position')
        choices = [('', '-- Seleziona --')] + [(t.term_value, t.term_value) for t in terms]
        self.fields['editing_type'].choices = choices


class RelCustodianSourceForm(forms.ModelForm):
    class Meta:
        model = RelCustodianSource
        fields = ['source']
        widgets = {
            'source': SourceSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'source', threshold=30)


class RelCustodianFondForm(forms.ModelForm):
    class Meta:
        model = RelCustodianFond
        fields = ['fond']
        widgets = {
            'fond': FondSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'fond', threshold=20)


# Formset per Custodian
CustodianNameFormSet = inlineformset_factory(
    Custodian, CustodianName, form=CustodianNameForm,
    extra=1, can_delete=True,
    fields=['preferred', 'name', 'qualifier', 'note']
)
CustodianIdentifierFormSet = inlineformset_factory(
    Custodian, CustodianIdentifier, form=CustodianIdentifierForm,
    extra=1, can_delete=True
)
CustodianContactFormSet = inlineformset_factory(
    Custodian, CustodianContact, form=CustodianContactForm,
    extra=1, can_delete=True
)
CustodianBuildingFormSet = inlineformset_factory(
    Custodian, CustodianBuilding, form=CustodianBuildingForm,
    extra=1, can_delete=True
)
CustodianOwnerFormSet = inlineformset_factory(
    Custodian, CustodianOwner, form=CustodianOwnerForm,
    extra=1, can_delete=True
)
CustodianUrlFormSet = inlineformset_factory(
    Custodian, CustodianUrl, form=CustodianUrlForm,
    extra=1, can_delete=True
)
CustodianEditorFormSet = inlineformset_factory(
    Custodian, CustodianEditor, form=CustodianEditorForm,
    extra=1, can_delete=True
)
RelCustodianSourceFormSet = inlineformset_factory(
    Custodian, RelCustodianSource, form=RelCustodianSourceForm,
    extra=1, can_delete=True
)
RelCustodianFondFormSet = inlineformset_factory(
    Custodian, RelCustodianFond, form=RelCustodianFondForm,
    extra=1, can_delete=True
)
