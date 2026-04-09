from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline
from .models import (
    Group, Fond, CreatorCorporateType, Creator, CustodianType, Custodian, Unit,
    Heading, DigitalObject, RelCreatorFond, RelCustodianFond, RelFondHeading, RelUnitHeading,
    Classification, BiogHist, Event,
    Sc2, IccdAuthor, IccdDescription,
    # Fond extensions
    FondName, FondIdentifier, FondLang, FondOwner, FondUrl, FondEditor,
    # Unit extensions
    UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage, UnitUrl, UnitEditor,
    # Creator extensions
    CreatorName, CreatorLegalStatus, CreatorUrl, CreatorIdentifier, CreatorActivity, CreatorEditor,
    # Custodian extensions
    CustodianName, CustodianIdentifier, CustodianContact, CustodianBuilding, CustodianOwner, CustodianUrl, CustodianEditor,
    # SC2 extensions
    Sc2TextualElement, Sc2VisualElement, Sc2Author, Sc2Commission, Sc2CommissionName, Sc2Technique, Sc2Scale,
    # ICCD extensions
    IccdSubject, IccdDamage, IccdTechSpec,
    # FSC extensions
    FscCode, FscOrganization, FscNationality, FscOpen, FscClose,
    # FE extensions
    FeIdentification, FeContext, FeOpera, FeDesigner, FeCadastral, FeLandParcel, FeFractLandParcel, FeFractEdilParcel,
    # Relational models
    RelCreatorCreator, RelCreatorInstitution, RelCreatorSource, RelCustodianSource, RelFondSource, RelUnitSource, RelFondDocumentForm, RelProjectFond, RelUnitAnagraphic,
    # Additional models
    Project, DocumentForm, Anagraphic, Place, Lang, Term, Vocabulary, Export, Import, Editor, Activity, DocumentFormEditor, AnagIdentifier, CreatorAssociationType,
    # Source models
    Source, SourceType, SourceUrl,
)

class DigitalObjectInline(GenericStackedInline):
    model = DigitalObject
    extra = 1
    fields = ('title', 'asset_file_name', 'description')

class BiogHistInline(GenericStackedInline):
    model = BiogHist
    extra = 1
    fields = ('body', 'abstract', 'note')

class EventInline(GenericStackedInline):
    model = Event
    extra = 1
    fields = ('event_type', 'start_date_display', 'end_date_display', 'preferred', 'is_valid')

class Sc2Inline(admin.StackedInline):
    model = Sc2
    can_delete = False
    verbose_name_plural = 'Scheda Disegno Tecnico (Sc2)'

class IccdDescriptionInline(admin.StackedInline):
    model = IccdDescription
    can_delete = False
    verbose_name_plural = 'Scheda Bene Culturale (Iccd)'
    filter_horizontal = ('authors',)

# Inlines per Fond
class FondNameInline(admin.TabularInline):
    model = FondName
    extra = 1

class FondIdentifierInline(admin.TabularInline):
    model = FondIdentifier
    extra = 1

class FondLangInline(admin.TabularInline):
    model = FondLang
    extra = 1

class FondOwnerInline(admin.TabularInline):
    model = FondOwner
    extra = 1

class FondUrlInline(admin.TabularInline):
    model = FondUrl
    extra = 1

class FondEditorInline(admin.TabularInline):
    model = FondEditor
    extra = 1

# Inlines per Creator
class CreatorNameInline(admin.TabularInline):
    model = CreatorName
    extra = 1

class CreatorLegalStatusInline(admin.TabularInline):
    model = CreatorLegalStatus
    extra = 1

class CreatorUrlInline(admin.TabularInline):
    model = CreatorUrl
    extra = 1

class CreatorIdentifierInline(admin.TabularInline):
    model = CreatorIdentifier
    extra = 1

class CreatorActivityInline(admin.TabularInline):
    model = CreatorActivity
    extra = 1

class CreatorEditorInline(admin.TabularInline):
    model = CreatorEditor
    extra = 1

# Inlines per Custodian
class CustodianNameInline(admin.TabularInline):
    model = CustodianName
    extra = 1

class CustodianIdentifierInline(admin.TabularInline):
    model = CustodianIdentifier
    extra = 1

