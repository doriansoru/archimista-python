"""
Porting di lib/report_support.rb — supporto per la generazione di report PDF/RTF.
Gestisce la definizione dei campi disponibili per ogni entità, la generazione HTML
(per PDF tramite WeasyPrint) e RTF (tramite RtfWriter).
"""

import re
from django.utils.html import escape
from django.utils.safestring import mark_safe


# ──────────────────────────────────────────────────────────────────────────────
# Costanti
# ──────────────────────────────────────────────────────────────────────────────

HTML_USE_UNORDERED_LIST_TAG = True
RTF_LIST_ITEM_TAG = "- "

ENTITY_NAME_SEPARATOR = "-"
REPORT_ATTRIBUTES_CONTROL_NAME_SUFFIX = f"{ENTITY_NAME_SEPARATOR}report_attributes[]"
REPORT_DONT_USE_CAPTIONS_CONTROL_NAME_SUFFIX = f"{ENTITY_NAME_SEPARATOR}cfg_dont_use_captions"


# ──────────────────────────────────────────────────────────────────────────────
# AttributeInfo
# ──────────────────────────────────────────────────────────────────────────────

class AttributeInfo:
    """Informazioni su un singolo attributo disponibile per il report."""

    def __init__(self, name, group_tag=None, name_caption=None, group_caption=None,
                 name_caption_list_note=None, is_value_translation=False,
                 is_default=False, is_multi_instance=False, callback=None):
        self.name = name
        self.group_tag = group_tag
        self.name_caption = name_caption
        self.group_caption = group_caption
        self.name_caption_list_note = name_caption_list_note
        self.is_value_translation = is_value_translation
        self.is_default = is_default
        self.is_multi_instance = is_multi_instance
        self.callback = callback

    def composed_caption(self):
        wrk_name_caption = self.name_caption or ""
        if self.name_caption_list_note:
            wrk_name_caption += self.name_caption_list_note
        if self.group_tag is None:
            return wrk_name_caption
        else:
            return f"{self.group_caption}/{wrk_name_caption}"


# ──────────────────────────────────────────────────────────────────────────────
# EntityReportSettings
# ──────────────────────────────────────────────────────────────────────────────

class EntityReportSettings:
    """Impostazioni di report per una singola entità."""

    def __init__(self, entity_name, available_attributes_info, dont_use_fld_captions):
        self.entity_name = entity_name
        self.available_attributes_info = available_attributes_info  # dict name→AttributeInfo
        self.selected_attribute_names = None
        self.dont_use_fld_captions = True

    def attribute_search(self, attr_name):
        return attr_name in self.available_attributes_info

    def has_any_selected_attributes(self):
        return bool(self.selected_attribute_names and len(self.selected_attribute_names) > 0)

    @property
    def default_attribute_names(self):
        return [ai.name for ai in self.available_attributes_info.values() if ai.is_default]

    @property
    def entity_control_names(self):
        return f"{self.entity_name}{REPORT_ATTRIBUTES_CONTROL_NAME_SUFFIX}"

    @property
    def entity_control_names_basename(self):
        return self.entity_control_names[:-3]

    @property
    def attribute_control_id_prefix(self):
        return f"{self.entity_name}{ENTITY_NAME_SEPARATOR}"

    @property
    def dont_use_fld_caption_control_name(self):
        return f"{self.entity_name}{REPORT_DONT_USE_CAPTIONS_CONTROL_NAME_SUFFIX}"


# ──────────────────────────────────────────────────────────────────────────────
# ReportSettings
# ──────────────────────────────────────────────────────────────────────────────

class ReportSettings:
    """Contiene le impostazioni di report per tutte le entità coinvolte."""

    def __init__(self, rtf_rw, report_name, report_caption, action, rtf_stylesheet_codes):
        self.rtf_rw = rtf_rw
        self.report_name = report_name
        self.report_caption = report_caption
        self.action = action
        self.rtf_stylesheet_codes = rtf_stylesheet_codes or {}
        self.entities = []
        self.rtf_stylesheet_code_archimista_label = 0

    def entity_add(self, ers):
        self.entities.append(ers)

    def entity_search_by_name(self, entity_name):
        for ers in self.entities:
            if str(ers.entity_name) == str(entity_name):
                return ers
        return None

    def entity_has_any_selected_attributes(self, entity_name):
        ers = self.entity_search_by_name(entity_name)
        return ers.has_any_selected_attributes() if ers else False

    def report_cookie_name(self):
        return f"{self.report_name}_report_settings"

    def initialize_entities_selected_attribute_names(self, params, cookies):
        cookie_value = None
        cookie_name = self.report_cookie_name()
        if cookies and cookie_name in cookies:
            cookie_value = cookies[cookie_name].split(",") if cookies[cookie_name] else []

        for ers in self.entities:
            selected_attr_names = params.get(ers.entity_control_names_basename)
            if selected_attr_names is None:
                selected_attr_names = ers.default_attribute_names

            dont_use_fld_captions = bool(params.get(ers.dont_use_fld_caption_control_name))

            if cookie_value is not None:
                selected_attr_names = []
                dont_use_fld_captions = False
                attr_prefix = ers.attribute_control_id_prefix
                for attr_name in cookie_value:
                    if attr_name.startswith(attr_prefix):
                        if attr_name == ers.dont_use_fld_caption_control_name:
                            dont_use_fld_captions = True
                        else:
                            attr_basename = attr_name[len(attr_prefix):]
                            if ers.attribute_search(attr_basename):
                                selected_attr_names.append(attr_basename)

            ers.selected_attribute_names = selected_attr_names
            ers.dont_use_fld_captions = dont_use_fld_captions

    def get_attribute_rtf_stylesheet_code(self, stylesheet_codes_key):
        try:
            return self.rtf_stylesheet_codes[stylesheet_codes_key]
        except (KeyError, TypeError):
            return -1  # GCrwStyleCurrent

    @staticmethod
    def make_attribute_rtf_stylesheet_codes_key(entity_name, attr_name):
        if attr_name:
            name_parts = attr_name.split(".")
            if entity_name:
                return f"{entity_name}_{name_parts[0]}"
            return name_parts[0]
        return ""


# ──────────────────────────────────────────────────────────────────────────────
# Helper: traduzione / vocabolari / lingue
# ──────────────────────────────────────────────────────────────────────────────

# Mappatura delle traduzioni i18n (da config/locales/it.yml di Ruby)
_I18N_TRANSLATIONS = {
    # Fond
    "fond_type": "Tipologia",
    "name": "Denominazione",
    "other_names": "Altre denominazioni",
    "date_event": "Estremi cronologici",
    "length": "Lunghezza",
    "fond_extent": "Entità",
    "abstract": "Abstract",
    "fond_description": "Descrizione",
    "history": "Storia archivistica",
    "arrangement_note": "Nota dell'archivista",
    "fond_langs": "Lingua",
    "owners": "Possessori",
    "related_materials": "Materiali correlati",
    "fond_note": "Note",
    "fond_urls": "URL",
    "fond_identifiers": "Identificativi",
    "access_condition": "Condizione di accesso",
    "access_condition_note": "Nota condizione di accesso",
    "use_condition": "Condizione di riproduzione",
    "use_condition_note": "Nota condizione di riproduzione",
    "preservation": "Stato di conservazione",
    "preservation_note": "Nota stato di conservazione",
    "creators": "Soggetto produttore",
    "custodians": "Soggetto conservatore",
    "projects": "Progetto",
    "document_forms": "Forma documentaria",
    "sources_area": "Fonti",
    "fond_editors": "Curatore",
    "units_count": "Numero unità archivistiche",
    # Creator
    "creator_type": "Tipologia",
    "creator_corporate_type": "Tipologia ente",
    "preferred_name": "Denominazione principale",
    "creator_legal_statuses": "Condizione giuridica",
    "residence": "Sede",
    "creator_urls": "URL",
    "creator_identifiers": "Identificativi",
    "creator_history": "Profilo storico / Biografia",
    "creator_note": "Appunti di servizio",
    "creator_activities": "Attività",
    "institutions": "Profilo istituzionale",
    "linked_creators": "Soggetti produttori collegati",
    "creator_editors": "Compilatore",
    # Custodian
    "legal_status": "Condizione giuridica",
    "custodian_macro_type": "Macrotipologia",
    "custodian_history": "Storia",
    "contacts": "Contatti",
    "contact_person": "Referente",
    "custodian_owners": "Ente titolare",
    "custodian_urls": "URL",
    "custodian_identifiers": "Identificativi",
    "holdings": "Patrimonio",
    "collecting_policies": "Politiche di gestione",
    "administrative_structure": "Struttura amministrativa",
    "accessibility": "Accessibilità",
    "services": "Servizi",
    "registered_office": "Sede legale",
    "custodian_other_buildings": "Altre sedi",
    "building_name": "Denominazione",
    "building_type": "Tipologia",
    "building_address": "Indirizzo",
    "city": "Città",
    "postcode": "CAP",
    "country": "Stato",
    "building_description": "Descrizione",
    "fonds": "Fondo",
    "custodian_editors": "Compilatore",
    # Unit
    "unit_type": "Tipologia",
    "title": "Denominazione",
    "content": "Contenuto",
    "unit_extent": "Entità",
    "tmp_reference_number": "Numero riferimento temporaneo",
    "tmp_reference_string": "Stringa riferimento temporanea",
    "folder_number": "Numero fascicolo",
    "file_number": "Numero file",
    "reference_number": "Segnatura",
    "physical_type": "Tipo supporto",
    "medium": "Supporto",
    "physical_description": "Descrizione estrinseca",
    "unit_damages": "Danni",
    "restoration": "Restauro",
    "unit_note": "Note",
    "physical_container": "Contenitore fisico",
    "physical_container_type": "Tipo contenitore",
    "physical_container_title": "Titolo contenitore",
    "physical_container_number": "Numero contenitore",
    "unit_other_reference_numbers": "Altre segnature",
    "unit_langs": "Lingua",
    "unit_urls": "URL",
    "unit_identifiers": "Identificativi",
    "unit_editors": "Compilatore",
    "sc2_tsk": "Scheda speciale",
    "sc2_textual_elements": "Elementi testuali",
    "sc2_visual_elements": "Elementi visivi",
    "sc2_authors": "Autore",
    "sc2_commissions": "Committenza",
    "sc2_techniques": "Tecnica",
    "sc2_scales": "Scala",
    # ICCD fields (legacy, commented out in Ruby but still in code)
    # Project
    "project_type": "Tipologia progetto",
    "display_date": "Datazione",
    "status": "Stato",
    "project_note": "Note",
    "project_description": "Descrizione",
    "project_urls": "URL",
    "project_managers": "Responsabile",
    "project_stakeholders": "Soggetto coinvolto",
    # SC2 specific captions
    "sc2_attribution_reasons": "Motivo dell'attribuzione",
    "sc2_commission_names": "Nome",
}

