"""
Export relations between entities for AEF.

Handles major entities (creator/custodian/project), institutions,
headings, document forms, sources, and editors.
"""

from django.db.models import Q
from .constants import (
    ENTITY_EXCLUDE, EXTENSION_EXCLUDE, RELATION_EXCLUDE,
    CREATOR_TABLES, CUSTODIAN_TABLES, PROJECT_TABLES,
    INSTITUTION_TABLES, SOURCE_TABLES, DOCUMENT_FORM_TABLES,
)
from .serializers import model_to_dict, write_record
from archimista_python.archive.models import (
    Creator, Custodian, Project, RelCreatorFond, RelCustodianFond,
    RelProjectFond, RelCreatorCreator, RelCreatorInstitution,
    RelCreatorSource, RelFondSource, RelUnitSource, RelCustodianSource,
    RelFondHeading, RelUnitHeading, Heading, RelFondDocumentForm,
    DocumentForm, Institution, Source, SourceUrl, Editor,
)


def export_major_entities(data_file, fond_ids, entity_ids_callback):
    """
    Export Creator, Custodian, Project entities and their relations to fonds.

    entity_ids_callback(dict): called with {'creator': [...], 'custodian': [...], 'project': [...]}
    """
    for entity_name, rel_model, entity_model, tables in [
        ('creator', RelCreatorFond, Creator, CREATOR_TABLES),
        ('custodian', RelCustodianFond, Custodian, CUSTODIAN_TABLES),
        ('project', RelProjectFond, Project, PROJECT_TABLES),
    ]:
        container = set()
        rels = rel_model.objects.filter(fond_id__in=fond_ids)

        for rel in rels:
            entity_id = getattr(rel, f'{entity_name}_id')
            container.add(entity_id)

            rel_fields = model_to_dict(rel, RELATION_EXCLUDE)
            rel_fields['legacy_fond_id'] = rel.fond_id
            rel_fields[f'legacy_{entity_name}_id'] = entity_id
            rel_fields.pop(f'{entity_name}_id', None)
            rel_fields.pop('fond_id', None)
            write_record(data_file, rel_model, rel_fields)

        # For creators: also traverse RelCreatorCreator
        if entity_name == 'creator' and container:
            creator_ids = list(container)
            rels_cc = RelCreatorCreator.objects.filter(
                Q(creator_id__in=creator_ids) |
                Q(related_creator_id__in=creator_ids)
            )
            for rel in rels_cc:
                rel_fields = model_to_dict(rel, RELATION_EXCLUDE)
                rel_fields['legacy_creator_id'] = rel.creator_id
                rel_fields['legacy_related_creator_id'] = rel.related_creator_id
                rel_fields.pop('creator_id', None)
                rel_fields.pop('related_creator_id', None)
                write_record(data_file, RelCreatorCreator, rel_fields)
                container.add(rel.creator_id)
                container.add(rel.related_creator_id)

        entity_ids = list(container)
        entity_ids_callback[entity_name] = entity_ids

        if entity_ids:
            # Export entity records
            for entity in entity_model.objects.filter(pk__in=entity_ids):
                fields = model_to_dict(entity, ENTITY_EXCLUDE)
                fields['legacy_id'] = entity.id
                write_record(data_file, entity_model, fields)

            # Export entity extensions
            for model_class, fk_field in tables:
                for obj in model_class.objects.filter(**{f'{fk_field}__in': entity_ids}):
                    fields = model_to_dict(obj, EXTENSION_EXCLUDE)
                    fields['legacy_id'] = getattr(obj, fk_field)
                    write_record(data_file, model_class, fields)


def export_institutions(data_file, creator_ids):
    """Export institutions related to creators."""
    if not creator_ids:
        return
    institution_ids = set()
    for rel in RelCreatorInstitution.objects.filter(creator_id__in=creator_ids):
        institution_ids.add(rel.institution_id)
        rel_fields = model_to_dict(rel, RELATION_EXCLUDE)
        rel_fields['legacy_creator_id'] = rel.creator_id
        rel_fields['legacy_institution_id'] = rel.institution_id
        rel_fields.pop('creator_id', None)
        rel_fields.pop('institution_id', None)
        write_record(data_file, RelCreatorInstitution, rel_fields)

    for inst in Institution.objects.filter(pk__in=list(institution_ids)):
        fields = model_to_dict(inst, ENTITY_EXCLUDE)
        fields['legacy_id'] = inst.id
        write_record(data_file, Institution, fields)

    for model_class, fk_field in INSTITUTION_TABLES:
        for obj in model_class.objects.filter(institution_id__in=institution_ids):
            fields = model_to_dict(obj, EXTENSION_EXCLUDE)
            fields['legacy_id'] = getattr(obj, fk_field)
            write_record(data_file, model_class, fields)


