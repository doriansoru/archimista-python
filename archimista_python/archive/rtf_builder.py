"""
Porting di app/models/rtf_builder.rb — Costruttore RTF di alto livello.
Genera file RTF completi per inventari, report progetto e report conservatore.
"""

import os
import time
from datetime import datetime

from archimista_python.archive.rtf_writer import (
    RtfWriter,
    GCrwStyleHeading, GCrwStyleHeading1, GCrwStyleHeading2, GCrwStyleHeading3,
    GCrwFontNameArial, GCrwFontBoldEnabled, GCrwFontItalicEnabled, GCrwFontItalicDisabled,
    GCrwTextAlignmentLeft, GCrwTextAlignmentRight, GCrwTextAlignmentCenter, GCrwTextAlignmentJustified,
    GCrwHeaderFooterPageLeft, GCrwHeaderFooterPageRight,
    GCrwStylePredefinedCount,
    GCrwTextColorCurrent, GCrwIndentationCMQuartersCurrent,
)
from archimista_python.archive.report_support import (
    ReportSettings, EntityReportSettings,
    fond_available_attributes_info, custodian_available_attributes_info,
    creator_available_attributes_info, unit_available_attributes_info,
    project_available_attributes_info,
    make_html,  # imported for consistency, not used directly in RTF
)
from archimista_python.archive.models import (
    Fond, Unit, Creator, Custodian, Project,
    RelCreatorFond, RelCustodianFond, RelProjectFond,
)
from django.db.models import Q


# ──────────────────────────────────────────────────────────────────────────────
# Costanti stylesheet (da Ruby RtfBuilder::CC*)
# ──────────────────────────────────────────────────────────────────────────────

CC_STYLESHEET_ARCHIMISTA_LABEL = "archimista_label"
CC_STYLESHEET_ARCHIMISTA_SECTION_HEADER = "archimista_section_header"
CC_STYLESHEET_ARCHIMISTA_PROJECT = "archimista_project"
CC_STYLESHEET_ARCHIMISTA_FOND = "archimista_fond"
CC_STYLESHEET_ARCHIMISTA_CUSTODIAN = "archimista_custodian"
CC_STYLESHEET_ARCHIMISTA_CREATOR = "archimista_creator"
CC_STYLESHEET_ARCHIMISTA_UNIT = "archimista_unit"
CC_STYLESHEET_UNIT_SEQUENCE_NUMBER = "unit_sequence_number"
CC_STYLESHEET_SEPARATOR = "separator"