# SC2 field captions (from report_support.rb :name_caption)
_SC2_CAPTIONS = {
    "sc2.sgti": "Soggetto",
    "sc2.cmmr": "Numero di commessa",
    "sc2.lrc": "Luogo della ripresa",
    "sc2.lrd": "Data della ripresa",
    "sc2.mtce": "Esecuzione",
    "sc2.sdtt": "Tipo di rappresentazione",
    "sc2.sdts": "Rappresentazione tematica",
    "sc2.dpgf": "Numero tavola",
    "sc2.misa": "Altezza",
    "sc2.misl": "Larghezza",
    "sc2.ort": "Orientamento",
}


def _t(key):
    """Traduzione i18n (simulata, da Ruby I18n.translate)."""
    return _I18N_TRANSLATIONS.get(key, key.replace("_", " "))


def _plural_human(entity_name, count):
    """Restituisce il nome plurale dell'entità con conteggio."""
    plurals = {
        "fond": ("Fondo", "Fondi"),
        "unit": ("Unità", "Unità"),
        "creator": ("Soggetto produttore", "Soggetti produttori"),
        "custodian": ("Soggetto conservatore", "Soggetti conservatori"),
        "project": ("Progetto", "Progetti"),
        "source": ("Fonte", "Fonti"),
    }
    singular, plural = plurals.get(entity_name, (entity_name, entity_name))
    return plural if count != 1 else singular


def _vocabulary_remap(is_html, vocabulary_spec, ip_value, is_value_translation):
    """Mappa un valore di vocabolario al termine leggibile."""
    from archimista_python.archive.models import Term
    try:
        rec = Term.objects.filter(vocabulary__name=vocabulary_spec, term_value=ip_value).first()
        if rec:
            op_value = rec.term_key
            if is_value_translation:
                if is_html:
                    op_value = _t(op_value)
                else:
                    op_value = _t(op_value)
            return op_value
    except Exception:
        pass
    return ip_value


def _lang_remap(is_html, lang_code, is_value_translation):
    """Mappa un codice lingua al nome completo."""
    from archimista_python.archive.models import Lang
    try:
        rec = Lang.objects.filter(code=lang_code).first()
        if rec:
            return getattr(rec, f'{_current_locale()}_name', lang_code)
    except Exception:
        pass
    return lang_code


def _current_locale():
    """Restituisce il locale corrente (default: 'it')."""
    return 'it'


def _textilize_with_entities(text):
    """Converte testo semplice in HTML (simula RedCloth/textilize di Ruby)."""
    if not text:
        return ""
    text = escape(text)
    # Bold: *text*
    text = re.sub(r'\*(.+?)\*', r'<strong>\1</strong>', text)
    # Italic: _text_
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    # Line breaks
    text = text.replace('\n', '<br />')
    return text


# ──────────────────────────────────────────────────────────────────────────────
# Available attributes info per entità (porting di fond_available_attributes_info, ecc.)
# ──────────────────────────────────────────────────────────────────────────────

def _make_available_attributes_info(attributes_template):
    """Costruisce il dict available_attributes_info da un template."""
    available = {}
    for attr_info in attributes_template:
        name = attr_info['name']
        name_caption = attr_info.get('name_caption')
        name_caption_list_note = attr_info.get('name_caption_list_note')
        group_tag = attr_info.get('group_tag')
        group_caption = attr_info.get('group_caption')
        name_tag = attr_info.get('name_tag')
        is_value_translation = attr_info.get('is_value_translation', False)
        is_default = attr_info.get('is_default', False)
        is_multi_instance = attr_info.get('is_multi_instance', False)
        callback = attr_info.get('callback')

        if name_caption is None:
            if name_tag is None:
                name_tag = name
            name_caption = _t(name_tag)
        if group_caption is None and group_tag is not None:
            group_caption = _t(group_tag)

        ai = AttributeInfo(
            name=name,
            group_tag=group_tag,
            name_caption=name_caption,
            group_caption=group_caption,
            name_caption_list_note=name_caption_list_note,
            is_value_translation=is_value_translation,
            is_default=is_default,
            is_multi_instance=is_multi_instance,
            callback=callback,
        )
        available[name] = ai
    return available


def fond_available_attributes_info():
    attributes_template = [
        # descrizione
        {'name': 'fond_type', 'is_default': True},
        {'name': 'name'},
        {'name': 'other_names.group', 'name_tag': 'other_names',
         'callback': lambda rs, es, eo, ai: _cb_other_names(rs, es, ai.name_caption, eo.other_names) if hasattr(eo, 'other_names') and eo.other_names else ""},
        {'name': 'events.group', 'name_tag': 'date_event',
         'callback': lambda rs, es, eo, ai: _cb_events(rs, es, eo, ai), 'is_default': True},
        {'name': 'length', 'is_default': True},
        {'name': 'extent', 'name_tag': 'fond_extent', 'is_default': True},
        {'name': 'abstract', 'is_default': True},
        {'name': 'description', 'is_default': True, 'name_tag': 'fond_description'},
        {'name': 'history', 'is_default': True},
        {'name': 'arrangement_note', 'is_default': True},
        # altre informazioni
        {'name': 'fond_langs.code', 'name_tag': 'fond_langs',
         'callback': lambda rs, es, eo, ai: _cb_langs(rs, es, ai.name_caption, eo.fond_langs) if hasattr(eo, 'fond_langs') and eo.fond_langs else ""},
        {'name': 'fond_owners.owner', 'name_tag': 'owners',
         'callback': lambda rs, es, eo, ai: _cb_fond_owners(rs, es, eo, ai) if hasattr(eo, 'fond_owners') and eo.fond_owners else ""},
        {'name': 'related_materials', 'is_default': True},
        {'name': 'note', 'is_default': True, 'name_tag': 'fond_note'},
        {'name': 'fond_urls.group', 'name_tag': 'fond_urls',
         'callback': lambda rs, es, eo, ai: _cb_urls(rs, es, ai.name_caption, eo.fond_urls) if hasattr(eo, 'fond_urls') and eo.fond_urls else ""},
        {'name': 'fond_identifiers.group', 'name_tag': 'fond_identifiers',
         'callback': lambda rs, es, eo, ai: _cb_identifiers(rs, es, ai.name_caption, eo.fond_identifiers) if hasattr(eo, 'fond_identifiers') and eo.fond_identifiers else ""},
        # accesso
        {'name': 'access_condition', 'is_default': True},
        {'name': 'access_condition_note', 'is_default': True},
        {'name': 'use_condition', 'is_default': True},
        {'name': 'use_condition_note', 'is_default': True},
        {'name': 'preservation', 'is_default': True},
        {'name': 'preservation_note', 'is_default': True},
        # relazioni
        {'name': 'creators.group', 'name_tag': 'creators',
         'callback': lambda rs, es, eo, ai: _cb_creators(rs, es, eo, ai) if hasattr(eo, 'creators') and eo.creators else ""},
        {'name': 'custodians.group', 'name_tag': 'custodians',
         'callback': lambda rs, es, eo, ai: _cb_custodians(rs, es, eo, ai) if hasattr(eo, 'custodians') and eo.custodians else ""},
        {'name': 'projects.group', 'name_tag': 'projects',
         'callback': lambda rs, es, eo, ai: _cb_projects(rs, es, f"{_plural_human('project', len(eo.projects))}", eo.projects) if hasattr(eo, 'projects') and eo.projects else ""},
        {'name': 'document_forms.group', 'name_tag': 'document_forms',
         'callback': lambda rs, es, eo, ai: _cb_document_forms(rs, es, f"{_plural_human('document_form', len(eo.document_forms))}", eo.document_forms) if hasattr(eo, 'document_forms') and eo.document_forms else ""},
        # fonti
        {'name': 'sources.group', 'name_tag': 'sources_area',
         'callback': lambda rs, es, eo, ai: _cb_sources(rs, es, eo, ai), 'is_default': True},
        # compilatori
        {'name': 'fond_editors.group', 'name_tag': 'fond_editors',
         'callback': lambda rs, es, eo, ai: _cb_editors(rs, es, ai.name_caption, eo.fond_editors) if hasattr(eo, 'fond_editors') and eo.fond_editors else ""},
        # xxxx
        {'name': 'units_count', 'name_caption': "Numero unità archivistiche", 'is_default': True},
    ]
    return _make_available_attributes_info(attributes_template)


