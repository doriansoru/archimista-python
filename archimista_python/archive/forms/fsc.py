from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Unit, FscCode, FscOrganization, FscNationality, FscOpen, FscClose,
)

# =============================================================================
# SCHEDE FSC (Fascicoli Sanitari Edilizia)
# =============================================================================

class FscCodeForm(forms.ModelForm):
    class Meta:
        model = FscCode
        fields = ['code', 'note']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class FscOrganizationForm(forms.ModelForm):
    class Meta:
        model = FscOrganization
        fields = ['organization']
        widgets = {
            'organization': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FscNationalityForm(forms.ModelForm):
    class Meta:
        model = FscNationality
        fields = ['nationality']
        widgets = {
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FscOpenForm(forms.ModelForm):
    class Meta:
        model = FscOpen
        fields = ['open', 'note']
        widgets = {
            'open': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class FscCloseForm(forms.ModelForm):
    class Meta:
        model = FscClose
        fields = ['close', 'note']
        widgets = {
            'close': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


FscCodeFormSet = inlineformset_factory(Unit, FscCode, form=FscCodeForm, extra=1, can_delete=True)
FscOrganizationFormSet = inlineformset_factory(Unit, FscOrganization, form=FscOrganizationForm, extra=1, can_delete=True)
FscNationalityFormSet = inlineformset_factory(Unit, FscNationality, form=FscNationalityForm, extra=1, can_delete=True)
FscOpenFormSet = inlineformset_factory(Unit, FscOpen, form=FscOpenForm, extra=1, can_delete=True)
FscCloseFormSet = inlineformset_factory(Unit, FscClose, form=FscCloseForm, extra=1, can_delete=True)