class RtfBuilder:
    """Costruttore RTF di alto livello. Porting di RtfBuilder da Ruby."""

    def __init__(self, target_id=None, dest_file=None):
        self.target_id = target_id
        self.dest_file = dest_file

    def build_fond_rtf_file(self, params, cookies):
        """Genera il file RTF per un inventario di fondo (complesso archivistico)."""
        rw = RtfWriter()

        # Report settings
        report_settings = ReportSettings(
            rw, "inventory", "Inventario di complesso archivistico", "inventory", None)

        report_settings.entity_add(EntityReportSettings('project', project_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('custodian', custodian_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('creator', creator_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('fond', fond_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('unit', unit_available_attributes_info(), False))

        # Build stylesheets
        stylesheets, stylesheet_codes = self._prv_build_rtf_stylesheets_info(
            report_settings, GCrwStylePredefinedCount)

        report_settings.initialize_entities_selected_attribute_names(params, cookies)
        report_settings.rtf_stylesheet_codes = stylesheet_codes
        report_settings.rtf_stylesheet_code_archimista_label = report_settings.get_attribute_rtf_stylesheet_code(
            CC_STYLESHEET_ARCHIMISTA_LABEL)

        separator_styleindex = report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_SEPARATOR)

        # Fetch data — same includes as Ruby
        fond = Fond.objects.get(pk=self.target_id)
        subtree_ids = fond.subtree_ids if hasattr(fond, 'subtree_ids') else [fond.pk]

        fonds = Fond.objects.filter(pk__in=subtree_ids).prefetch_related(
            'events',
            'fond_names', 'fond_langs', 'fond_owners', 'fond_urls', 'fond_identifiers',
            'fond_editors',
            'units__unit_damages', 'units__unit_other_reference_numbers',
            'units__unit_langs', 'units__unit_urls', 'units__unit_identifiers',
            'units__unit_editors',
            'units__sc2_textual_elements', 'units__sc2_visual_elements',
            'units__sc2_authors', 'units__sc2_commissions',
            'units__sc2_techniques', 'units__sc2_scales',
            'units__iccd_damages',
        ).order_by('sequence_number')

        root_fond = fonds.first()
        display_sequence_numbers = Unit.display_sequence_numbers_of(root_fond) if root_fond else {}

        # Open file and write
        rw.file_create(self.dest_file)
        rw.write_file_head(stylesheets)

        self._prv_write_header_and_footer(rw, root_fond.name if root_fond else "")

        # Title page
        title_parts = []
        if root_fond:
            title_parts.append(root_fond.name)
            pe = getattr(root_fond, 'preferred_event', None)
            if pe:
                fd = getattr(pe, 'full_display_date', '')
                if fd:
                    title_parts.append(str(fd))
        self._prv_title_page(rw, "\n".join(title_parts))
        rw.write_new_page()

        # Write content
        fond_index = 0
        fond_count = fonds.count()

        for fond in fonds:
            self._prv_h1(rw, fond.name, report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_ARCHIMISTA_FOND))
            rw.write_new_line()

            insert_separator = False

            if getattr(fond, 'projects', None):
                rw.write_line_separator(separator_styleindex)
                self._prv_write_projects_info(rw, report_settings, list(fond.projects.all()))

            if getattr(fond, 'custodians', None):
                rw.write_line_separator(separator_styleindex)
                self._prv_write_custodians_info(rw, report_settings, list(fond.custodians.all()))

            if getattr(fond, 'creators', None):
                rw.write_line_separator(separator_styleindex)
                self._prv_write_creators_info(rw, report_settings, list(fond.creators.all()))

            # Import make_rtf here for actual field output
            from archimista_python.archive.report_support import make_rtf
            make_rtf(rw, report_settings, 'fond', fond)

            if getattr(fond, 'units', None):
                rw.write_line_separator(separator_styleindex)
                self._prv_write_units_info(rw, report_settings, list(fond.units.all()),
                                          display_sequence_numbers, separator_styleindex)

            if fond_index < fond_count - 1:
                rw.write_line_separator(separator_styleindex)
            fond_index += 1

        rw.write_file_tail()
        rw.file_close()

    def build_custodian_rtf_file(self, params, cookies):
        """Genera il file RTF per un report conservatore."""
        rw = RtfWriter()

        report_settings = ReportSettings(
            rw, "custodian", "Report per conservatore", "custodian", None)

        report_settings.entity_add(EntityReportSettings('custodian', custodian_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('project', project_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('creator', creator_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('fond', fond_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('unit', unit_available_attributes_info(), False))

        stylesheets, stylesheet_codes = self._prv_build_rtf_stylesheets_info(
            report_settings, GCrwStylePredefinedCount)

        report_settings.initialize_entities_selected_attribute_names(params, cookies)
        report_settings.rtf_stylesheet_codes = stylesheet_codes
        report_settings.rtf_stylesheet_code_archimista_label = report_settings.get_attribute_rtf_stylesheet_code(
            CC_STYLESHEET_ARCHIMISTA_LABEL)

        separator_styleindex = report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_SEPARATOR)

        custodian = Custodian.objects.prefetch_related(
            'custodian_names', 'custodian_contacts', 'custodian_urls',
            'custodian_identifiers', 'custodian_buildings', 'custodian_owners',
            'custodian_editors',
        ).get(pk=self.target_id)

        # Fonds for this custodian
        fond_ids = list(RelCustodianFond.objects.filter(custodian_id=self.target_id).values_list('fond_id', flat=True))
        fonds = Fond.objects.filter(pk__in=fond_ids).prefetch_related(
            'events',
            'fond_names', 'fond_langs', 'fond_owners', 'fond_urls', 'fond_identifiers',
            'fond_editors',
            'units__unit_damages', 'units__unit_other_reference_numbers',
            'units__unit_langs', 'units__unit_urls', 'units__unit_identifiers',
            'units__unit_editors',
            'units__sc2_textual_elements', 'units__sc2_visual_elements',
            'units__sc2_authors', 'units__sc2_commissions',
            'units__sc2_techniques', 'units__sc2_scales',
            'units__iccd_damages',
        )

        # Collect projects
        projects = []
        for f in fonds:
            for p in f.projects.all():
                if p not in projects:
                    projects.append(p)

        rw.file_create(self.dest_file)
        rw.write_file_head(stylesheets)

        display_name = self._get_custodian_display_name(custodian)
        self._prv_write_header_and_footer(rw, display_name)
        self._prv_title_page(rw, display_name)
        rw.write_new_page()

        self._prv_h1(rw, display_name, report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_ARCHIMISTA_CUSTODIAN))
        rw.write_new_line()

        from archimista_python.archive.report_support import make_rtf
        make_rtf(rw, report_settings, 'custodian', custodian)

        if projects:
            rw.write_line_separator(separator_styleindex)
            self._prv_write_projects_info(rw, report_settings, projects)

        if fonds:
            rw.write_line_separator(separator_styleindex)
            self._prv_write_fonds_info(rw, report_settings, list(fonds), separator_styleindex)

        rw.write_file_tail()
        rw.file_close()

    def build_project_rtf_file(self, params, cookies):
        """Genera il file RTF per un report progetto."""
        rw = RtfWriter()

        report_settings = ReportSettings(
            rw, "project", "report per progetto", "project", None)

        report_settings.entity_add(EntityReportSettings('project', project_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('custodian', custodian_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('creator', creator_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('fond', fond_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('unit', unit_available_attributes_info(), False))

        stylesheets, stylesheet_codes = self._prv_build_rtf_stylesheets_info(
            report_settings, GCrwStylePredefinedCount)

        report_settings.initialize_entities_selected_attribute_names(params, cookies)
        report_settings.rtf_stylesheet_codes = stylesheet_codes
        report_settings.rtf_stylesheet_code_archimista_label = report_settings.get_attribute_rtf_stylesheet_code(
            CC_STYLESHEET_ARCHIMISTA_LABEL)

        separator_styleindex = report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_SEPARATOR)

        project = Project.objects.prefetch_related(
            'project_managers', 'project_stakeholders', 'project_urls'
        ).get(pk=self.target_id)

        # Fonds for this project
        fond_ids = list(RelProjectFond.objects.filter(project_id=self.target_id).values_list('fond_id', flat=True))
        fonds = Fond.objects.filter(pk__in=fond_ids).prefetch_related(
            'events',
            'fond_names', 'fond_langs', 'fond_owners', 'fond_urls', 'fond_identifiers',
            'fond_editors',
            'units__unit_damages', 'units__unit_other_reference_numbers',
            'units__unit_langs', 'units__unit_urls', 'units__unit_identifiers',
            'units__unit_editors',
            'units__sc2_textual_elements', 'units__sc2_visual_elements',
            'units__sc2_authors', 'units__sc2_commissions',
            'units__sc2_techniques', 'units__sc2_scales',
            'units__iccd_damages',
        )

        # Collect custodians
        custodians = []
        for f in fonds:
            for c in f.custodians.all():
                if c not in custodians:
                    custodians.append(c)
        custodians.sort(key=lambda x: x.display_name if hasattr(x, 'display_name') else "")

        rw.file_create(self.dest_file)
        rw.write_file_head(stylesheets)

        self._prv_write_header_and_footer(rw, project.name)

        title_parts = [project.name]
        dd = getattr(project, 'display_date', '')
        if dd:
            title_parts.append(str(dd))
        self._prv_title_page(rw, "\n".join(title_parts))
        rw.write_new_page()

        self._prv_h1(rw, project.name, report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_ARCHIMISTA_PROJECT))
        rw.write_new_line()

        from archimista_python.archive.report_support import make_rtf
        make_rtf(rw, report_settings, 'project', project)

        if custodians:
            rw.write_line_separator(separator_styleindex)
            custodian_index = 0
            custodian_count = len(custodians)
            for custodian in custodians:
                self._prv_h2(rw, "Soggetto conservatore")
                rw.write_new_line()
                self._prv_h3(rw, custodian.display_name if hasattr(custodian, 'display_name') else f"Conservatore #{custodian.pk}",
                            report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_ARCHIMISTA_CUSTODIAN))
                make_rtf(rw, report_settings, 'custodian', custodian)

                if getattr(custodian, 'fonds', None):
                    rw.write_line_separator(separator_styleindex)
                    self._prv_write_fonds_info(rw, report_settings, list(custodian.fonds.all()), separator_styleindex)

                if custodian_index < custodian_count - 1:
                    rw.write_line_separator(separator_styleindex)
                custodian_index += 1

        rw.write_file_tail()
        rw.file_close()

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _prv_write_header_and_footer(rw, header_text):
        rw.write_raw("\\facingp\\titlepg")
        rw.write_header(header_text, None, GCrwFontNameArial, 10, None, None, None,
                       GCrwTextAlignmentLeft, None, None, None, GCrwHeaderFooterPageLeft)
        rw.write_header(header_text, None, GCrwFontNameArial, 10, None, None, None,
                       GCrwTextAlignmentRight, None, None, None, GCrwHeaderFooterPageRight)
        rw.write_footer("pag. %PAGE% di %NUMPAGES%", None, GCrwFontNameArial, 10, None, None, None,
                       GCrwTextAlignmentLeft, None, None, None, GCrwHeaderFooterPageLeft)
        rw.write_footer("pag. %PAGE% di %NUMPAGES%", None, GCrwFontNameArial, 10, None, None, None,
                       GCrwTextAlignmentRight, None, None, None, GCrwHeaderFooterPageRight)

    @staticmethod
    def _prv_title_page(rw, s):
        rw.write_paragraph(s, GCrwStyleHeading, None, 18, GCrwFontBoldEnabled, None, None,
                          GCrwTextAlignmentCenter, None, None, None)

    @staticmethod
    def _prv_h1(rw, s, style_index=None):
        if style_index is None:
            style_index = GCrwStyleHeading1
        rw.write_paragraph(s, style_index, None, 16, GCrwFontBoldEnabled, None, None,
                          GCrwTextAlignmentJustified, None, None, None)

    @staticmethod
    def _prv_h2(rw, s, style_index=None):
        if style_index is None:
            style_index = GCrwStyleHeading2
        rw.write_paragraph(s, style_index, None, 14, GCrwFontBoldEnabled, None, None,
                          GCrwTextAlignmentJustified, None, None, None)

    @staticmethod
    def _prv_h3(rw, s, style_index=None):
        if style_index is None:
            style_index = GCrwStyleHeading3
        rw.write_paragraph(s, style_index, None, 12, GCrwFontBoldEnabled, None, None,
                          GCrwTextAlignmentJustified, None, None, None)

    @staticmethod
    def _prv_build_rtf_stylesheets_info(report_settings, start_code):
        """Crea gli stylesheet RTF personalizzati."""
        stylesheets = []
        stylesheet_codes = {}

        code = start_code

        # Predefined styles
        for label in [
            CC_STYLESHEET_ARCHIMISTA_LABEL,
            CC_STYLESHEET_ARCHIMISTA_SECTION_HEADER,
            CC_STYLESHEET_ARCHIMISTA_PROJECT,
            CC_STYLESHEET_ARCHIMISTA_FOND,
            CC_STYLESHEET_ARCHIMISTA_CUSTODIAN,
            CC_STYLESHEET_ARCHIMISTA_CREATOR,
            CC_STYLESHEET_ARCHIMISTA_UNIT,
            CC_STYLESHEET_UNIT_SEQUENCE_NUMBER,
        ]:
            stylesheets.append(
                f"{{\\s{code}\\widctlpar \\f1\\fs20 \\sbasedon0\\snext{code} {label};}}")
            stylesheet_codes[label] = code
            code += 1

        # Separator style (very small font)
        stylesheets.append(
            f"{{\\s{code}\\widctlpar \\f1\\fs4 \\sbasedon0\\snext{code} {CC_STYLESHEET_SEPARATOR};}}")
        stylesheet_codes[CC_STYLESHEET_SEPARATOR] = code
        code += 1

        # Attribute styles
        stylesheet_codes_key_prev = ""
        for ers in report_settings.entities:
            for key, ai in ers.available_attributes_info.items():
                stylesheet_codes_key = report_settings.make_attribute_rtf_stylesheet_codes_key(
                    str(ers.entity_name), ai.name)
                if stylesheet_codes_key != stylesheet_codes_key_prev:
                    stylesheets.append(
                        f"{{\\s{code}\\widctlpar \\f0\\fs20\\lang1040 \\sbasedon0\\snext{code} {stylesheet_codes_key};}}")
                    stylesheet_codes[stylesheet_codes_key] = code
                    code += 1
                    stylesheet_codes_key_prev = stylesheet_codes_key

        return stylesheets, stylesheet_codes

    @staticmethod
    def _prv_write_projects_info(rw, report_settings, projects):
        from archimista_python.archive.report_support import make_rtf
        plural = "Progetti" if len(projects) != 1 else "Progetto"
        rw.write_paragraph(plural, GCrwStyleHeading2)
        rw.write_new_line()
        for project in projects:
            display_name = project.display_name if hasattr(project, 'display_name') else project.name
            rw.write_paragraph(display_name, GCrwStyleHeading3,
                              report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_ARCHIMISTA_PROJECT))
            rw.write_new_line()
            make_rtf(rw, report_settings, 'project', project)

    @staticmethod
    def _prv_write_custodians_info(rw, report_settings, custodians):
        from archimista_python.archive.report_support import make_rtf
        plural = "Soggetti conservatori" if len(custodians) != 1 else "Soggetto conservatore"
        rw.write_paragraph(plural, GCrwStyleHeading2)
        rw.write_new_line()
        for c in custodians:
            dn = c.display_name if hasattr(c, 'display_name') else f"Conservatore #{getattr(c, 'pk', '?')}"
            rw.write_paragraph(dn, GCrwStyleHeading3,
                              report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_ARCHIMISTA_CUSTODIAN))
            rw.write_new_line()
            make_rtf(rw, report_settings, 'custodian', c)

    @staticmethod
    def _prv_write_creators_info(rw, report_settings, creators):
        from archimista_python.archive.report_support import make_rtf
        plural = "Soggetti produttori" if len(creators) != 1 else "Soggetto produttore"
        rw.write_paragraph(plural, GCrwStyleHeading2)
        rw.write_new_line()
        creators_sorted = sorted(creators, key=lambda x: x.display_name if hasattr(x, 'display_name') else "")
        for creator in creators_sorted:
            dn = creator.display_name if hasattr(creator, 'display_name') else f"Creatore #{getattr(creator, 'pk', '?')}"
            rw.write_paragraph(dn, GCrwStyleHeading3,
                              report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_ARCHIMISTA_CREATOR))
            rw.write_new_line()
            make_rtf(rw, report_settings, 'creator', creator)

    @staticmethod
    def _prv_write_units_info(rw, report_settings, units, display_sequence_numbers, separator_styleindex):
        from archimista_python.archive.report_support import make_rtf
        count = len(units) if isinstance(units, list) else units.count() if hasattr(units, 'count') else 0
        plural = "Unità" if count != 1 else "Unità"
        rw.write_paragraph(plural, GCrwStyleHeading2)
        rw.write_new_line()
        for u in units:
            seq = u.display_sequence_number_from_hash(display_sequence_numbers) if hasattr(u, 'display_sequence_number_from_hash') else ""
            rw.write_paragraph(str(seq), report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_UNIT_SEQUENCE_NUMBER),
                              None, 10, GCrwFontBoldEnabled, None, None, GCrwTextAlignmentJustified, None, None, None)
            rw.write_line_separator(separator_styleindex)
            formatted_title = u.formatted_title if hasattr(u, 'formatted_title') else (u.title or f"Unità #{getattr(u, 'pk', '?')}")
            rw.write_paragraph(formatted_title,
                              report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_ARCHIMISTA_UNIT))
            rw.write_new_line()
            make_rtf(rw, report_settings, 'unit', u)

    @staticmethod
    def _prv_write_fond_and_units_info(rw, report_settings, fond, separator_styleindex):
        from archimista_python.archive.report_support import make_rtf
        if getattr(fond, 'creators', None):
            rw.write_line_separator(separator_styleindex)
            RtfBuilder._prv_write_creators_info(rw, report_settings, list(fond.creators.all()))

        rw.write_line_separator(separator_styleindex)
        RtfBuilder._prv_h3(rw, fond.name, report_settings.get_attribute_rtf_stylesheet_code(CC_STYLESHEET_ARCHIMISTA_FOND))
        rw.write_new_line()
        make_rtf(rw, report_settings, 'fond', fond)

        if getattr(fond, 'units', None):
            display_sequence_numbers = Unit.display_sequence_numbers_of(fond)
            rw.write_line_separator(separator_styleindex)
            RtfBuilder._prv_write_units_info(rw, report_settings, list(fond.units.all()),
                                            display_sequence_numbers, separator_styleindex)

    @staticmethod
    def _prv_write_fonds_info(rw, report_settings, fonds, separator_styleindex):
        count = len(fonds) if isinstance(fonds, list) else fonds.count() if hasattr(fonds, 'count') else 0
        plural = "Fondi" if count != 1 else "Fondo"
        rw.write_paragraph(plural, GCrwStyleHeading2)
        rw.write_new_line()
        for fond in fonds:
            RtfBuilder._prv_write_fond_and_units_info(rw, report_settings, fond, separator_styleindex)

    @staticmethod
    def _get_custodian_display_name(custodian):
        pn = custodian.preferred_name if hasattr(custodian, 'preferred_name') else None
        if pn and hasattr(pn, 'name') and pn.name:
            return pn.name
        return f"Soggetto conservatore #{getattr(custodian, 'pk', '?')}"