class CustodianContactInline(admin.TabularInline):
    model = CustodianContact
    extra = 1

class CustodianBuildingInline(admin.TabularInline):
    model = CustodianBuilding
    extra = 1

class CustodianOwnerInline(admin.TabularInline):
    model = CustodianOwner
    extra = 1

class CustodianUrlInline(admin.TabularInline):
    model = CustodianUrl
    extra = 1

class CustodianEditorInline(admin.TabularInline):
    model = CustodianEditor
    extra = 1

# Inlines per Unit
class UnitIdentifierInline(admin.TabularInline):
    model = UnitIdentifier
    extra = 1

class UnitOtherReferenceNumberInline(admin.TabularInline):
    model = UnitOtherReferenceNumber
    extra = 1

class UnitLangInline(admin.TabularInline):
    model = UnitLang
    extra = 1

class UnitDamageInline(admin.TabularInline):
    model = UnitDamage
    extra = 1

class UnitUrlInline(admin.TabularInline):
    model = UnitUrl
    extra = 1

class UnitEditorInline(admin.TabularInline):
    model = UnitEditor
    extra = 1

# SC2 inlines
class Sc2TextualElementInline(admin.TabularInline):
    model = Sc2TextualElement
    extra = 1

class Sc2VisualElementInline(admin.TabularInline):
    model = Sc2VisualElement
    extra = 1

class Sc2AuthorInline(admin.TabularInline):
    model = Sc2Author
    extra = 1

class Sc2CommissionInline(admin.TabularInline):
    model = Sc2Commission
    extra = 1

class Sc2TechniqueInline(admin.TabularInline):
    model = Sc2Technique
    extra = 1

class Sc2ScaleInline(admin.TabularInline):
    model = Sc2Scale
    extra = 1

# ICCD inlines
class IccdSubjectInline(admin.TabularInline):
    model = IccdSubject
    extra = 1

class IccdDamageInline(admin.TabularInline):
    model = IccdDamage
    extra = 1

class IccdTechSpecInline(admin.StackedInline):
    model = IccdTechSpec
    can_delete = False
    verbose_name_plural = 'Specifiche Tecniche (Iccd)'

# FE inlines
class FeIdentificationInline(admin.TabularInline):
    model = FeIdentification
    extra = 1

class FeContextInline(admin.TabularInline):
    model = FeContext
    extra = 1

class FeOperaInline(admin.TabularInline):
    model = FeOpera
    extra = 1

class FeDesignerInline(admin.TabularInline):
    model = FeDesigner
    extra = 1

class FeCadastralInline(admin.TabularInline):
    model = FeCadastral
    extra = 1

class FeLandParcelInline(admin.TabularInline):
    model = FeLandParcel
    extra = 1

# FSC inlines
class FscCodeInline(admin.TabularInline):
    model = FscCode
    extra = 1

class FscOrganizationInline(admin.TabularInline):
    model = FscOrganization
    extra = 1

class FscNationalityInline(admin.TabularInline):
    model = FscNationality
    extra = 1

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'created_at')
    search_fields = ('name', 'short_name')

@admin.register(Fond)
class FondAdmin(admin.ModelAdmin):
    list_display = ('name', 'fond_type', 'sequence_number', 'units_count', 'published')
    list_filter = ('published', 'fond_type')
    search_fields = ('name', 'description')
    inlines = [DigitalObjectInline, BiogHistInline, EventInline, FondNameInline, FondIdentifierInline, FondLangInline, FondOwnerInline, FondUrlInline, FondEditorInline]

@admin.register(CreatorCorporateType)
class CreatorCorporateTypeAdmin(admin.ModelAdmin):
    list_display = ('corporate_type',)

@admin.register(Creator)
class CreatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator_type', 'legal_status', 'published')
    list_filter = ('published', 'creator_type')
    inlines = [DigitalObjectInline, BiogHistInline, EventInline, CreatorNameInline, CreatorLegalStatusInline, CreatorIdentifierInline, CreatorActivityInline, CreatorUrlInline, CreatorEditorInline]

@admin.register(CustodianType)
class CustodianTypeAdmin(admin.ModelAdmin):
    list_display = ('custodian_type',)

