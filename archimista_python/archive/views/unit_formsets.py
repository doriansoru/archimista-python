"""
Handler per i formset delle viste Unit.

Questo modulo estrae la logica di gestione dei 37 form/formset
dalle viste UnitCreateView/UnitUpdateView, riducendole a semplici orchestratori.

Inventario: 4 form singoli + 33 formset = 37 oggetti form
"""

from django.db import transaction
from django.db import models
from django.contrib.contenttypes.models import ContentType
from datetime import date

from archimista_python.archive.models import Unit, Event, Term
from archimista_python.archive.forms import (
    UnitForm,
    UnitIdentifierFormSet, UnitOtherReferenceNumberFormSet, UnitLangFormSet,
    UnitDamageFormSet, UnitUrlFormSet, UnitEditorFormSet,
    RelUnitHeadingFormSet, RelUnitSourceFormSet, RelUnitAnagraphicFormSet,
    FeFractLandParcelFormSet, FeFractEdilParcelFormSet,
    Sc2Form, Sc2CommissionForm, Sc2AuthorFormSet, Sc2TextualElementFormSet,
    Sc2VisualElementFormSet, Sc2TechniqueFormSet, Sc2ScaleFormSet, Sc2CommissionFormSet,
    Sc2AttributionReasonForm, Sc2CommissionNameForm,
    IccdDescriptionForm, IccdTechSpecForm, IccdSubjectFormSet, IccdDamageFormSet,
    FscCodeFormSet, FscOrganizationFormSet, FscNationalityFormSet, FscOpenFormSet, FscCloseFormSet,
    FeIdentificationFormSet, FeContextFormSet, FeOperaFormSet, FeDesignerFormSet,
    FeCadastralFormSet, FeLandParcelFormSet,
    EventFormSet,
)


# =============================================================================
# Helper generico per salvataggio formset
# =============================================================================

def save_formset_group(formsets, instance=None, link_field='unit', request_post=None):
    """Salva un gruppo di formset inline con validazione e controllo dati vuoti.

    Pattern estratto da UnitCreateView/UnitUpdateView:
    - fs.instance = instance
    - fs.is_valid() → fs.save(commit=False)
    - Per ogni form: salva solo se c'è almeno un campo compilato
    - Se DELETE=True e ha pk, elimina

    Args:
        formsets: lista di formset da salvare
        instance: istanza del modello padre (Unit, IccdDescription, ecc.)
        link_field: nome del campo FK per collegare all'istanza ('unit', 'iccd', ecc.)
        request_post: se fornito, inizializza i formset con POST data
    """
    for fs in formsets:
        if instance is not None:
            fs.instance = instance
        if fs.is_valid():
            fs.save(commit=False)
            for form in fs.forms:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    # Salva solo se c'è almeno un campo compilato
                    if any(v for k, v in form.cleaned_data.items() if k not in ('id', 'DELETE') and v):
                        if instance is not None:
                            setattr(form.instance, link_field, instance)
                        form.save()
                elif form.cleaned_data and form.cleaned_data.get('DELETE', False) and form.instance.pk:
                    form.instance.delete()


# =============================================================================
# Handler: Estensioni Unit (6 formset + 3 relazioni)
# =============================================================================

