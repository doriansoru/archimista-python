from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Unit, Sc2, Sc2TextualElement, Sc2VisualElement, Sc2Author,
    Sc2AttributionReason,
    Sc2Commission, Sc2CommissionName, Sc2Technique, Sc2Scale,
)

# =============================================================================
# SCHEDE SC2 (Disegni Tecnici e Fotografie)
# =============================================================================

class Sc2Form(forms.ModelForm):
    class Meta:
        model = Sc2
        fields = ['card_type', 'mtce', 'sdtt', 'sdts', 'misa', 'misl', 'lrc', 'lrd', 'dpgf', 'sgti', 'sca', 'cmmr', 'ort']
        widgets = {
            'card_type': forms.Select(attrs={'class': 'form-select sc2_field'}),
            'mtce': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Esecuzione'}),
            'sdtt': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Tipo rappresentazione'}),
            'sdts': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Rappresentazione tematica'}),
            'misa': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Altezza'}),
            'misl': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Larghezza'}),
            'lrc': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Luogo ripresa'}),
            'lrd': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Data ripresa'}),
            'dpgf': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Numero tavola'}),
            'sgti': forms.Textarea(attrs={'rows': 2, 'class': 'form-control sc2_field', 'placeholder': 'Soggetto iconografico'}),
            'sca': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Scala'}),
            'cmmr': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Numero commessa'}),
            'ort': forms.TextInput(attrs={'class': 'form-control sc2_field', 'placeholder': 'Orientamento'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # card_type è impostato dalla view da sc2_tsk, non richiesto nel form
        self.fields['card_type'].required = False


class Sc2TextualElementForm(forms.ModelForm):
    class Meta:
        model = Sc2TextualElement
        fields = ['isri']
        widgets = {
            'isri': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Iscrizione sul retro'})
        }


class Sc2VisualElementForm(forms.ModelForm):
    class Meta:
        model = Sc2VisualElement
        fields = ['stmd']
        widgets = {
            'stmd': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Stato di conservazione'})
        }


class Sc2AuthorForm(forms.ModelForm):
    class Meta:
        model = Sc2Author
        fields = ['autr', 'autn', 'auta']
        widgets = {
            'autr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ruolo'}),
            'autn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome autore'}),
            'auta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Datazione'}),
        }


class Sc2CommissionForm(forms.ModelForm):
    class Meta:
        model = Sc2Commission
        fields = ['cmmc']
        widgets = {
            'cmmc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ente committente'})
        }


class Sc2TechniqueForm(forms.ModelForm):
    class Meta:
        model = Sc2Technique
        fields = ['mtct']
        widgets = {
            'mtct': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tecnica'})
        }


class Sc2ScaleForm(forms.ModelForm):
    class Meta:
        model = Sc2Scale
        fields = ['sca']
        widgets = {
            'sca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Scala'})
        }


class Sc2AttributionReasonForm(forms.ModelForm):
    class Meta:
        model = Sc2AttributionReason
        fields = ['autm']
        widgets = {
            'autm': forms.TextInput(attrs={'class': 'form-control sc2_field sc2_voc'}),
        }


class Sc2CommissionNameForm(forms.ModelForm):
    class Meta:
        model = Sc2CommissionName
        fields = ['cmmn']
        widgets = {
            'cmmn': forms.TextInput(attrs={'class': 'form-control sc2_field'}),
        }


# Formset per elementi multipli - tutti collegati a Unit
Sc2AuthorFormSet = inlineformset_factory(Unit, Sc2Author, form=Sc2AuthorForm, extra=1, can_delete=True)
Sc2TextualElementFormSet = inlineformset_factory(Unit, Sc2TextualElement, form=Sc2TextualElementForm, extra=1, can_delete=True)
Sc2VisualElementFormSet = inlineformset_factory(Unit, Sc2VisualElement, form=Sc2VisualElementForm, extra=1, can_delete=True)
Sc2TechniqueFormSet = inlineformset_factory(Unit, Sc2Technique, form=Sc2TechniqueForm, extra=1, can_delete=True)
Sc2ScaleFormSet = inlineformset_factory(Unit, Sc2Scale, form=Sc2ScaleForm, extra=1, can_delete=True)
Sc2CommissionFormSet = inlineformset_factory(Unit, Sc2Commission, form=Sc2CommissionForm, extra=1, can_delete=True)

