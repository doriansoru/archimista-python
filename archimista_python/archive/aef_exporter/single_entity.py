"""
Export single entity for AEF (mode='not-full').

Handles export of a single fond/custodian/project/creator/source/unit
without traversing cross-entity relationships.
"""

from django.contrib.contenttypes.models import ContentType
from .constants import (
    ENTITY_EXCLUDE, UNIT_EXCLUDE, EXTENSION_EXCLUDE, RELATION_EXCLUDE,
    CUSTODIAN_TABLES, PROJECT_TABLES, CREATOR_TABLES,
)
from .serializers import model_to_dict, write_record
from .fond_units import export_fonds_and_units
from .extensions import export_unit_extensions
from archimista_python.archive.models import (
    Fond, Unit, Custodian, Project, Creator, Source, SourceUrl, Event,
    RelCreatorFond, RelCreatorCreator, RelCreatorInstitution, RelCreatorSource,
)


def export_single_entity(data_file, exporter):
    """Export a single entity (non-full mode)."""
    if exporter.fond_id:
        unit_ids = export_fonds_and_units(data_file, exporter.fond_ids)
        exporter.unit_ids_collected = unit_ids
    elif exporter.custodian_id:
        custodian = Custodian.objects.get(pk=exporter.custodian_id)
        fields = model_to_dict(custodian, ENTITY_EXCLUDE)
        fields['legacy_id'] = custodian.id
        write_record(data_file, Custodian, fields)
        for model_class, fk_field in CUSTODIAN_TABLES:
            for obj in model_class.objects.filter(custodian_id=exporter.custodian_id):
                fields = model_to_dict(obj, EXTENSION_EXCLUDE)
                fields['legacy_id'] = obj.custodian_id
                write_record(data_file, model_class, fields)
    elif exporter.project_id:
        project = Project.objects.get(pk=exporter.project_id)
        fields = model_to_dict(project, ENTITY_EXCLUDE)
        fields['legacy_id'] = project.id
        write_record(data_file, Project, fields)
    elif exporter.creator_id:
        _export_single_creator(data_file, exporter.creator_id)
    elif exporter.source_id:
        _export_single_source(data_file, exporter.source_id)
    elif exporter.unit_ids:
        for unit in Unit.objects.filter(pk__in=exporter.unit_ids):
            fields = model_to_dict(unit, UNIT_EXCLUDE)
            fields['legacy_id'] = unit.id
            fields['legacy_parent_unit_id'] = str(unit.parent_id) if unit.parent_id else None
            write_record(data_file, Unit, fields)
            exporter.unit_ids_collected.append(unit.id)
        export_unit_extensions(data_file, exporter.unit_ids_collected)


def _export_single_creator(data_file, creator_id):
    """Export a single creator with extensions and relations."""
    creator = Creator.objects.get(pk=creator_id)
    fields = model_to_dict(creator, ENTITY_EXCLUDE)
    fields['legacy_id'] = creator.id
    write_record(data_file, Creator, fields)

    for model_class, fk_field in CREATOR_TABLES:
        for obj in model_class.objects.filter(creator_id=creator_id):
            ofields = model_to_dict(obj, EXTENSION_EXCLUDE)
            ofields['legacy_id'] = obj.creator_id
            write_record(data_file, model_class, ofields)

    # Creator events
    creator_ct = ContentType.objects.get_for_model(Creator)
    event_exclude = EXTENSION_EXCLUDE + [
        'content_type', 'object_id', 'content_object', 'event_type',
    ]
    for event in Event.objects.filter(content_type_id=creator_ct.id, object_id=creator_id):
        efields = model_to_dict(event, event_exclude)
        efields['creator_id'] = event.object_id
        efields['legacy_id'] = event.object_id
        write_record(data_file, Event, efields, override_name='creator_event')

    # Relations
    for rel in RelCreatorFond.objects.filter(creator_id=creator_id):
        rfields = model_to_dict(rel, RELATION_EXCLUDE)
        rfields['legacy_id'] = rel.creator_id
        write_record(data_file, RelCreatorFond, rfields)
    for rel in RelCreatorCreator.objects.filter(creator_id=creator_id):
        rfields = model_to_dict(rel, RELATION_EXCLUDE)
        rfields['legacy_id'] = rel.creator_id
        write_record(data_file, RelCreatorCreator, rfields)
    for rel in RelCreatorInstitution.objects.filter(creator_id=creator_id):
        rfields = model_to_dict(rel, RELATION_EXCLUDE)
        rfields['legacy_id'] = rel.creator_id
        write_record(data_file, RelCreatorInstitution, rfields)
    for rel in RelCreatorSource.objects.filter(creator_id=creator_id):
        rfields = model_to_dict(rel, RELATION_EXCLUDE)
        rfields['legacy_id'] = rel.creator_id
        write_record(data_file, RelCreatorSource, rfields)


def _export_single_source(data_file, source_id):
    """Export a single source with extensions."""
    source = Source.objects.get(pk=source_id)
    fields = model_to_dict(source, ENTITY_EXCLUDE)
    fields['legacy_id'] = source.id
    write_record(data_file, Source, fields)

    for obj in SourceUrl.objects.filter(source_id=source_id):
        sfields = model_to_dict(obj, EXTENSION_EXCLUDE)
        sfields['legacy_id'] = obj.source_id
        write_record(data_file, SourceUrl, sfields)