@admin.register(Custodian)
class CustodianAdmin(admin.ModelAdmin):
    list_display = ('id', 'custodian_type', 'published')
    list_filter = ('published',)
    inlines = [DigitalObjectInline, BiogHistInline, EventInline, CustodianNameInline, CustodianIdentifierInline, CustodianContactInline, CustodianBuildingInline, CustodianOwnerInline, CustodianUrlInline, CustodianEditorInline]

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'fond', 'unit_type', 'reference_number', 'published')
    list_filter = ('published', 'unit_type', 'physical_type')
    search_fields = ('title', 'reference_number', 'content')
    inlines = [DigitalObjectInline, EventInline, Sc2Inline, IccdDescriptionInline, IccdTechSpecInline, UnitIdentifierInline, UnitOtherReferenceNumberInline, UnitLangInline, UnitDamageInline, UnitUrlInline, UnitEditorInline, Sc2TextualElementInline, Sc2VisualElementInline, Sc2AuthorInline, Sc2CommissionInline, Sc2TechniqueInline, Sc2ScaleInline, IccdDamageInline, FeIdentificationInline, FeContextInline, FeOperaInline, FeDesignerInline, FeCadastralInline, FeLandParcelInline, FscCodeInline, FscOrganizationInline, FscNationalityInline]

@admin.register(IccdAuthor)
class IccdAuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')

@admin.register(Heading)
class HeadingAdmin(admin.ModelAdmin):
    list_display = ('name', 'heading_type', 'dates')
    search_fields = ('name', 'qualifier')

@admin.register(DigitalObject)
class DigitalObjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'asset_file_name', 'content_type', 'object_id', 'published')
    list_filter = ('published', 'content_type')

@admin.register(RelCreatorFond)
class RelCreatorFondAdmin(admin.ModelAdmin):
    list_display = ('creator', 'fond')

@admin.register(RelCustodianFond)
class RelCustodianFondAdmin(admin.ModelAdmin):
    list_display = ('custodian', 'fond')

@admin.register(RelFondHeading)
class RelFondHeadingAdmin(admin.ModelAdmin):
    list_display = ('fond', 'heading')

@admin.register(RelUnitHeading)
class RelUnitHeadingAdmin(admin.ModelAdmin):
    list_display = ('unit', 'heading')

@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent')
    search_fields = ('code', 'name')

@admin.register(BiogHist)
class BiogHistAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'start_date_display', 'end_date_display', 'content_type', 'object_id', 'preferred')


# Registrazioni per nuovi modelli
@admin.register(FondName)
class FondNameAdmin(admin.ModelAdmin):
    list_display = ('fond', 'name', 'qualifier', 'preferred')
    search_fields = ('name',)

@admin.register(FondIdentifier)
class FondIdentifierAdmin(admin.ModelAdmin):
    list_display = ('fond', 'identifier', 'identifier_source')

@admin.register(FondLang)
class FondLangAdmin(admin.ModelAdmin):
    list_display = ('fond', 'code')

@admin.register(FondOwner)
class FondOwnerAdmin(admin.ModelAdmin):
    list_display = ('fond', 'owner')

@admin.register(FondUrl)
class FondUrlAdmin(admin.ModelAdmin):
    list_display = ('fond', 'url', 'position')

@admin.register(FondEditor)
class FondEditorAdmin(admin.ModelAdmin):
    list_display = ('fond', 'name', 'edited_at')

@admin.register(UnitIdentifier)
class UnitIdentifierAdmin(admin.ModelAdmin):
    list_display = ('unit', 'identifier')

@admin.register(UnitOtherReferenceNumber)
class UnitOtherReferenceNumberAdmin(admin.ModelAdmin):
    list_display = ('unit', 'other_reference_number')

@admin.register(UnitLang)
class UnitLangAdmin(admin.ModelAdmin):
    list_display = ('unit', 'code')

@admin.register(UnitDamage)
class UnitDamageAdmin(admin.ModelAdmin):
    list_display = ('unit', 'code')

@admin.register(UnitUrl)
class UnitUrlAdmin(admin.ModelAdmin):
    list_display = ('unit', 'url')

@admin.register(UnitEditor)
class UnitEditorAdmin(admin.ModelAdmin):
    list_display = ('unit', 'name', 'edited_at')

