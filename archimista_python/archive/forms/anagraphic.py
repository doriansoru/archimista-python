"""
Form per Anagrafiche (Anagraphic)
"""

from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import Anagraphic, AnagIdentifier


class AnagraphicForm(forms.ModelForm):
    """Form per Anagraphic allineato a Ruby _new_anagraphic.html.erb"""

    class Meta:
        model = Anagraphic
        fields = ['name', 'surname', 'start_date_place', 'start_date', 'end_date_place', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date_place': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date_place': forms.TextInput(attrs={'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'name': 'Nome',
            'surname': 'Cognome',
            'start_date_place': 'Luogo di nascita',
            'start_date': 'Data di nascita',
            'end_date_place': 'Luogo di morte',
            'end_date': 'Data di morte',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ruby: name e surname sono obbligatori
        self.fields['name'].required = True
        self.fields['surname'].required = True


# Formset inline per AnagIdentifier (Codice identificativo)
class AnagIdentifierForm(forms.ModelForm):
    class Meta:
        model = AnagIdentifier
        fields = ['identifier', 'qualifier']
        widgets = {
            'identifier': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'identifier': 'Codice identificativo',
            'qualifier': 'Qualifica',
        }


AnagIdentifierFormSet = inlineformset_factory(
    Anagraphic,
    AnagIdentifier,
    form=AnagIdentifierForm,
    extra=0,
    can_delete=True
)
