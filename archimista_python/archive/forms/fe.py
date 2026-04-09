from django import forms
from django.forms import inlineformset_factory
from archimista_python.archive.models import (
    Unit, FeIdentification, FeContext, FeOpera, FeDesigner, FeCadastral, FeLandParcel,
    FeFractLandParcel, FeFractEdilParcel,
)

# =============================================================================
# SCHEDE FE (Fabbricati Edilizia)
# =============================================================================

class FeIdentificationForm(forms.ModelForm):
    class Meta:
        model = FeIdentification
        fields = ['code', 'file_year', 'category', 'identification_class']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'file_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'identification_class': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FeContextForm(forms.ModelForm):
    class Meta:
        model = FeContext
        fields = [
            'number', 'sub_number', 'classification', 'applicant', 'request',
            'license_number', 'license_year', 'license_date',
            'habitability_number', 'habitability_year', 'habitability_date'
        ]
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'sub_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'classification': forms.TextInput(attrs={'class': 'form-control'}),
            'applicant': forms.TextInput(attrs={'class': 'form-control'}),
            'request': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'license_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'license_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'license_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'habitability_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'habitability_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'habitability_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class FeOperaForm(forms.ModelForm):
    class Meta:
        model = FeOpera
        fields = ['is_present', 'status', 'building_name', 'building_type', 'place_name', 'place_type', 'house_number', 'district']
        widgets = {
            'is_present': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '---'), ('nuovo', 'Nuovo'), ('esistente', 'Esistente'), ('demolito', 'Demolito'),
            ]),
            'building_name': forms.TextInput(attrs={'class': 'form-control'}),
            'building_type': forms.TextInput(attrs={'class': 'form-control'}),
            'place_name': forms.TextInput(attrs={'class': 'form-control'}),
            'place_type': forms.TextInput(attrs={'class': 'form-control'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FeDesignerForm(forms.ModelForm):
    class Meta:
        model = FeDesigner
        fields = ['designer_name', 'designer_role']
        widgets = {
            'designer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'designer_role': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FeCadastralForm(forms.ModelForm):
    class Meta:
        model = FeCadastral
        fields = ['way_code', 'cadastral_municipality', 'municipality_code', 'paper_code']
        widgets = {
            'way_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'cadastral_municipality': forms.TextInput(attrs={'class': 'form-control'}),
            'municipality_code': forms.NumberInput(attrs={'class': 'form-control'}),
            'paper_code': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class FeLandParcelForm(forms.ModelForm):
    class Meta:
        model = FeLandParcel
        fields = ['land_parcel_number']
        widgets = {
            'land_parcel_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FeFractLandParcelForm(forms.ModelForm):
    class Meta:
        model = FeFractLandParcel
        fields = ['fract_land_parcel_number', 'edil_parcel_number']
        widgets = {
            'fract_land_parcel_number': forms.NumberInput(attrs={'class': 'form-control fe_field'}),
            'edil_parcel_number': forms.NumberInput(attrs={'class': 'form-control fe_field'}),
        }


class FeFractEdilParcelForm(forms.ModelForm):
    class Meta:
        model = FeFractEdilParcel
        fields = ['fract_edil_parcel_number', 'material_portion']
        widgets = {
            'fract_edil_parcel_number': forms.NumberInput(attrs={'class': 'form-control fe_field'}),
            'material_portion': forms.NumberInput(attrs={'class': 'form-control fe_field'}),
        }


FeIdentificationFormSet = inlineformset_factory(Unit, FeIdentification, form=FeIdentificationForm, extra=1, can_delete=True)
FeContextFormSet = inlineformset_factory(Unit, FeContext, form=FeContextForm, extra=1, can_delete=True)
FeOperaFormSet = inlineformset_factory(Unit, FeOpera, form=FeOperaForm, extra=1, can_delete=True)
FeDesignerFormSet = inlineformset_factory(Unit, FeDesigner, form=FeDesignerForm, extra=1, can_delete=True)
FeCadastralFormSet = inlineformset_factory(Unit, FeCadastral, form=FeCadastralForm, extra=1, can_delete=True)
FeLandParcelFormSet = inlineformset_factory(Unit, FeLandParcel, form=FeLandParcelForm, extra=1, can_delete=True)
FeFractLandParcelFormSet = inlineformset_factory(Unit, FeFractLandParcel, form=FeFractLandParcelForm, extra=1, can_delete=True)
FeFractEdilParcelFormSet = inlineformset_factory(Unit, FeFractEdilParcel, form=FeFractEdilParcelForm, extra=1, can_delete=True)

