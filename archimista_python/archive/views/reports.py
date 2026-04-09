"""
Reports — viste per la generazione di report PDF e RTF.
Porting di ReportsController + RtfBuilder da Ruby.
PDF: HTML template → WeasyPrint (come Ruby usa HTML ERB → wkhtmltopdf/PDFKit).
RTF: RtfBuilder + RtfWriter (come Ruby).
"""

import os
import time
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Q

from archimista_python.archive.models import (
    Project, Custodian, Fond, Unit, Creator,
    RelCustodianFond, RelProjectFond, RelCreatorFond,
)
from archimista_python.archive.report_support import (
    ReportSettings, EntityReportSettings,
    fond_available_attributes_info, custodian_available_attributes_info,
    creator_available_attributes_info, unit_available_attributes_info,
    project_available_attributes_info,
    make_html,
)
from archimista_python.archive.rtf_builder import RtfBuilder


# ──────────────────────────────────────────────────────────────────────────────
# Helper: tree ordering (come Ruby tree_array)
# ──────────────────────────────────────────────────────────────────────────────

def _tree_ordered_ids(base_ids):
    """Restituisce gli ID dei fondi in ordine ad albero (pre-order traversal)."""
    result = []
    stack = list(base_ids)
    while stack:
        node_id = stack.pop(0)
        result.append(node_id)
        children = list(Fond.objects.filter(parent_id=node_id).order_by('position').values_list('pk', flat=True))
        stack = children + stack  # prepend children
    return result


def _get_fond_subtree(fond_id):
    """Ottiene tutti i fondi nel sottoalbero, ordinati come in Ruby."""
    fond = Fond.objects.get(pk=fond_id)
    subtree_ids = fond.subtree_ids if hasattr(fond, 'subtree_ids') else [fond_id]
    tree_order = _tree_ordered_ids([fond_id])

    # Solo prefetch per relazioni dirette (no nested attraverso properties)
    fonds = Fond.objects.filter(pk__in=subtree_ids).prefetch_related(
        'events',
        'fond_names', 'fond_langs', 'fond_owners', 'fond_urls', 'fond_identifiers',
        'fond_editors',
        'units__unit_damages', 'units__unit_other_reference_numbers',
        'units__unit_langs', 'units__unit_urls', 'units__unit_identifiers',
        'units__unit_editors',
        'units__sc2_textual_elements', 'units__sc2_visual_elements',
        'units__sc2_authors__sc2_attribution_reasons',
        'units__sc2_commissions__sc2_commission_names',
        'units__sc2_techniques', 'units__sc2_scales',
        'units__fsc_codes', 'units__fsc_organizations', 'units__fsc_nationalities',
        'units__fsc_opens', 'units__fsc_closes',
        'units__fe_identifications', 'units__fe_contexts', 'units__fe_operas',
        'units__fe_designers', 'units__fe_cadastrals', 'units__fe_land_parcels',
        'units__fe_fract_land_parcels', 'units__fe_fract_edil_parcels',
        'units__iccd_damages',
    )

    # Sort by tree order
    fond_map = {f.pk: f for f in fonds}
    ordered = []
    for fid in tree_order:
        if fid in fond_map:
            ordered.append(fond_map[fid])
    return ordered


# ──────────────────────────────────────────────────────────────────────────────
# Report Index
# ──────────────────────────────────────────────────────────────────────────────

class ReportIndexView(View):
    """Pagina indice per i report."""
    template_name = 'archive/report_index.html'

    def get(self, request):
        context = {
            'projects': Project.objects.all().order_by('name'),
            'custodians': Custodian.objects.all().order_by('legal_status'),
            'fonds': Fond.objects.filter(parent__isnull=True).order_by('sequence_number'),
        }
        return render(request, self.template_name, context)


# ──────────────────────────────────────────────────────────────────────────────
# Inventory Report (per fondo — complesso archivistico)
# ──────────────────────────────────────────────────────────────────────────────

