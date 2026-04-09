import json
import zipfile
import os
import shutil
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from .models import (
    Group, Fond, Unit, Creator, Custodian, Heading, DigitalObject,
    Classification, BiogHist, Event, Sc2, IccdAuthor, IccdDescription,
    RelCreatorFond, RelCustodianFond, RelFondHeading, RelUnitHeading,
    # Nuovi modelli per importazione completa
    FondName, FondIdentifier, FondLang, FondOwner, FondUrl, FondEditor,
    UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage, UnitUrl, UnitEditor,
    CreatorName, CreatorLegalStatus, CreatorUrl, CreatorIdentifier, CreatorActivity, CreatorEditor,
    CustodianName, CustodianIdentifier, CustodianContact, CustodianBuilding, CustodianOwner, CustodianUrl, CustodianEditor,
    Sc2TextualElement, Sc2VisualElement, Sc2Author, Sc2AttributionReason, Sc2Commission, Sc2CommissionName, Sc2Technique, Sc2Scale,
    IccdSubject, IccdDamage, IccdTechSpec,
    FscCode, FscOrganization, FscNationality, FscOpen, FscClose,
    FeIdentification, FeContext, FeOpera, FeDesigner, FeCadastral, FeLandParcel, FeFractLandParcel, FeFractEdilParcel,
    RelCreatorCreator, RelCreatorInstitution, RelCreatorSource, RelCustodianSource, RelFondSource, RelUnitSource, RelFondDocumentForm, RelProjectFond, RelUnitAnagraphic,
    Project, ProjectUrl, ProjectManager, ProjectStakeholder,
    DocumentForm, DocumentFormEditor, Anagraphic, AnagIdentifier, Place, Lang,
    Term, Vocabulary, Export, Import, Editor, Activity, CreatorAssociationType,
    Institution, InstitutionEditor,
    Source, SourceUrl,
)

