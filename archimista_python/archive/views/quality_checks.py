"""
Quality Checks views — porting da Ruby QualityChecksController.

Controlla la completezza e consistenza dei dati per:
- Fond (complesso archivistico)
- Creator (soggetto produttore)
- Custodian (soggetto conservatore)
"""
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from archimista_python.archive.models import Fond, Creator, Custodian, Project


def _pct(part, total):
    """Calcola la percentuale con 2 decimali, formato italiano."""
    if total == 0:
        return "0,00"
    return f"{part / total * 100:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


class QualityCheckIndexView(View):
    """Vista principale: lista fondi root, creatori, conservatori."""

    def get(self, request, *args, **kwargs):
        # Redirect diretto se viene passato un ID specifico
        if request.GET.get('fond_id'):
            from django.urls import reverse
            from django.http import HttpResponseRedirect
            url = reverse('archive:quality_check_fond', kwargs={'pk': request.GET['fond_id']})
            if request.GET.get('complete'):
                url += '?complete=1'
            return HttpResponseRedirect(url)

        if request.GET.get('creator_id'):
            from django.urls import reverse
            from django.http import HttpResponseRedirect
            url = reverse('archive:quality_check_creator', kwargs={'pk': request.GET['creator_id']})
            return HttpResponseRedirect(url)

        if request.GET.get('custodian_id'):
            from django.urls import reverse
            from django.http import HttpResponseRedirect
            url = reverse('archive:quality_check_custodian', kwargs={'pk': request.GET['custodian_id']})
            return HttpResponseRedirect(url)

        fonds = Fond.objects.filter(
            parent__isnull=True,
            trashed=False
        ).order_by('sequence_number')

        creators = list(Creator.objects.all().prefetch_related('creator_names'))
        creators.sort(key=lambda c: (c.preferred_name.name if c.preferred_name else ''))

        custodians = list(Custodian.objects.all().prefetch_related('custodian_names'))
        custodians.sort(key=lambda c: (c.preferred_name.name if c.preferred_name else ''))

        return render(request, 'archive/quality_check_index.html', {
            'fonds': fonds,
            'creators': creators,
            'custodians': custodians,
        })


class QualityCheckFondView(View):
    """Controllo qualità per un fondo (e tutto il suo sottoalbero)."""

    @staticmethod
    def _subtree_of(pk):
        """Porting di Ruby `Fond.subtree_of(pk)` — tutti i fondi il cui ancestry contiene pk."""
        pk_str = str(pk)
        return Fond.objects.filter(
            Q(pk=pk) |
            Q(ancestry=pk_str) |
            Q(ancestry__startswith=pk_str + '/') |
            Q(ancestry__endswith='/' + pk_str) |
            Q(ancestry__contains='/' + pk_str + '/')
        )

    def get(self, request, pk, *args, **kwargs):
        fond = get_object_or_404(Fond, pk=pk)

        # Ottieni tutto il sottoalbero attivo
        fonds = self._subtree_of(pk).filter(trashed=False).order_by('sequence_number')
        if not fonds.exists():
            fonds = Fond.objects.filter(pk=pk)

        # Campi minimi (requisiti)
        fonds_with_no_name = [f for f in fonds if not f.name or f.name.strip() == '' or f.name == '[nome non compilato]']
        fonds_with_no_event = [f for f in fonds if not f.preferred_event]
        fonds_with_no_fond_type = [f for f in fonds if not f.fond_type and not f.fond_type_term]

        # Campi per un record "decoroso" (requisiti medi)
        fonds_with_no_description = [f for f in fonds if not f.description or not f.description.strip()]
        fonds_with_no_history = [f for f in fonds if not f.history or not f.history.strip()]
        fonds_with_no_length = [f for f in fonds if not f.length]

        # Unità collegate
        fonds_with_no_units = []
        for f in fonds:
            if f.active_descendant_units_count == 0:
                fonds_with_no_units.append(f)

        fond_root_name = fonds.first().name if fonds.exists() else ''

        # Creator collegati
        fond_ids = [f.id for f in fonds]
        creators = list(Creator.objects.filter(
            rel_creator_fonds__fond_id__in=fond_ids
        ).prefetch_related('creator_names', 'events').distinct())
        creators.sort(key=lambda c: (c.preferred_name.name if c.preferred_name else ''))

        # Custodian collegati
        custodians = list(Custodian.objects.filter(
            rel_custodian_fonds__fond_id__in=fond_ids
        ).prefetch_related('custodian_names', 'custodian_buildings', 'events').distinct())
        custodians.sort(key=lambda c: (c.preferred_name.name if c.preferred_name else ''))

        # Progetti collegati
        projects = Project.objects.filter(
            rel_project_fonds__fond_id__in=fond_ids
        ).distinct()

        # Fonti collegate al fondo
        fonds_with_sources = Fond.objects.filter(
            pk__in=fond_ids,
            rel_fond_sources__isnull=False
        ).distinct()

        is_complete = request.GET.get('complete') == '1'

        # Calcola percentuali
        total = len(fonds)

        return render(request, 'archive/quality_check_fond.html', {
            'fond': fond,
            'fonds': fonds,
            'fond_root_name': fond_root_name,
            'fonds_with_no_name': fonds_with_no_name,
            'fonds_no_name_pct': _pct(len(fonds_with_no_name), total),
            'fonds_with_no_event': fonds_with_no_event,
            'fonds_no_event_pct': _pct(len(fonds_with_no_event), total),
            'fonds_with_no_fond_type': fonds_with_no_fond_type,
            'fonds_no_fond_type_pct': _pct(len(fonds_with_no_fond_type), total),
            'fonds_with_no_description': fonds_with_no_description,
            'fonds_no_description_pct': _pct(len(fonds_with_no_description), total),
            'fonds_with_no_history': fonds_with_no_history,
            'fonds_no_history_pct': _pct(len(fonds_with_no_history), total),
            'fonds_with_no_length': fonds_with_no_length,
            'fonds_no_length_pct': _pct(len(fonds_with_no_length), total),
            'fonds_with_no_units': fonds_with_no_units,
            'fonds_no_units_pct': _pct(len(fonds_with_no_units), total),
            'creators': creators,
            'custodians': custodians,
            'projects': projects,
            'fonds_with_sources': fonds_with_sources,
            'is_complete': is_complete,
            'total': total,
        })


class QualityCheckCreatorView(View):
    """Controllo qualità per un soggetto produttore."""

    def get(self, request, pk, *args, **kwargs):
        creator = get_object_or_404(Creator, pk=pk)

        return render(request, 'archive/quality_check_creator.html', {
            'creator': creator,
        })


class QualityCheckCustodianView(View):
    """Controllo qualità per un soggetto conservatore."""

    def get(self, request, pk, *args, **kwargs):
        custodian = get_object_or_404(Custodian, pk=pk)

        return render(request, 'archive/quality_check_custodian.html', {
            'custodian': custodian,
        })
