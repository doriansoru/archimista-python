"""
Export AEF views — single entity and batch export to .aef format.
Supports: Fond, Custodian, Project, Creator, Source.
Options: include_digital_objects, include_entities (mode full/not-full),
         SAN XML export, EAD/ICAR-IMPORT export.
"""

import datetime
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from archimista_python.archive.aef_exporter import AEFExporter
from archimista_python.archive.models import Fond, Custodian, Project, Unit, Creator, Source


class ExportAEFView(View):
    """Batch export AEF — select target entity and options."""
    template_name = 'archive/export_aef_form.html'

    def get(self, request):
        context = {
            'root_fonds': Fond.objects.filter(parent_id__isnull=True, trashed=False).order_by('name')[:100],
            'custodians': Custodian.objects.all().order_by('legal_status')[:100],
            'projects': Project.objects.all().order_by('name')[:100],
            'creators': Creator.objects.all().order_by('creator_type')[:100],
            'sources': Source.objects.all().order_by('title')[:100],
        }
        return render(request, self.template_name, context)

    def post(self, request):
        export_type = request.POST.get('export_type', 'fond')
        include_digital = request.POST.get('include_digital_objects', 'on') == 'on'
        include_entities = request.POST.get('include_entities', 'on') == 'on'
        inc_san = request.POST.get('inc_san', 'on') == 'on'
        inc_ead = request.POST.get('inc_ead', 'on') == 'on'
        mode = 'full' if include_entities else 'not-full'

        # Determine target ID and label
        target_id = None
        exporter_kwargs = {'mode': mode, 'include_digital_objects': include_digital}
        filename_base = 'export'

        try:
            if export_type == 'fond':
                target_id = request.POST.get('fond_id')
                if not target_id:
                    messages.error(request, 'Seleziona un fondo.')
                    return self.get(request)
                exporter_kwargs['fond_id'] = int(target_id)
                fond = Fond.objects.get(pk=target_id)
                filename_base = fond.name.replace(' ', '_')[:30] if fond.name else 'fond'
            elif export_type == 'custodian':
                target_id = request.POST.get('custodian_id')
                if not target_id:
                    messages.error(request, 'Seleziona un soggetto conservatore.')
                    return self.get(request)
                exporter_kwargs['custodian_id'] = int(target_id)
                custodian = Custodian.objects.get(pk=target_id)
                pref_name = custodian.custodian_names.filter(preferred=True).first()
                filename_base = (pref_name.name if pref_name else f"custodian-{target_id}").replace(' ', '_')[:30]
            elif export_type == 'project':
                target_id = request.POST.get('project_id')
                if not target_id:
                    messages.error(request, 'Seleziona un progetto.')
                    return self.get(request)
                exporter_kwargs['project_id'] = int(target_id)
                exporter_kwargs['mode'] = 'full'  # Projects always full
                project = Project.objects.get(pk=target_id)
                filename_base = project.name.replace(' ', '_')[:30] if project.name else 'project'
            elif export_type == 'creator':
                target_id = request.POST.get('creator_id')
                if not target_id:
                    messages.error(request, 'Seleziona un soggetto produttore.')
                    return self.get(request)
                exporter_kwargs['creator_id'] = int(target_id)
                creator = Creator.objects.get(pk=target_id)
                pref_name = creator.creator_names.filter(preferred=True).first()
                filename_base = (pref_name.name if pref_name and pref_name.name else
                                 f"{pref_name.first_name} {pref_name.last_name}" if pref_name else
                                 f"creator-{target_id}").replace(' ', '_')[:30]
            elif export_type == 'source':
                target_id = request.POST.get('source_id')
                if not target_id:
                    messages.error(request, 'Seleziona una fonte.')
                    return self.get(request)
                exporter_kwargs['source_id'] = int(target_id)
                source = Source.objects.get(pk=target_id)
                filename_base = (source.title or f"source-{target_id}").replace(' ', '_')[:30]
            else:
                messages.error(request, 'Tipo di esportazione non valido.')
                return self.get(request)

            exporter = AEFExporter(**exporter_kwargs)

            # Determine export format
            if inc_san:
                zip_bytes = exporter.run_xml_export('san')
                ext = 'xml'
            elif inc_ead:
                zip_bytes = exporter.run_xml_export('ead')
                ext = 'xml'
            else:
                zip_bytes = exporter.run()
                ext = 'aef'

            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"archimista-export_{filename_base}-{timestamp}.{ext}"

            response = HttpResponse(zip_bytes, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except Exception as e:
            messages.error(request, f'Errore durante l\'esportazione: {str(e)}')
            return self.get(request)


class ExportFondAEFView(View):
    """Export a single fond (with subtree) to AEF."""

    def get(self, request, pk):
        fond = get_object_or_404(Fond, pk=pk)
        try:
            exporter = AEFExporter(
                fond_id=fond.id,
                mode='full',
                include_digital_objects=True,
            )
            zip_bytes = exporter.run()

            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename_base = fond.name.replace(' ', '_')[:30] if fond.name else 'fond'
            filename = f"archimista-export_{filename_base}-{timestamp}.aef"

            response = HttpResponse(zip_bytes, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            messages.error(request, f'Errore durante l\'esportazione: {str(e)}')
            return HttpResponseRedirect(reverse('archive:fond_detail', kwargs={'pk': pk}))


class ExportUnitsAEFView(View):
    """Export selected units to AEF."""
    template_name = 'archive/export_units_aef.html'

    def post(self, request):
        unit_ids_str = request.POST.getlist('unit_ids', [])
        unit_ids = [int(uid) for uid in unit_ids_str if uid.isdigit()]

        if not unit_ids:
            messages.error(request, 'Nessuna unità selezionata.')
            return HttpResponseRedirect(reverse('archive:unit_list'))

        try:
            exporter = AEFExporter(
                unit_ids=unit_ids,
                mode='single',
                include_digital_objects=True,
            )
            zip_bytes = exporter.run()

            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"archimista-export_units-{timestamp}.aef"

            response = HttpResponse(zip_bytes, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            messages.error(request, f'Errore durante l\'esportazione: {str(e)}')
            return HttpResponseRedirect(reverse('archive:unit_list'))