class UnitExtensionsHandler:
    """Gestisce i formset delle estensioni e relazioni dell'unità.

    Formset gestiti (9):
    - UnitIdentifier, UnitOtherReferenceNumber, UnitLang
    - UnitDamage, UnitUrl, UnitEditor
    - RelUnitHeading, RelUnitSource, RelUnitAnagraphic
    - FeFractLandParcel, FeFractEdilParcel (FE frazionamenti)
    """

    EXTENSION_FORMSETS = [
        'unit_identifier_formset',
        'unit_other_reference_number_formset',
        'unit_lang_formset',
        'unit_damage_formset',
        'unit_url_formset',
        'unit_editor_formset',
        'rel_unit_heading_formset',
        'rel_unit_source_formset',
        'rel_unit_anagraphic_formset',
        'fe_fract_land_formset',
        'fe_fract_edil_formset',
    ]

    @staticmethod
    def build_formsets(post_data=None, instance=None):
        """Crea tutti i formset delle estensioni."""
        kwargs = {'instance': instance} if instance else {}
        if post_data:
            kwargs['data'] = post_data

        return {
            'unit_identifier_formset': UnitIdentifierFormSet(**kwargs),
            'unit_other_reference_number_formset': UnitOtherReferenceNumberFormSet(**kwargs),
            'unit_lang_formset': UnitLangFormSet(**kwargs),
            'unit_damage_formset': UnitDamageFormSet(**kwargs),
            'unit_url_formset': UnitUrlFormSet(**kwargs),
            'unit_editor_formset': UnitEditorFormSet(**kwargs),
            'rel_unit_heading_formset': RelUnitHeadingFormSet(
                prefix='rel_unit_heading', **({'data': post_data} if post_data else {})
            ),
            'rel_unit_source_formset': RelUnitSourceFormSet(
                prefix='rel_unit_source', **({'data': post_data} if post_data else {})
            ),
            'rel_unit_anagraphic_formset': RelUnitAnagraphicFormSet(
                prefix='rel_unit_anagraphic', **({'data': post_data} if post_data else {})
            ),
            'fe_fract_land_formset': FeFractLandParcelFormSet(**kwargs),
            'fe_fract_edil_formset': FeFractEdilParcelFormSet(**kwargs),
        }

    @staticmethod
    def save_all(unit, formsets_dict):
        """Salva tutti i formset delle estensioni."""
        formsets = [formsets_dict[name] for name in UnitExtensionsHandler.EXTENSION_FORMSETS]
        save_formset_group(formsets, instance=unit, link_field='unit')


# =============================================================================
# Handler: Estremi Cronologici (Event)
# =============================================================================

class EventHandler:
    """Gestisce il formset degli eventi (estremi cronologici).

    Logica speciale: costruzione manuale delle date da year/month/day.
    """

    PREFIX = 'unit_events'

    @staticmethod
    def build_formset(post_data=None, instance=None):
        kwargs = {'prefix': EventHandler.PREFIX}
        if instance:
            kwargs['instance'] = instance
        if post_data:
            kwargs['data'] = post_data
        return EventFormSet(**kwargs)

    @staticmethod
    def save_all(unit, formset):
        """Salva gli eventi collegati all'unità."""
        formset.is_valid()
        for form in formset.forms:
            if not form.cleaned_data:
                continue
            if form.cleaned_data.get('DELETE', False):
                if form.instance.pk:
                    form.instance.delete()
                continue

            # Verifica se c'è almeno un dato compilato
            has_data = any(form.cleaned_data.get(f) for f in [
                'start_date_from_year', 'start_date_from_month', 'start_date_from_day',
                'end_date_from_year', 'end_date_from_month', 'end_date_from_day',
                'start_date_spec', 'end_date_spec', 'start_date_place', 'end_date_place', 'note'
            ])
            if not has_data and not form.instance.pk:
                continue

            # Costruisci o aggiorna l'evento
            if form.instance.pk:
                event = form.instance
            else:
                event = Event(
                    content_type=ContentType.objects.get_for_model(Unit),
                    object_id=unit.pk
                )

            # Aggiorna i campi dal cleaned_data
            for field_name in ['preferred', 'is_valid', 'event_type',
                               'start_date_spec', 'start_date_valid', 'start_date_format', 'start_date_place',
                               'end_date_spec', 'end_date_valid', 'end_date_format', 'end_date_place', 'note']:
                if field_name in form.cleaned_data:
                    setattr(event, field_name, form.cleaned_data[field_name])

            # Costruisci le date
            EventHandler._build_date(form, event, 'start_date_from', 'start_date_to', 'start_date_display',
                                     'start_date_from_year', 'start_date_from_month', 'start_date_from_day')

            if not form.cleaned_data.get('equal_bounds'):
                EventHandler._build_date(form, event, 'end_date_from', 'end_date_to', 'end_date_display',
                                         'end_date_from_year', 'end_date_from_month', 'end_date_from_day')
            else:
                event.end_date_from = event.start_date_from
                event.end_date_to = event.start_date_to
                event.end_date_display = event.start_date_display

            if event.start_date_from:
                event.order_date = event.start_date_from.isoformat()

            event.save()

    @staticmethod
    def _build_date(form, event, from_attr, to_attr, display_attr, year_field, month_field, day_field):
        """Costruisce una data da year/month/day."""
        year = form.cleaned_data.get(year_field, '').strip() if form.cleaned_data.get(year_field) else ''
        month = form.cleaned_data.get(month_field, '')
        day = form.cleaned_data.get(day_field, '')
        if year:
            try:
                d = date(int(year), int(month or 1), int(day or 1))
                setattr(event, from_attr, d)
                setattr(event, to_attr, date(int(year), int(month or 12), int(day or 31)))
                setattr(event, display_attr, d.strftime('%Y-%m-%d'))
            except (ValueError, TypeError):
                pass


