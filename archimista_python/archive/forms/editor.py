from django import forms
from archimista_python.archive.models import Editor


class EditorForm(forms.ModelForm):
    """Form per Compilatori (Editor) — allineato a Ruby."""

    class Meta:
        model = Editor
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nome',
            'last_name': 'Cognome',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
