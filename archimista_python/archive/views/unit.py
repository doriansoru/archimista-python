from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, DeleteView, View
from django.urls import reverse_lazy
from django.db import transaction
from django.db import models
from django.contrib.contenttypes.models import ContentType
from archimista_python.archive.models import Unit, Event
from archimista_python.archive.forms import UnitForm
from archimista_python.archive.views.unit_formsets import (
    UnitExtensionsHandler,
    EventHandler,
    SC2Handler,
    ICCDHandler,
    FSCHandler,
    FEHandler,
    build_unit_context,
)


class UnitCreateView(View):
    """Vista per creare nuova unità con tutte le schede specialistiche.

    Orchestratore: delega la gestione dei 37 form/formset agli handler.
    """
    template_name = 'archive/unit_form.html'

    def get(self, request, *args, **kwargs):
        fond_id = request.GET.get('fond_id')
        parent_id = request.GET.get('parent_id')

        initial = {}
        if fond_id:
            initial['fond'] = fond_id
        if parent_id:
            initial['parent'] = parent_id
        unit_form = UnitForm(initial=initial)

        # Build all formsets via handlers
        extensions = UnitExtensionsHandler.build_formsets()
        event_formset = EventHandler.build_formset()
        sc2_form = SC2Handler.build_form()
        sc2_formsets = SC2Handler.build_formsets()
        sc2_nested = SC2Handler.build_nested_forms()
        iccd_form, iccd_tech_form = ICCDHandler.build_forms()
        iccd_formsets = ICCDHandler.build_formsets()
        fsc_formsets = FSCHandler.build_formsets()
        fe_formsets = FEHandler.build_formsets()

        context = build_unit_context(
            unit=None,
            unit_form=unit_form,
            extensions=extensions,
            event_formset=event_formset,
            sc2_form=sc2_form,
            sc2_formsets=sc2_formsets,
            sc2_nested=sc2_nested,
            iccd_form=iccd_form,
            iccd_tech_form=iccd_tech_form,
            iccd_formsets=iccd_formsets,
            fsc_formsets=fsc_formsets,
            fe_formsets=fe_formsets,
        )

        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        unit_form = UnitForm(request.POST)

        # Build all formsets from POST data
        extensions = UnitExtensionsHandler.build_formsets(post_data=request.POST)
        event_formset = EventHandler.build_formset(post_data=request.POST)
        sc2_form = SC2Handler.build_form(post_data=request.POST)
        sc2_formsets = SC2Handler.build_formsets(post_data=request.POST)
        sc2_nested = SC2Handler.build_nested_forms(post_data=request.POST)
        iccd_form, iccd_tech_form = ICCDHandler.build_forms(post_data=request.POST)
        iccd_formsets = ICCDHandler.build_formsets(post_data=request.POST)
        fsc_formsets = FSCHandler.build_formsets(post_data=request.POST)
        fe_formsets = FEHandler.build_formsets(post_data=request.POST)

        if unit_form.is_valid():
            unit = unit_form.save()

            # Delegate saving to handlers
            UnitExtensionsHandler.save_all(unit, extensions)
            EventHandler.save_all(unit, event_formset)
            SC2Handler.save_main(sc2_form, unit, unit_form.data)
            SC2Handler.save_formsets(unit, sc2_formsets)
            iccd_instance = ICCDHandler.save_main(iccd_form, iccd_tech_form, unit)
            ICCDHandler.save_subjects(iccd_instance, formset_data=request.POST)
            ICCDHandler.save_damages(unit, formset_data=request.POST)
            FSCHandler.save_all(unit, fsc_formsets)
            FEHandler.save_main(unit, fe_formsets)

            if unit.fond:
                return redirect('archive:fond_detail', pk=unit.fond.pk)
            return redirect('archive:unit_detail', pk=unit.pk)

        # Errors: re-present form with all formsets
        context = build_unit_context(
            unit=None,
            unit_form=unit_form,
            extensions=extensions,
            event_formset=event_formset,
            sc2_form=sc2_form,
            sc2_formsets=sc2_formsets,
            sc2_nested=sc2_nested,
            iccd_form=iccd_form,
            iccd_tech_form=iccd_tech_form,
            iccd_formsets=iccd_formsets,
            fsc_formsets=fsc_formsets,
            fe_formsets=fe_formsets,
        )
        return render(request, self.template_name, context)