@admin.register(CreatorName)
class CreatorNameAdmin(admin.ModelAdmin):
    list_display = ('creator', 'name', 'qualifier', 'preferred')
    search_fields = ('name',)

@admin.register(CreatorLegalStatus)
class CreatorLegalStatusAdmin(admin.ModelAdmin):
    list_display = ('creator', 'legal_status')

@admin.register(CreatorUrl)
class CreatorUrlAdmin(admin.ModelAdmin):
    list_display = ('creator', 'url')

@admin.register(CreatorIdentifier)
class CreatorIdentifierAdmin(admin.ModelAdmin):
    list_display = ('creator', 'identifier')

@admin.register(CreatorActivity)
class CreatorActivityAdmin(admin.ModelAdmin):
    list_display = ('creator', 'activity')

@admin.register(CreatorEditor)
class CreatorEditorAdmin(admin.ModelAdmin):
    list_display = ('creator', 'name', 'edited_at')

@admin.register(CustodianName)
class CustodianNameAdmin(admin.ModelAdmin):
    list_display = ('custodian', 'name', 'qualifier', 'preferred')

@admin.register(CustodianIdentifier)
class CustodianIdentifierAdmin(admin.ModelAdmin):
    list_display = ('custodian', 'identifier')

@admin.register(CustodianContact)
class CustodianContactAdmin(admin.ModelAdmin):
    list_display = ('custodian', 'contact', 'contact_type')

@admin.register(CustodianBuilding)
class CustodianBuildingAdmin(admin.ModelAdmin):
    list_display = ('custodian', 'name', 'city', 'country')

@admin.register(CustodianOwner)
class CustodianOwnerAdmin(admin.ModelAdmin):
    list_display = ('custodian', 'owner')

@admin.register(CustodianUrl)
class CustodianUrlAdmin(admin.ModelAdmin):
    list_display = ('custodian', 'url')

@admin.register(CustodianEditor)
class CustodianEditorAdmin(admin.ModelAdmin):
    list_display = ('custodian', 'name', 'edited_at')

@admin.register(Sc2TextualElement)
class Sc2TextualElementAdmin(admin.ModelAdmin):
    list_display = ('unit', 'isri')

@admin.register(Sc2VisualElement)
class Sc2VisualElementAdmin(admin.ModelAdmin):
    list_display = ('unit', 'stmd')

@admin.register(Sc2Author)
class Sc2AuthorAdmin(admin.ModelAdmin):
    list_display = ('unit', 'autn', 'autr')

@admin.register(Sc2Commission)
class Sc2CommissionAdmin(admin.ModelAdmin):
    list_display = ('unit', 'cmmc')

@admin.register(Sc2CommissionName)
class Sc2CommissionNameAdmin(admin.ModelAdmin):
    list_display = ('sc2_commission', 'cmmn')

@admin.register(Sc2Technique)
class Sc2TechniqueAdmin(admin.ModelAdmin):
    list_display = ('unit', 'mtct')

@admin.register(Sc2Scale)
class Sc2ScaleAdmin(admin.ModelAdmin):
    list_display = ('unit', 'sca')

@admin.register(IccdSubject)
class IccdSubjectAdmin(admin.ModelAdmin):
    list_display = ('iccd_description', 'subject')

@admin.register(IccdDamage)
class IccdDamageAdmin(admin.ModelAdmin):
    list_display = ('unit', 'code')

@admin.register(IccdTechSpec)
class IccdTechSpecAdmin(admin.ModelAdmin):
    list_display = ('unit', 'mtcm', 'mtct')

@admin.register(FscCode)
class FscCodeAdmin(admin.ModelAdmin):
    list_display = ('unit', 'code')

@admin.register(FscOrganization)
class FscOrganizationAdmin(admin.ModelAdmin):
    list_display = ('unit', 'organization')

@admin.register(FscNationality)
class FscNationalityAdmin(admin.ModelAdmin):
    list_display = ('unit', 'nationality')

@admin.register(FscOpen)
class FscOpenAdmin(admin.ModelAdmin):
    list_display = ('unit', 'open')

@admin.register(FscClose)
class FscCloseAdmin(admin.ModelAdmin):
    list_display = ('unit', 'close')