def custodian_available_attributes_info():
    attributes_template = [
        # identificazione
        {'name': 'legal_status', 'is_value_translation': True, 'is_default': True},
        {'name': 'custodian_type.custodian_type', 'name_tag': 'custodian_macro_type', 'is_default': True},
        {'name': 'preferred_name.group', 'name_tag': 'preferred_name',
         'callback': lambda rs, es, eo, ai: _cb_preferred_name(rs, es, eo, ai)},
        {'name': 'other_names.group', 'name_tag': 'other_names',
         'callback': lambda rs, es, eo, ai: _cb_other_names(rs, es, ai.name_caption, eo.other_names) if hasattr(eo, 'other_names') and eo.other_names else ""},
        {'name': 'history', 'name_tag': 'custodian_history', 'is_default': True},
        {'name': 'custodian_contacts.group', 'name_tag': 'contacts',
         'callback': lambda rs, es, eo, ai: _cb_custodian_contacts(rs, es, eo, ai) if hasattr(eo, 'custodian_contacts') and eo.custodian_contacts else ""},
        {'name': 'contact_person', 'name_tag': 'contact_person', 'is_default': True},
        {'name': 'owner', 'name_tag': 'custodian_owners', 'is_default': True, 'is_multi_instance': True},
        {'name': 'custodian_urls.group', 'name_tag': 'custodian_urls',
         'callback': lambda rs, es, eo, ai: _cb_urls(rs, es, ai.name_caption, eo.custodian_urls) if hasattr(eo, 'custodian_urls') and eo.custodian_urls else ""},
        {'name': 'custodian_identifiers.group', 'name_tag': 'custodian_identifiers',
         'callback': lambda rs, es, eo, ai: _cb_identifiers(rs, es, ai.name_caption, eo.custodian_identifiers) if hasattr(eo, 'custodian_identifiers') and eo.custodian_identifiers else ""},
        # descrizione
        {'name': 'holdings', 'is_default': True},
        {'name': 'collecting_policies', 'is_default': True},
        {'name': 'administrative_structure', 'is_default': True},
        # accesso
        {'name': 'accessibility', 'is_default': True},
        {'name': 'services', 'is_default': True},
        # sedi
        {'name': 'custodian_headquarter.name', 'group_caption': "Sede legale", 'group_tag': 'registered_office', 'name_tag': 'building_name'},
        {'name': 'custodian_headquarter.custodian_building_type', 'group_caption': "Sede legale", 'group_tag': 'registered_office', 'name_tag': 'building_type'},
        {'name': 'custodian_headquarter.address', 'group_caption': "Sede legale", 'group_tag': 'registered_office', 'name_tag': 'building_address'},
        {'name': 'custodian_headquarter.city', 'group_caption': "Sede legale", 'group_tag': 'registered_office', 'name_tag': 'city'},
        {'name': 'custodian_headquarter.postcode', 'group_caption': "Sede legale", 'group_tag': 'registered_office', 'name_tag': 'postcode'},
        {'name': 'custodian_headquarter.country', 'group_caption': "Sede legale", 'group_tag': 'registered_office', 'name_tag': 'country'},
        {'name': 'custodian_headquarter.description', 'group_caption': "Sede legale", 'group_tag': 'registered_office', 'name_tag': 'building_description'},
        # altre sedi
        {'name': 'custodian_other_buildings.name', 'group_caption': "Altre sedi", 'group_tag': 'custodian_other_buildings', 'name_tag': 'building_name', 'is_multi_instance': True},
        {'name': 'custodian_other_buildings.custodian_building_type', 'group_caption': "Altre sedi", 'group_tag': 'custodian_other_buildings', 'name_tag': 'building_type', 'is_multi_instance': True},
        {'name': 'custodian_other_buildings.address', 'group_caption': "Altre sedi", 'group_tag': 'custodian_other_buildings', 'name_tag': 'building_address', 'is_multi_instance': True},
        {'name': 'custodian_other_buildings.city', 'group_caption': "Altre sedi", 'group_tag': 'custodian_other_buildings', 'name_tag': 'city', 'is_multi_instance': True},
        {'name': 'custodian_other_buildings.postcode', 'group_caption': "Altre sedi", 'group_tag': 'custodian_other_buildings', 'name_tag': 'postcode', 'is_multi_instance': True},
        {'name': 'custodian_other_buildings.country', 'group_caption': "Altre sedi", 'group_tag': 'custodian_other_buildings', 'name_tag': 'country', 'is_multi_instance': True},
        {'name': 'custodian_other_buildings.description', 'group_caption': "Altre sedi", 'group_tag': 'custodian_other_buildings', 'name_tag': 'building_description', 'is_multi_instance': True},
        # relazioni
        {'name': 'fonds.group', 'name_tag': 'fonds',
         'callback': lambda rs, es, eo, ai: _cb_fonds(rs, es, eo, ai) if hasattr(eo, 'fonds') and eo.fonds else ""},
        # fonti
        {'name': 'sources.group', 'name_tag': 'sources_area',
         'callback': lambda rs, es, eo, ai: _cb_sources(rs, es, eo, ai), 'is_default': True},
        # compilatori
        {'name': 'custodian_editors.group', 'name_tag': 'custodian_editors',
         'callback': lambda rs, es, eo, ai: _cb_editors(rs, es, ai.name_caption, eo.custodian_editors) if hasattr(eo, 'custodian_editors') and eo.custodian_editors else ""},
    ]
    return _make_available_attributes_info(attributes_template)