# =============================================================================
# Handler: Scheda SC2 (1 form + 6 formset + 2 nested)
# =============================================================================

class SC2Handler:
    """Gestisce la scheda SC2 (disegni tecnici e fotografie).

    Form/Formset gestiti (9):
    - Sc2Form (singolo)
    - Sc2Author, Sc2TextualElement, Sc2VisualElement
    - Sc2Technique, Sc2Scale, Sc2Commission
    - Sc2AttributionReason (nested), Sc2CommissionName (nested)
    """

    FORMSET_NAMES = [
        'sc2_author_formset', 'sc2_textual_formset', 'sc2_visual_formset',
        'sc2_technique_formset', 'sc2_scale_formset', 'sc2_commission_formset',
    ]

    @staticmethod
    def build_form(post_data=None, instance=None):
        kwargs = {'instance': instance} if instance else {}
        if post_data:
            kwargs['data'] = post_data
        return Sc2Form(**kwargs)

    @staticmethod
    def build_formsets(post_data=None, instance=None):
        kwargs = {'instance': instance} if instance else {}
        if post_data:
            kwargs['data'] = post_data
        return {
            'sc2_author_formset': Sc2AuthorFormSet(**kwargs),
            'sc2_textual_formset': Sc2TextualElementFormSet(**kwargs),
            'sc2_visual_formset': Sc2VisualElementFormSet(**kwargs),
            'sc2_technique_formset': Sc2TechniqueFormSet(**kwargs),
            'sc2_scale_formset': Sc2ScaleFormSet(**kwargs),
            'sc2_commission_formset': Sc2CommissionFormSet(**kwargs),
        }

    @staticmethod
    def build_nested_forms(post_data=None):
        kwargs = {'data': post_data} if post_data else {}
        return {
            'sc2_attribution_reason_form': Sc2AttributionReasonForm(**kwargs),
            'sc2_commission_name_form': Sc2CommissionNameForm(**kwargs),
        }

    @staticmethod
    def save_main(sc2_form, unit, form_data):
        """Salva il form principale SC2 e sincronizza card_type."""
        if sc2_form.is_valid():
            sc2 = sc2_form.save(commit=False)
            sc2.unit = unit
            sc2_tsk_value = form_data.get('sc2_tsk', '')
            if sc2_tsk_value:
                sc2.card_type = sc2_tsk_value
            sc2.save()
            return sc2
        return None

    @staticmethod
    def save_formsets(unit, formsets_dict):
        """Salva tutti i formset SC2."""
        formsets = [formsets_dict[name] for name in SC2Handler.FORMSET_NAMES]
        save_formset_group(formsets, instance=unit, link_field='unit')


# =============================================================================
# Handler: Scheda ICCD (2 form + 2 formset)
# =============================================================================

