# Archive Forms - Archimista Python/Django
# Questo modulo espone tutti i form per mantenere la compatibilitÃ 
# con gli import esistenti: from archive.forms import X

from archimista_python.archive.forms.fond import (
    FondForm,
    FondNameForm, FondIdentifierForm, FondLangForm, FondOwnerForm, FondUrlForm, FondEditorForm,
    RelFondHeadingForm, RelFondSourceForm, RelFondDocumentFormForm,
    FondNameFormSet, FondIdentifierFormSet, FondLangFormSet, FondOwnerFormSet,
    FondUrlFormSet, FondEditorFormSet,
    RelFondHeadingFormSet, RelFondSourceFormSet, RelFondDocumentFormFormSet,
)

from archimista_python.archive.forms.event import (
    EventForm, EventFormSet,
)

from archimista_python.archive.forms.unit import (
    UnitForm,
    UnitIdentifierForm, UnitOtherReferenceNumberForm, UnitLangForm,
    UnitDamageForm, UnitUrlForm, UnitEditorForm,
    RelUnitHeadingForm, RelUnitSourceForm, RelUnitAnagraphicForm,
    UnitIdentifierFormSet, UnitOtherReferenceNumberFormSet, UnitLangFormSet,
    UnitDamageFormSet, UnitUrlFormSet, UnitEditorFormSet,
    RelUnitHeadingFormSet, RelUnitSourceFormSet, RelUnitAnagraphicFormSet,
)

from archimista_python.archive.forms.sc2 import (
    Sc2Form,
    Sc2TextualElementForm, Sc2VisualElementForm, Sc2AuthorForm,
    Sc2AttributionReasonForm,
    Sc2CommissionForm, Sc2CommissionNameForm, Sc2TechniqueForm, Sc2ScaleForm,
    Sc2AuthorFormSet, Sc2TextualElementFormSet, Sc2VisualElementFormSet,
    Sc2TechniqueFormSet, Sc2ScaleFormSet, Sc2CommissionFormSet,
)

from archimista_python.archive.forms.iccd import (
    IccdDescriptionForm, IccdTechSpecForm, IccdSubjectForm, IccdDamageForm,
    IccdSubjectFormSet, IccdDamageFormSet,
)

from archimista_python.archive.forms.fsc import (
    FscCodeForm, FscOrganizationForm, FscNationalityForm, FscOpenForm, FscCloseForm,
    FscCodeFormSet, FscOrganizationFormSet, FscNationalityFormSet,
    FscOpenFormSet, FscCloseFormSet,
)

from archimista_python.archive.forms.fe import (
    FeIdentificationForm, FeContextForm, FeOperaForm, FeDesignerForm,
    FeCadastralForm, FeLandParcelForm, FeFractLandParcelForm, FeFractEdilParcelForm,
    FeIdentificationFormSet, FeContextFormSet, FeOperaFormSet,
    FeDesignerFormSet, FeCadastralFormSet, FeLandParcelFormSet,
    FeFractLandParcelFormSet, FeFractEdilParcelFormSet,
)

from archimista_python.archive.forms.creator import (
    CreatorForm, CreatorPreferredNameForm, CreatorOtherNameForm,
    CreatorLegalStatusForm, CreatorUrlForm, CreatorIdentifierForm,
    CreatorActivityForm, CreatorEditorForm,
    RelCreatorCreatorForm, RelCreatorInstitutionForm, RelCreatorSourceForm, RelCreatorFondForm,
    CreatorLegalStatusFormSet,
    CreatorOtherNameFormSet, CreatorUrlFormSet,
    CreatorIdentifierFormSet, CreatorActivityFormSet, CreatorEditorFormSet,
    RelCreatorCreatorFormSet, RelCreatorInstitutionFormSet, RelCreatorSourceFormSet,
    RelCreatorFondFormSet,
)

from archimista_python.archive.forms.custodian import (
    CustodianForm, CustodianPreferredNameForm,
    CustodianNameForm, CustodianIdentifierForm, CustodianContactForm,
    CustodianBuildingForm, CustodianOwnerForm, CustodianUrlForm, CustodianEditorForm,
    RelCustodianSourceForm, RelCustodianFondForm,
    CustodianNameFormSet, CustodianIdentifierFormSet, CustodianContactFormSet,
    CustodianBuildingFormSet, CustodianOwnerFormSet, CustodianUrlFormSet,
    CustodianEditorFormSet, RelCustodianSourceFormSet, RelCustodianFondFormSet,
)

from archimista_python.archive.forms.source import (
    SourceForm, SourceUrlForm,
    SourceUrlFormSet,
)

from archimista_python.archive.forms.institution import (
    InstitutionForm, InstitutionEditorForm,
    InstitutionEditorFormSet,
)

from archimista_python.archive.forms.heading import (
    HeadingForm,
)

from archimista_python.archive.forms.anagraphic import (
    AnagraphicForm, AnagIdentifierForm, AnagIdentifierFormSet,
)

from archimista_python.archive.forms.document_form import (
    DocumentFormForm, DocumentFormEditorForm,
    DocumentFormEditorFormSet,
)

from archimista_python.archive.forms.classification import (
    ClassificationForm,
)

from archimista_python.archive.forms.editor import (
    EditorForm,
)

from archimista_python.archive.forms.digital_object import (
    DigitalObjectForm,
)