def creator_available_attributes_info():
    attributes_template = [
        # identificazione
        {'name': 'preferred_name.group', 'name_tag': 'preferred_name',
         'callback': lambda rs, es, eo, ai: _cb_preferred_name(rs, es, eo, ai), 'is_default': True},
        {'name': 'creator_type', 'is_value_translation': True},
        {'name': 'creator_corporate_type.corporate_type', 'name_tag': 'creator_corporate_type', 'is_default': True},
        {'name': 'other_names.group', 'name_tag': 'other_names',
         'callback': lambda rs, es, eo, ai: _cb_other_names(rs, es, ai.name_caption, eo.other_names) if hasattr(eo, 'other_names') and eo.other_names else ""},
        {'name': 'events.group', 'name_tag': 'date_event',
         'callback': lambda rs, es, eo, ai: _cb_events(rs, es, eo, ai), 'is_default': True},
        {'name': 'creator_legal_statuses.group', 'name_tag': 'creator_legal_statuses',
         'callback': lambda rs, es, eo, ai: _cb_creator_legal_statuses(rs, es, eo, ai) if hasattr(eo, 'creator_legal_statuses') and eo.creator_legal_statuses else ""},
        {'name': 'residence', 'is_default': True},
        {'name': 'creator_urls.group', 'name_tag': 'creator_urls',
         'callback': lambda rs, es, eo, ai: _cb_urls(rs, es, ai.name_caption, eo.creator_urls) if hasattr(eo, 'creator_urls') and eo.creator_urls else ""},
        {'name': 'creator_identifiers.group', 'name_tag': 'creator_identifiers',
         'callback': lambda rs, es, eo, ai: _cb_identifiers(rs, es, ai.name_caption, eo.creator_identifiers) if hasattr(eo, 'creator_identifiers') and eo.creator_identifiers else ""},
        # descrizione
        {'name': 'abstract', 'is_default': True},
        {'name': 'history', 'name_tag': 'creator_history', 'is_default': True},
        {'name': 'note', 'name_tag': 'creator_note', 'is_default': True},
        {'name': 'creator_activities.group', 'name_tag': 'creator_activities',
         'callback': lambda rs, es, eo, ai: _cb_creator_activities(rs, es, eo, ai) if hasattr(eo, 'creator_activities') and eo.creator_activities else ""},
        # relazioni
        {'name': 'fonds.group', 'name_tag': 'fonds',
         'callback': lambda rs, es, eo, ai: _cb_fonds(rs, es, eo, ai) if hasattr(eo, 'fonds') and eo.fonds else ""},
        {'name': 'institutions.group', 'name_tag': 'institutions',
         'callback': lambda rs, es, eo, ai: _cb_institutions(rs, es, eo, ai) if hasattr(eo, 'institutions') and eo.institutions else ""},
        {'name': 'linked_creators.group', 'name_tag': 'linked_creators',
         'callback': lambda rs, es, eo, ai: _cb_linked_creators(rs, es, eo, ai) if hasattr(eo, 'rel_creator_creators') and eo.rel_creator_creators else ""},
        # fonti
        {'name': 'sources.group', 'name_tag': 'sources_area',
         'callback': lambda rs, es, eo, ai: _cb_sources(rs, es, eo, ai), 'is_default': True},
        # compilatori
        {'name': 'creator_editors.group', 'name_tag': 'creator_editors',
         'callback': lambda rs, es, eo, ai: _cb_editors(rs, es, ai.name_caption, eo.creator_editors) if hasattr(eo, 'creator_editors') and eo.creator_editors else ""},
    ]
    return _make_available_attributes_info(attributes_template)


def unit_available_attributes_info():
    attributes_template = [
        # descrizione
        {'name': 'unit_type'},
        {'name': 'title.group', 'name_tag': 'title',
         'name_caption_list_note': " (N.B.: viene inserito sempre come identificativo dell'unità)",
         'callback': lambda rs, es, eo, ai: _cb_unit_title(rs, es, eo, ai), 'is_default': True},
        {'name': 'events.group', 'name_tag': 'date_event',
         'callback': lambda rs, es, eo, ai: _cb_events(rs, es, eo, ai), 'is_default': True},
        {'name': 'content', 'is_default': True},
        {'name': 'extent', 'name_tag': 'unit_extent'},
        {'name': 'tmp_reference_number', 'is_default': True},
        {'name': 'tmp_reference_string', 'is_default': True},
        {'name': 'folder_number'},
        {'name': 'file_number'},
        {'name': 'reference_number', 'is_default': True},
        {'name': 'arrangement_note'},
        # descrizione fisica
        {'name': 'physical_type'},
        {'name': 'medium'},
        {'name': 'related_materials'},
        {'name': 'physical_description'},
        {'name': 'preservation', 'is_default': True},
        {'name': 'preservation_note', 'is_default': True},
        {'name': 'unit_damages.group', 'name_tag': 'unit_damages',
         'callback': lambda rs, es, eo, ai: _cb_unit_damages(rs, es, eo, ai) if hasattr(eo, 'unit_damages') and eo.unit_damages else ""},
        {'name': 'restoration'},
        {'name': 'note', 'name_tag': 'unit_note'},
        {'name': 'physical_container.group', 'name_tag': 'physical_container',
         'callback': lambda rs, es, eo, ai: _cb_unit_physical_container(rs, es, eo, ai)},
        {'name': 'unit_other_reference_numbers.group', 'name_tag': 'unit_other_reference_numbers',
         'callback': lambda rs, es, eo, ai: _cb_unit_other_reference_numbers(rs, es, eo, ai) if hasattr(eo, 'unit_other_reference_numbers') and eo.unit_other_reference_numbers else ""},
        # accesso
        {'name': 'unit_langs.code', 'name_tag': 'unit_langs',
         'callback': lambda rs, es, eo, ai: _cb_langs(rs, es, ai.name_caption, eo.unit_langs) if hasattr(eo, 'unit_langs') and eo.unit_langs else ""},
        {'name': 'access_condition'},
        {'name': 'access_condition_note'},
        {'name': 'use_condition'},
        {'name': 'use_condition_note'},
        {'name': 'unit_urls.group', 'name_tag': 'unit_urls',
         'callback': lambda rs, es, eo, ai: _cb_urls(rs, es, ai.name_caption, eo.unit_urls) if hasattr(eo, 'unit_urls') and eo.unit_urls else ""},
        {'name': 'unit_identifiers.group', 'name_tag': 'unit_identifiers',
         'callback': lambda rs, es, eo, ai: _cb_identifiers(rs, es, ai.name_caption, eo.unit_identifiers) if hasattr(eo, 'unit_identifiers') and eo.unit_identifiers else ""},
        # fonti
        {'name': 'sources.group', 'name_tag': 'sources_area',
         'callback': lambda rs, es, eo, ai: _cb_sources(rs, es, eo, ai), 'is_default': True},
        # compilatori
        {'name': 'unit_editors.group', 'name_tag': 'unit_editors',
         'callback': lambda rs, es, eo, ai: _cb_editors(rs, es, ai.name_caption, eo.unit_editors) if hasattr(eo, 'unit_editors') and eo.unit_editors else ""},
        # schede speciali SC2
        {'name': 'sc2_tsk', 'name_caption': "Scheda speciale"},
        {'name': 'sc2_textual_elements.group', 'name_tag': 'sc2_textual_elements',
         'callback': lambda rs, es, eo, ai: _cb_sc2_textual_elements(rs, es, eo, ai) if hasattr(eo, 'sc2_textual_elements') and eo.sc2_textual_elements else ""},
        {'name': 'sc2_visual_elements.group', 'name_tag': 'sc2_visual_elements',
         'callback': lambda rs, es, eo, ai: _cb_sc2_visual_elements(rs, es, eo, ai) if hasattr(eo, 'sc2_visual_elements') and eo.sc2_visual_elements else ""},
        {'name': 'sc2.sgti', 'name_caption': "Soggetto"},
        {'name': 'sc2_authors.group', 'name_tag': 'sc2_authors',
         'callback': lambda rs, es, eo, ai: _cb_sc2_authors(rs, es, eo, ai) if hasattr(eo, 'sc2_authors') and eo.sc2_authors else ""},
        {'name': 'sc2_commissions.group', 'name_tag': 'sc2_commissions',
         'callback': lambda rs, es, eo, ai: _cb_sc2_commissions(rs, es, eo, ai) if hasattr(eo, 'sc2_commissions') and eo.sc2_commissions else ""},
        {'name': 'sc2.cmmr', 'name_caption': "Numero di commessa"},
        {'name': 'sc2.lrc', 'name_caption': "Luogo della ripresa"},
        {'name': 'sc2.lrd', 'name_caption': "Data della ripresa"},
        {'name': 'sc2_techniques.group', 'name_tag': 'sc2_techniques',
         'callback': lambda rs, es, eo, ai: _cb_sc2_techniques(rs, es, eo, ai) if hasattr(eo, 'sc2_techniques') and eo.sc2_techniques else ""},
        {'name': 'sc2.mtce', 'name_caption': "Esecuzione"},
        {'name': 'sc2_scales.group', 'name_tag': 'sc2_scales',
         'callback': lambda rs, es, eo, ai: _cb_sc2_scales(rs, es, eo, ai) if hasattr(eo, 'sc2_scales') and eo.sc2_scales else ""},
        {'name': 'sc2.sdtt', 'name_caption': "Tipo di rappresentazione"},
        {'name': 'sc2.sdts', 'name_caption': "Rappresentazione tematica"},
        {'name': 'sc2.dpgf', 'name_caption': "Numero tavola"},
        {'name': 'sc2.misa', 'name_caption': "Altezza"},
        {'name': 'sc2.misl', 'name_caption': "Larghezza"},
        {'name': 'sc2.ort', 'name_caption': "Orientamento"},
    ]
    return _make_available_attributes_info(attributes_template)


