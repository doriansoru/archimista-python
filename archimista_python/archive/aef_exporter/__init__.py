"""
AEF Exporter — generates .aef ZIP packages compatible with the existing AEFImporter.

Mirrors the Ruby Export model logic (create_data_file + create_metadata_file + create_aef_file).
Refactored into sub-modules for maintainability:
  - constants: exclusion lists, table mappings, model name map
  - serializers: JSON encoding, model_to_dict, NDJSON writing
  - fond_units: fond subtree, fond+unit export
  - extensions: unit extensions, creator/source single entity
  - relations: major entities, institutions, headings, sources, editors
  - digital_objects: digital object metadata + file inclusion
  - single_entity: mode='not-full' exports
  - metadata: metadata.json + ZIP packaging
  - xml_export: SAN/EAD/METS XML generation
"""

import os
import tempfile
import shutil
from .constants import APP_VERSION
from .fond_units import get_fond_subtree_ids, export_fonds_and_units
from .relations import (
    export_major_entities, export_institutions,
    export_headings, export_document_forms, export_sources, export_editors,
)
from .extensions import export_creator_entity, export_source_entity
from .digital_objects import export_digital_objects, add_digital_objects_to_zip
from .single_entity import export_single_entity
from .metadata import create_metadata, create_zip
from .xml_export import generate_xml_export

# Re-export for external use
from .constants import APP_VERSION