class UnitUpdateView(View):
    """Vista per modificare unità con tutte le schede specialistiche.

    Orchestratore: delega la gestione dei 37 form/formset agli handler.
    """
    template_name = 'archive/unit_form.html'

    def get(self, request, pk, *args, **kwargs):
        unit = get_object_or_404(Unit, pk=pk)
        unit_form = UnitForm(instance=unit)

        # Pre-fill sc2_tsk from existing SC2 card
        sc2 = getattr(unit, 'sc2_card', None)
        if sc2:
            card_type_map = {
                'SC3': 'F', 'F': 'F',
                'CARS': 'CARS', 'D': 'D', 'DT': 'DT', 'S': 'S',
            }
            unit_form.initial['sc2_tsk'] = card_type_map.get(sc2.card_type, '')

        # Build all formsets with existing instance
        extensions = UnitExtensionsHandler.build_formsets(instance=unit)
        event_formset = EventHandler.build_formset(instance=unit)
        sc2_form = SC2Handler.build_form(instance=sc2)
        sc2_formsets = SC2Handler.build_formsets(instance=unit)
        sc2_nested = SC2Handler.build_nested_forms()
        iccd_form, iccd_tech_form = ICCDHandler.build_forms(
            iccd_instance=getattr(unit, 'iccd_card', None),
            iccd_tech_instance=getattr(unit, 'iccd_tech_spec', None),
        )
        iccd_formsets = ICCDHandler.build_formsets(
            iccd_instance=getattr(unit, 'iccd_card', None),
            unit_instance=unit,
        )
        fsc_formsets = FSCHandler.build_formsets(instance=unit)
        fe_formsets = FEHandler.build_formsets(instance=unit)

        context = build_unit_context(
            unit=unit,
            unit_form=unit_form,
            extensions=extensions,
            event_formset=event_formset,
            sc2_form=sc2_form,
            sc2_formsets=sc2_formsets,
            sc2_nested=sc2_nested,
            iccd_form=iccd_form,
            iccd_tech_form=iccd_tech_form,
            iccd_formsets=iccd_formsets,
            fsc_formsets=fsc_formsets,
            fe_formsets=fe_formsets,
        )

        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        unit = get_object_or_404(Unit, pk=pk)
        unit_form = UnitForm(request.POST, instance=unit)

        # Build all formsets from POST data with instance
        sc2 = getattr(unit, 'sc2_card', None)
        iccd = getattr(unit, 'iccd_card', None)

        extensions = UnitExtensionsHandler.build_formsets(post_data=request.POST, instance=unit)
        event_formset = EventHandler.build_formset(post_data=request.POST, instance=unit)
        sc2_form = SC2Handler.build_form(post_data=request.POST, instance=sc2)
        sc2_formsets = SC2Handler.build_formsets(post_data=request.POST, instance=unit)
        sc2_nested = SC2Handler.build_nested_forms(post_data=request.POST)
        iccd_form, iccd_tech_form = ICCDHandler.build_forms(
            post_data=request.POST,
            iccd_instance=iccd,
            iccd_tech_instance=getattr(unit, 'iccd_tech_spec', None),
        )
        iccd_formsets = ICCDHandler.build_formsets(
            post_data=request.POST,
            iccd_instance=iccd,
            unit_instance=unit,
        )
        fsc_formsets = FSCHandler.build_formsets(post_data=request.POST, instance=unit)
        fe_formsets = FEHandler.build_formsets(post_data=request.POST, instance=unit)

        if unit_form.is_valid():
            unit = unit_form.save()

            # Delegate saving to handlers
            UnitExtensionsHandler.save_all(unit, extensions)
            EventHandler.save_all(unit, event_formset)
            SC2Handler.save_main(sc2_form, unit, unit_form.data)
            SC2Handler.save_formsets(unit, sc2_formsets)
            iccd_instance = ICCDHandler.save_main(iccd_form, iccd_tech_form, unit)
            ICCDHandler.save_subjects(iccd_instance, formset_data=request.POST)
            ICCDHandler.save_damages(unit, formset_data=request.POST)
            FSCHandler.save_all(unit, fsc_formsets)
            FEHandler.save_main(unit, fe_formsets)

            if unit.fond:
                return redirect('archive:fond_detail', pk=unit.fond.pk)
            return redirect('archive:unit_detail', pk=unit.pk)

        # Errors: re-present form with all formsets
        context = build_unit_context(
            unit=unit,
            unit_form=unit_form,
            extensions=extensions,
            event_formset=event_formset,
            sc2_form=sc2_form,
            sc2_formsets=sc2_formsets,
            sc2_nested=sc2_nested,
            iccd_form=iccd_form,
            iccd_tech_form=iccd_tech_form,
            iccd_formsets=iccd_formsets,
            fsc_formsets=fsc_formsets,
            fe_formsets=fe_formsets,
        )
        return render(request, self.template_name, context)


class UnitDetailView(DetailView):
    model = Unit
    template_name = 'archive/unit_detail.html'
    context_object_name = 'unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.filter(
            content_type=ContentType.objects.get_for_model(self.object),
            object_id=self.object.pk
        ).order_by('order_date')
        return context

class UnitDeleteView(DeleteView):
    model = Unit
    template_name = 'archive/unit_confirm_delete.html'

    def get_success_url(self):
        fond_id = self.object.fond_id
        if fond_id:
            return reverse_lazy('archive:fond_detail', kwargs={'pk': fond_id})
        return reverse_lazy('archive:fond_list')


# =============================================================================
# Classificazione di massa (porting da Ruby units_controller.rb classify)
# =============================================================================

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