def project_available_attributes_info():
    attributes_template = [
        # identificazione
        {'name': 'name', 'is_default': True},
        {'name': 'project_type', 'is_default': True},
        {'name': 'display_date', 'is_default': True},
        {'name': 'status'},
        {'name': 'description', 'name_tag': 'project_description', 'is_default': True},
        {'name': 'note', 'name_tag': 'project_note'},
        {'name': 'project_urls.group', 'name_tag': 'project_urls',
         'callback': lambda rs, es, eo, ai: _cb_urls(rs, es, ai.name_caption, eo.project_urls) if hasattr(eo, 'project_urls') and eo.project_urls else ""},
        # responsabilità
        {'name': 'project_managers.group', 'name_tag': 'project_managers',
         'callback': lambda rs, es, eo, ai: _cb_project_managers(rs, es, eo, ai) if hasattr(eo, 'project_managers') and eo.project_managers else ""},
        {'name': 'project_stakeholders.group', 'name_tag': 'project_stakeholders',
         'callback': lambda rs, es, eo, ai: _cb_project_stakeholders(rs, es, eo, ai) if hasattr(eo, 'project_stakeholders') and eo.project_stakeholders else ""},
        # relazioni
        {'name': 'fonds.group', 'name_tag': 'fonds',
         'callback': lambda rs, es, eo, ai: _cb_fonds(rs, es, eo, ai) if hasattr(eo, 'fonds') and eo.fonds else ""},
    ]
    return _make_available_attributes_info(attributes_template)


# ──────────────────────────────────────────────────────────────────────────────
# make_html — porting di make_html da ReportSupport
# ──────────────────────────────────────────────────────────────────────────────

def make_html(report_settings, entity_sym, entity_obj):
    """Genera HTML per i campi selezionati di un'entità."""
    op_html = ""
    ers = report_settings.entity_search_by_name(entity_sym)
    if not ers or not ers.has_any_selected_attributes():
        return op_html

    packed = _pack_selected_attribute_names(ers)

    for packed_names_set in packed:
        packed_names = packed_names_set.split('/')
        ref_attribute_name = packed_names[0]
        methods = ref_attribute_name.split('.')

        ai = ers.available_attributes_info.get(ref_attribute_name)
        if not ai:
            continue

        if ai.is_multi_instance:
            instances = _safe_getattr(entity_obj, methods[0])
            if instances:
                op_html += "<div>"
                group_caption_printed = False
                for instance_index, instance in enumerate(instances):
                    instance_caption_printed = False
                    for fld_index in range(len(packed_names)):
                        fld_methods = packed_names[fld_index].split('.')
                        value = _safe_getattr(instance, fld_methods[1] if len(fld_methods) > 1 else fld_methods[0])
                        if value:
                            ai_fld = ers.available_attributes_info.get(packed_names[fld_index])
                            if ai_fld and ai_fld.callback is None:
                                if not ers.dont_use_fld_captions:
                                    if not group_caption_printed and ai_fld.group_caption:
                                        op_html += _html_print_group_caption(ai_fld, "")
                                        op_html += _html_get_list_open_tag()
                                        group_caption_printed = True

                                    caption_postfix = _make_caption_postfix(
                                        ai_fld.group_tag, len(packed_names), instance_index, len(instances))
                                    if not instance_caption_printed and ai_fld.group_caption:
                                        op_html += _html_get_list_item_open_tag()
                                        op_html += "<div>"
                                        op_html += _html_print_group_caption(ai_fld, caption_postfix)
                                        instance_caption_printed = True
                                    if instance_caption_printed:
                                        caption_postfix = ""
                                else:
                                    caption_postfix = ""

                                text = _safe_getattr(instance, fld_methods[1] if len(fld_methods) > 1 else fld_methods[0])
                                op_html += _html_print_field(ers.dont_use_fld_captions, ai_fld, caption_postfix, str(text) if text else "")
                            elif ai_fld and ai_fld.callback:
                                callback_html = ai_fld.callback(report_settings, entity_sym, entity_obj, ai_fld)
                                if callback_html:
                                    op_html += callback_html
                    if instance_caption_printed:
                        op_html += "</div>"
                        op_html += _html_get_list_item_close_tag()
                if group_caption_printed:
                    op_html += _html_get_list_close_tag()
                op_html += "</div>"
        else:
            if ai.callback:
                callback_html = ai.callback(report_settings, entity_sym, entity_obj, ai)
                if callback_html:
                    op_html += f"<div>{callback_html}</div>"
            else:
                try:
                    if len(methods) > 1:
                        val = _safe_getattr(_safe_getattr(entity_obj, methods[0]), methods[1])
                    else:
                        val = _safe_getattr(entity_obj, methods[0])
                    if val and val != 0:
                        text = str(val)
                        if text:
                            op_html += f"<div>{_html_print_field(ers.dont_use_fld_captions, ai, '', text)}</div>"
                except Exception:
                    pass

    return op_html


# ──────────────────────────────────────────────────────────────────────────────
# Callback HTML (porting dei prv_html_rtf_*_callback)
# ──────────────────────────────────────────────────────────────────────────────

def _cb_other_names(report_settings, entity_sym, caption, other_names):
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "other_names")
    if str(ers.entity_name) == "fond":
        return _html_rtf_items_concat(report_settings, ers, caption, rtf_key, other_names,
                                      ["name", "note"], " ", ["", "["], ["", "]"], ["", ""])
    else:
        return _html_rtf_items_concat(report_settings, ers, caption, rtf_key, other_names,
                                      ["name", "qualifier", "note"], " ",
                                      ["", "(", "["], ["", ")", "]"],
                                      ["", "translate", ""])


def _cb_langs(report_settings, entity_sym, caption, langs):
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), f"{entity_sym}_langs")
    return _html_rtf_items_concat(report_settings, ers, caption, rtf_key, langs,
                                  ["code"], " ", [""], [""], ["langRemap"])


def _cb_urls(report_settings, entity_sym, caption, urls):
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), f"{entity_sym}_urls")
    return _html_rtf_items_concat(report_settings, ers, caption, rtf_key, urls,
                                  ["url", "note"], " ", ["", "["], ["", "]"], ["", ""])


def _cb_identifiers(report_settings, entity_sym, caption, identifiers):
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), f"{entity_sym}_identifiers")
    return _html_rtf_items_concat(report_settings, ers, caption, rtf_key, identifiers,
                                  ["identifier", "identifier_source", "note"], " ",
                                  ["", "(", "["], ["", ")", "]"], ["", "", ""])


def _cb_editors(report_settings, entity_sym, caption, editors):
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), f"{entity_sym}_editors")
    return _html_rtf_items_concat(report_settings, ers, caption, rtf_key, editors,
                                  ["name", "qualifier", "editing_type", "edited_at"], "",
                                  ["", " (", ", ", ", "], ["", ")", "", ""],
                                  ["", "", "", "dateLongFormat"])


def _cb_sources(report_settings, entity_sym, entity_obj, ai):
    from archimista_python.archive.models import Source
    sources = getattr(entity_obj, 'sources', None)
    if not sources:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    html = ""
    if not ers.dont_use_fld_captions:
        src_count = len(list(sources) if hasattr(sources, '__iter__') else [sources])
        human_name = _plural_human('source', src_count)
        html += f'<p class="fldcaption"><strong class="field-header">{human_name}</strong></p>'
    html += _html_get_list_open_tag()
    for source in (sources if hasattr(sources, '__iter__') else [sources]):
        html += _html_get_list_item_open_tag()
        html += f'[<em>{escape(getattr(source, "short_title", ""))}</em>] '
        html += escape(_formatted_source(source))
        html += _html_get_list_item_close_tag()
    html += _html_get_list_close_tag()
    return html


def _formatted_source(source):
    """Simula formatted_source di Ruby ApplicationHelper."""
    parts = []
    if hasattr(source, 'title') and source.title:
        parts.append(escape(str(source.title)))
    if hasattr(source, 'author') and source.author:
        parts.append(escape(str(source.author)))
    if hasattr(source, 'date') and source.date:
        parts.append(escape(str(source.date)))
    return ", ".join(parts) if parts else ""


def _cb_events(report_settings, entity_sym, entity_obj, ai):
    events = getattr(entity_obj, 'events', None)
    if not events:
        return ""
    # events is a GenericRelatedObjectManager, need .all()
    events_list = events.all() if hasattr(events, 'all') else events
    if not events_list:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    html = ""
    if not ers.dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{ai.name_caption}</strong></p>'
    for event in events_list:
        s = getattr(event, 'full_display_date_with_place', '') or getattr(event, 'full_display_date', '') or ''
        note = getattr(event, 'note', '')
        if note:
            s += f" [{note}]"
        html += f"<p>{escape(str(s))}</p>"
    return html


