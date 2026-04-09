"""
Form per la gestione del Titolario di classificazione.
"""

from django import forms
from ..models import Classification
from archimista_python.archive.widgets import ClassificationSelect2Widget, auto_select_threshold


class ClassificationForm(forms.ModelForm):
    """Form per creazione/modifica classificazione."""

    class Meta:
        model = Classification
        fields = ['code', 'name', 'description', 'parent']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Es. 1, 1.1, 1.1.1'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Denominazione della classe'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrizione opzionale'
            }),
            'parent': ClassificationSelect2Widget(),
        }
        labels = {
            'code': 'Codice',
            'name': 'Denominazione',
            'description': 'Descrizione',
            'parent': 'Classe padre',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Select2 minimum-input-length=0 if few items
        auto_select_threshold(self, 'parent', threshold=30)

        # Dropdown per classe padre: mostra solo le classificazioni root o di primo livello
        # Escludi self per evitare riferimenti circolari
        queryset = Classification.objects.select_related('parent').order_by('code', 'name')
        if self.instance.pk:
            # Escludi self e tutti i suoi discendenti
            descendants = self._get_descendants_ids(self.instance.pk)
            descendants.append(self.instance.pk)
            queryset = queryset.exclude(pk__in=descendants)

        self.fields['parent'].queryset = queryset
        self.fields['parent'].empty_label = '-- Nessuna (classe root) --'

    def _get_descendants_ids(self, parent_id):
        """Ricorsivamente ottieni tutti gli ID dei discendenti."""
        ids = []
        children = Classification.objects.filter(parent_id=parent_id)
        for child in children:
            ids.append(child.pk)
            ids.extend(self._get_descendants_ids(child.pk))
        return ids

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Calcola automaticamente la profondità gerarchica
        depth = 0
        current = instance.parent
        while current:
            depth += 1
            current = current.parent
        # Salviamo depth come attributo temporaneo (non è un campo del modello)
        instance._depth = depth
        if commit:
            instance.save()
        return instance
