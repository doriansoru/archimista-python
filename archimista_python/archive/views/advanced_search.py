"""
Advanced Search — multi-filter search across entities.
"""

from django.views import View
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator

from archimista_python.archive.models import (
    Fond, Unit, Creator, Custodian, Heading, Source, Project,
    Institution, DocumentForm, Anagraphic,
)


class AdvancedSearchView(View):
    """Advanced search with multiple filters across entities."""
    template_name = 'archive/advanced_search.html'

    def get(self, request):
        query = request.GET.get('q', '').strip()
        entity_type = request.GET.get('entity_type', 'all')
        fond_id = request.GET.get('fond_id')
        unit_type = request.GET.get('unit_type')
        creator_type = request.GET.get('creator_type')
        published_only = request.GET.get('published_only') == 'on'

        results = []
        result_type = ''

        # Build querysets based on entity type
        if entity_type in ('all', 'fond'):
            fonds = Fond.objects.filter(trashed=False)
            if query:
                fonds = fonds.filter(
                    Q(name__icontains=query) |
                    Q(abstract__icontains=query) |
                    Q(description__icontains=query) |
                    Q(history__icontains=query)
                )
            if published_only:
                fonds = fonds.filter(published=True)
            results.extend([('fond', f) for f in fonds.order_by('name')[:50]])

        if entity_type in ('all', 'unit'):
            units = Unit.objects.all()
            if query:
                units = units.filter(
                    Q(title__icontains=query) |
                    Q(reference_number__icontains=query) |
                    Q(content__icontains=query)
                )
            if fond_id:
                units = units.filter(fond_id=int(fond_id))
            if unit_type:
                units = units.filter(unit_type=unit_type)
            if published_only:
                units = units.filter(published=True)
            results.extend([('unit', u) for u in units.order_by('sequence_number')[:100]])

        if entity_type in ('all', 'creator'):
            creators = Creator.objects.all()
            if query:
                # Creator doesn't have a direct name field; search via abstract/history
                creators = creators.filter(
                    Q(abstract__icontains=query) |
                    Q(history__icontains=query) |
                    Q(residence__icontains=query)
                )
            if creator_type:
                creators = creators.filter(creator_type=creator_type)
            if published_only:
                creators = creators.filter(published=True)
            results.extend([('creator', c) for c in creators.order_by('creator_type')[:50]])

        if entity_type in ('all', 'custodian'):
            custodians = Custodian.objects.all()
            if query:
                # Custodian doesn't have a direct name field; search via holdings/history
                custodians = custodians.filter(
                    Q(holdings__icontains=query) |
                    Q(history__icontains=query)
                )
            if published_only:
                custodians = custodians.filter(published=True)
            results.extend([('custodian', c) for c in custodians.order_by('legal_status')[:50]])

        if entity_type in ('all', 'heading'):
            headings = Heading.objects.all()
            if query:
                headings = headings.filter(
                    Q(name__icontains=query)
                )
            results.extend([('heading', h) for h in headings.order_by('name')[:50]])

        if entity_type in ('all', 'source'):
            sources = Source.objects.all()
            if query:
                sources = sources.filter(
                    Q(title__icontains=query) |
                    Q(author__icontains=query) |
                    Q(abstract__icontains=query)
                )
            results.extend([('source', s) for s in sources.order_by('year')[:50]])

        if entity_type in ('all', 'project'):
            projects = Project.objects.all()
            if query:
                projects = projects.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query)
                )
            results.extend([('project', p) for p in projects.order_by('name')[:50]])

        # Pagination
        paginator = Paginator(results, 50)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'query': query,
            'entity_type': entity_type,
            'fond_id': fond_id,
            'unit_type': unit_type,
            'creator_type': creator_type,
            'published_only': request.GET.get('published_only') == 'on',
            'page_obj': page_obj,
            'results_count': len(results),
            # Filter options
            'fonds': Fond.objects.filter(parent_id__isnull=True, trashed=False).order_by('name')[:100],
        }
        return render(request, self.template_name, context)
