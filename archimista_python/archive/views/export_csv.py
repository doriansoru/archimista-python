"""
Export CSV — export units to CSV format.
"""

import csv
import io
import datetime
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render

from archimista_python.archive.models import Unit, Fond


class ExportUnitsCSVView(View):
    """Export units (optionally filtered) to CSV."""
    template_name = 'archive/export_units_csv.html'

    def get(self, request):
        """Show export options form."""
        context = {
            'fonds': Fond.objects.filter(parent_id__isnull=True, trashed=False).order_by('name')[:100],
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Generate and download CSV."""
        fond_id = request.POST.get('fond_id')
        query = request.POST.get('query', '').strip()

        units = Unit.objects.all()

        # Filter by fond
        if fond_id:
            units = units.filter(fond_id=int(fond_id))

        # Filter by search query
        if query:
            units = units.filter(title__icontains=query) | units.filter(reference_number__icontains=query)

        units = units.order_by('sequence_number')

        # Build CSV
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow([
            'ID', 'Segnatura', 'Titolo', 'Attribuito', 'Contenuto',
            'Tipo unità', 'Fondo', 'Padre',
            'Condizione accesso', 'Nota accesso',
            'Condizione uso', 'Nota uso',
            'Stato conservazione', 'Tipo fisico', 'Supporto',
            'Descrizione fisica', 'Consistenza',
            'Pubblicato', 'Nota',
        ])

        # Data
        for unit in units:
            fond_name = unit.fond.name if unit.fond else ''
            parent_title = unit.parent.title if unit.parent else ''

            writer.writerow([
                unit.id,
                unit.reference_number or '',
                unit.title or '',
                'Sì' if unit.given_title else '',
                unit.content or '',
                unit.unit_type or '',
                fond_name,
                parent_title,
                unit.access_condition or '',
                unit.access_condition_note if hasattr(unit, 'access_condition_note') else '',
                unit.use_condition or '',
                unit.use_condition_note if hasattr(unit, 'use_condition_note') else '',
                unit.preservation or '',
                unit.physical_type or '',
                unit.medium or '',
                unit.physical_description or '',
                unit.extent or '',
                'Sì' if unit.published else 'No',
                unit.note or '',
            ])

        # Build response
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"archimista_units_export-{timestamp}.csv"

        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
