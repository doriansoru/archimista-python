# Archive Models - Archimista Python/Django
# Questo modulo espone tutti i modelli per mantenere la compatibilità
# con gli import esistenti: from archive.models import X

from archimista_python.archive.models.core import (
    Group,
    Fond,
    CreatorCorporateType,
    Creator,
    CustodianType,
    Custodian,
    Classification,
    Unit,
    Heading,
    DigitalObject,
)

from archimista_python.archive.models.relations import (
    RelCreatorFond,
    RelCustodianFond,
    RelFondHeading,
    RelUnitHeading,
    RelCreatorCreator,
    RelCreatorInstitution,
    RelCreatorSource,
    RelCustodianSource,
    RelFondSource,
    RelUnitSource,
    RelProjectFond,
    RelFondDocumentForm,
    RelUnitAnagraphic,
)

from archimista_python.archive.models.extensions import (
    # Fond extensions
    FondName,
    FondIdentifier,
    FondLang,
    FondOwner,
    FondUrl,
    FondEditor,
    # Unit extensions
    UnitIdentifier,
    UnitOtherReferenceNumber,
    UnitLang,
    UnitDamage,
    UnitUrl,
    UnitEditor,
    # Creator extensions
    CreatorName,
    CreatorLegalStatus,
    CreatorUrl,
    CreatorIdentifier,
    CreatorActivity,
    CreatorEditor,
    # Custodian extensions
    CustodianName,
    CustodianIdentifier,
    CustodianContact,
    CustodianBuilding,
    CustodianOwner,
    CustodianUrl,
    CustodianEditor,
)

from archimista_python.archive.models.sc2 import (
    Sc2,
    Sc2TextualElement,
    Sc2VisualElement,
    Sc2Author,
    Sc2AttributionReason,
    Sc2Commission,
    Sc2CommissionName,
    Sc2Technique,
    Sc2Scale,
)

from archimista_python.archive.models.iccd import (
    IccdAuthor,
    IccdDescription,
    IccdSubject,
    IccdDamage,
    IccdTechSpec,
)

from archimista_python.archive.models.fsc import (
    FscCode,
    FscOrganization,
    FscNationality,
    FscOpen,
    FscClose,
)

from archimista_python.archive.models.fe import (
    FeIdentification,
    FeContext,
    FeOpera,
    FeDesigner,
    FeCadastral,
    FeLandParcel,
    FeFractLandParcel,
    FeFractEdilParcel,
)

from archimista_python.archive.models.vocabulary import (
    Term,
    Vocabulary,
)

from archimista_python.archive.models.system import (
    Institution,
    InstitutionEditor,
    Source,
    SourceType,
    SourceUrl,
    BiogHist,
    Event,
    Project,
    ProjectUrl,
    ProjectManager,
    ProjectStakeholder,
    DocumentForm,
    Anagraphic,
    Place,
    Lang,
    Export,
    Import,
    Editor,
    Activity,
    CreatorAssociationType,
    DocumentFormEditor,
    AnagIdentifier,
    EditorLog,
    UserProfile,
)

# Export all models as a list for easy access
__all__ = [
    # Core
    'Group', 'Fond', 'CreatorCorporateType', 'Creator', 'CustodianType',
    'Custodian', 'Classification', 'Unit', 'Heading', 'DigitalObject',
    # Relations
    'RelCreatorFond', 'RelCustodianFond', 'RelFondHeading', 'RelUnitHeading',
    'RelCreatorCreator', 'RelCreatorInstitution', 'RelCreatorSource',
    'RelCustodianSource', 'RelFondSource', 'RelUnitSource',
    'RelProjectFond', 'RelFondDocumentForm', 'RelUnitAnagraphic',
    # Extensions
    'FondName', 'FondIdentifier', 'FondLang', 'FondOwner', 'FondUrl', 'FondEditor',
    'UnitIdentifier', 'UnitOtherReferenceNumber', 'UnitLang', 'UnitDamage', 'UnitUrl', 'UnitEditor',
    'CreatorName', 'CreatorLegalStatus', 'CreatorUrl', 'CreatorIdentifier', 'CreatorActivity', 'CreatorEditor',
    'CustodianName', 'CustodianIdentifier', 'CustodianContact', 'CustodianBuilding',
    'CustodianOwner', 'CustodianUrl', 'CustodianEditor',
    # SC2
    'Sc2', 'Sc2TextualElement', 'Sc2VisualElement', 'Sc2Author',
    'Sc2AttributionReason',
    'Sc2Commission', 'Sc2CommissionName', 'Sc2Technique', 'Sc2Scale',
    # ICCD
    'IccdAuthor', 'IccdDescription', 'IccdSubject', 'IccdDamage', 'IccdTechSpec',
    # FSC
    'FscCode', 'FscOrganization', 'FscNationality', 'FscOpen', 'FscClose',
    # FE
    'FeIdentification', 'FeContext', 'FeOpera', 'FeDesigner',
    'FeCadastral', 'FeLandParcel', 'FeFractLandParcel', 'FeFractEdilParcel',
    # Vocabulary
    'Term', 'Vocabulary',
    # System
    'Institution', 'InstitutionEditor', 'Source', 'SourceType', 'SourceUrl', 'BiogHist', 'Event', 'Project',
    'ProjectUrl', 'ProjectManager', 'ProjectStakeholder',
    'DocumentForm',
    'Anagraphic', 'Place', 'Lang', 'Export', 'Import', 'Editor',
    'Activity', 'CreatorAssociationType', 'DocumentFormEditor', 'AnagIdentifier',
    'EditorLog', 'UserProfile',
]
