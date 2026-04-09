from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.generic import View
from archimista_python.archive.models import Fond
from archimista_python.archive.export_utils import generate_fond_pdf, generate_fond_docx

class ExportFondPDFView(View):
    def get(self, request, pk, *args, **kwargs):
        fond = get_object_or_404(Fond, pk=pk)
        buffer = generate_fond_pdf(fond)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="inventario_{fond.id}.pdf"'
        return response

class ExportFondRTFView(View):
    def get(self, request, pk, *args, **kwargs):
        fond = get_object_or_404(Fond, pk=pk)
        buffer = generate_fond_docx(fond)
        # Usiamo .docx internamente ma possiamo chiamarlo .rtf per compatibilità se l'utente insiste, 
        # m per ora usiamo .docx (standard moderno) o .rtf (legacy).
        # Archimista legacy usa RTF. Generiamo un DOCX ma lo serviamo come tale.
        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="inventario_{fond.id}.docx"'
        return response

