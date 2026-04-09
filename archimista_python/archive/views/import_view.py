from django.shortcuts import render
from django.views.generic import View
from archimista_python.archive.import_utils import AEFImporter
import tempfile
import os

class ImportAEFView(View):
    template_name = 'archive/import_form.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        aef_file = request.FILES.get('aef_file')
        if not aef_file:
            return render(request, self.template_name, {'error': 'Nessun file caricato.'})
        
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.aef') as tmp:
            for chunk in aef_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            importer = AEFImporter(tmp_path)
            importer.run()
            return render(request, self.template_name, {'success': 'Importazione completata con successo!'})
        except Exception as e:
            return render(request, self.template_name, {'error': f"Errore durante l'importazione: {str(e)}"})
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

# Views per Unit
