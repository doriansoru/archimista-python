from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Fond,
    FondName, FondIdentifier, FondLang, FondOwner, FondUrl, FondEditor,
    RelFondHeading, RelFondSource, RelFondDocumentForm,
    Heading, Source, DocumentForm, Term,
)
from archimista_python.archive.widgets import (
    HeadingSelect2Widget, SourceSelect2Widget, DocumentFormSelect2Widget,
    FondSelect2Widget, LangSelect2Widget, auto_select_threshold,
)

class FondForm(forms.ModelForm):
    # Campi a scelta con vocabolari controllati
    fond_type_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --",
        label="Tipologia del livello di descrizione",
    )
    access_condition_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --",
        label="Condizione di accesso",
    )
    use_condition_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --",
        label="Condizione di riproduzione",
    )
    preservation_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --",
        label="Stato di conservazione",
    )
    description_type_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --",
        label="Tipo descrizione",
    )

    class Meta:
        model = Fond
        fields = [
            'parent', 'name', 'fond_type_term', 'fond_type', 'length', 'extent',
            'abstract', 'description', 'history', 'arrangement_note', 'related_materials',
            'access_condition_term', 'access_condition', 'access_condition_note',
            'use_condition_term', 'use_condition', 'use_condition_note',
            'type_materials', 'preservation_term', 'preservation', 'preservation_note',
            'description_type_term', 'description_type', 'note', 'published'
        ]
        widgets = {
            'name': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'history': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'arrangement_note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'extent': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'related_materials': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'access_condition': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'access_condition_note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'use_condition': forms.TextInput(attrs={'class': 'form-control'}),
            'use_condition_note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'type_materials': forms.TextInput(attrs={'class': 'form-control'}),
            'preservation': forms.TextInput(attrs={'class': 'form-control'}),
            'preservation_note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'parent': FondSelect2Widget(),
            'fond_type': forms.TextInput(attrs={'class': 'form-control'}),
            'length': forms.NumberInput(attrs={'class': 'form-control'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'parent': 'Fondo padre',
            'name': 'Denominazione',
            'fond_type': 'Tipologia del livello di descrizione',
            'length': 'Metri lineari',
            'extent': 'Consistenza archivistica',
            'abstract': 'Abstract',
            'description': 'Contenuto',
            'history': 'Storia archivistica',
            'arrangement_note': "Nota dell'archivista",
            'related_materials': 'Documentazione collegata',
            'access_condition': 'Condizione di accesso',
            'access_condition_note': 'Note alla condizione di accesso',
            'use_condition': 'Condizione di riproduzione',
            'use_condition_note': 'Note alla condizione di riproduzione',
            'type_materials': 'Tipo materiali',
            'preservation': 'Stato di conservazione',
            'preservation_note': 'Note sullo stato di conservazione',
            'description_type': 'Tipo descrizione',
            'note': 'Appunti di servizio',
            'published': 'Pubblicato',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Select2 minimum-input-length=0 if few items (shows all options immediately)
        auto_select_threshold(self, 'parent', threshold=20)

        # Imposta i queryset per i campi a scelta
        self.fields['fond_type_term'].queryset = Term.objects.filter(
            vocabulary__name='fonds.fond_type'
        ).order_by('position')
        self.fields['access_condition_term'].queryset = Term.objects.filter(
            vocabulary__name='fonds.access_condition'
        ).order_by('position')
        self.fields['use_condition_term'].queryset = Term.objects.filter(
            vocabulary__name='fonds.use_condition'
        ).order_by('position')
        self.fields['preservation_term'].queryset = Term.objects.filter(
            vocabulary__name='fonds.preservation'
        ).order_by('position')
        self.fields['description_type_term'].queryset = Term.objects.filter(
            vocabulary__name='fonds.description_type'
        ).order_by('position')

        # Sincronizza fond_type_term con fond_type per pre-selezione corretta
        if self.instance and self.instance.pk and not self.instance.fond_type_term_id and self.instance.fond_type:
            matching_term = Term.objects.filter(
                vocabulary__name='fonds.fond_type',
                term_value=self.instance.fond_type
            ).first()
            if matching_term:
                self.instance.fond_type_term_id = matching_term.pk
                self.initial['fond_type_term'] = matching_term.pk

        # Stessa logica per access_condition_term
        if self.instance and self.instance.pk and not self.instance.access_condition_term_id and self.instance.access_condition:
            matching_term = Term.objects.filter(
                vocabulary__name='fonds.access_condition',
                term_value=self.instance.access_condition
            ).first()
            if matching_term:
                self.instance.access_condition_term_id = matching_term.pk
                self.initial['access_condition_term'] = matching_term.pk

        # Stessa logica per use_condition_term
        if self.instance and self.instance.pk and not self.instance.use_condition_term_id and self.instance.use_condition:
            matching_term = Term.objects.filter(
                vocabulary__name='fonds.use_condition',
                term_value=self.instance.use_condition
            ).first()
            if matching_term:
                self.instance.use_condition_term_id = matching_term.pk
                self.initial['use_condition_term'] = matching_term.pk

        # Stessa logica per preservation_term
        if self.instance and self.instance.pk and not self.instance.preservation_term_id and self.instance.preservation:
            matching_term = Term.objects.filter(
                vocabulary__name='fonds.preservation',
                term_value=self.instance.preservation
            ).first()
            if matching_term:
                self.instance.preservation_term_id = matching_term.pk
                self.initial['preservation_term'] = matching_term.pk

    def save(self, commit=True):
        """Sincronizza i campi term con i campi testo al salvataggio."""
        instance = super().save(commit=False)
        for field_name in ['fond_type_term', 'access_condition_term', 'use_condition_term',
                           'preservation_term']:
            text_field = field_name.replace('_term', '')
            if self.cleaned_data.get(field_name):
                setattr(instance, text_field, self.cleaned_data[field_name].term_value)
            elif self.cleaned_data.get(text_field):
                setattr(instance, field_name, None)
        if commit:
            instance.save()
        return instance


# =============================================================================
# FORM PER FOND (COMPLETI CON ESTENSIONI)
# =============================================================================

class FondNameForm(forms.ModelForm):
    class Meta:
        model = FondName
        fields = ['preferred', 'name', 'qualifier', 'note', 'patronymic', 'nickname']
        widgets = {
            'preferred': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'name': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'qualifier': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FondIdentifierForm(forms.ModelForm):
    class Meta:
        model = FondIdentifier
        fields = ['identifier', 'identifier_source', 'note']
        widgets = {
            'identifier': forms.TextInput(attrs={'class': 'form-control'}),
            'identifier_source': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class FondLangForm(forms.ModelForm):
    class Meta:
        model = FondLang
        fields = ['code']
        widgets = {
            'code': LangSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'code', threshold=50)

class FondOwnerForm(forms.ModelForm):
    class Meta:
        model = FondOwner
        fields = ['owner']
        widgets = {
            'owner': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FondUrlForm(forms.ModelForm):
    class Meta:
        model = FondUrl
        fields = ['url', 'note', 'position']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class FondEditorForm(forms.ModelForm):
    class Meta:
        model = FondEditor
        fields = ['name', 'qualifier', 'editing_type', 'edited_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.TextInput(attrs={'class': 'form-control'}),
            'editing_type': forms.TextInput(attrs={'class': 'form-control'}),
            'edited_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class RelFondHeadingForm(forms.ModelForm):
    class Meta:
        model = RelFondHeading
        fields = ['heading']
        widgets = {
            'heading': HeadingSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'heading', threshold=30)

class RelFondSourceForm(forms.ModelForm):
    class Meta:
        model = RelFondSource
        fields = ['source']
        widgets = {
            'source': SourceSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'source', threshold=30)

class RelFondDocumentFormForm(forms.ModelForm):
    class Meta:
        model = RelFondDocumentForm
        fields = ['document_form']
        widgets = {
            'document_form': DocumentFormSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'document_form', threshold=30)

# Formset per Fond
FondNameFormSet = inlineformset_factory(Fond, FondName, form=FondNameForm, extra=1, can_delete=True)
FondIdentifierFormSet = inlineformset_factory(Fond, FondIdentifier, form=FondIdentifierForm, extra=1, can_delete=True)
FondLangFormSet = inlineformset_factory(Fond, FondLang, form=FondLangForm, extra=1, can_delete=True)
FondOwnerFormSet = inlineformset_factory(Fond, FondOwner, form=FondOwnerForm, extra=1, can_delete=True)
FondUrlFormSet = inlineformset_factory(Fond, FondUrl, form=FondUrlForm, extra=1, can_delete=True)
FondEditorFormSet = inlineformset_factory(Fond, FondEditor, form=FondEditorForm, extra=1, can_delete=True)
RelFondHeadingFormSet = inlineformset_factory(Fond, RelFondHeading, form=RelFondHeadingForm, extra=1, can_delete=True)
RelFondSourceFormSet = inlineformset_factory(Fond, RelFondSource, form=RelFondSourceForm, extra=1, can_delete=True)
RelFondDocumentFormFormSet = inlineformset_factory(Fond, RelFondDocumentForm, form=RelFondDocumentFormForm, extra=1, can_delete=True)

