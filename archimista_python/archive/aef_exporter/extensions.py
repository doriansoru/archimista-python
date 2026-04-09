"""
Export unit extensions and single entity helpers for AEF.

Handles SC2/ICCD/FSC/FE for units, plus creator/source/single entity exports.
"""

from django.contrib.contenttypes.models import ContentType
from .constants import (
    EXTENSION_EXCLUDE, RELATION_EXCLUDE, CREATOR_TABLES, ENTITY_EXCLUDE,
)
from .serializers import model_to_dict, write_record
from archimista_python.archive.models import (
    Sc2, Sc2TextualElement, Sc2VisualElement, Sc2Author, Sc2AttributionReason,
    Sc2Commission, Sc2CommissionName, Sc2Technique, Sc2Scale,
    IccdDescription, IccdSubject, IccdDamage, IccdTechSpec,
    FscCode, FscOrganization, FscNationality, FscOpen, FscClose,
    FeIdentification, FeContext, FeOpera, FeDesigner, FeCadastral,
    FeLandParcel, FeFractLandParcel, FeFractEdilParcel,
    UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage,
    UnitUrl, UnitEditor,
    Creator, Source, SourceUrl, Event,
    RelCreatorFond, RelCreatorCreator, RelCreatorInstitution, RelCreatorSource,
)


def export_unit_extensions(data_file, unit_ids):
    """Export all unit-related extension tables."""
    # Standard unit extensions
    for model_class, fk_field in [
        (UnitIdentifier, 'unit_id'), (UnitOtherReferenceNumber, 'unit_id'),
        (UnitLang, 'unit_id'), (UnitDamage, 'unit_id'),
        (UnitUrl, 'unit_id'), (UnitEditor, 'unit_id'),
    ]:
        for obj in model_class.objects.filter(unit_id__in=unit_ids):
            fields = model_to_dict(obj, EXTENSION_EXCLUDE)
            fields['legacy_id'] = obj.unit_id
            write_record(data_file, model_class, fields)

    # SC2 cards
    for sc2 in Sc2.objects.filter(unit_id__in=unit_ids):
        fields = model_to_dict(sc2, EXTENSION_EXCLUDE)
        fields['legacy_id'] = sc2.unit_id
        fields['obj_type'] = fields.get('card_type', 'SC2')
        write_record(data_file, Sc2, fields)

    for obj in Sc2TextualElement.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in Sc2VisualElement.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)

    for obj in Sc2Author.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
        for reason in obj.sc2_attribution_reasons.all():
            rfields = model_to_dict(reason, EXTENSION_EXCLUDE)
            rfields['unit_id'] = obj.unit_id
            rfields['legacy_id'] = obj.unit_id
            write_record(data_file, Sc2AttributionReason, rfields)

    for obj in Sc2Commission.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
        for cname in obj.sc2_commission_names.all():
            cfields = model_to_dict(cname, EXTENSION_EXCLUDE)
            cfields['unit_id'] = obj.unit_id
            cfields['legacy_id'] = obj.unit_id
            write_record(data_file, Sc2CommissionName, cfields)

    for obj in Sc2Technique.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in Sc2Scale.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)

    # ICCD — IccdSubject/IccdDamage/IccdTechSpec link via IccdDescription (OneToOne to Unit)
    # IccdDescription has unit_id, so we filter through it
    from archimista_python.archive.models import IccdDescription, IccdAuthor
    iccd_descs = IccdDescription.objects.filter(unit_id__in=unit_ids)
    iccd_desc_ids = list(iccd_descs.values_list('id', flat=True))

    for desc in iccd_descs:
        fields = model_to_dict(desc, EXTENSION_EXCLUDE)
        fields['legacy_id'] = desc.unit_id
        # Map unit OneToOne → unit_id for import compatibility
        if 'unit_id' not in fields and hasattr(desc, 'unit_id'):
            fields['unit_id'] = desc.unit_id
        write_record(data_file, IccdDescription, fields)

    for obj in IccdSubject.objects.filter(iccd_description_id__in=iccd_desc_ids):
        fields = model_to_dict(obj, EXTENSION_EXCLUDE)
        fields['legacy_id'] = obj.iccd_description.unit_id if obj.iccd_description else None
        write_record(data_file, IccdSubject, fields)

    # IccdDamage links to Unit directly
    for obj in IccdDamage.objects.filter(unit_id__in=unit_ids):
        fields = model_to_dict(obj, EXTENSION_EXCLUDE)
        fields['legacy_id'] = obj.unit_id
        write_record(data_file, IccdDamage, fields)

    # IccdTechSpec links via OneToOne to Unit
    for obj in IccdTechSpec.objects.filter(unit_id__in=unit_ids):
        fields = model_to_dict(obj, EXTENSION_EXCLUDE)
        fields['legacy_id'] = obj.unit_id
        if 'unit_id' not in fields and hasattr(obj, 'unit_id'):
            fields['unit_id'] = obj.unit_id
        write_record(data_file, IccdTechSpec, fields)

    # FSC
    for obj in FscCode.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FscOrganization.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FscNationality.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FscOpen.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FscClose.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)

    # FE
    for obj in FeIdentification.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FeContext.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FeOpera.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FeDesigner.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FeCadastral.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FeLandParcel.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FeFractLandParcel.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)
    for obj in FeFractEdilParcel.objects.filter(unit_id__in=unit_ids):
        _ext_record(data_file, obj)


