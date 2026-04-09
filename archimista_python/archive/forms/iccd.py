from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Unit, IccdDescription, IccdTechSpec, IccdSubject, IccdDamage,
)

# =============================================================================
# SCHEDE ICCD (Beni Culturali)
# =============================================================================

class IccdDescriptionForm(forms.ModelForm):
    class Meta:
        model = IccdDescription
        fields = ['denomination', 'object_type', 'category', 'age_century']
        widgets = {
            'denomination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Denominazione'}),
            'object_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo oggetto'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoria'}),
            'age_century': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Secolo'}),
        }


class IccdTechSpecForm(forms.ModelForm):
    class Meta:
        model = IccdTechSpec
        fields = ['mtcm', 'mtct', 'misa', 'misl', 'misp', 'misu']
        widgets = {
            'mtcm': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Materiale'}),
            'mtct': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tecnica'}),
            'misa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Altezza'}),
            'misl': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Larghezza'}),
            'misp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Profondità'}),
            'misu': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('cm', 'cm'), ('mm', 'mm'), ('m', 'm'),
            ]),
        }


class IccdSubjectForm(forms.ModelForm):
    class Meta:
        model = IccdSubject
        fields = ['subject', 'subject_type']
        widgets = {
            'subject': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Soggetto'}),
            'subject_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo soggetto'}),
        }


class IccdDamageForm(forms.ModelForm):
    class Meta:
        model = IccdDamage
        fields = ['code', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Codice danno'}),
            'description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Descrizione'}),
        }


IccdSubjectFormSet = inlineformset_factory(IccdDescription, IccdSubject, form=IccdSubjectForm, extra=1, can_delete=True)
IccdDamageFormSet = inlineformset_factory(Unit, IccdDamage, form=IccdDamageForm, extra=1, can_delete=True)

