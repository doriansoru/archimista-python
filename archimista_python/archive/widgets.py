"""
Select2 widgets per l'autocomplete delle relazioni.

Ogni widget estende ModelSelect2Widget di django-select2,
che gestisce automaticamente le chiamate AJAX per la ricerca.

INCLUDE: helper auto_select_threshold() che imposta minimum-input-length=0
quando il queryset ha pochi elementi, così Select2 mostra subito tutte
le opzioni senza richiedere digitazione.
"""

from django import forms
from django.db.models import Model
from django.db.models.query import QuerySet
from django.db.models import Q
from django_select2.forms import ModelSelect2Widget

from archimista_python.archive.models import (
    Fond, Creator, Custodian, Source, Institution,
    Heading, Anagraphic, DocumentForm, Unit, Classification, Lang,
)


# Soglia: se il queryset ha meno di N elementi, azzera minimum-input-length
HYBRID_THRESHOLD = 20


def auto_select_threshold(form, field_name, threshold=HYBRID_THRESHOLD, min_input_length=0):
    """
    Se il queryset del campo ha meno di `threshold` elementi, imposta
    minimum-input-length=0 sul widget Select2.
    Così Select2 mostra tutte le opzioni subito, senza richiedere digitazione.

    Da chiamare nel __init__ del form, dopo il super().__init__().

    Esempio:
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            auto_select_threshold(self, 'parent')
            auto_select_threshold(self, 'fond')
    """
    field = form.fields.get(field_name)
    if field is None:
        return
    qs = getattr(field, 'queryset', None)
    if qs is None or not isinstance(qs, QuerySet):
        return
    try:
        count = qs.count()
    except Exception:
        return
    if count < threshold:
        # Modifica gli attributi del widget Select2
        widget = field.widget
        if hasattr(widget, 'attrs'):
            widget.attrs['data-minimum-input-length'] = str(min_input_length)
        # Anche se il widget ha build_attrs, override diretto
        if hasattr(widget, 'data_attrs'):
            widget.data_attrs['data-minimum-input-length'] = str(min_input_length)


class FondSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Fondi."""
    model = Fond
    search_fields = ['name__icontains']

    def label_from_instance(self, obj):
        return obj.name or f'Fondo #{obj.pk}'


class CreatorSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Soggetti produttori."""
    model = Creator
    # Search fields on the Creator model itself
    search_fields = ['residence__icontains']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Prefetch preferred name for display
        return qs.prefetch_related('creator_names')

    def label_from_instance(self, obj):
        pn = obj.creator_names.filter(preferred=True).first()
        if pn:
            if pn.first_name or pn.last_name:
                return f'{pn.first_name} {pn.last_name}'.strip()
            if pn.name:
                return pn.name
        return f'Soggetto #{obj.pk}'

    def filter_queryset(self, request, term, queryset=None):
        """Override to search through preferred_name as well."""
        qs = queryset or self.get_queryset(request)
        if not term:
            return qs

        # Find creators whose preferred_name matches
        from archimista_python.archive.models import CreatorName
        matching_names = CreatorName.objects.filter(
            preferred=True,
        ).filter(
            Q(name__icontains=term) |
            Q(first_name__icontains=term) |
            Q(last_name__icontains=term)
        ).values_list('creator_id', flat=True)

        return qs.filter(pk__in=matching_names)


class CustodianSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Soggetti conservatori."""
    model = Custodian
    search_fields = ['contact_person__icontains']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('custodian_names')

    def label_from_instance(self, obj):
        pn = obj.custodian_names.filter(preferred=True).first()
        return pn.name if pn else f'Conservatore #{obj.pk}'

    def filter_queryset(self, request, term, queryset=None):
        qs = queryset or self.get_queryset(request)
        if not term:
            return qs

        from archimista_python.archive.models import CustodianName
        matching_names = CustodianName.objects.filter(
            preferred=True,
            name__icontains=term
        ).values_list('custodian_id', flat=True)

        return qs.filter(pk__in=matching_names)


class SourceSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Fonti."""
    model = Source
    search_fields = ['title__icontains', 'author__icontains']

    def label_from_instance(self, obj):
        parts = []
        if obj.author:
            parts.append(obj.author)
        if obj.title:
            parts.append(f'_{obj.title}_')
        return ', '.join(parts) if parts else f'Fonte #{obj.pk}'


class InstitutionSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Istituzioni."""
    model = Institution
    search_fields = ['name__icontains']

    def label_from_instance(self, obj):
        return obj.name or f'Istituzione #{obj.pk}'


class HeadingSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Voci di indice."""
    model = Heading
    search_fields = ['name__icontains']

    def label_from_instance(self, obj):
        return obj.name or f'Voce #{obj.pk}'


class AnagraphicSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Anagrafiche."""
    model = Anagraphic
    search_fields = ['name__icontains', 'surname__icontains']

    def label_from_instance(self, obj):
        parts = []
        if obj.surname:
            parts.append(obj.surname)
        if obj.name:
            parts.append(obj.name)
        return ', '.join(parts) if parts else f'Anagrafica #{obj.pk}'


class DocumentFormSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Forme documentarie."""
    model = DocumentForm
    search_fields = ['name__icontains']

    def label_from_instance(self, obj):
        return obj.name or f'Forma documentaria #{obj.pk}'


class UnitSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Unità archivistiche."""
    model = Unit
    search_fields = ['title__icontains', 'reference_number__icontains']

    def label_from_instance(self, obj):
        parts = []
        if obj.reference_number:
            parts.append(obj.reference_number)
        if obj.title:
            parts.append(obj.title)
        return ' — '.join(parts) if parts else f'Unità #{obj.pk}'


class ClassificationSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Classificazioni (Titolario)."""
    model = Classification
    search_fields = ['code__icontains', 'name__icontains']

    def label_from_instance(self, obj):
        return f'{obj.code} — {obj.name}' if obj.code else (obj.name or f'Classificazione #{obj.pk}')


class LangSelect2Widget(ModelSelect2Widget):
    """Widget Select2 per la selezione di Lingue."""
    model = Lang
    search_fields = ['code__icontains', 'name__icontains']

    def label_from_instance(self, obj):
        return f'{obj.code} — {obj.name}' if obj.code and obj.name else (obj.name or obj.code or f'Lingua #{obj.pk}')