def _ext_record(data_file, obj):
    """Write a generic extension record."""
    fields = model_to_dict(obj, EXTENSION_EXCLUDE)
    # Detect FK field name
    for f in obj._meta.get_fields():
        if f.is_relation and f.concrete and f.name.endswith('_id'):
            fields['legacy_id'] = getattr(obj, f.name)
            break
    write_record(data_file, type(obj), fields)


def export_creator_entity(data_file, creator_id):
    """Export a single creator entity with all its related data (for full mode)."""
    try:
        creator = Creator.objects.get(pk=creator_id)
    except Creator.DoesNotExist:
        return
    fields = model_to_dict(creator, ENTITY_EXCLUDE)
    fields['legacy_id'] = creator.id
    write_record(data_file, Creator, fields)

    # Creator extensions
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

    # Creator -> Fond relations
    _write_rel_records(data_file, RelCreatorFond, 'creator_id', creator_id)
    # Creator -> Creator relations
    _write_rel_records(data_file, RelCreatorCreator, 'creator_id', creator_id)
    # Creator -> Institution relations
    _write_rel_records(data_file, RelCreatorInstitution, 'creator_id', creator_id)
    # Creator -> Source relations
    _write_rel_records(data_file, RelCreatorSource, 'creator_id', creator_id)


def export_source_entity(data_file, source_id):
    """Export a single source entity with all its related data (for full mode)."""
    try:
        source = Source.objects.get(pk=source_id)
    except Source.DoesNotExist:
        return
    fields = model_to_dict(source, ENTITY_EXCLUDE)
    fields['legacy_id'] = source.id
    write_record(data_file, Source, fields)

    # Source extensions (URLs)
    for obj in SourceUrl.objects.filter(source_id=source_id):
        ofields = model_to_dict(obj, EXTENSION_EXCLUDE)
        ofields['legacy_id'] = obj.source_id
        write_record(data_file, SourceUrl, ofields)


def _write_rel_records(data_file, rel_model, fk_name, fk_value):
    """Write relation records with legacy IDs."""
    kwargs = {fk_name: fk_value}
    for rel in rel_model.objects.filter(**kwargs):
        rfields = model_to_dict(rel, RELATION_EXCLUDE)
        rfields['legacy_id'] = fk_value
        # Add legacy FK IDs
        for f in rel._meta.get_fields():
            if f.is_relation and f.concrete:
                val = getattr(rel, f.name)
                if val:
                    rfields[f'legacy_{f.name}_id'] = val
        write_record(data_file, rel_model, rfields)
