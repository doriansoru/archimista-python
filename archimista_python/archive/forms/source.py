from django import forms
from django.forms import inlineformset_factory

from archimista_python.archive.models import Source, SourceUrl


class SourceForm(forms.ModelForm):
    """Form per la creazione/modifica di una Fonte.
    
    Allineato al form Ruby (_form.html.erb) con 2 tab:
    - Tab 1: Descrizione (tipologia, sottotipologia, dati bibliografici, URL)
    - Tab 2: Relazioni (fondi, creatori, custodi)
    """

    class Meta:
        model = Source
        fields = [
            'source_type_code',
            'source_subtype_code',
            'short_title',
            'author',
            'title',
            'editor',
            'place',
            'publisher',
            'date_string',
            'finding_aid_valid',
            'finding_aid_published',
            'related_item',
            'related_item_specs',
            'abstract',
        ]
        widgets = {
            'source_type_code': forms.Select(attrs={'class': 'form-select'}),
            'source_subtype_code': forms.Select(attrs={'class': 'form-select'}),
            'short_title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'editor': forms.TextInput(attrs={'class': 'form-control'}),
            'place': forms.TextInput(attrs={'class': 'form-control'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'date_string': forms.TextInput(attrs={'class': 'form-control'}),
            'finding_aid_valid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'finding_aid_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'related_item': forms.TextInput(attrs={'class': 'form-control'}),
            'related_item_specs': forms.TextInput(attrs={'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'source_type_code': 'Tipologia',
            'source_subtype_code': 'Tipologia specifica',
            'short_title': 'Sigla',
            'author': 'Autore',
            'title': 'Titolo',
            'editor': 'Curatore',
            'place': 'Luogo di pubblicazione',
            'publisher': 'Editore',
            'date_string': 'Data di pubblicazione',
            'finding_aid_valid': 'Validità dello strumento',
            'finding_aid_published': 'Edito?',
            'related_item': 'Titolo correlato',
            'related_item_specs': 'Note titolo correlato',
            'abstract': 'Abstract',
        }

    def __init__(self, *args, **kwargs):
        source_types = kwargs.pop('source_types', None)
        source_subtypes = kwargs.pop('source_subtypes', None)
        super().__init__(*args, **kwargs)

        if source_types:
            choices = [('', '---')] + [(t.code, t.source_type.capitalize()) for t in source_types]
            self.fields['source_type_code'].widget = forms.Select(
                attrs={'class': 'form-select'},
                choices=choices
            )
        if source_subtypes is not None:
            choices = [('', '---')] + [(t.code, t.source_type.capitalize()) for t in source_subtypes]
            self.fields['source_subtype_code'].widget = forms.Select(
                attrs={'class': 'form-select'},
                choices=choices
            )


class SourceUrlForm(forms.ModelForm):
    class Meta:
        model = SourceUrl
        fields = ['url', 'note']
        widgets = {
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }
        labels = {
            'url': 'URL',
            'note': 'Nota',
        }


SourceUrlFormSet = inlineformset_factory(
    Source, SourceUrl,
    form=SourceUrlForm,
    extra=1,
    can_delete=True
)