class ICCDHandler:
    """Gestisce la scheda ICCD (beni culturali).

    Form/Formset gestiti (4):
    - IccdDescriptionForm, IccdTechSpecForm
    - IccdSubjectFormSet, IccdDamageFormSet
    """

    @staticmethod
    def build_forms(post_data=None, iccd_instance=None, iccd_tech_instance=None):
        kwargs = {'instance': iccd_instance} if iccd_instance else {}
        if post_data:
            kwargs['data'] = post_data
        iccd_form = IccdDescriptionForm(**kwargs)

        kwargs_tech = {'instance': iccd_tech_instance} if iccd_tech_instance else {}
        if post_data:
            kwargs_tech['data'] = post_data
        iccd_tech_form = IccdTechSpecForm(**kwargs_tech)

        return iccd_form, iccd_tech_form

    @staticmethod
    def build_formsets(post_data=None, iccd_instance=None, unit_instance=None):
        kwargs_subj = {'instance': iccd_instance} if iccd_instance else {}
        if post_data:
            kwargs_subj['data'] = post_data

        kwargs_dmg = {'instance': unit_instance} if unit_instance else {}
        if post_data:
            kwargs_dmg['data'] = post_data

        return {
            'iccd_subject_formset': IccdSubjectFormSet(**kwargs_subj),
            'iccd_damage_formset': IccdDamageFormSet(**kwargs_dmg),
        }

    @staticmethod
    def save_main(iccd_form, iccd_tech_form, unit):
        """Salva i form ICCD principali."""
        iccd_instance = None
        if iccd_form.is_valid():
            iccd = iccd_form.save(commit=False)
            iccd.unit = unit
            iccd.save()
            iccd_instance = iccd

        if iccd_tech_form.is_valid():
            iccd_tech = iccd_tech_form.save(commit=False)
            iccd_tech.unit = unit
            iccd_tech.save()

        return iccd_instance

    @staticmethod
    def save_subjects(iccd_instance, formset_data=None):
        """Salva il formset dei soggetti ICCD."""
        if iccd_instance:
            kwargs = {'instance': iccd_instance}
            if formset_data:
                kwargs['data'] = formset_data
            subject_formset = IccdSubjectFormSet(**kwargs)
            if subject_formset.is_valid():
                subject_formset.save()

    @staticmethod
    def save_damages(unit, formset_data=None):
        """Salva il formset dei danni ICCD."""
        kwargs = {'instance': unit}
        if formset_data:
            kwargs['data'] = formset_data
        damage_formset = IccdDamageFormSet(**kwargs)
        damage_formset.is_valid()
        damage_formset.save()


# =============================================================================
# Handler: FSC (5 formset)
# =============================================================================

class FSCHandler:
    """Gestisce i formset FSC (fascicoli sanitari edilizia).

    Formset gestiti (5):
    - FscCode, FscOrganization, FscNationality, FscOpen, FscClose
    """

    FORMSET_NAMES = [
        'fsc_code_formset', 'fsc_org_formset', 'fsc_nationality_formset',
        'fsc_open_formset', 'fsc_close_formset',
    ]

    @staticmethod
    def build_formsets(post_data=None, instance=None):
        kwargs = {'instance': instance} if instance else {}
        if post_data:
            kwargs['data'] = post_data
        return {
            'fsc_code_formset': FscCodeFormSet(**kwargs),
            'fsc_org_formset': FscOrganizationFormSet(**kwargs),
            'fsc_nationality_formset': FscNationalityFormSet(**kwargs),
            'fsc_open_formset': FscOpenFormSet(**kwargs),
            'fsc_close_formset': FscCloseFormSet(**kwargs),
        }

    @staticmethod
    def save_all(unit, formsets_dict):
        """Salva tutti i formset FSC."""
        formsets = [formsets_dict[name] for name in FSCHandler.FORMSET_NAMES]
        save_formset_group(formsets, instance=unit, link_field='unit')


# =============================================================================
# Handler: FE (8 formset)
# =============================================================================