def _cb_fond_owners(report_settings, entity_sym, entity_obj, ai):
    owners = getattr(entity_obj, 'fond_owners', None)
    if not owners:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "fond_owners")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, owners,
                                  ["owner"], " ", [""], [""], [""])


def _cb_creators(report_settings, entity_sym, entity_obj, ai):
    creators = getattr(entity_obj, 'creators', None)
    if not creators:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    html = ""
    if not ers.dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{_plural_human("creator", len(list(creators)))}</strong></p>'
    html += _html_get_list_open_tag()
    for creator in creators:
        pn = getattr(creator, 'preferred_name', None)
        name = getattr(pn, 'name', f'Creatore #{getattr(creator, "id", "?")}') if pn else f'Creatore #{getattr(creator, "id", "?")}'
        pe = getattr(creator, 'preferred_event', None)
        date_str = getattr(pe, 'full_display_date', '') if pe else ''
        html += _html_get_list_item_open_tag()
        html += f"{escape(name)}"
        if date_str:
            html += f" {escape(str(date_str))}"
        html += _html_get_list_item_close_tag()
    html += _html_get_list_close_tag()
    return html


def _cb_custodians(report_settings, entity_sym, entity_obj, ai):
    custodians = getattr(entity_obj, 'custodians', None)
    if not custodians:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    html = ""
    if not ers.dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{_plural_human("custodian", len(list(custodians)))}</strong></p>'
    html += _html_get_list_open_tag()
    for c in custodians:
        pn = getattr(c, 'preferred_name', None)
        name = getattr(pn, 'name', f'Conservatore #{getattr(c, "id", "?")}') if pn else f'Conservatore #{getattr(c, "id", "?")}'
        html += _html_get_list_item_open_tag()
        html += escape(name)
        html += _html_get_list_item_close_tag()
    html += _html_get_list_close_tag()
    return html


def _cb_projects(report_settings, entity_sym, caption, projects):
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "projects")
    return _html_rtf_items_concat(report_settings, ers, caption, rtf_key, projects,
                                  ["name", "display_date"], " ", ["", ""], ["", ""], ["", ""])


def _cb_document_forms(report_settings, entity_sym, caption, document_forms):
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "document_forms")
    return _html_rtf_items_concat(report_settings, ers, caption, rtf_key, document_forms,
                                  ["name"], " ", [""], [""], [""])


def _cb_fonds(report_settings, entity_sym, entity_obj, ai):
    fonds = getattr(entity_obj, 'fonds', None)
    if not fonds:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    html = ""
    if not ers.dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{_plural_human("fond", len(list(fonds)))}</strong></p>'
    html += _html_get_list_open_tag()
    for fond in fonds:
        html += _html_get_list_item_open_tag()
        html += escape(getattr(fond, 'name', ''))
        pe = getattr(fond, 'preferred_event', None)
        if pe:
            html += f" {escape(str(getattr(pe, 'full_display_date', '')))}"
        html += _html_get_list_item_close_tag()
    html += _html_get_list_close_tag()
    return html


def _cb_preferred_name(report_settings, entity_sym, entity_obj, ai):
    pn = getattr(entity_obj, 'preferred_name', None)
    if not pn:
        return ""
    value = getattr(pn, 'name', '')
    ers = report_settings.entity_search_by_name(entity_sym)
    html = ""
    if not ers.dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{_t("preferred_name")}</strong></p>'
    html += f"<p>{escape(str(value))}</p>"
    return html


def _cb_custodian_contacts(report_settings, entity_sym, entity_obj, ai):
    contacts = getattr(entity_obj, 'custodian_contacts', None)
    if not contacts:
        return ""
    contact_strs = []
    for c in contacts:
        ct = getattr(c, 'contact_type', '')
        cv = getattr(c, 'contact', '')
        contact_strs.append(f"{_t(ct)}: {cv}")
    value = ", ".join(contact_strs)
    ers = report_settings.entity_search_by_name(entity_sym)
    html = ""
    if not ers.dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{_t("contacts")}</strong></p>'
    html += f"<p>{escape(str(value))}</p>"
    return html


def _cb_creator_legal_statuses(report_settings, entity_sym, entity_obj, ai):
    ls_list = getattr(entity_obj, 'creator_legal_statuses', None)
    if not ls_list:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "creator_legal_statuses")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, ls_list,
                                  ["legal_status", "note"], " ", ["", "["], ["", "]"],
                                  ["vocRemapAndTranslate/creator_legal_statuses.legal_status", ""])


def _cb_creator_activities(report_settings, entity_sym, entity_obj, ai):
    acts = getattr(entity_obj, 'creator_activities', None)
    if not acts:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "creator_activities")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, acts,
                                  ["activity", "note"], " ", ["", "["], ["", "]"], ["", ""])


def _cb_institutions(report_settings, entity_sym, entity_obj, ai):
    insts = getattr(entity_obj, 'institutions', None)
    if not insts:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "institutions")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, insts,
                                  ["name"], " ", [""], [""], [""])


def _cb_linked_creators(report_settings, entity_sym, entity_obj, ai):
    rels = getattr(entity_obj, 'rel_creator_creators', None)
    if not rels:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    html = ""
    if not ers.dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{ai.name_caption}</strong></p>'
    html += _html_get_list_open_tag()
    for rel in rels:
        cat = getattr(rel, 'creator_association_type', None)
        assoc_type = getattr(cat, 'association_type', 'legacy data: qualifica non presente') if cat else 'legacy data: qualifica non presente'
        rc = getattr(rel, 'related_creator', None)
        if rc:
            pn = getattr(rc, 'preferred_name', None)
            name = getattr(pn, 'name', f'Creatore #{getattr(rc, "id", "?")}') if pn else f'Creatore #{getattr(rc, "id", "?")}'
            pe = getattr(rc, 'preferred_event', None)
            date_str = getattr(pe, 'full_display_date', '') if pe else ''
            html += _html_get_list_item_open_tag()
            html += f"({escape(assoc_type)}) {escape(name)}"
            if date_str:
                html += f" {escape(str(date_str))}"
            html += _html_get_list_item_close_tag()
    html += _html_get_list_close_tag()
    return html


def _cb_unit_title(report_settings, entity_sym, entity_obj, ai):
    value = getattr(entity_obj, 'title', '') or ''
    if getattr(entity_obj, 'given_title', False):
        value += " [attribuito]"
    ers = report_settings.entity_search_by_name(entity_sym)
    html = ""
    if not ers.dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{ai.name_caption}</strong></p>'
    html += f"<p>{escape(str(value))}</p>"
    return html


def _cb_unit_damages(report_settings, entity_sym, entity_obj, ai):
    damages = getattr(entity_obj, 'unit_damages', None)
    if not damages:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "unit_damages")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, damages,
                                  ["code"], " ", [""], [""], [""])


def _cb_unit_physical_container(report_settings, entity_sym, entity_obj, ai):
    ers = report_settings.entity_search_by_name(entity_sym)
    parts = []
    for fld, label_key in [
        ('physical_container_type', 'physical_container_type'),
        ('physical_container_title', 'physical_container_title'),
        ('physical_container_number', 'physical_container_number'),
    ]:
        val = getattr(entity_obj, fld, '')
        if val:
            parts.append(f"{_t(label_key)}: {escape(str(val))}")
    if not parts:
        return ""
    html = ""
    if not ers.dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{ai.name_caption}</strong></p>'
    html += "<p>" + "<br />".join(parts) + "</p>"
    return html


def _cb_unit_other_reference_numbers(report_settings, entity_sym, entity_obj, ai):
    orns = getattr(entity_obj, 'unit_other_reference_numbers', None)
    if not orns:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "unit_other_reference_numbers")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, orns,
                                  ["other_reference_number", "qualifier", "note"], " ",
                                  ["", "(", "| " + _t("note") + ": "], ["", ")", ""], ["", "", ""])


def _cb_sc2_textual_elements(report_settings, entity_sym, entity_obj, ai):
    els = getattr(entity_obj, 'sc2_textual_elements', None)
    if not els:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "sc2_textual_elements")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, els,
                                  ["isri"], " ", [""], [""], [""])


def _cb_sc2_visual_elements(report_settings, entity_sym, entity_obj, ai):
    els = getattr(entity_obj, 'sc2_visual_elements', None)
    if not els:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "sc2_visual_elements")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, els,
                                  ["stmd"], " ", [""], [""], [""])


