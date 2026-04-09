"""
Form per Voci di Indice (Heading)
"""

from django import forms
from archimista_python.archive.models import Heading, Term


class HeadingForm(forms.ModelForm):
    """Form per Heading allineato a Ruby _form.html.erb"""

    heading_type_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --",
        label="Tipologia"
    )

    class Meta:
        model = Heading
        fields = ['heading_type', 'name', 'dates', 'qualifier']
        widgets = {
            'heading_type': forms.HiddenInput(),  # Campo DB nascosto, sincronizzato con term
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'dates': forms.TextInput(attrs={'class': 'form-control'}),
            'qualifier': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Lemma',
            'dates': 'Estremi cronologici',
            'qualifier': 'Qualifica',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Popola heading_type_term con i termini del vocabolario
        self.fields['heading_type_term'].queryset = Term.objects.filter(
            vocabulary__name='headings.heading_type'
        ).order_by('position')

        # Pre-seleziona il termine corrente se heading_type è impostato
        if self.instance and self.instance.pk and self.instance.heading_type:
            try:
                term = Term.objects.filter(
                    vocabulary__name='headings.heading_type',
                    term_value=self.instance.heading_type
                ).first()
                if term:
                    self.fields['heading_type_term'].initial = term.pk
            except Exception:
                pass

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Sincronizza heading_type con heading_type_term
        term = self.cleaned_data.get('heading_type_term')
        if term:
            instance.heading_type = term.term_value

        # Imposta group di default se non presente
        if not instance.group_id:
            from archimista_python.archive.models import Group
            group = Group.objects.first()
            if group:
                instance.group = group
            # Se non esiste Group, lascia None (il campo è nullable)

        if commit:
            instance.save()
        return instance
