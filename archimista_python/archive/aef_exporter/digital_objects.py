"""
Export digital objects for AEF.

Handles digital object metadata export and file inclusion in ZIP.
"""

import os
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from .constants import ENTITY_EXCLUDE
from .serializers import model_to_dict, write_record
from archimista_python.archive.models import (
    DigitalObject, Fond, Unit, Creator, Custodian, Source,
)


def export_digital_objects(data_file, fond_ids, unit_ids, creator_ids, custodian_ids, source_ids):
    """Export digital object metadata for all exported entities."""
    entity_map = [
        (Fond, fond_ids),
        (Unit, unit_ids),
        (Creator, creator_ids),
        (Custodian, custodian_ids),
        (Source, source_ids),
    ]

    for model_class, ids in entity_map:
        if not ids:
            continue
        ct = ContentType.objects.get_for_model(model_class)
        for dobj in DigitalObject.objects.filter(content_type_id=ct.id, object_id__in=ids):
            fields = model_to_dict(dobj, ENTITY_EXCLUDE)
            fields['legacy_id'] = dobj.object_id
            write_record(data_file, DigitalObject, fields)


def add_digital_objects_to_zip(zf, fond_ids, unit_ids, creator_ids, custodian_ids, source_ids):
    """Add digital object files to the ZIP package."""
    media_root = getattr(settings, 'MEDIA_ROOT', '')
    if not media_root:
        return

    dobjects = []
    entity_map = [
        (Fond, fond_ids), (Unit, unit_ids), (Creator, creator_ids),
        (Custodian, custodian_ids), (Source, source_ids),
    ]

    for model_class, ids in entity_map:
        if not ids:
            continue
        ct = ContentType.objects.get_for_model(model_class)
        dobjects.extend(DigitalObject.objects.filter(content_type_id=ct.id, object_id__in=ids))

    for dobj in dobjects:
        if dobj.asset and dobj.asset.name:
            asset_path = os.path.join(media_root, dobj.asset.name)
            if os.path.exists(asset_path):
                zip_path = f"public/digital_objects/{dobj.access_token}/{dobj.asset_file_name or os.path.basename(dobj.asset.name)}"
                zf.write(asset_path, zip_path)
