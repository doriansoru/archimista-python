"""Test: import di tutti i moduli (models, forms, views, widgets, utils)."""
from tests import test, section


def run():
    section("1. Import di tutti i moduli")

    def _import_models():
        from archimista_python.archive.models import (
            Group, Fond, Unit, Creator, Custodian, Heading, DigitalObject,
            Classification, BiogHist, Event, Institution, Source,
            FondName, FondIdentifier, FondLang, FondOwner, FondUrl, FondEditor,
            UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage, UnitUrl, UnitEditor,
            CreatorName, CreatorLegalStatus, CreatorUrl, CreatorIdentifier, CreatorActivity, CreatorEditor,
            CustodianName, CustodianIdentifier, CustodianContact, CustodianBuilding, CustodianOwner, CustodianUrl, CustodianEditor,
            Sc2, Sc2TextualElement, Sc2VisualElement, Sc2Author, Sc2Commission, Sc2CommissionName, Sc2Technique, Sc2Scale,
            IccdDescription, IccdTechSpec, IccdSubject, IccdDamage, IccdAuthor,
            FscCode, FscOrganization, FscNationality, FscOpen, FscClose,
            FeIdentification, FeContext, FeOpera, FeDesigner, FeCadastral, FeLandParcel, FeFractLandParcel, FeFractEdilParcel,
            RelCreatorFond, RelCustodianFond, RelFondHeading, RelUnitHeading,
            RelCreatorCreator, RelCreatorInstitution, RelCreatorSource,
            RelCustodianSource, RelFondSource, RelUnitSource, RelFondDocumentForm, RelProjectFond, RelUnitAnagraphic,
            Project, DocumentForm, Anagraphic, Place, Lang, Term, Vocabulary,
            Export, Import, Editor, Activity, DocumentFormEditor, AnagIdentifier,
            CreatorAssociationType, CreatorCorporateType, CustodianType,
            SourceType, SourceUrl, InstitutionEditor, EditorLog, UserProfile,
        )
    test("Import tutti i modelli", _import_models)

    def _import_forms():
        from archimista_python.archive.forms import (
            FondForm, UnitForm, CreatorForm, CustodianForm,
            FondNameFormSet, FondIdentifierFormSet, FondLangFormSet, FondOwnerFormSet, FondUrlFormSet, FondEditorFormSet,
            UnitIdentifierFormSet, UnitOtherReferenceNumberFormSet, UnitLangFormSet, UnitDamageFormSet, UnitUrlFormSet, UnitEditorFormSet,
            CreatorOtherNameFormSet, CreatorLegalStatusFormSet, CreatorUrlFormSet, CreatorIdentifierFormSet, CreatorActivityFormSet, CreatorEditorFormSet,
            CustodianNameFormSet, CustodianIdentifierFormSet, CustodianContactFormSet, CustodianBuildingFormSet, CustodianOwnerFormSet, CustodianUrlFormSet, CustodianEditorFormSet,
        )
    test("Import tutti i form", _import_forms)

    def _import_views():
        from archimista_python.archive.views import (
            FondListView, FondDetailView, FondCreateView, FondUpdateView, FondDeleteView,
            UnitListView, UnitCreateView, UnitUpdateView, UnitDetailView, UnitDeleteView,
            CreatorListView, CreatorDetailView, CreatorCreateView, CreatorUpdateView, CreatorDeleteView,
            CustodianListView, CustodianDetailView, CustodianCreateView, CustodianUpdateView, CustodianDeleteView,
            tree_data, tree_children,
        )
    test("Import tutte le viste", _import_views)

    def _import_widgets():
        from archimista_python.archive.widgets import (
            FondSelect2Widget, CreatorSelect2Widget, CustodianSelect2Widget,
            SourceSelect2Widget, InstitutionSelect2Widget, HeadingSelect2Widget,
            AnagraphicSelect2Widget, DocumentFormSelect2Widget,
            UnitSelect2Widget, ClassificationSelect2Widget, LangSelect2Widget,
        )
    test("Import tutti i widget Select2", _import_widgets)

    def _import_utils():
        from archimista_python.archive import import_utils
        from archimista_python.archive import aef_exporter
        from archimista_python.archive import report_support
        from archimista_python.archive import rtf_writer
        from archimista_python.archive import rtf_builder
    test("Import utility (import, export, report)", _import_utils)
