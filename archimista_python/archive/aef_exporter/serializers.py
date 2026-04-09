"""
Serializers for AEF Exporter.

JSON encoding, model-to-dict conversion, and NDJSON record writing.
"""

import json
import re
from .constants import MODEL_NAME_MAP


class AEFEncoder(json.JSONEncoder):
    """Custom JSON encoder that safely handles Django model instances."""
    def default(self, obj):
        if hasattr(obj, '_meta') and hasattr(obj, 'pk'):
            return obj.pk
        if hasattr(obj, 'all'):
            return str(obj)
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if hasattr(obj, 'hex'):
            return str(obj)
        return super().default(obj)


def _to_snake_case(s):
    """Convert a camelCase string (like Django's model_name) to snake_case."""
    s = re.sub(r'([a-z])([A-Z])', r'\1_\2', s)
    s = re.sub(r'(\d)([A-Z])', r'\1_\2', s)
    return s.lower()


def model_to_dict(obj, exclude_fields):
    """Convert a model instance to a dict, excluding specified fields."""
    data = {}
    for field in obj._meta.get_fields():
        if field.name in exclude_fields:
            continue
        if field.auto_created and not field.concrete:
            continue
        if field.many_to_many:
            continue
        if field.is_relation and field.concrete:
            value = getattr(obj, f'{field.name}_id', None)
            data[f'{field.name}_id'] = value
        else:
            value = getattr(obj, field.name, None)
            if value is not None and hasattr(value, 'all'):
                continue
            if value is not None and hasattr(value, 'isoformat'):
                value = str(value)
            if value is not None and hasattr(value, 'name'):
                value = value.name
            if value is not None and hasattr(value, '_meta'):
                value = value.pk
            data[field.name] = value
    return data


def write_record(data_file, model_class, fields_dict, override_name=None):
    """
    Write a single record to data.json (newline-delimited JSON).

    Uses explicit snake_case model names for AEF/Ruby compatibility.
    """
    name_map = {
        'fondname': 'fond_name', 'fondidentifier': 'fond_identifier',
        'fondlang': 'fond_lang', 'fondowner': 'fond_owner',
        'fondurl': 'fond_url', 'fondeditor': 'fond_editor',
        'unitidentifier': 'unit_identifier',
        'unitotherreferencenumber': 'unit_other_reference_number',
        'unitlang': 'unit_lang', 'unitdamage': 'unit_damage',
        'uniturl': 'unit_url', 'uniteditor': 'unit_editor',
        'creatorname': 'creator_name',
        'creatorlegalstatus': 'creator_legal_status',
        'creatorurl': 'creator_url',
        'creatoridentifier': 'creator_identifier',
        'creatoractivity': 'creator_activity',
        'creatoreditor': 'creator_editor',
        'custodianname': 'custodian_name',
        'custodianidentifier': 'custodian_identifier',
        'custodiancontact': 'custodian_contact',
        'custodianbuilding': 'custodian_building',
        'custodianowner': 'custodian_owner',
        'custodianurl': 'custodian_url',
        'custodianeditor': 'custodian_editor',
        'sc2textualelement': 'sc2_textual_element',
        'sc2visualelement': 'sc2_visual_element',
        'sc2author': 'sc2_author',
        'sc2attributionreason': 'sc2_attribution_reason',
        'sc2commission': 'sc2_commission',
        'sc2commissionname': 'sc2_commission_name',
        'sc2technique': 'sc2_technique',
        'sc2scale': 'sc2_scale',
        'iccddescription': 'iccd_description',
        'iccdsubject': 'iccd_subject',
        'iccddamage': 'iccd_damage',
        'iccdtechspec': 'iccd_tech_spec',
        'fsccode': 'fsc_code', 'fscorganization': 'fsc_organization',
        'fscnationality': 'fsc_nationality',
        'fscopen': 'fsc_open', 'fscclose': 'fsc_close',
        'feidentification': 'fe_identification',
        'fecontext': 'fe_context', 'feopera': 'fe_opera',
        'fedesigner': 'fe_designer', 'fecadastral': 'fe_cadastral',
        'felandparcel': 'fe_land_parcel',
        'fefractlandparcel': 'fe_fract_land_parcel',
        'fefractedilparcel': 'fe_fract_edil_parcel',
        'projecturl': 'project_url',
        'projectmanager': 'project_manager',
        'projectstakeholder': 'project_stakeholder',
        'institutioneditor': 'institution_editor',
        'sourceurl': 'source_url',
        'documentformeditor': 'document_form_editor',
        # Underscore models (Django strips underscores from model_name)
        'documentform': 'document_form',
        'digitalobject': 'digital_object',
        # Relations
        'relcreatorfond': 'rel_creator_fond',
        'relcustodianfond': 'rel_custodian_fond',
        'relprojectfond': 'rel_project_fond',
        'relcreatorcreator': 'rel_creator_creator',
        'relcreatorinstitution': 'rel_creator_institution',
        'relcreatorsource': 'rel_creator_source',
        'relcustodiansource': 'rel_custodian_source',
        'relfondsource': 'rel_fond_source',
        'relunitsource': 'rel_unit_source',
        'relfondheading': 'rel_fond_heading',
        'relunitheading': 'rel_unit_heading',
        'relfonddocumentform': 'rel_fond_document_form',
        'relunitanagraphic': 'rel_unit_anagraphic',
    }

    if override_name:
        snake_name = override_name
    else:
        model_name = model_class._meta.model_name
        snake_name = name_map.get(model_name, _to_snake_case(model_name))
    record = {snake_name: fields_dict}
    line = json.dumps(record, ensure_ascii=False, cls=AEFEncoder).replace('\\r', '')
    data_file.write(line + '\r\n')
