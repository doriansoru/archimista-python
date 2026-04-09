from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q
from archimista_python.archive.models import Fond, Unit, Heading, DigitalObject

class GlobalSearchView(View):
    template_name = 'archive/search_results.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        results = {
            'fonds': [],
            'units': [],
            'headings': [],
            'digital_objects': []
        }
        
        if query:
            results['fonds'] = Fond.objects.filter(
                Q(name__icontains=query) | 
                Q(abstract__icontains=query) | 
                Q(history__icontains=query)
            ).distinct()
            
            results['units'] = Unit.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) | 
                Q(reference_number__icontains=query)
            ).distinct()
            
            results['headings'] = Heading.objects.filter(
                Q(name__icontains=query)
            ).distinct()
            
            results['digital_objects'] = DigitalObject.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            ).distinct()

        return render(request, self.template_name, {
            'query': query,
            'results': results,
            'total_count': len(results['fonds']) + len(results['units']) + 
                           len(results['headings']) + len(results['digital_objects'])
        })