class FEHandler:
    """Gestisce i formset FE (fabbricati edilizia).

    Formset gestiti (8):
    - FeIdentification, FeContext, FeOpera, FeDesigner
    - FeCadastral, FeLandParcel, FeFractLandParcel, FeFractEdilParcel
    """

    FORMSET_NAMES = [
        'fe_id_formset', 'fe_context_formset', 'fe_opera_formset',
        'fe_designer_formset', 'fe_cadastral_formset', 'fe_land_formset',
    ]

    @staticmethod
    def build_formsets(post_data=None, instance=None):
        kwargs = {'instance': instance} if instance else {}
        if post_data:
            kwargs['data'] = post_data
        return {
            'fe_id_formset': FeIdentificationFormSet(**kwargs),
            'fe_context_formset': FeContextFormSet(**kwargs),
            'fe_opera_formset': FeOperaFormSet(**kwargs),
            'fe_designer_formset': FeDesignerFormSet(**kwargs),
            'fe_cadastral_formset': FeCadastralFormSet(**kwargs),
            'fe_land_formset': FeLandParcelFormSet(**kwargs),
        }

    @staticmethod
    def save_main(unit, formsets_dict):
        """Salva i formset FE principali (esclusi frazionamenti)."""
        formsets = [formsets_dict[name] for name in FEHandler.FORMSET_NAMES]
        save_formset_group(formsets, instance=unit, link_field='unit')


# =============================================================================
# Builder del context per il template
# =============================================================================

def get_vocabulary_terms():
    """Recupera i termini dai vocabolari usati nel form unità."""
    return {
        'unit_damages_code': Term.objects.filter(vocabulary__name='unit_damages.code').order_by('position'),
        'units_medium': Term.objects.filter(vocabulary__name='units.medium').order_by('position'),
    }


def get_editing_type_terms():
    """Recupera i termini per il tipo di compilazione."""
    return Term.objects.filter(vocabulary__name='editors.editing_type').order_by('position')


def build_unit_context(unit=None, unit_form=None,
                     extensions=None, event_formset=None,
                     sc2_form=None, sc2_formsets=None, sc2_nested=None,
                     iccd_form=None, iccd_tech_form=None, iccd_formsets=None,
                     fsc_formsets=None, fe_formsets=None):
    """Costruisce il context dictionary per il template unit_form.html.

    Questo sostituisce i ~50 righe di context duplicati in GET e POST error.

    Args:
        unit: istanza Unit (None per create view)
        unit_form: istanza UnitForm
        extensions: dict di formset estensioni (da UnitExtensionsHandler.build_formsets)
        event_formset: istanza EventFormSet
        sc2_form: istanza Sc2Form
        sc2_formsets: dict di formset SC2
        sc2_nested: dict di form nested SC2
        iccd_form: istanza IccdDescriptionForm
        iccd_tech_form: istanza IccdTechSpecForm
        iccd_formsets: dict di formset ICCD
        fsc_formsets: dict di formset FSC
        fe_formsets: dict di formset FE

    Returns:
        dict pronto per render()
    """
    context = {
        'unit_form': unit_form,
        'form': unit_form,
        'terms': get_vocabulary_terms(),
        'editing_type_terms': get_editing_type_terms(),
        'unit': unit,
    }

    # Estensioni Unit
    if extensions:
        context.update(extensions)

    # Eventi
    if event_formset:
        context['event_formset'] = event_formset

    # SC2
    if sc2_form:
        context['sc2_form'] = sc2_form
    if sc2_formsets:
        context.update(sc2_formsets)
    if sc2_nested:
        context.update(sc2_nested)

    # ICCD
    if iccd_form:
        context['iccd_form'] = iccd_form
    if iccd_tech_form:
        context['iccd_tech_form'] = iccd_tech_form
    if iccd_formsets:
        context.update(iccd_formsets)

    # FSC
    if fsc_formsets:
        context.update(fsc_formsets)

    # FE
    if fe_formsets:
        context.update(fe_formsets)

    return context
