from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Unit,
    UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage, UnitUrl, UnitEditor,
    RelUnitHeading, RelUnitSource, RelUnitAnagraphic,
    Heading, Source, Anagraphic, Term, Classification,
)
from archimista_python.archive.widgets import (
    HeadingSelect2Widget, SourceSelect2Widget, AnagraphicSelect2Widget,
    FondSelect2Widget, UnitSelect2Widget, ClassificationSelect2Widget, LangSelect2Widget,
    auto_select_threshold,
)

# EventForm e EventFormSet sono definiti in event.py e importati da views

class UnitForm(forms.ModelForm):
    # Campi a scelta con vocabolari controllati
    unit_type_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --",
        label="Tipologia",
    )
    sc2_tsk = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select sc2_field', 'id': 'id_unit_sc2_tsk'}),
        label="Scheda speciale",
    )
    file_type = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select fsc_field', 'id': 'id_unit_file_type'}),
        label="Tipologia fascicolo",
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
    physical_type_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --",
        label="Tipologia fisica",
    )
    classification = forms.ModelChoiceField(
        queryset=Classification.objects.order_by('code', 'name'),
        required=False,
        widget=ClassificationSelect2Widget(),
        empty_label="-- Nessuna classificazione --",
        label="Classificazione",
    )

    class Meta:
        model = Unit
        fields = [
            'parent', 'fond', 'classification', 'title', 'given_title', 'unit_type_term', 'unit_type', 'sc2_tsk', 'file_type',
            'tmp_reference_number', 'tmp_reference_string', 'folder_number', 'file_number',
            'reference_number', 'fsc_name', 'fsc_surname', 'published',
            'extent', 'content', 'arrangement_note',
            'physical_description', 'physical_type_term', 'physical_type',
            'physical_container_type', 'physical_container_title', 'physical_container_number',
            'related_materials', 'preservation_term', 'preservation', 'preservation_note',
            'restoration', 'note',
            'access_condition_term', 'access_condition',
            'use_condition_term', 'use_condition',
            'medium',
        ]
        widgets = {
            'title': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'given_title': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'arrangement_note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'extent': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'physical_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'related_materials': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'preservation_note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'restoration': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'reference_number': forms.Textarea(attrs={'rows': 1, 'class': 'form-control'}),
            'tmp_reference_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'tmp_reference_string': forms.TextInput(attrs={'class': 'form-control'}),
            'folder_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'file_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'parent': UnitSelect2Widget(),
            'fond': FondSelect2Widget(),
            'classification': ClassificationSelect2Widget(),
            'unit_type': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_unit_type_text'}),
            'fsc_name': forms.TextInput(attrs={'class': 'form-control fsc_field'}),
            'fsc_surname': forms.TextInput(attrs={'class': 'form-control fsc_field'}),
            'physical_type': forms.TextInput(attrs={'class': 'form-control'}),
            'physical_container_type': forms.TextInput(attrs={'class': 'form-control'}),
            'physical_container_title': forms.TextInput(attrs={'class': 'form-control'}),
            'physical_container_number': forms.TextInput(attrs={'class': 'form-control'}),
            'medium': forms.TextInput(attrs={'class': 'form-control'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'parent': 'Unità padre',
            'fond': 'Complesso',
            'classification': 'Classificazione',
            'title': 'Titolo',
            'given_title': 'Attribuito?',
            'unit_type': 'Tipologia',
            'tmp_reference_number': 'Segnatura provvisoria - numero',
            'tmp_reference_string': 'Segnatura provvisoria - testo',
            'folder_number': 'Busta',
            'file_number': 'Fascicolo',
            'reference_number': 'Segnatura definitiva',
            'fsc_name': 'Nome',
            'fsc_surname': 'Cognome',
            'published': 'Pubblicato',
            'extent': 'Consistenza',
            'content': 'Contenuto',
            'arrangement_note': "Nota dell'archivista",
            'physical_description': 'Descrizione estrinseca',
            'physical_type': 'Tipologia fisica',
            'physical_container_type': 'Tipologia',
            'physical_container_title': 'Titolo',
            'physical_container_number': 'Numero',
            'related_materials': 'Documentazione collegata',
            'preservation': 'Stato di conservazione',
            'preservation_note': 'Note sullo stato di conservazione',
            'restoration': 'Restauri',
            'note': 'Appunti di servizio',
            'access_condition': 'Condizione di accesso',
            'use_condition': 'Condizione di riproduzione',
            'medium': 'Supporto',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Select2 minimum-input-length=0 if few items
        auto_select_threshold(self, 'parent', threshold=20)
        auto_select_threshold(self, 'fond', threshold=20)
        auto_select_threshold(self, 'classification', threshold=30)

        # Imposta i queryset per i campi a scelta
        self.fields['unit_type_term'].queryset = Term.objects.filter(
            vocabulary__name='units.unit_type'
        ).order_by('position')
        self.fields['access_condition_term'].queryset = Term.objects.filter(
            vocabulary__name='units.access_condition'
        ).order_by('position')
        self.fields['use_condition_term'].queryset = Term.objects.filter(
            vocabulary__name='units.use_condition'
        ).order_by('position')
        self.fields['preservation_term'].queryset = Term.objects.filter(
            vocabulary__name='units.preservation'
        ).order_by('position')
        self.fields['physical_type_term'].queryset = Term.objects.filter(
            vocabulary__name='units.physical_type'
        ).order_by('position')

        # sc2_tsk choices (from Ruby: CARS, D, DT, F, S)
        self.fields['sc2_tsk'].choices = [
            ('', '---'),
            ('CARS', 'CARS - Cartografia storica'),
            ('D', 'D - Disegno artistico'),
            ('DT', 'DT - Disegno Tecnico'),
            ('F', 'F - Fotografia'),
            ('S', 'S - Stampa'),
        ]

        # file_type choices (from Ruby: personale, edilizia)
        self.fields['file_type'].choices = [
            ('', '---'),
            ('personale', 'Fascicolo personale'),
            ('edilizia', 'Fascicolo edilizia'),
        ]

        # Sincronizza unit_type_term con unit_type per pre-selezione corretta
        # Quando si modifica un'unità esistente, se unit_type_term non è impostato
        # ma unit_type sì, trova il termine corrispondente
        if self.instance and self.instance.pk and not self.instance.unit_type_term_id and self.instance.unit_type:
            matching_term = Term.objects.filter(
                vocabulary__name='units.unit_type',
                term_value=self.instance.unit_type
            ).first()
            if matching_term:
                self.instance.unit_type_term_id = matching_term.pk
                self.initial['unit_type_term'] = matching_term.pk

        # Stessa logica per access_condition_term
        if self.instance and self.instance.pk and not self.instance.access_condition_term_id and self.instance.access_condition:
            matching_term = Term.objects.filter(
                vocabulary__name='units.access_condition',
                term_value=self.instance.access_condition
            ).first()
            if matching_term:
                self.instance.access_condition_term_id = matching_term.pk
                self.initial['access_condition_term'] = matching_term.pk

        # Stessa logica per use_condition_term
        if self.instance and self.instance.pk and not self.instance.use_condition_term_id and self.instance.use_condition:
            matching_term = Term.objects.filter(
                vocabulary__name='units.use_condition',
                term_value=self.instance.use_condition
            ).first()
            if matching_term:
                self.instance.use_condition_term_id = matching_term.pk
                self.initial['use_condition_term'] = matching_term.pk

        # Stessa logica per preservation_term
        if self.instance and self.instance.pk and not self.instance.preservation_term_id and self.instance.preservation:
            matching_term = Term.objects.filter(
                vocabulary__name='units.preservation',
                term_value=self.instance.preservation
            ).first()
            if matching_term:
                self.instance.preservation_term_id = matching_term.pk
                self.initial['preservation_term'] = matching_term.pk

        # Stessa logica per physical_type_term
        if self.instance and self.instance.pk and not self.instance.physical_type_term_id and self.instance.physical_type:
            matching_term = Term.objects.filter(
                vocabulary__name='units.physical_type',
                term_value=self.instance.physical_type
            ).first()
            if matching_term:
                self.instance.physical_type_term_id = matching_term.pk
                self.initial['physical_type_term'] = matching_term.pk

    def save(self, commit=True):
        """Sincronizza i campi term con i campi testo al salvataggio."""
        instance = super().save(commit=False)
        # Sincronizza ogni campo term → campo testo
        for field_name in ['unit_type_term', 'access_condition_term', 'use_condition_term',
                           'preservation_term', 'physical_type_term']:
            text_field = field_name.replace('_term', '')
            if self.cleaned_data.get(field_name):
                setattr(instance, text_field, self.cleaned_data[field_name].term_value)
            elif self.cleaned_data.get(text_field):
                setattr(instance, field_name, None)
        if commit:
            instance.save()
        return instance



# =============================================================================
# FORM PER ESTENSIONI UNIT (ALLINEATI AD ARCHIMISTA RUBY)
# =============================================================================

class UnitIdentifierForm(forms.ModelForm):
    class Meta:
        model = UnitIdentifier
        fields = ['identifier', 'identifier_source', 'note']
        widgets = {
            'identifier': forms.TextInput(attrs={'class': 'form-control'}),
            'identifier_source': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class UnitOtherReferenceNumberForm(forms.ModelForm):
    class Meta:
        model = UnitOtherReferenceNumber
        fields = ['other_reference_number', 'qualifier', 'note']
        widgets = {
            'other_reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UnitLangForm(forms.ModelForm):
    class Meta:
        model = UnitLang
        fields = ['code']
        widgets = {
            'code': LangSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'code', threshold=50)

class UnitDamageForm(forms.ModelForm):
    class Meta:
        model = UnitDamage
        fields = ['code', 'note']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'list': 'damage_code_list',
                'placeholder': 'Seleziona o inserisci tipo danno'
            }),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class UnitUrlForm(forms.ModelForm):
    class Meta:
        model = UnitUrl
        fields = ['url', 'note', 'position']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class UnitEditorForm(forms.ModelForm):
    editing_type = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = UnitEditor
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

class RelUnitHeadingForm(forms.ModelForm):
    class Meta:
        model = RelUnitHeading
        fields = ['heading']
        widgets = {
            'heading': HeadingSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'heading', threshold=30)

class RelUnitSourceForm(forms.ModelForm):
    class Meta:
        model = RelUnitSource
        fields = ['source']
        widgets = {
            'source': SourceSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'source', threshold=30)

class RelUnitAnagraphicForm(forms.ModelForm):
    class Meta:
        model = RelUnitAnagraphic
        fields = ['anagraphic']
        widgets = {
            'anagraphic': AnagraphicSelect2Widget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        auto_select_threshold(self, 'anagraphic', threshold=30)

# Formset per Unit
UnitIdentifierFormSet = inlineformset_factory(Unit, UnitIdentifier, form=UnitIdentifierForm, extra=1, can_delete=True)
UnitOtherReferenceNumberFormSet = inlineformset_factory(Unit, UnitOtherReferenceNumber, form=UnitOtherReferenceNumberForm, extra=1, can_delete=True)
UnitLangFormSet = inlineformset_factory(Unit, UnitLang, form=UnitLangForm, extra=1, can_delete=True)
UnitDamageFormSet = inlineformset_factory(Unit, UnitDamage, form=UnitDamageForm, extra=1, can_delete=True)
UnitUrlFormSet = inlineformset_factory(Unit, UnitUrl, form=UnitUrlForm, extra=1, can_delete=True)
UnitEditorFormSet = inlineformset_factory(Unit, UnitEditor, form=UnitEditorForm, extra=0, can_delete=True)
RelUnitHeadingFormSet = inlineformset_factory(Unit, RelUnitHeading, form=RelUnitHeadingForm, extra=1, can_delete=True)
RelUnitSourceFormSet = inlineformset_factory(Unit, RelUnitSource, form=RelUnitSourceForm, extra=1, can_delete=True)
RelUnitAnagraphicFormSet = inlineformset_factory(Unit, RelUnitAnagraphic, form=RelUnitAnagraphicForm, extra=1, can_delete=True)