def _cb_sc2_authors(report_settings, entity_sym, entity_obj, ai):
    authors = getattr(entity_obj, 'sc2_authors', None)
    if not authors:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "sc2_authors")
    reasons = getattr(entity_obj, 'sc2_attribution_reasons', [])
    settings = {
        'l1_fld_names': ['autn', 'auta', 'autr'],
        'l1_fld_separator': ' ',
        'l1_fld_prefixes': ['', '', ' ('],
        'l1_fld_postfixes': ['', '', ')'],
        'l1_fld_value_transformations': ['', '', ''],
        'l1_item_key_fldname': 'id',
        'l2_caption': _t("sc2_attribution_reasons") + ": ",
        'l2_fld_names': ['autm'],
        'l2_fld_separator': ' ',
        'l2_fld_prefixes': [''],
        'l2_fld_postfixes': [''],
        'l2_fld_value_transformations': [''],
        'l2_foreign_key_fldname': 'sc2_author_id',
        'l2_inst_separator': ', ',
        'l1vsl2_separator': ' - ',
        'l2_position': 'after',
    }
    return _html_rtf_items_concat_with_subtable(report_settings, ers, ai.name_caption, rtf_key, authors, reasons, settings)


def _cb_sc2_commissions(report_settings, entity_sym, entity_obj, ai):
    commissions = getattr(entity_obj, 'sc2_commissions', None)
    if not commissions:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "sc2_commissions")
    cnames = getattr(entity_obj, 'sc2_commission_names', [])
    settings = {
        'l1_fld_names': ['cmmc'],
        'l1_fld_separator': ' ',
        'l1_fld_prefixes': [''],
        'l1_fld_postfixes': [''],
        'l1_fld_value_transformations': [''],
        'l1_item_key_fldname': 'id',
        'l2_caption': _t("sc2_commission_names") + ": ",
        'l2_fld_names': ['cmmn'],
        'l2_fld_separator': ' ',
        'l2_fld_prefixes': [''],
        'l2_fld_postfixes': [''],
        'l2_fld_value_transformations': [''],
        'l2_foreign_key_fldname': 'sc2_commission_id',
        'l2_inst_separator': ', ',
        'l1vsl2_separator': ' - ',
        'l2_position': 'before',
    }
    return _html_rtf_items_concat_with_subtable(report_settings, ers, ai.name_caption, rtf_key, commissions, cnames, settings)


def _cb_sc2_techniques(report_settings, entity_sym, entity_obj, ai):
    techs = getattr(entity_obj, 'sc2_techniques', None)
    if not techs:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "sc2_techniques")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, techs,
                                  ["mtct"], " ", [""], [""], [""])


def _cb_sc2_scales(report_settings, entity_sym, entity_obj, ai):
    scales = getattr(entity_obj, 'sc2_scales', None)
    if not scales:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "sc2_scales")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, scales,
                                  ["sca"], " ", [""], [""], [""])


def _cb_project_managers(report_settings, entity_sym, entity_obj, ai):
    pms = getattr(entity_obj, 'project_managers', None)
    if not pms:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "project_managers")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, pms,
                                  ["name", "qualifier"], " ", ["", " ["], ["", "]"], ["", ""])


def _cb_project_stakeholders(report_settings, entity_sym, entity_obj, ai):
    pss = getattr(entity_obj, 'project_stakeholders', None)
    if not pss:
        return ""
    ers = report_settings.entity_search_by_name(entity_sym)
    rtf_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(str(entity_sym), "project_stakeholders")
    return _html_rtf_items_concat(report_settings, ers, ai.name_caption, rtf_key, pss,
                                  ["name", "qualifier"], " ", ["", " ["], ["", "]"], ["", ""])


# ──────────────────────────────────────────────────────────────────────────────
# HTML helper functions
# ──────────────────────────────────────────────────────────────────────────────

def _html_print_group_caption(ai, caption_postfix):
    return f'<p class="fldcaption"><strong class="field-header">{ai.group_caption}{caption_postfix}</strong></p>'


def _html_print_field(dont_use_fld_captions, ai, caption_postfix, text):
    html = ""
    if not dont_use_fld_captions:
        html += f'<p class="fldcaption"><strong class="field-header">{ai.name_caption}{caption_postfix}</strong></p>'
    html += _textilize_with_entities(text)
    return html


def _html_get_list_open_tag():
    return "<ul>" if HTML_USE_UNORDERED_LIST_TAG else ""


def _html_get_list_close_tag():
    return "</ul>" if HTML_USE_UNORDERED_LIST_TAG else ""


def _html_get_list_item_open_tag():
    return "<li>" if HTML_USE_UNORDERED_LIST_TAG else "<p>"


def _html_get_list_item_close_tag():
    return "</li>" if HTML_USE_UNORDERED_LIST_TAG else "</p>"


# ──────────────────────────────────────────────────────────────────────────────
# _html_rtf_items_concat (versione HTML) — porting di prv_html_rtf_items_concat
# ──────────────────────────────────────────────────────────────────────────────

def _html_rtf_items_concat(report_settings, ers, caption, rtf_stylesheet_key, items,
                           fld_names, separator, fld_prefixes, fld_postfixes, fld_value_transformations):
    return _html_rtf_items_concat_with_subtable(
        report_settings, ers, caption, rtf_stylesheet_key, items, None,
        {
            'l1_fld_names': fld_names,
            'l1_fld_separator': separator,
            'l1_fld_prefixes': fld_prefixes,
            'l1_fld_postfixes': fld_postfixes,
            'l1_fld_value_transformations': fld_value_transformations,
            'l1_item_key_fldname': 'id',
            'l2_caption': '',
            'l2_fld_names': [],
            'l2_fld_separator': '',
            'l2_fld_prefixes': [],
            'l2_fld_postfixes': [],
            'l2_fld_value_transformations': [],
            'l2_foreign_key_fldname': '',
            'l2_inst_separator': '',
            'l1vsl2_separator': '',
            'l2_position': '',
        }
    )


def _html_rtf_items_concat_with_subtable(report_settings, ers, caption, rtf_stylesheet_key,
                                         l1_items, l2_items, settings):
    l1_fld_names = settings.get('l1_fld_names', []) or []
    l1_fld_separator = settings.get('l1_fld_separator', '') or ''
    l1_fld_prefixes = settings.get('l1_fld_prefixes', []) or []
    l1_fld_postfixes = settings.get('l1_fld_postfixes', []) or []
    l1_fld_value_transformations = settings.get('l1_fld_value_transformations', []) or []
    l1_item_key_fldname = settings.get('l1_item_key_fldname', 'id') or 'id'

    l2_caption = settings.get('l2_caption', '') or ''
    l2_fld_names = settings.get('l2_fld_names', []) or []
    l2_fld_separator = settings.get('l2_fld_separator', '') or ''
    l2_fld_prefixes = settings.get('l2_fld_prefixes', []) or []
    l2_fld_postfixes = settings.get('l2_fld_postfixes', []) or []
    l2_fld_value_transformations = settings.get('l2_fld_value_transformations', []) or []
    l2_foreign_key_fldname = settings.get('l2_foreign_key_fldname', '') or ''
    l2_inst_separator = settings.get('l2_inst_separator', '') or ''

    l1vsl2_separator = settings.get('l1vsl2_separator', '') or ''
    l2_position = settings.get('l2_position', '') or ''

    if not l1_items:
        return ""

    html = ""
    is_html = True  # In this context we always generate HTML

    if not ers.dont_use_fld_captions and caption:
        html += f'<p class="fldcaption"><strong class="field-header">{caption}</strong></p>'

    html += _html_get_list_open_tag()

    for l1_item in l1_items:
        # Check first field is not empty
        if not l1_fld_names:
            continue
        first_val = _safe_getattr(l1_item, l1_fld_names[0])
        if not first_val:
            continue

        l1_value = _html_rtf_fld_values_concat(
            is_html, l1_item, l1_fld_names, l1_fld_separator,
            l1_fld_prefixes, l1_fld_postfixes, l1_fld_value_transformations)

        l2_value = ""
        if l2_items and l2_foreign_key_fldname:
            l1_id = _safe_getattr(l1_item, l1_item_key_fldname)
            for l2_item in l2_items:
                l2_fk = _safe_getattr(l2_item, l2_foreign_key_fldname)
                if l2_fk == l1_id:
                    l2_item_val = _html_rtf_fld_values_concat(
                        is_html, l2_item, l2_fld_names, l2_fld_separator,
                        l2_fld_prefixes, l2_fld_postfixes, l2_fld_value_transformations)
                    if l2_item_val:
                        if l2_inst_separator and l2_value:
                            l2_value += l2_inst_separator
                        l2_value += l2_item_val
            if l2_value and l2_caption:
                l2_value = l2_caption + l2_value

        if l2_value:
            if l1_value:
                if l2_position == "before":
                    l1_value = l2_value + l1vsl2_separator + l1_value
                elif l2_position == "after":
                    l1_value = l1_value + l1vsl2_separator + l2_value
            else:
                l1_value = l2_value

        html += _html_get_list_item_open_tag() + l1_value + _html_get_list_item_close_tag()

    html += _html_get_list_close_tag()
    return html