class AEFExporter:
    """
    Exports archivist data to AEF format (ZIP with data.json + metadata.json + digital objects).
    Compatible with the existing AEFImporter for round-trip export/import.
    """

    def __init__(self, fond_id=None, custodian_id=None, project_id=None,
                 creator_id=None, source_id=None,
                 unit_ids=None, mode='full', include_digital_objects=True):
        self.fond_id = fond_id
        self.custodian_id = custodian_id
        self.project_id = project_id
        self.creator_id = creator_id
        self.source_id = source_id
        self.unit_ids = unit_ids or []
        self.mode = mode
        self.include_digital_objects = include_digital_objects

        self.fond_ids = []
        self.unit_ids_collected = []
        self.creator_ids = []
        self.custodian_ids = []
        self.source_ids = []
        self.project_ids_collected = []
        self.heading_ids = []
        self.institution_ids = []
        self.document_form_ids = []
        self.anagraphic_ids = []

        self.tmp_dir = None

    def run(self):
        """Run the export and return the ZIP file as bytes."""
        self.tmp_dir = tempfile.mkdtemp(prefix='aef_export_')
        data_file_path = os.path.join(self.tmp_dir, 'data.json')
        metadata_file_path = os.path.join(self.tmp_dir, 'metadata.json')
        zip_file_path = os.path.join(self.tmp_dir, 'export.aef')

        try:
            self._collect_fond_ids()

            with open(data_file_path, 'w', encoding='utf-8') as data_file:
                if self.mode == 'full':
                    self.unit_ids_collected = export_fonds_and_units(data_file, self.fond_ids)
                    entity_ids = {}
                    export_major_entities(data_file, self.fond_ids, entity_ids)
                    self.creator_ids = entity_ids.get('creator', [])
                    self.custodian_ids = entity_ids.get('custodian', [])
                    self.project_ids_collected = entity_ids.get('project', [])

                    # Ensure target creator is exported
                    if self.creator_id and self.creator_id not in self.creator_ids:
                        self.creator_ids.append(self.creator_id)
                        export_creator_entity(data_file, self.creator_id)
                    # Ensure target source is exported
                    if self.source_id and self.source_id not in self.source_ids:
                        self.source_ids.append(self.source_id)
                        export_source_entity(data_file, self.source_id)

                    export_institutions(data_file, self.creator_ids)
                    export_headings(data_file, self.fond_ids, self.unit_ids_collected)
                    export_document_forms(data_file, self.fond_ids)
                    export_sources(data_file, self.creator_ids, self.custodian_ids,
                                   self.fond_ids, self.unit_ids_collected)
                    export_editors(data_file)
                    export_digital_objects(
                        data_file, self.fond_ids, self.unit_ids_collected,
                        self.creator_ids, self.custodian_ids, self.source_ids,
                    )
                else:
                    export_single_entity(data_file, self)

            attached = self._attached_entity_label()
            create_metadata(metadata_file_path, data_file_path, attached, self.mode)
            create_zip(zip_file_path, data_file_path, metadata_file_path)

            if self.include_digital_objects:
                with open(zip_file_path, 'r+b') as zf:
                    pass  # need to reopen for appending
                with open(zip_file_path, 'r+b') as f:
                    # Reopen as ZIP and add files
                    import zipfile
                    with zipfile.ZipFile(zip_file_path, 'a', zipfile.ZIP_DEFLATED) as z:
                        add_digital_objects_to_zip(
                            z, self.fond_ids, self.unit_ids_collected,
                            self.creator_ids, self.custodian_ids, self.source_ids,
                        )

            with open(zip_file_path, 'rb') as f:
                return f.read()
        finally:
            if self.tmp_dir and os.path.exists(self.tmp_dir):
                shutil.rmtree(self.tmp_dir)

    def run_xml_export(self, format_type):
        """
        Run XML export (SAN/EAD/METS).
        format_type: 'san', 'ead', or 'mets'
        Returns ZIP file as bytes.
        """
        self.tmp_dir = tempfile.mkdtemp(prefix='aef_xml_export_')
        try:
            self._collect_fond_ids()
            return generate_xml_export(self, format_type)
        finally:
            if self.tmp_dir and os.path.exists(self.tmp_dir):
                shutil.rmtree(self.tmp_dir)

    def _collect_fond_ids(self):
        """Collect all fond IDs to export based on the target entity."""
        if self.fond_id:
            self.fond_ids = get_fond_subtree_ids(self.fond_id)
        elif self.custodian_id:
            from archimista_python.archive.models import RelCustodianFond
            for rel in RelCustodianFond.objects.filter(custodian_id=self.custodian_id):
                self.fond_ids.extend(get_fond_subtree_ids(rel.fond_id))
        elif self.project_id:
            from archimista_python.archive.models import RelProjectFond
            for rel in RelProjectFond.objects.filter(project_id=self.project_id):
                self.fond_ids.extend(get_fond_subtree_ids(rel.fond_id))
        elif self.creator_id:
            from archimista_python.archive.models import RelCreatorFond
            for rel in RelCreatorFond.objects.filter(creator_id=self.creator_id):
                self.fond_ids.extend(get_fond_subtree_ids(rel.fond_id))
        elif self.source_id:
            from archimista_python.archive.models import (
                RelFondSource, RelCreatorSource, RelCustodianSource,
            )
            for rel in RelFondSource.objects.filter(source_id=self.source_id):
                self.fond_ids.extend(get_fond_subtree_ids(rel.fond_id))
            for rel in RelCreatorSource.objects.filter(source_id=self.source_id):
                if rel.creator_id and rel.creator_id not in self.creator_ids:
                    self.creator_ids.append(rel.creator_id)
            for rel in RelCustodianSource.objects.filter(source_id=self.source_id):
                if rel.custodian_id and rel.custodian_id not in self.custodian_ids:
                    self.custodian_ids.append(rel.custodian_id)
        elif self.unit_ids:
            from archimista_python.archive.models import Unit
            for u in Unit.objects.filter(pk__in=self.unit_ids):
                if u.fond_id and u.fond_id not in self.fond_ids:
                    self.fond_ids.append(u.fond_id)

    def _attached_entity_label(self):
        if self.custodian_id:
            return 'Custodian'
        elif self.project_id:
            return 'Project'
        elif self.creator_id:
            return 'Creator'
        elif self.source_id:
            return 'Source'
        elif self.unit_ids:
            return 'Unit'
        return 'Fond'