class AEFImporter:
    def __init__(self, zip_path, group_id=1):
        self.zip_path = zip_path
        self.group_id = Group.objects.get_or_create(id=group_id, defaults={'name': 'Imported Group'})[0]
        self.id_map = {} # Maps (model_class, legacy_id) -> new_object_id
        self.pending_rels = [] # List of relations to process in second pass
        self.pending_hierarchy = [] # (model_class, new_obj_id, legacy_parent_id)
        self.pending_unit_fond_links = [] # (unit_id, legacy_fond_id, legacy_root_fond_id)

    def run(self):
        with zipfile.ZipFile(self.zip_path, 'r') as z:
            # 1. Read data.json
            if 'data.json' not in z.namelist():
                raise Exception("Missing data.json in AEF package")
            
            with z.open('data.json') as f:
                with transaction.atomic():
                    for line in f:
                        if not line.strip(): continue
                        data = json.loads(line)
                        self.process_record(data, z)
                    
                    # 2. Second pass: Restore hierarchy first
                    self.process_pending_hierarchy()
                    
                    # 3. Third pass: Link Units to Fond/RootFond
                    self.process_pending_unit_fond_links()
                    
                    # 4. Final pass: Restore M2M relations
                    self.process_pending_relations()

    def process_record(self, data, z):
        # Data is usually like {"fond": {...}} or {"unit": {...}}
        model_name = list(data.keys())[0]
        fields = data[model_name]
        legacy_id = fields.get('legacy_id')

        if model_name == 'fond':
            obj = self.import_fond(fields)
            self.id_map[(Fond, str(legacy_id))] = obj.id
            if fields.get('legacy_parent_id'):
                self.pending_hierarchy.append((Fond, obj.id, str(fields.get('legacy_parent_id'))))
        elif model_name == 'unit':
            obj = self.import_unit(fields)
            self.id_map[(Unit, str(legacy_id))] = obj.id
            if fields.get('legacy_parent_unit_id'):
                self.pending_hierarchy.append((Unit, obj.id, str(fields.get('legacy_parent_unit_id'))))
            # Capture links to Fond/RootFond
            self.pending_unit_fond_links.append((obj.id, str(fields.get('legacy_parent_fond_id')), str(fields.get('legacy_root_fond_id'))))
        elif model_name == 'creator':
            obj = self.import_creator(fields)
            self.id_map[(Creator, str(legacy_id))] = obj.id
        elif model_name == 'custodian':
            obj = self.import_custodian(fields)
            self.id_map[(Custodian, str(legacy_id))] = obj.id
        elif model_name == 'heading':
            obj = self.import_heading(fields)
            self.id_map[(Heading, str(legacy_id))] = obj.id
        elif model_name == 'digital_object':
            self.import_digital_object(fields, z)
        elif model_name == 'editor':
            self.import_editor(fields)
        elif model_name == 'institution':
            self.import_institution(fields)
        elif model_name == 'institution_editor':
            self.import_institution_editor(fields)
        elif model_name == 'source':
            self.import_source(fields)
        elif model_name == 'source_url':
            self.import_source_url(fields)
        elif model_name == 'project':
            self.import_project(fields)
        elif model_name == 'project_url':
            self.import_project_url(fields)
        elif model_name == 'project_manager':
            self.import_project_manager(fields)
        elif model_name == 'project_stakeholder':
            self.import_project_stakeholder(fields)
        elif model_name == 'document_form':
            self.import_document_form(fields)
        elif model_name == 'document_form_editor':
            self.import_document_form_editor(fields)
        elif model_name == 'anagraphic':
            self.import_anagraphic(fields)
        elif model_name == 'lang':
            self.import_lang(fields)
        elif model_name == 'place':
            self.import_place(fields)
        elif model_name.startswith('rel_'):
            self.pending_rels.append((model_name, fields))
        # Handle specialized cards
        elif model_name == 'sc2':
            self.import_sc2(fields)
        elif model_name == 'iccd_description':
            self.import_iccd(fields)
        # Handle extension models
        elif model_name == 'fond_name':
            self.import_fond_name(fields)
        elif model_name == 'fond_identifier':
            self.import_fond_identifier(fields)
        elif model_name == 'fond_lang':
            self.import_fond_lang(fields)
        elif model_name == 'fond_owner':
            self.import_fond_owner(fields)
        elif model_name == 'fond_url':
            self.import_fond_url(fields)
        elif model_name == 'fond_editor':
            self.import_fond_editor(fields)
        elif model_name == 'unit_identifier':
            self.import_unit_identifier(fields)
        elif model_name == 'unit_other_reference_number':
            self.import_unit_other_reference_number(fields)
        elif model_name == 'unit_lang':
            self.import_unit_lang(fields)
        elif model_name == 'unit_damage':
            self.import_unit_damage(fields)
        elif model_name == 'unit_url':
            self.import_unit_url(fields)
        elif model_name == 'unit_editor':
            self.import_unit_editor(fields)
        elif model_name == 'creator_name':
            self.import_creator_name(fields)
        elif model_name == 'creator_legal_status':
            self.import_creator_legal_status(fields)
        elif model_name == 'creator_url':
            self.import_creator_url(fields)
        elif model_name == 'creator_identifier':
            self.import_creator_identifier(fields)
        elif model_name == 'creator_activity':
            self.import_creator_activity(fields)
        elif model_name == 'creator_editor':
            self.import_creator_editor(fields)
        elif model_name == 'custodian_name':
            self.import_custodian_name(fields)
        elif model_name == 'custodian_identifier':
            self.import_custodian_identifier(fields)
        elif model_name == 'custodian_contact':
            self.import_custodian_contact(fields)
        elif model_name == 'custodian_building':
            self.import_custodian_building(fields)
        elif model_name == 'custodian_owner':
            self.import_custodian_owner(fields)
        elif model_name == 'custodian_url':
            self.import_custodian_url(fields)
        elif model_name == 'custodian_editor':
            self.import_custodian_editor(fields)
        elif model_name == 'sc2_textual_element':
            self.import_sc2_textual_element(fields)
        elif model_name == 'sc2_visual_element':
            self.import_sc2_visual_element(fields)
        elif model_name == 'sc2_author':
            self.import_sc2_author(fields)
        elif model_name == 'sc2_attribution_reason':
            self.import_sc2_attribution_reason(fields)
        elif model_name == 'sc2_commission':
            self.import_sc2_commission(fields)
        elif model_name == 'sc2_commission_name':
            self.import_sc2_commission_name(fields)
        elif model_name == 'sc2_technique':
            self.import_sc2_technique(fields)
        elif model_name == 'sc2_scale':
            self.import_sc2_scale(fields)
        elif model_name == 'iccd_subject':
            self.import_iccd_subject(fields)
        elif model_name == 'iccd_damage':
            self.import_iccd_damage(fields)
        elif model_name == 'iccd_tech_spec':
            self.import_iccd_tech_spec(fields)
        elif model_name == 'fsc_code':
            self.import_fsc_code(fields)
        elif model_name == 'fsc_organization':
            self.import_fsc_organization(fields)
        elif model_name == 'fsc_nationality':
            self.import_fsc_nationality(fields)
        elif model_name == 'fsc_open':
            self.import_fsc_open(fields)
        elif model_name == 'fsc_close':
            self.import_fsc_close(fields)
        elif model_name == 'fe_identification':
            self.import_fe_identification(fields)
        elif model_name == 'fe_context':
            self.import_fe_context(fields)
        elif model_name == 'fe_opera':
            self.import_fe_opera(fields)
        elif model_name == 'fe_designer':
            self.import_fe_designer(fields)
        elif model_name == 'fe_cadastral':
            self.import_fe_cadastral(fields)
        elif model_name == 'fe_land_parcel':
            self.import_fe_land_parcel(fields)
        elif model_name == 'fe_fract_land_parcel':
            self.import_fe_fract_land_parcel(fields)
        elif model_name == 'fe_fract_edil_parcel':
            self.import_fe_fract_edil_parcel(fields)
        elif model_name == 'unit_event':
            self.import_unit_event(fields)
        elif model_name == 'fond_event':
            self.import_fond_event(fields)
        elif model_name == 'rel_creator_creator':
            self.pending_rels.append((model_name, fields))
        elif model_name == 'rel_creator_institution':
            self.pending_rels.append((model_name, fields))
        elif model_name == 'rel_creator_source':
            self.pending_rels.append((model_name, fields))
        elif model_name == 'rel_custodian_source':
            self.pending_rels.append((model_name, fields))
        elif model_name == 'rel_fond_source':
            self.pending_rels.append((model_name, fields))
        elif model_name == 'rel_unit_source':
            self.pending_rels.append((model_name, fields))
        elif model_name == 'rel_fond_document_form':
            self.pending_rels.append((model_name, fields))
        elif model_name == 'rel_project_fond':
            self.pending_rels.append((model_name, fields))
        elif model_name == 'rel_unit_anagraphic':
            self.pending_rels.append((model_name, fields))
        # Altri modelli (project, document_form, etc.) possono essere aggiunti se necessario

    def import_fond(self, fields):
        clean_fields = self.clean_fields(Fond, fields, ['parent_id', 'group_id', 'db_source'])
        fond = Fond.objects.create(group=self.group_id, **clean_fields)
        return fond

    def import_unit(self, fields):
        clean_fields = self.clean_fields(Unit, fields, ['parent_id', 'fond_id', 'root_fond_id', 'classification_id'])
        unit = Unit.objects.create(**clean_fields)
        return unit

    def import_creator(self, fields):
        clean_fields = self.clean_fields(Creator, fields, ['group_id'])
        return Creator.objects.create(group=self.group_id, **clean_fields)

    def import_custodian(self, fields):
        clean_fields = self.clean_fields(Custodian, fields, ['group_id'])
        return Custodian.objects.create(group=self.group_id, **clean_fields)

    def import_heading(self, fields):
        clean_fields = self.clean_fields(Heading, fields, ['group_id'])
        return Heading.objects.create(group=self.group_id, **clean_fields)

    def import_digital_object(self, fields, z):
        clean_fields = self.clean_fields(DigitalObject, fields, ['group_id', 'content_type_id', 'object_id', 'attachable', 'attachable_id'])
        access_token = fields.get('access_token')
        file_name = fields.get('asset_file_name')
        
        legacy_unit_id = fields.get('legacy_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        
        if new_unit_id:
            dobj = DigitalObject.objects.create(
                group=self.group_id,
                content_type=ContentType.objects.get_for_model(Unit),
                object_id=new_unit_id,
                **clean_fields
            )
            
            # Archimista AEF stores them in public/digital_objects/<token>/<filename>
            zip_internal_path = f"public/digital_objects/{access_token}/{file_name}"
            if zip_internal_path in z.namelist():
                # Store in media/digital_objects
                storage_path = os.path.join('digital_objects', str(access_token), file_name)
                full_path = os.path.join(settings.MEDIA_ROOT, storage_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with z.open(zip_internal_path) as source, open(full_path, 'wb') as target:
                    shutil.copyfileobj(source, target)

    def import_sc2(self, fields):
        legacy_unit_id = fields.get('legacy_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(Sc2, fields, ['unit_id', 'id'])
            # Mappiamo obj_type (SC2/SC3) su card_type nel nostro modello
            if 'obj_type' in fields:
                clean_fields['card_type'] = fields['obj_type']
            else:
                # Se obj_type non è presente, controlliamo sc2_tsk dall'unità
                # sc2_tsk='F' indica Fotografia (SC3), altri valori sono disegni (SC2)
                unit = Unit.objects.get(id=new_unit_id)
                if unit.sc2_tsk == 'F':
                    clean_fields['card_type'] = 'SC3'
                else:
                    clean_fields['card_type'] = 'SC2'
            Sc2.objects.update_or_create(unit_id=new_unit_id, defaults=clean_fields)

    def import_iccd(self, fields):
        legacy_unit_id = fields.get('legacy_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(IccdDescription, fields, ['unit_id', 'id'])
            IccdDescription.objects.update_or_create(unit_id=new_unit_id, defaults=clean_fields)

    # Metodi di importazione per modelli estesi
    def import_fond_name(self, fields):
        legacy_fond_id = fields.get('fond_id')
        new_fond_id = self.id_map.get((Fond, str(legacy_fond_id)))
        if new_fond_id:
            clean_fields = self.clean_fields(FondName, fields, ['fond_id', 'id'])
            FondName.objects.create(fond_id=new_fond_id, **clean_fields)

    def import_fond_identifier(self, fields):
        legacy_fond_id = fields.get('fond_id')
        new_fond_id = self.id_map.get((Fond, str(legacy_fond_id)))
        if new_fond_id:
            clean_fields = self.clean_fields(FondIdentifier, fields, ['fond_id', 'id'])
            FondIdentifier.objects.create(fond_id=new_fond_id, **clean_fields)

    def import_fond_lang(self, fields):
        legacy_fond_id = fields.get('fond_id')
        new_fond_id = self.id_map.get((Fond, str(legacy_fond_id)))
        if new_fond_id:
            clean_fields = self.clean_fields(FondLang, fields, ['fond_id', 'id'])
            FondLang.objects.create(fond_id=new_fond_id, **clean_fields)

    def import_fond_owner(self, fields):
        legacy_fond_id = fields.get('fond_id')
        new_fond_id = self.id_map.get((Fond, str(legacy_fond_id)))
        if new_fond_id:
            clean_fields = self.clean_fields(FondOwner, fields, ['fond_id', 'id'])
            FondOwner.objects.create(fond_id=new_fond_id, **clean_fields)

    def import_fond_url(self, fields):
        legacy_fond_id = fields.get('fond_id')
        new_fond_id = self.id_map.get((Fond, str(legacy_fond_id)))
        if new_fond_id:
            clean_fields = self.clean_fields(FondUrl, fields, ['fond_id', 'id'])
            FondUrl.objects.create(fond_id=new_fond_id, **clean_fields)

    def import_fond_editor(self, fields):
        legacy_fond_id = fields.get('fond_id')
        new_fond_id = self.id_map.get((Fond, str(legacy_fond_id)))
        if new_fond_id:
            clean_fields = self.clean_fields(FondEditor, fields, ['fond_id', 'id'])
            FondEditor.objects.create(fond_id=new_fond_id, **clean_fields)

    def import_unit_identifier(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(UnitIdentifier, fields, ['unit_id', 'id'])
            UnitIdentifier.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_unit_other_reference_number(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(UnitOtherReferenceNumber, fields, ['unit_id', 'id'])
            UnitOtherReferenceNumber.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_unit_lang(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(UnitLang, fields, ['unit_id', 'id'])
            UnitLang.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_unit_damage(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(UnitDamage, fields, ['unit_id', 'id'])
            UnitDamage.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_unit_url(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(UnitUrl, fields, ['unit_id', 'id'])
            UnitUrl.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_unit_editor(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(UnitEditor, fields, ['unit_id', 'id'])
            UnitEditor.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_creator_name(self, fields):
        legacy_creator_id = fields.get('creator_id')
        new_creator_id = self.id_map.get((Creator, str(legacy_creator_id)))
        if new_creator_id:
            clean_fields = self.clean_fields(CreatorName, fields, ['creator_id', 'id'])
            CreatorName.objects.create(creator_id=new_creator_id, **clean_fields)

    def import_creator_legal_status(self, fields):
        legacy_creator_id = fields.get('creator_id')
        new_creator_id = self.id_map.get((Creator, str(legacy_creator_id)))
        if new_creator_id:
            clean_fields = self.clean_fields(CreatorLegalStatus, fields, ['creator_id', 'id'])
            CreatorLegalStatus.objects.create(creator_id=new_creator_id, **clean_fields)

    def import_creator_url(self, fields):
        legacy_creator_id = fields.get('creator_id')
        new_creator_id = self.id_map.get((Creator, str(legacy_creator_id)))
        if new_creator_id:
            clean_fields = self.clean_fields(CreatorUrl, fields, ['creator_id', 'id'])
            CreatorUrl.objects.create(creator_id=new_creator_id, **clean_fields)

    def import_creator_identifier(self, fields):
        legacy_creator_id = fields.get('creator_id')
        new_creator_id = self.id_map.get((Creator, str(legacy_creator_id)))
        if new_creator_id:
            clean_fields = self.clean_fields(CreatorIdentifier, fields, ['creator_id', 'id'])
            CreatorIdentifier.objects.create(creator_id=new_creator_id, **clean_fields)

    def import_creator_activity(self, fields):
        legacy_creator_id = fields.get('creator_id')
        new_creator_id = self.id_map.get((Creator, str(legacy_creator_id)))
        if new_creator_id:
            clean_fields = self.clean_fields(CreatorActivity, fields, ['creator_id', 'id'])
            CreatorActivity.objects.create(creator_id=new_creator_id, **clean_fields)

    def import_creator_editor(self, fields):
        legacy_creator_id = fields.get('creator_id')
        new_creator_id = self.id_map.get((Creator, str(legacy_creator_id)))
        if new_creator_id:
            clean_fields = self.clean_fields(CreatorEditor, fields, ['creator_id', 'id'])
            CreatorEditor.objects.create(creator_id=new_creator_id, **clean_fields)

    def import_custodian_name(self, fields):
        legacy_custodian_id = fields.get('custodian_id')
        new_custodian_id = self.id_map.get((Custodian, str(legacy_custodian_id)))
        if new_custodian_id:
            clean_fields = self.clean_fields(CustodianName, fields, ['custodian_id', 'id'])
            CustodianName.objects.create(custodian_id=new_custodian_id, **clean_fields)

    def import_custodian_identifier(self, fields):
        legacy_custodian_id = fields.get('custodian_id')
        new_custodian_id = self.id_map.get((Custodian, str(legacy_custodian_id)))
        if new_custodian_id:
            clean_fields = self.clean_fields(CustodianIdentifier, fields, ['custodian_id', 'id'])
            CustodianIdentifier.objects.create(custodian_id=new_custodian_id, **clean_fields)

    def import_custodian_contact(self, fields):
        legacy_custodian_id = fields.get('custodian_id')
        new_custodian_id = self.id_map.get((Custodian, str(legacy_custodian_id)))
        if new_custodian_id:
            clean_fields = self.clean_fields(CustodianContact, fields, ['custodian_id', 'id'])
            CustodianContact.objects.create(custodian_id=new_custodian_id, **clean_fields)

    def import_custodian_building(self, fields):
        legacy_custodian_id = fields.get('custodian_id')
        new_custodian_id = self.id_map.get((Custodian, str(legacy_custodian_id)))
        if new_custodian_id:
            clean_fields = self.clean_fields(CustodianBuilding, fields, ['custodian_id', 'id'])
            CustodianBuilding.objects.create(custodian_id=new_custodian_id, **clean_fields)

    def import_custodian_owner(self, fields):
        legacy_custodian_id = fields.get('custodian_id')
        new_custodian_id = self.id_map.get((Custodian, str(legacy_custodian_id)))
        if new_custodian_id:
            clean_fields = self.clean_fields(CustodianOwner, fields, ['custodian_id', 'id'])
            CustodianOwner.objects.create(custodian_id=new_custodian_id, **clean_fields)

    def import_custodian_url(self, fields):
        legacy_custodian_id = fields.get('custodian_id')
        new_custodian_id = self.id_map.get((Custodian, str(legacy_custodian_id)))
        if new_custodian_id:
            clean_fields = self.clean_fields(CustodianUrl, fields, ['custodian_id', 'id'])
            CustodianUrl.objects.create(custodian_id=new_custodian_id, **clean_fields)

    def import_custodian_editor(self, fields):
        legacy_custodian_id = fields.get('custodian_id')
        new_custodian_id = self.id_map.get((Custodian, str(legacy_custodian_id)))
        if new_custodian_id:
            clean_fields = self.clean_fields(CustodianEditor, fields, ['custodian_id', 'id'])
            CustodianEditor.objects.create(custodian_id=new_custodian_id, **clean_fields)

    def import_sc2_textual_element(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(Sc2TextualElement, fields, ['unit_id', 'id'])
            Sc2TextualElement.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_sc2_visual_element(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(Sc2VisualElement, fields, ['unit_id', 'id'])
            Sc2VisualElement.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_sc2_author(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(Sc2Author, fields, ['unit_id', 'id'])
            Sc2Author.objects.create(unit_id=new_unit_id, **clean_fields)
            # Store mapping for nested Sc2AttributionReason
            self.id_map[(Sc2Author, str(fields.get('legacy_id')))] = Sc2Author.objects.filter(
                unit_id=new_unit_id, autr=clean_fields.get('autr')
            ).first().id if 'autr' in clean_fields else None

    def import_sc2_attribution_reason(self, fields):
        # Export stores unit_id; resolve to the most recent Sc2Author for that unit
        legacy_unit_id = fields.get('unit_id') or fields.get('sc2_author_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            # Find the most recently created Sc2Author for this unit
            last_author = Sc2Author.objects.filter(unit_id=new_unit_id).last()
            if last_author:
                clean_fields = self.clean_fields(Sc2AttributionReason, fields, ['sc2_author_id', 'id', 'unit_id'])
                Sc2AttributionReason.objects.create(sc2_author_id=last_author.id, **clean_fields)

    def import_sc2_commission(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(Sc2Commission, fields, ['unit_id', 'id'])
            Sc2Commission.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_sc2_commission_name(self, fields):
        # Export stores unit_id; resolve to the most recent Sc2Commission for that unit
        legacy_unit_id = fields.get('unit_id') or fields.get('sc2_commission_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            last_commission = Sc2Commission.objects.filter(unit_id=new_unit_id).last()
            if last_commission:
                clean_fields = self.clean_fields(Sc2CommissionName, fields, ['sc2_commission_id', 'id', 'unit_id'])
                Sc2CommissionName.objects.create(sc2_commission_id=last_commission.id, **clean_fields)

    def import_sc2_technique(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(Sc2Technique, fields, ['unit_id', 'id'])
            Sc2Technique.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_sc2_scale(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(Sc2Scale, fields, ['unit_id', 'id'])
            Sc2Scale.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_iccd_subject(self, fields):
        # Export stores iccd_description_id which points to unit_id
        legacy_unit_id = fields.get('iccd_description_id') or fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            # Find the most recently created IccdDescription for this unit
            last_desc = IccdDescription.objects.filter(unit_id=new_unit_id).last()
            if last_desc:
                clean_fields = self.clean_fields(IccdSubject, fields, ['iccd_description_id', 'id', 'unit_id'])
                IccdSubject.objects.create(iccd_description_id=last_desc.id, **clean_fields)

    def import_iccd_damage(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(IccdDamage, fields, ['unit_id', 'id'])
            IccdDamage.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_iccd_tech_spec(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(IccdTechSpec, fields, ['unit_id', 'id'])
            IccdTechSpec.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fsc_code(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FscCode, fields, ['unit_id', 'id'])
            FscCode.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fsc_organization(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FscOrganization, fields, ['unit_id', 'id'])
            FscOrganization.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fsc_nationality(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FscNationality, fields, ['unit_id', 'id'])
            FscNationality.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fsc_open(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FscOpen, fields, ['unit_id', 'id'])
            FscOpen.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fsc_close(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FscClose, fields, ['unit_id', 'id'])
            FscClose.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fe_identification(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FeIdentification, fields, ['unit_id', 'id'])
            FeIdentification.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fe_context(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FeContext, fields, ['unit_id', 'id'])
            FeContext.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fe_opera(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FeOpera, fields, ['unit_id', 'id'])
            FeOpera.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fe_designer(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FeDesigner, fields, ['unit_id', 'id'])
            FeDesigner.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fe_cadastral(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FeCadastral, fields, ['unit_id', 'id'])
            FeCadastral.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fe_land_parcel(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FeLandParcel, fields, ['unit_id', 'id'])
            FeLandParcel.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fe_fract_land_parcel(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FeFractLandParcel, fields, ['unit_id', 'id'])
            FeFractLandParcel.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_fe_fract_edil_parcel(self, fields):
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(FeFractEdilParcel, fields, ['unit_id', 'id'])
            FeFractEdilParcel.objects.create(unit_id=new_unit_id, **clean_fields)

    def import_unit_event(self, fields):
        """Importa estremi cronologici per un'unità."""
        legacy_unit_id = fields.get('unit_id')
        new_unit_id = self.id_map.get((Unit, str(legacy_unit_id)))
        if new_unit_id:
            clean_fields = self.clean_fields(Event, fields, ['unit_id', 'id', 'legacy_id'])
            Event.objects.create(
                content_type=ContentType.objects.get_for_model(Unit),
                object_id=new_unit_id,
                **clean_fields
            )

    def import_fond_event(self, fields):
        """Importa estremi cronologici per un fondo."""
        legacy_fond_id = fields.get('fond_id')
        new_fond_id = self.id_map.get((Fond, str(legacy_fond_id)))
        if new_fond_id:
            clean_fields = self.clean_fields(Event, fields, ['fond_id', 'id', 'legacy_id'])
            Event.objects.create(
                content_type=ContentType.objects.get_for_model(Fond),
                object_id=new_fond_id,
                **clean_fields
            )

    # =========================================================================
    # Additional entity import handlers (for round-trip compatibility)
    # =========================================================================

    def import_editor(self, fields):
        clean_fields = self.clean_fields(Editor, fields, ['id', 'group_id', 'db_source'])
        # Editor uses first_name/last_name, not name/surname
        obj, _ = Editor.objects.get_or_create(
            first_name=fields.get('first_name', ''),
            last_name=fields.get('last_name', ''),
            defaults=clean_fields
        )
        legacy_id = fields.get('legacy_id')
        if legacy_id:
            self.id_map[(Editor, str(legacy_id))] = obj.id

    def import_institution(self, fields):
        clean_fields = self.clean_fields(Institution, fields, ['group_id', 'db_source'])
        obj = Institution.objects.create(group=self.group_id, **clean_fields)
        legacy_id = fields.get('legacy_id')
        if legacy_id:
            self.id_map[(Institution, str(legacy_id))] = obj.id

    def import_institution_editor(self, fields):
        legacy_institution_id = fields.get('institution_id')
        new_institution_id = self.id_map.get((Institution, str(legacy_institution_id)))
        if new_institution_id:
            clean_fields = self.clean_fields(InstitutionEditor, fields, ['institution_id', 'id'])
            InstitutionEditor.objects.create(institution_id=new_institution_id, **clean_fields)

    def import_source(self, fields):
        clean_fields = self.clean_fields(Source, fields, ['group_id', 'db_source'])
        obj = Source.objects.create(group=self.group_id, **clean_fields)
        legacy_id = fields.get('legacy_id')
        if legacy_id:
            self.id_map[(Source, str(legacy_id))] = obj.id

    def import_source_url(self, fields):
        legacy_source_id = fields.get('source_id')
        new_source_id = self.id_map.get((Source, str(legacy_source_id)))
        if new_source_id:
            clean_fields = self.clean_fields(SourceUrl, fields, ['source_id', 'id'])
            SourceUrl.objects.create(source_id=new_source_id, **clean_fields)

    def import_project(self, fields):
        clean_fields = self.clean_fields(Project, fields, ['group_id', 'db_source'])
        obj = Project.objects.create(group=self.group_id, **clean_fields)
        legacy_id = fields.get('legacy_id')
        if legacy_id:
            self.id_map[(Project, str(legacy_id))] = obj.id

    def import_project_url(self, fields):
        legacy_project_id = fields.get('project_id')
        new_project_id = self.id_map.get((Project, str(legacy_project_id)))
        if new_project_id:
            clean_fields = self.clean_fields(ProjectUrl, fields, ['project_id', 'id'])
            ProjectUrl.objects.create(project_id=new_project_id, **clean_fields)

    def import_project_manager(self, fields):
        legacy_project_id = fields.get('project_id')
        new_project_id = self.id_map.get((Project, str(legacy_project_id)))
        if new_project_id:
            clean_fields = self.clean_fields(ProjectManager, fields, ['project_id', 'id'])
            ProjectManager.objects.create(project_id=new_project_id, **clean_fields)

    def import_project_stakeholder(self, fields):
        legacy_project_id = fields.get('project_id')
        new_project_id = self.id_map.get((Project, str(legacy_project_id)))
        if new_project_id:
            clean_fields = self.clean_fields(ProjectStakeholder, fields, ['project_id', 'id'])
            ProjectStakeholder.objects.create(project_id=new_project_id, **clean_fields)

    def import_document_form(self, fields):
        clean_fields = self.clean_fields(DocumentForm, fields, ['group_id', 'db_source'])
        obj = DocumentForm.objects.create(group=self.group_id, **clean_fields)
        legacy_id = fields.get('legacy_id')
        if legacy_id:
            self.id_map[(DocumentForm, str(legacy_id))] = obj.id

    def import_document_form_editor(self, fields):
        legacy_document_form_id = fields.get('document_form_id')
        new_document_form_id = self.id_map.get((DocumentForm, str(legacy_document_form_id)))
        if new_document_form_id:
            clean_fields = self.clean_fields(DocumentFormEditor, fields, ['document_form_id', 'id'])
            DocumentFormEditor.objects.create(document_form_id=new_document_form_id, **clean_fields)

    def import_anagraphic(self, fields):
        clean_fields = self.clean_fields(Anagraphic, fields, ['group_id', 'db_source'])
        obj = Anagraphic.objects.create(group=self.group_id, **clean_fields)
        legacy_id = fields.get('legacy_id')
        if legacy_id:
            self.id_map[(Anagraphic, str(legacy_id))] = obj.id

    def import_lang(self, fields):
        clean_fields = self.clean_fields(Lang, fields, ['group_id', 'db_source'])
        obj = Lang.objects.create(group=self.group_id, **clean_fields)
        legacy_id = fields.get('legacy_id')
        if legacy_id:
            self.id_map[(Lang, str(legacy_id))] = obj.id

    def import_place(self, fields):
        clean_fields = self.clean_fields(Place, fields, ['group_id', 'db_source'])
        obj = Place.objects.create(group=self.group_id, **clean_fields)
        legacy_id = fields.get('legacy_id')
        if legacy_id:
            self.id_map[(Place, str(legacy_id))] = obj.id

    def clean_fields(self, model_class, fields, exclude_list):
        # Also exclude FK fields by their base name (e.g. 'group') if the _id variant is in exclude_list
        fk_base_names = set()
        for f in model_class._meta.get_fields():
            if f.is_relation and f.concrete:
                fk_base_names.add(f.name)

        extended_exclude = set(exclude_list)
        for exc in exclude_list:
            if exc.endswith('_id'):
                base = exc[:-3]
                if base in fk_base_names:
                    extended_exclude.add(base)

        return {k: v for k, v in fields.items() if k not in extended_exclude and hasattr(model_class, k)}

    def process_pending_hierarchy(self):
        for model_class, obj_id, legacy_parent_id in self.pending_hierarchy:
            parent_id = self.id_map.get((model_class, str(legacy_parent_id)))
            if parent_id:
                model_class.objects.filter(id=obj_id).update(parent_id=parent_id)

    def process_pending_unit_fond_links(self):
        for unit_id, legacy_fond_id, legacy_root_fond_id in self.pending_unit_fond_links:
            fond_id = self.id_map.get((Fond, legacy_fond_id))
            root_fond_id = self.id_map.get((Fond, legacy_root_fond_id))
            updates = {}
            if fond_id: updates['fond_id'] = fond_id
            if root_fond_id: updates['root_fond_id'] = root_fond_id
            if updates:
                Unit.objects.filter(id=unit_id).update(**updates)

    def process_pending_relations(self):
        # Iterate through pending_rels to restore hierarchy and M2M
        for model_name, fields in self.pending_rels:
            if model_name == 'rel_creator_fond':
                self.restore_rel(RelCreatorFond, fields, (Creator, 'legacy_creator_id', 'creator'), (Fond, 'legacy_fond_id', 'fond'))
            elif model_name == 'rel_custodian_fond':
                self.restore_rel(RelCustodianFond, fields, (Custodian, 'legacy_custodian_id', 'custodian'), (Fond, 'legacy_fond_id', 'fond'))
            elif model_name == 'rel_unit_heading':
                self.restore_rel(RelUnitHeading, fields, (Unit, 'legacy_unit_id', 'unit'), (Heading, 'legacy_heading_id', 'heading'))
            elif model_name == 'rel_fond_heading':
                self.restore_rel(RelFondHeading, fields, (Fond, 'legacy_fond_id', 'fond'), (Heading, 'legacy_heading_id', 'heading'))
            elif model_name == 'rel_creator_creator':
                self.restore_rel(RelCreatorCreator, fields, (Creator, 'legacy_creator_id', 'creator'), (Creator, 'legacy_related_creator_id', 'related_creator'))
            elif model_name == 'rel_creator_institution':
                self.restore_rel(RelCreatorInstitution, fields, (Creator, 'legacy_creator_id', 'creator'), (Institution, 'legacy_institution_id', 'institution'))
            elif model_name == 'rel_creator_source':
                self.restore_rel(RelCreatorSource, fields, (Creator, 'legacy_creator_id', 'creator'), (Source, 'legacy_source_id', 'source'))
            elif model_name == 'rel_custodian_source':
                self.restore_rel(RelCustodianSource, fields, (Custodian, 'legacy_custodian_id', 'custodian'), (Source, 'legacy_source_id', 'source'))
            elif model_name == 'rel_fond_source':
                self.restore_rel(RelFondSource, fields, (Fond, 'legacy_fond_id', 'fond'), (Source, 'legacy_source_id', 'source'))
            elif model_name == 'rel_unit_source':
                self.restore_rel(RelUnitSource, fields, (Unit, 'legacy_unit_id', 'unit'), (Source, 'legacy_source_id', 'source'))
            elif model_name == 'rel_fond_document_form':
                self.restore_rel(RelFondDocumentForm, fields, (Fond, 'legacy_fond_id', 'fond'), (DocumentForm, 'legacy_document_form_id', 'document_form'))
            elif model_name == 'rel_project_fond':
                self.restore_rel(RelProjectFond, fields, (Project, 'legacy_project_id', 'project'), (Fond, 'legacy_fond_id', 'fond'))
            elif model_name == 'rel_unit_anagraphic':
                self.restore_rel(RelUnitAnagraphic, fields, (Unit, 'legacy_unit_id', 'unit'), (Anagraphic, 'legacy_anagraphic_id', 'anagraphic'))

    def restore_rel(self, rel_model, fields, left_spec, right_spec):
        left_class, left_legacy_key, left_attr = left_spec
        right_class, right_legacy_key, right_attr = right_spec
        
        left_id = self.id_map.get((left_class, str(fields.get(left_legacy_key))))
        right_id = self.id_map.get((right_class, str(fields.get(right_legacy_key))))
        
        if left_id and right_id:
            rel_model.objects.get_or_create(**{
                f"{left_attr}_id": left_id,
                f"{right_attr}_id": right_id
            })