def _html_rtf_fld_values_concat(is_html, item, fld_names, fld_separator, fld_prefixes,
                                fld_postfixes, fld_value_transformations):
    item_value = ""
    for i in range(len(fld_names)):
        if hasattr(item, fld_names[i]):
            value = _safe_getattr(item, fld_names[i])
            if value is not None and str(value) != "":
                if fld_separator and item_value:
                    item_value += fld_separator
                if fld_value_transformations and i < len(fld_value_transformations) and fld_value_transformations[i]:
                    transform = fld_value_transformations[i]
                    if transform == "translate":
                        value = _t(str(value))
                    elif transform == "dateLongFormat":
                        value = str(value)  # date already formatted via full_display_date
                    elif transform.startswith("vocRemapAndTranslate/"):
                        vocab_spec = transform.split("/")[1]
                        value = _vocabulary_remap(is_html, vocab_spec, str(value), True)
                    elif transform.startswith("vocRemap/"):
                        vocab_spec = transform.split("/")[1]
                        value = _vocabulary_remap(is_html, vocab_spec, str(value), False)
                    elif transform == "langRemap":
                        value = _lang_remap(is_html, str(value), False)
                    elif transform == "langRemapAndTranslate":
                        value = _lang_remap(is_html, str(value), True)
                item_value += (fld_prefixes[i] if i < len(fld_prefixes) else "") + str(value) + (fld_postfixes[i] if i < len(fld_postfixes) else "")
    return item_value


# ──────────────────────────────────────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────────────────────────────────────

def _safe_getattr(obj, attr, default=None):
    """getattr sicuro che gestisce None e AttributeError."""
    if obj is None:
        return default
    try:
        return getattr(obj, attr, default)
    except (AttributeError, Exception):
        return default


def _pack_selected_attribute_names(ers):
    """Pack dei nomi degli attributi selezionati (gestione multi-instance con group_tag)."""
    packed = []
    attr_index_current = -1
    for attr_index in range(len(ers.selected_attribute_names)):
        attr_name = ers.selected_attribute_names[attr_index]
        if attr_index > attr_index_current:
            ai = ers.available_attributes_info.get(attr_name)
            if ai and ai.is_multi_instance:
                if ai.group_tag is None:
                    packed.append(attr_name)
                    attr_index_current = attr_index
                else:
                    attr_index_current = attr_index
                    group_tag = ai.group_tag
                    packed_set = ""
                    for i in range(attr_index, len(ers.selected_attribute_names)):
                        tgt_name = ers.selected_attribute_names[i]
                        tgt_ai = ers.available_attributes_info.get(tgt_name)
                        if tgt_ai and group_tag == tgt_ai.group_tag:
                            if packed_set:
                                packed_set += "/"
                            packed_set += tgt_name
                            attr_index_current = i
                        else:
                            break
                    packed.append(packed_set)
            else:
                packed.append(attr_name)
                attr_index_current = attr_index
    return packed


def _make_caption_postfix(group_tag, group_items_count, instance_index, instance_count):
    if group_tag is None:
        if group_items_count > 1:
            return f" [{instance_index + 1}/{instance_count}]"
        return ""
    else:
        return f" [{instance_index + 1}/{instance_count}]"


# ──────────────────────────────────────────────────────────────────────────────
# make_rtf — porting di make_rtf da ReportSupport
# ──────────────────────────────────────────────────────────────────────────────

def make_rtf(rw, report_settings, entity_sym, entity_obj):
    """Genera RTF per i campi selezionati di un'entità (scrive direttamente su RtfWriter)."""
    from archimista_python.archive.rtf_writer import GCrwFontBoldEnabled, GCrwTextAlignmentJustified

    ers = report_settings.entity_search_by_name(entity_sym)
    if not ers or not ers.has_any_selected_attributes():
        return

    packed = _pack_selected_attribute_names(ers)

    for packed_names_set in packed:
        packed_names = packed_names_set.split('/')
        ref_attribute_name = packed_names[0]
        methods = ref_attribute_name.split('.')

        ai = ers.available_attributes_info.get(ref_attribute_name)
        if not ai:
            continue

        if ai.is_multi_instance:
            instances = _safe_getattr(entity_obj, methods[0])
            if instances:
                group_caption_printed = False
                for instance_index, instance in enumerate(instances):
                    instance_caption_printed = False
                    for fld_index in range(len(packed_names)):
                        fld_methods = packed_names[fld_index].split('.')
                        value = _safe_getattr(instance, fld_methods[1] if len(fld_methods) > 1 else fld_methods[0])
                        if value:
                            ai_fld = ers.available_attributes_info.get(packed_names[fld_index])
                            if ai_fld and ai_fld.callback is None:
                                if not ers.dont_use_fld_captions:
                                    if not group_caption_printed and ai_fld.group_caption:
                                        rw.write_paragraph(
                                            ai_fld.group_caption,
                                            report_settings.rtf_stylesheet_code_archimista_label,
                                            None, None, GCrwFontBoldEnabled, None, None,
                                            GCrwTextAlignmentJustified, None, None, None)
                                        group_caption_printed = True

                                    caption_postfix = _make_caption_postfix(
                                        ai_fld.group_tag, len(packed_names), instance_index, len(instances))
                                    if not instance_caption_printed and ai_fld.group_caption:
                                        rw.write_paragraph(
                                            ai_fld.group_caption + caption_postfix,
                                            report_settings.rtf_stylesheet_code_archimista_label,
                                            None, None, GCrwFontBoldEnabled, None, None,
                                            GCrwTextAlignmentJustified, None, None, None)
                                        instance_caption_printed = True
                                    if instance_caption_printed:
                                        caption_postfix = ""
                                else:
                                    caption_postfix = ""

                                text = str(_safe_getattr(instance, fld_methods[1] if len(fld_methods) > 1 else fld_methods[0]))
                                stylesheet_codes_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(
                                    str(ers.entity_name), packed_names[fld_index])
                                _rtf_print_field(
                                    rw, report_settings.rtf_stylesheet_code_archimista_label,
                                    report_settings.get_attribute_rtf_stylesheet_code(stylesheet_codes_key),
                                    str(ers.entity_name), ers.dont_use_fld_captions, ai_fld, caption_postfix, text)
                            elif ai_fld and ai_fld.callback:
                                ai_fld.callback(report_settings, entity_sym, entity_obj, ai_fld)
        else:
            if ai.callback:
                ai.callback(report_settings, entity_sym, entity_obj, ai)
            else:
                try:
                    if len(methods) > 1:
                        val = _safe_getattr(_safe_getattr(entity_obj, methods[0]), methods[1])
                    else:
                        val = _safe_getattr(entity_obj, methods[0])
                    if val and val != 0:
                        text = str(val)
                        if text:
                            stylesheet_codes_key = ReportSettings.make_attribute_rtf_stylesheet_codes_key(
                                str(ers.entity_name), ref_attribute_name)
                            _rtf_print_field(
                                rw, report_settings.rtf_stylesheet_code_archimista_label,
                                report_settings.get_attribute_rtf_stylesheet_code(stylesheet_codes_key),
                                str(ers.entity_name), ers.dont_use_fld_captions, ai, "", text)
                except Exception:
                    pass


def _rtf_print_field(rw, rtf_caption_stylesheet_index, rtf_value_stylesheet_index,
                     entity_name, dont_use_fld_captions, ai, caption_postfix, text):
    """Scrive un campo RTF con caption e valore."""
    from archimista_python.archive.rtf_writer import GCrwFontBoldEnabled, GCrwTextAlignmentJustified

    if ai.is_value_translation:
        text = _t(text)

    if not dont_use_fld_captions:
        rw.write_paragraph(
            ai.name_caption + caption_postfix,
            rtf_caption_stylesheet_index,
            None, None, GCrwFontBoldEnabled, None, None,
            GCrwTextAlignmentJustified, None, None, None)

    rw.write_paragraph(text, rtf_value_stylesheet_index, None, 10, None, None, None,
                      GCrwTextAlignmentJustified, None, None, None)
    rw.write_new_line(None, None, 8)
