"""
Export Fonds and Units for AEF.

Handles fond subtree collection, fond export with unit trees,
and unit extension export.
"""

from django.contrib.contenttypes.models import ContentType
from .constants import FOND_EXCLUDE, UNIT_EXCLUDE, EXTENSION_EXCLUDE, FOND_TABLES
from .serializers import model_to_dict, write_record
from archimista_python.archive.models import Fond, Unit, Event


def get_fond_subtree_ids(fond_id):
    """Get all fond IDs in the subtree (including the root)."""
    try:
        fond = Fond.objects.get(pk=fond_id)
        return fond.subtree_ids if hasattr(fond, 'subtree_ids') else [fond_id]
    except Fond.DoesNotExist:
        return []


def export_fonds_and_units(data_file, fond_ids):
    """Export fonds with their unit trees and all extension data."""
    if not fond_ids:
        return []

    unit_ids_collected = []

    # Export root fonds
    fonda = Fond.objects.filter(pk__in=fond_ids).order_by('sequence_number')
    for fond in fonda:
        fields = model_to_dict(fond, FOND_EXCLUDE)
        fields['legacy_id'] = fond.id
        if fond.is_root if hasattr(fond, 'is_root') else fond.parent_id is None:
            fields['legacy_parent_id'] = None
        else:
            fields['legacy_parent_id'] = str(fond.parent_id) if fond.parent_id else None
        write_record(data_file, Fond, fields)

        # Export units belonging to this fond
        units = Unit.objects.filter(fond_id=fond.id).order_by('sequence_number')

        root_fond_id = fond.id
        if hasattr(fond, 'root') and fond.root:
            root_fond_id = fond.root.id

        for idx, unit in enumerate(units, 1):
            fields = model_to_dict(unit, UNIT_EXCLUDE)
            fields['legacy_id'] = unit.id
            if not fields.get('sequence_number'):
                fields['sequence_number'] = idx
            if fields.get('ancestry_depth') is None:
                ancestry = fields.get('ancestry', '')
                if ancestry:
                    fields['ancestry_depth'] = len(str(ancestry).split(','))
                else:
                    fields['ancestry_depth'] = 0
            fields.pop('ancestry', None)
            fields['legacy_parent_unit_id'] = str(unit.parent_id) if unit.parent_id else None
            fields['legacy_root_fond_id'] = root_fond_id
            fields['legacy_parent_fond_id'] = unit.fond_id if unit.fond_id else None
            write_record(data_file, Unit, fields)
            unit_ids_collected.append(unit.id)

    # Export fond extensions
    _export_fond_extensions(data_file, fond_ids)

    # Export unit extensions
    if unit_ids_collected:
        from .extensions import export_unit_extensions
        export_unit_extensions(data_file, unit_ids_collected)

    return unit_ids_collected


def _export_fond_extensions(data_file, fond_ids):
    """Export fond extension tables and events."""
    for model_class, fk_field in FOND_TABLES:
        for obj in model_class.objects.filter(fond_id__in=fond_ids):
            fields = model_to_dict(obj, EXTENSION_EXCLUDE)
            fields['legacy_id'] = obj.fond_id
            write_record(data_file, model_class, fields)

    # Export fond events
    fond_ct = ContentType.objects.get_for_model(Fond)
    event_exclude = EXTENSION_EXCLUDE + [
        'content_type', 'object_id', 'content_object', 'event_type',
    ]
    for event in Event.objects.filter(content_type_id=fond_ct.id, object_id__in=fond_ids):
        fields = model_to_dict(event, event_exclude)
        fields['fond_id'] = event.object_id
        fields['legacy_id'] = event.object_id
        write_record(data_file, Event, fields, override_name='fond_event')
