"""
Constants for AEF Exporter.

All exclusion lists, table definitions, and model name mappings.
Separated from the main exporter to keep it focused on orchestration.
"""

from archimista_python.archive.models import (
    Fond, Unit, Creator, Custodian, Heading, DigitalObject,
    Project, Institution, InstitutionEditor, Source, SourceUrl, Editor, DocumentForm, DocumentFormEditor, Anagraphic,
    # Fond extensions
    FondName, FondIdentifier, FondLang, FondOwner, FondUrl, FondEditor,
    # Unit extensions
    UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage, UnitUrl, UnitEditor,
    # Creator extensions
    CreatorName, CreatorLegalStatus, CreatorUrl, CreatorIdentifier, CreatorActivity, CreatorEditor,
    # Custodian extensions
    CustodianName, CustodianIdentifier, CustodianContact, CustodianBuilding, CustodianOwner, CustodianUrl, CustodianEditor,
    # SC2
    Sc2, Sc2TextualElement, Sc2VisualElement, Sc2Author, Sc2AttributionReason,
    Sc2Commission, Sc2CommissionName, Sc2Technique, Sc2Scale,
    # ICCD
    IccdDescription, IccdSubject, IccdDamage, IccdTechSpec,
    # FSC
    FscCode, FscOrganization, FscNationality, FscOpen, FscClose,
    # FE
    FeIdentification, FeContext, FeOpera, FeDesigner, FeCadastral, FeLandParcel, FeFractLandParcel, FeFractEdilParcel,
    # Relations
    RelCreatorFond, RelCustodianFond, RelFondHeading, RelUnitHeading,
    RelCreatorCreator, RelCreatorInstitution, RelCreatorSource,
    RelCustodianSource, RelFondSource, RelUnitSource,
    RelFondDocumentForm, RelProjectFond, RelUnitAnagraphic,
    # System
    Event,
)

# ─── Exclusion lists (match Ruby :except) ─────────────────────────────
FOND_EXCLUDE = [
    'id', 'ancestry', 'ancestry_depth', 'group', 'db_source', 'created_by',
    'updated_by', 'created_at', 'updated_at',
    'fond_type_term', 'access_condition_term', 'use_condition_term',
    'preservation_term', 'description_type_term', 'parent',
]
UNIT_EXCLUDE = [
    'id', 'ancestry', 'db_source', 'created_by', 'updated_by', 'created_at',
    'updated_at', 'unit_type_term', 'access_condition_term', 'use_condition_term',
    'preservation_term', 'physical_type_term', 'medium_term',
    'parent', 'classification',
]
ENTITY_EXCLUDE = [
    'id', 'group_id', 'db_source', 'created_by', 'updated_by', 'created_at',
    'updated_at', 'creator_type_term', 'custodian_type', 'legal_status_term',
]
EXTENSION_EXCLUDE = ['id', 'db_source', 'created_at', 'updated_at']
RELATION_EXCLUDE = ['id', 'db_source', 'created_at', 'updated_at']

# ─── Extension tables per entity (mirrors Ruby tables hash) ────────────
FOND_TABLES = [
    (FondName, 'fond_id'), (FondIdentifier, 'fond_id'), (FondLang, 'fond_id'),
    (FondOwner, 'fond_id'), (FondUrl, 'fond_id'), (FondEditor, 'fond_id'),
]

CREATOR_TABLES = [
    (CreatorName, 'creator_id'), (CreatorLegalStatus, 'creator_id'),
    (CreatorUrl, 'creator_id'), (CreatorIdentifier, 'creator_id'),
    (CreatorActivity, 'creator_id'), (CreatorEditor, 'creator_id'),
]

CUSTODIAN_TABLES = [
    (CustodianName, 'custodian_id'), (CustodianIdentifier, 'custodian_id'),
    (CustodianContact, 'custodian_id'), (CustodianBuilding, 'custodian_id'),
    (CustodianOwner, 'custodian_id'), (CustodianUrl, 'custodian_id'),
    (CustodianEditor, 'custodian_id'),
]

