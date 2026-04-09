from django.views.generic import ListView
from django.db.models import Q
from archimista_python.archive.models import Unit, Fond


class UnitListView(ListView):
    """Lista globale di tutte le unità, con filtro opzionale per fondo.
    Mostra anche le unità orfane (senza fondo associato).
    Ruby: units_controller#index
    """
    model = Unit
    template_name = 'archive/unit_list.html'
    context_object_name = 'units'
    paginate_by = 50

    def get_queryset(self):
        qs = Unit.objects.select_related('fond', 'parent').order_by('fond_id', 'position')

        # Filtro per fondo
        fond_id = self.request.GET.get('fond_id')
        if fond_id:
            qs = qs.filter(fond_id=fond_id)

        # Filtro per ricerca libera
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(reference_number__icontains=q) |
                Q(content__icontains=q)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fonds'] = Fond.objects.filter(parent__isnull=True, trashed=False).order_by('name')
        context['selected_fond_id'] = self.request.GET.get('fond_id')
        context['q'] = self.request.GET.get('q', '')

        # Conteggio unità orfane
        context['orphan_count'] = Unit.objects.filter(fond__isnull=True).count()

        return context