def export_headings(data_file, fond_ids, unit_ids):
    """Export headings linked to fonds/units."""
    heading_ids = set()
    for rel in RelFondHeading.objects.filter(fond_id__in=fond_ids):
        heading_ids.add(rel.heading_id)
        rel_fields = model_to_dict(rel, RELATION_EXCLUDE)
        rel_fields['legacy_fond_id'] = rel.fond_id
        rel_fields['legacy_heading_id'] = rel.heading_id
        rel_fields.pop('fond_id', None)
        rel_fields.pop('heading_id', None)
        write_record(data_file, RelFondHeading, rel_fields)

    for rel in RelUnitHeading.objects.filter(unit_id__in=unit_ids):
        heading_ids.add(rel.heading_id)
        rel_fields = model_to_dict(rel, RELATION_EXCLUDE)
        rel_fields['legacy_unit_id'] = rel.unit_id
        rel_fields['legacy_heading_id'] = rel.heading_id
        rel_fields.pop('unit_id', None)
        rel_fields.pop('heading_id', None)
        write_record(data_file, RelUnitHeading, rel_fields)

    if heading_ids:
        for heading in Heading.objects.filter(pk__in=list(heading_ids)):
            fields = model_to_dict(heading, ENTITY_EXCLUDE)
            fields['legacy_id'] = heading.id
            write_record(data_file, Heading, fields)


def export_document_forms(data_file, fond_ids):
    """Export document forms linked to fonds."""
    df_ids = set()
    for rel in RelFondDocumentForm.objects.filter(fond_id__in=fond_ids):
        df_ids.add(rel.document_form_id)
        rel_fields = model_to_dict(rel, RELATION_EXCLUDE)
        rel_fields['legacy_fond_id'] = rel.fond_id
        rel_fields['legacy_document_form_id'] = rel.document_form_id
        rel_fields.pop('fond_id', None)
        rel_fields.pop('document_form_id', None)
        write_record(data_file, RelFondDocumentForm, rel_fields)

    if df_ids:
        for df in DocumentForm.objects.filter(pk__in=list(df_ids)):
            fields = model_to_dict(df, ENTITY_EXCLUDE)
            fields['legacy_id'] = df.id
            write_record(data_file, DocumentForm, fields)

        for model_class, fk_field in DOCUMENT_FORM_TABLES:
            for obj in model_class.objects.filter(document_form_id__in=df_ids):
                fields = model_to_dict(obj, EXTENSION_EXCLUDE)
                fields['legacy_id'] = getattr(obj, fk_field)
                write_record(data_file, model_class, fields)


def export_sources(data_file, creator_ids, custodian_ids, fond_ids, unit_ids):
    """Export sources linked to creators, custodians, fonds, units."""
    source_ids = set()

    for rel_model, fk_name in [
        (RelCreatorSource, 'creator_id'),
        (RelCustodianSource, 'custodian_id'),
        (RelFondSource, 'fond_id'),
        (RelUnitSource, 'unit_id'),
    ]:
        id_list = {
            'creator_id': creator_ids, 'custodian_id': custodian_ids,
            'fond_id': fond_ids, 'unit_id': unit_ids,
        }[fk_name]
        if not id_list:
            continue
        for rel in rel_model.objects.filter(**{fk_name + '__in': id_list}):
            source_ids.add(rel.source_id)
            rel_fields = model_to_dict(rel, RELATION_EXCLUDE)
            rel_fields['legacy_fond_id'] = getattr(rel, 'fond_id', None)
            rel_fields[f'legacy_{fk_name}'] = getattr(rel, fk_name)
            rel_fields['legacy_source_id'] = rel.source_id
            for key in ['fond_id', 'creator_id', 'custodian_id', 'unit_id', 'source_id']:
                rel_fields.pop(key, None)
            write_record(data_file, rel_model, rel_fields)

    if source_ids:
        for source in Source.objects.filter(pk__in=list(source_ids)):
            fields = model_to_dict(source, ENTITY_EXCLUDE)
            fields['legacy_id'] = source.id
            write_record(data_file, Source, fields)

        for obj in SourceUrl.objects.filter(source_id__in=source_ids):
            fields = model_to_dict(obj, EXTENSION_EXCLUDE)
            fields['legacy_id'] = obj.source_id
            write_record(data_file, SourceUrl, fields)


def export_editors(data_file, group_id=None):
    """Export all editors for the group."""
    qs = Editor.objects.all()
    if group_id:
        qs = qs.filter(group_id=group_id)
    for editor in qs:
        fields = model_to_dict(editor, EXTENSION_EXCLUDE)
        fields['legacy_id'] = editor.id
        write_record(data_file, Editor, fields)