PROJECT_TABLES = []  # No direct extension tables
INSTITUTION_TABLES = [(InstitutionEditor, 'institution_id')]
SOURCE_TABLES = [(SourceUrl, 'source_id')]
DOCUMENT_FORM_TABLES = [(DocumentFormEditor, 'document_form_id')]

# ─── Model name mapping (Ruby snake_case name -> Django model) ─────────
MODEL_NAME_MAP = {
    'fond': Fond, 'unit': Unit, 'creator': Creator, 'custodian': Custodian,
    'heading': Heading, 'digital_object': DigitalObject,
    'project': Project, 'institution': Institution, 'source': Source,
    'editor': Editor, 'document_form': DocumentForm, 'anagraphic': Anagraphic,
    # Relations
    'rel_creator_fond': RelCreatorFond, 'rel_custodian_fond': RelCustodianFond,
    'rel_fond_heading': RelFondHeading, 'rel_unit_heading': RelUnitHeading,
    'rel_creator_creator': RelCreatorCreator,
    'rel_creator_institution': RelCreatorInstitution,
    'rel_creator_source': RelCreatorSource,
    'rel_custodian_source': RelCustodianSource,
    'rel_fond_source': RelFondSource, 'rel_unit_source': RelUnitSource,
    'rel_fond_document_form': RelFondDocumentForm,
    'rel_project_fond': RelProjectFond, 'rel_unit_anagraphic': RelUnitAnagraphic,
    # Extensions
    'fond_name': FondName, 'fond_identifier': FondIdentifier,
    'fond_lang': FondLang, 'fond_owner': FondOwner,
    'fond_url': FondUrl, 'fond_editor': FondEditor,
    'unit_identifier': UnitIdentifier,
    'unit_other_reference_number': UnitOtherReferenceNumber,
    'unit_lang': UnitLang, 'unit_damage': UnitDamage,
    'unit_url': UnitUrl, 'unit_editor': UnitEditor,
    'creator_name': CreatorName, 'creator_legal_status': CreatorLegalStatus,
    'creator_url': CreatorUrl, 'creator_identifier': CreatorIdentifier,
    'creator_activity': CreatorActivity, 'creator_editor': CreatorEditor,
    'custodian_name': CustodianName,
    'custodian_identifier': CustodianIdentifier,
    'custodian_contact': CustodianContact,
    'custodian_building': CustodianBuilding,
    'custodian_owner': CustodianOwner, 'custodian_url': CustodianUrl,
    'custodian_editor': CustodianEditor,
    'sc2': Sc2, 'sc2_textual_element': Sc2TextualElement,
    'sc2_visual_element': Sc2VisualElement, 'sc2_author': Sc2Author,
    'sc2_attribution_reason': Sc2AttributionReason,
    'sc2_commission': Sc2Commission,
    'sc2_commission_name': Sc2CommissionName,
    'sc2_technique': Sc2Technique, 'sc2_scale': Sc2Scale,
    'iccd_description': IccdDescription, 'iccd_subject': IccdSubject,
    'iccd_damage': IccdDamage, 'iccd_tech_spec': IccdTechSpec,
    'fsc_code': FscCode, 'fsc_organization': FscOrganization,
    'fsc_nationality': FscNationality, 'fsc_open': FscOpen,
    'fsc_close': FscClose,
    'fe_identification': FeIdentification, 'fe_context': FeContext,
    'fe_opera': FeOpera, 'fe_designer': FeDesigner,
    'fe_cadastral': FeCadastral, 'fe_land_parcel': FeLandParcel,
    'fe_fract_land_parcel': FeFractLandParcel,
    'fe_fract_edil_parcel': FeFractEdilParcel,
    'unit_event': Event, 'fond_event': Event,
    # Django strips underscores from model_name, need explicit mapping
    'documentform': DocumentForm, 'digitalobject': DigitalObject,
    'projecturl': 'project_url', 'projectmanager': 'project_manager',
    'projectstakeholder': 'project_stakeholder',
    'institutioneditor': 'institution_editor',
    'sourceurl': 'source_url',
    'documentformeditor': 'document_form_editor',
}

APP_VERSION = 300  # matches Ruby APP_VERSION