class InventoryReportView(View):
    """Report inventario per un fondo (complesso archivistico). PDF + RTF."""

    def get(self, request, pk):
        fond = get_object_or_404(Fond, pk=pk)

        # Setup report settings (same as Ruby)
        report_settings = ReportSettings(None, "inventory", "Inventario di complesso archivistico", "inventory", None)
        report_settings.entity_add(EntityReportSettings('project', project_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('custodian', custodian_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('creator', creator_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('fond', fond_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('unit', unit_available_attributes_info(), False))
        report_settings.initialize_entities_selected_attribute_names(request.GET, request.COOKIES)

        # Fetch subtree
        fonds = _get_fond_subtree(pk)
        root_fond = fonds[0] if fonds else fond
        display_sequence_numbers = Unit.display_sequence_numbers_of(root_fond)

        fmt = request.GET.get('format', 'html')

        # Pre-compute HTML for each entity (since Django templates can't call make_html directly)
        fonds_data = []
        for fond in fonds:
            creators_sorted = sorted(list(fond.creators.all()), key=lambda x: x.display_name if hasattr(x, 'display_name') else "")
            creators_data = [(c, make_html(report_settings, 'creator', c)) for c in creators_sorted]
            custodians_data = [(c, make_html(report_settings, 'custodian', c)) for c in fond.custodians.all()]
            projects_data = [(p, make_html(report_settings, 'project', p)) for p in fond.projects.all()]
            # Pre-compute sequence number for units
            units_data = []
            for u in fond.units.all():
                seq_num = ""
                if hasattr(u, 'display_sequence_number_from_hash'):
                    seq_num = u.display_sequence_number_from_hash(display_sequence_numbers)
                units_data.append((u, make_html(report_settings, 'unit', u), seq_num))
            fond_html = make_html(report_settings, 'fond', fond)

            fonds_data.append({
                'fond': fond,
                'fond_html': fond_html,
                'creators_data': creators_data,
                'custodians_data': custodians_data,
                'projects_data': projects_data,
                'units_data': units_data,
            })

        if fmt == 'pdf':
            return self._generate_pdf(request, 'archive/inventory_report.html', {
                'fonds_data': fonds_data,
                'root_fond': root_fond,
                'display_sequence_numbers': display_sequence_numbers,
                'report_settings': report_settings,
            }, f"inventory-{int(time.time())}.pdf")
        elif fmt == 'rtf':
            return self._generate_rtf(request, fond.pk, f"inventory-{int(time.time())}.rtf",
                                     request.GET, request.COOKIES, 'fond')
        else:
            # HTML preview
            return render(request, 'archive/inventory_report.html', {
                'fonds_data': fonds_data,
                'root_fond': root_fond,
                'display_sequence_numbers': display_sequence_numbers,
                'report_settings': report_settings,
            })

    @staticmethod
    def _generate_pdf(request, template_name, context, filename):
        """Genera PDF da HTML template usando WeasyPrint."""
        html_content = render(request, template_name, context)
        html_str = html_content.content.decode('utf-8')

        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration

            font_config = FontConfiguration()
            html_doc = HTML(string=html_str, base_url=request.build_absolute_uri('/'))
            css = CSS(string="""
                @page {
                    size: A4;
                    margin: 2.5cm 2cm 2.5cm 2cm;
                    @bottom-center {
                        content: "pag. " counter(page) " di " counter(pages);
                        font-size: 8pt;
                    }
                }
                body { font-family: Arial, sans-serif; font-size: 10pt; }
                h2 { font-size: 16pt; font-weight: bold; }
                h3 { font-size: 14pt; font-weight: bold; }
                h4 { font-size: 12pt; font-weight: bold; }
                .fldcaption { margin-top: 12px; margin-bottom: 2px; }
                .field-header { font-weight: bold; }
                .pbi_avoid { page-break-inside: avoid; }
                hr { border: none; border-bottom: 1px solid #000; margin: 10px 0; }
            """, font_config=font_config)

            pdf = html_doc.write_pdf(stylesheets=[css], font_config=font_config)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except ImportError:
            # Fallback se WeasyPrint non è installato
            response = HttpResponse(html_str, content_type='text/html')
            return response

    @staticmethod
    def _generate_rtf(request, fond_id, filename, params, cookies, entity_type):
        """Genera RTF usando RtfBuilder."""
        downloads_dir = getattr(settings, 'MEDIA_ROOT', '/tmp')
        dest_file = os.path.join(downloads_dir, filename)

        builder = RtfBuilder(target_id=fond_id, dest_file=dest_file)
        builder.build_fond_rtf_file(params, cookies)

        if os.path.exists(dest_file):
            with open(dest_file, 'rb') as f:
                content = f.read()
            response = HttpResponse(content, content_type='application/rtf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            # Clean up
            os.remove(dest_file)
            return response
        return HttpResponse("Errore nella generazione RTF", status=500)


# ──────────────────────────────────────────────────────────────────────────────
# Project Report
# ──────────────────────────────────────────────────────────────────────────────

class ProjectReportView(View):
    """Report per progetto. PDF + RTF."""

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        # Setup report settings
        report_settings = ReportSettings(None, "project", "report per progetto", "project", None)
        report_settings.entity_add(EntityReportSettings('project', project_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('custodian', custodian_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('creator', creator_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('fond', fond_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('unit', unit_available_attributes_info(), False))
        report_settings.initialize_entities_selected_attribute_names(request.GET, request.COOKIES)

        # Fetch data
        fond_ids = list(RelProjectFond.objects.filter(project_id=pk).values_list('fond_id', flat=True))
        fonds = Fond.objects.filter(pk__in=fond_ids).prefetch_related(
            'events',
            'fond_names', 'fond_langs', 'fond_owners', 'fond_urls', 'fond_identifiers',
            'fond_editors',
            'units__unit_damages', 'units__unit_other_reference_numbers',
            'units__unit_langs', 'units__unit_urls', 'units__unit_identifiers',
            'units__unit_editors',
            'units__sc2_textual_elements', 'units__sc2_visual_elements',
            'units__sc2_authors__sc2_attribution_reasons',
            'units__sc2_commissions__sc2_commission_names',
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

        fmt = request.GET.get('format', 'html')

        # Pre-compute HTML
        fonds_data = []
        for fond in fonds:
            creators_sorted = sorted(list(fond.creators.all()), key=lambda x: x.display_name if hasattr(x, 'display_name') else "")
            creators_data = [(c, make_html(report_settings, 'creator', c)) for c in creators_sorted]
            # Pre-compute sequence number for units
            display_seq = Unit.display_sequence_numbers_of(fond) if hasattr(Unit, 'display_sequence_numbers_of') else {}
            units_data = []
            for u in fond.units.all():
                seq_num = ""
                if hasattr(u, 'display_sequence_number_from_hash'):
                    seq_num = u.display_sequence_number_from_hash(display_seq)
                units_data.append((u, make_html(report_settings, 'unit', u), seq_num))
            fond_html = make_html(report_settings, 'fond', fond)
            fonds_data.append({
                'fond': fond,
                'fond_html': fond_html,
                'creators_data': creators_data,
                'units_data': units_data,
            })

        custodians_data = [(c, make_html(report_settings, 'custodian', c)) for c in custodians]
        project_html = make_html(report_settings, 'project', project)

        if fmt == 'pdf':
            return InventoryReportView._generate_pdf(request, 'archive/project_report.html', {
                'project': project,
                'project_html': project_html,
                'custodians_data': custodians_data,
                'fonds_data': fonds_data,
                'report_settings': report_settings,
            }, f"project-{int(time.time())}.pdf")
        elif fmt == 'rtf':
            return self._generate_rtf(request, pk, f"project-{int(time.time())}.rtf",
                                     request.GET, request.COOKIES)
        else:
            return render(request, 'archive/project_report.html', {
                'project': project,
                'project_html': project_html,
                'custodians_data': custodians_data,
                'fonds_data': fonds_data,
                'report_settings': report_settings,
            })

    @staticmethod
    def _generate_rtf(request, project_id, filename, params, cookies):
        downloads_dir = getattr(settings, 'MEDIA_ROOT', '/tmp')
        dest_file = os.path.join(downloads_dir, filename)

        builder = RtfBuilder(target_id=project_id, dest_file=dest_file)
        builder.build_project_rtf_file(params, cookies)

        if os.path.exists(dest_file):
            with open(dest_file, 'rb') as f:
                content = f.read()
            response = HttpResponse(content, content_type='application/rtf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            os.remove(dest_file)
            return response
        return HttpResponse("Errore nella generazione RTF", status=500)


# ──────────────────────────────────────────────────────────────────────────────
# Custodian Report
# ──────────────────────────────────────────────────────────────────────────────

class CustodianReportView(View):
    """Report per soggetto conservatore. PDF + RTF."""

    def get(self, request, pk):
        custodian = get_object_or_404(Custodian, pk=pk)

        # Setup report settings
        report_settings = ReportSettings(None, "custodian", "Report per conservatore", "custodian", None)
        report_settings.entity_add(EntityReportSettings('custodian', custodian_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('project', project_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('creator', creator_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('fond', fond_available_attributes_info(), False))
        report_settings.entity_add(EntityReportSettings('unit', unit_available_attributes_info(), False))
        report_settings.initialize_entities_selected_attribute_names(request.GET, request.COOKIES)

        # Fetch data
        fond_ids = list(RelCustodianFond.objects.filter(custodian_id=pk).values_list('fond_id', flat=True))
        fonds = Fond.objects.filter(pk__in=fond_ids).prefetch_related(
            'events',
            'fond_names', 'fond_langs', 'fond_owners', 'fond_urls', 'fond_identifiers',
            'fond_editors',
            'units__unit_damages', 'units__unit_other_reference_numbers',
            'units__unit_langs', 'units__unit_urls', 'units__unit_identifiers',
            'units__unit_editors',
            'units__sc2_textual_elements', 'units__sc2_visual_elements',
            'units__sc2_authors__sc2_attribution_reasons',
            'units__sc2_commissions__sc2_commission_names',
            'units__sc2_techniques', 'units__sc2_scales',
            'units__iccd_damages',
        )

        # Collect projects
        projects = []
        for f in fonds:
            for p in f.projects.all():
                if p not in projects:
                    projects.append(p)

        display_name = _get_custodian_display_name(custodian)

        fmt = request.GET.get('format', 'html')

        # Pre-compute HTML
        fonds_data = []
        for fond in fonds:
            creators_sorted = sorted(list(fond.creators.all()), key=lambda x: x.display_name if hasattr(x, 'display_name') else "")
            creators_data = [(c, make_html(report_settings, 'creator', c)) for c in creators_sorted]
            # Pre-compute sequence number for units
            display_seq = Unit.display_sequence_numbers_of(fond) if hasattr(Unit, 'display_sequence_numbers_of') else {}
            units_data = []
            for u in fond.units.all():
                seq_num = ""
                if hasattr(u, 'display_sequence_number_from_hash'):
                    seq_num = u.display_sequence_number_from_hash(display_seq)
                units_data.append((u, make_html(report_settings, 'unit', u), seq_num))
            fond_html = make_html(report_settings, 'fond', fond)
            fonds_data.append({
                'fond': fond,
                'fond_html': fond_html,
                'creators_data': creators_data,
                'units_data': units_data,
            })

        projects_data = [(p, make_html(report_settings, 'project', p)) for p in projects]
        custodian_html = make_html(report_settings, 'custodian', custodian)

        if fmt == 'pdf':
            return InventoryReportView._generate_pdf(request, 'archive/custodian_report.html', {
                'custodian': custodian,
                'display_name': display_name,
                'custodian_html': custodian_html,
                'fonds_data': fonds_data,
                'projects_data': projects_data,
                'report_settings': report_settings,
            }, f"custodian-{int(time.time())}.pdf")
        elif fmt == 'rtf':
            return self._generate_rtf(request, pk, f"custodian-{int(time.time())}.rtf",
                                     request.GET, request.COOKIES)
        else:
            return render(request, 'archive/custodian_report.html', {
                'custodian': custodian,
                'display_name': display_name,
                'custodian_html': custodian_html,
                'fonds_data': fonds_data,
                'projects_data': projects_data,
                'report_settings': report_settings,
            })

    @staticmethod
    def _generate_rtf(request, custodian_id, filename, params, cookies):
        downloads_dir = getattr(settings, 'MEDIA_ROOT', '/tmp')
        dest_file = os.path.join(downloads_dir, filename)

        builder = RtfBuilder(target_id=custodian_id, dest_file=dest_file)
        builder.build_custodian_rtf_file(params, cookies)

        if os.path.exists(dest_file):
            with open(dest_file, 'rb') as f:
                content = f.read()
            response = HttpResponse(content, content_type='application/rtf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            os.remove(dest_file)
            return response
        return HttpResponse("Errore nella generazione RTF", status=500)


# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────

def _get_custodian_display_name(custodian):
    """Ottiene il nome visualizzabile del conservatore."""
    pn = custodian.preferred_name if hasattr(custodian, 'preferred_name') else None
    if pn and hasattr(pn, 'name') and pn.name:
        return pn.name
    return f"Soggetto conservatore #{getattr(custodian, 'pk', '?')}"