@admin.register(FeIdentification)
class FeIdentificationAdmin(admin.ModelAdmin):
    list_display = ('unit', 'code', 'file_year')

@admin.register(FeContext)
class FeContextAdmin(admin.ModelAdmin):
    list_display = ('unit', 'number', 'license_year')

@admin.register(FeOpera)
class FeOperaAdmin(admin.ModelAdmin):
    list_display = ('unit', 'building_name', 'is_present')

@admin.register(FeDesigner)
class FeDesignerAdmin(admin.ModelAdmin):
    list_display = ('unit', 'designer_name')

@admin.register(FeCadastral)
class FeCadastralAdmin(admin.ModelAdmin):
    list_display = ('unit', 'cadastral_municipality')

@admin.register(FeLandParcel)
class FeLandParcelAdmin(admin.ModelAdmin):
    list_display = ('unit', 'land_parcel_number')

@admin.register(FeFractLandParcel)
class FeFractLandParcelAdmin(admin.ModelAdmin):
    list_display = ('unit', 'fract_land_parcel_number')

@admin.register(FeFractEdilParcel)
class FeFractEdilParcelAdmin(admin.ModelAdmin):
    list_display = ('unit', 'fract_edil_parcel_number')

@admin.register(RelCreatorCreator)
class RelCreatorCreatorAdmin(admin.ModelAdmin):
    list_display = ('creator', 'related_creator')

@admin.register(RelCreatorInstitution)
class RelCreatorInstitutionAdmin(admin.ModelAdmin):
    list_display = ('creator', 'institution')

@admin.register(RelCreatorSource)
class RelCreatorSourceAdmin(admin.ModelAdmin):
    list_display = ('creator', 'source')

@admin.register(RelCustodianSource)
class RelCustodianSourceAdmin(admin.ModelAdmin):
    list_display = ('custodian', 'source')

@admin.register(RelFondSource)
class RelFondSourceAdmin(admin.ModelAdmin):
    list_display = ('fond', 'source')

@admin.register(RelUnitSource)
class RelUnitSourceAdmin(admin.ModelAdmin):
    list_display = ('unit', 'source')

@admin.register(RelFondDocumentForm)
class RelFondDocumentFormAdmin(admin.ModelAdmin):
    list_display = ('fond', 'document_form')

@admin.register(RelProjectFond)
class RelProjectFondAdmin(admin.ModelAdmin):
    list_display = ('project', 'fond')

@admin.register(RelUnitAnagraphic)
class RelUnitAnagraphicAdmin(admin.ModelAdmin):
    list_display = ('unit', 'anagraphic')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'published')
    list_filter = ('status', 'published')

@admin.register(DocumentForm)
class DocumentFormAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    list_filter = ('status',)

@admin.register(Anagraphic)
class AnagraphicAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name', 'anagraphic_type')
    search_fields = ('surname', 'name')


@admin.register(SourceType)
class SourceTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'source_type', 'parent_code', 'position')
    list_filter = ('parent_code',)


class SourceUrlInline(admin.TabularInline):
    model = SourceUrl
    extra = 1


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'author', 'title', 'source_type_code')
    search_fields = ('short_title', 'title', 'author')
    inlines = [SourceUrlInline]


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'province', 'country')
    search_fields = ('name',)

@admin.register(Lang)
class LangAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'term_type')
    search_fields = ('term',)

@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Export)
class ExportAdmin(admin.ModelAdmin):
    list_display = ('export_type', 'file_name', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(Import)
class ImportAdmin(admin.ModelAdmin):
    list_display = ('importable', 'file_name', 'status', 'deletable')
    list_filter = ('status', 'deletable')

@admin.register(Editor)
class EditorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_it', 'activity_en', 'identifier')
    search_fields = ('activity_it', 'activity_en')

@admin.register(CreatorAssociationType)
class CreatorAssociationTypeAdmin(admin.ModelAdmin):
    list_display = ('association_type',)

@admin.register(DocumentFormEditor)
class DocumentFormEditorAdmin(admin.ModelAdmin):
    list_display = ('document_form', 'name', 'edited_at')

@admin.register(AnagIdentifier)
class AnagIdentifierAdmin(admin.ModelAdmin):
    list_display = ('anagraphic', 'identifier', 'qualifier')