@require_http_methods(["PUT", "POST"])
@csrf_exempt
def units_classify(request):
    """Sposta le unità selezionate sotto un nuovo fondo.
    Ruby: PUT /units/classify con record_ids[] e new_fond_id
    """
    try:
        data = json.loads(request.body) if request.body else request.POST
        record_ids = data.get('record_ids', [])
        new_fond_id = data.get('new_fond_id')

        if not record_ids:
            return JsonResponse({'status': 'error', 'message': 'Nessuna unità selezionata'}, status=400)

        if not new_fond_id:
            return JsonResponse({'status': 'error', 'message': 'Nessun fondo di destinazione'}, status=400)

        # Verifica che il fondo di destinazione esista
        from archimista_python.archive.models import Fond
        new_fond = get_object_or_404(Fond, pk=new_fond_id)

        with transaction.atomic():
            # Sposta le unità
            units = Unit.objects.filter(pk__in=record_ids)
            count = units.count()

            if count == 0:
                return JsonResponse({'status': 'error', 'message': 'Nessuna unità trovata'}, status=404)

            # Aggiorna il fond_id e ricalcola le posizioni
            max_pos = Unit.objects.filter(fond_id=new_fond_id).aggregate(
                models.Max('position')
            )['position__max'] or 0

            for i, unit in enumerate(units):
                unit.fond_id = new_fond_id
                unit.position = max_pos + i + 1
                unit.save(update_fields=['fond_id', 'position'])

        return JsonResponse({
            'status': 'success',
            'message': f'{count} unità classificate sotto "{new_fond.name}"'
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# =============================================================================
# Modifica livello unità (porting da Ruby units_controller.rb: move, move_up, move_down)
# =============================================================================

def unit_move(request, pk):
    """Mostra il modale 'Modifica livello' per spostare un'unità su/giù nella gerarchia.
    Ruby: GET /units/:id/move
    """
    unit = get_object_or_404(Unit, pk=pk)

    # Fratelli stessi livello (stesso genitore, stesso fondo, escluso self)
    siblings = Unit.objects.filter(
        parent_id=unit.parent_id,
        fond_id=unit.fond_id
    ).exclude(pk=unit.pk).order_by('position')

    # Calcola numero di visualizzazione (semplificato: uso reference_number o posizione)
    display_seq = unit.reference_number or f"#{unit.position}"

    # Determina i livelli
    level_names = {0: 'Unità', 1: 'Sottounità', 2: 'Sottosottounità'}
    current_level = level_names.get(unit.ancestry_depth or 0, 'Unità')
    up_level = level_names.get((unit.ancestry_depth or 1) - 1, 'Unità')
    down_level = level_names.get((unit.ancestry_depth or 0) + 1, 'Sottosottounità')

    return render(request, 'archive/unit_move.html', {
        'unit': unit,
        'siblings': siblings,
        'display_seq': display_seq,
        'current_level': current_level,
        'up_level': up_level,
        'down_level': down_level,
    })


def unit_move_up(request, pk):
    """Sposta l'unità al livello del genitore (promozione).
    Ruby: POST /units/:id/move_up
    """
    unit = get_object_or_404(Unit, pk=pk)

    if unit.is_root_unit():
        return redirect('archive:unit_detail', pk=pk)

    old_parent = unit.parent

    # Ancestry del genitore del genitore (nonno)
    if old_parent:
        unit.ancestry = old_parent.ancestry or ''
        unit.ancestry_depth = (old_parent.ancestry_depth or 0) - 1 if old_parent.ancestry_depth else 0
        unit.parent = old_parent.parent
    else:
        unit.ancestry = None
        unit.ancestry_depth = 0
        unit.parent = None

    # Posizione: ultima tra i nuovi fratelli
    if unit.ancestry:
        max_pos = Unit.objects.filter(
            ancestry=unit.ancestry,
            fond_id=unit.fond_id
        ).aggregate(models.Max('position'))['position__max'] or 0
    else:
        max_pos = Unit.objects.filter(
            parent__isnull=True,
            fond_id=unit.fond_id
        ).aggregate(models.Max('position'))['position__max'] or 0

    unit.position = max_pos + 1
    unit.save()

    return redirect('archive:unit_detail', pk=pk)


def unit_move_down(request, pk):
    """Sposta l'unità sotto un fratello (demozione).
    Ruby: POST /units/:id/move_down con new_parent_id
    """
    unit = get_object_or_404(Unit, pk=pk)
    new_parent_id = request.POST.get('new_parent_id')

    if not new_parent_id:
        return redirect('archive:unit_detail', pk=pk)

    new_parent = get_object_or_404(Unit, pk=new_parent_id)

    # Nuova ancestry
    if new_parent.ancestry:
        unit.ancestry = f"{new_parent.ancestry}/{new_parent.id}"
    else:
        unit.ancestry = str(new_parent.id)

    unit.ancestry_depth = (new_parent.ancestry_depth or 0) + 1
    unit.parent = new_parent

    # Posizione: ultimo figlio del nuovo genitore
    max_pos = Unit.objects.filter(
        parent=new_parent
    ).aggregate(models.Max('position'))['position__max'] or 0
    unit.position = max_pos + 1
    unit.save()

    return redirect('archive:unit_detail', pk=pk)

# API per l'Albero Archivistico
