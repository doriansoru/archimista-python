"""
Viste per la gestione del Titolario di classificazione.
"""

import json

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from ..models import Classification, Unit
from ..forms import ClassificationForm


def _build_tree_nodes(classifications):
    """Costruisce una struttura ad albero dalle classificazioni."""
    nodes = []
    for c in classifications:
        nodes.append({
            'id': c.pk,
            'code': c.code or '',
            'name': c.name,
            'description': c.description or '',
            'parent_id': c.parent_id,
            'unit_count': c.units.count(),
        })
    return nodes


def _build_tree_json(nodes):
    """Costruisce un albero JSON per jsTree."""
    # Mappa nodi per ID
    node_map = {}
    for node in nodes:
        node_map[node['id']] = {
            'id': str(node['id']),
            'text': f"{node['code']} - {node['name']}" if node['code'] else node['name'],
            'icon': 'fas fa-folder' if node['unit_count'] == 0 else 'fas fa-folder-open',
            'data': node,
            'children': [],
        }

    # Costruisci albero
    roots = []
    for node_id, tree_node in node_map.items():
        parent_id = tree_node['data']['parent_id']
        if parent_id and parent_id in node_map:
            node_map[parent_id]['children'].append(tree_node)
        else:
            roots.append(tree_node)

    return roots


class ClassificationListView(ListView):
    """Lista titolario - vista ad albero."""
    model = Classification
    template_name = 'archive/classification_list.html'
    context_object_name = 'classifications'

    def get_queryset(self):
        return Classification.objects.select_related('parent').order_by('code', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classifications = list(context['classifications'])
        nodes = _build_tree_nodes(classifications)
        context['tree_data'] = json.dumps(_build_tree_json(nodes))
        context['total'] = classifications.__len__()
        return context


class ClassificationDetailView(DetailView):
    """Dettaglio classificazione."""
    model = Classification
    template_name = 'archive/classification_detail.html'
    context_object_name = 'classification'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classification = self.object

        # Figli diretti
        context['children'] = classification.children.select_related('parent').order_by('code', 'name')

        # Unità classificate con questa classificazione
        context['units'] = classification.units.select_related('fond').order_by('title')[:50]

        # Percorso gerarchico (breadcrumb)
        breadcrumbs = []
        current = classification.parent
        while current:
            breadcrumbs.append(current)
            current = current.parent
        context['breadcrumbs'] = list(reversed(breadcrumbs))

        return context


class ClassificationCreateView(CreateView):
    """Crea nuova classificazione."""
    model = Classification
    form_class = ClassificationForm
    template_name = 'archive/classification_form.html'
    success_url = reverse_lazy('archive:classification_list')

    def form_valid(self, form):
        messages.success(self.request, 'Classificazione creata con successo.')
        return super().form_valid(form)


class ClassificationUpdateView(UpdateView):
    """Modifica classificazione."""
    model = Classification
    form_class = ClassificationForm
    template_name = 'archive/classification_form.html'
    success_url = reverse_lazy('archive:classification_list')

    def form_valid(self, form):
        messages.success(self.request, 'Classificazione aggiornata con successo.')
        return super().form_valid(form)


class ClassificationDeleteView(DeleteView):
    """Elimina classificazione."""
    model = Classification
    template_name = 'archive/classification_confirm_delete.html'
    success_url = reverse_lazy('archive:classification_list')

    def delete(self, request, *args, **kwargs):
        classification = self.get_object()
        # Verifica se ci sono unità collegate
        unit_count = classification.units.count()
        if unit_count > 0:
            messages.error(
                request,
                f'Impossibile eliminare: {unit_count} unità sono collegate a questa classificazione.'
            )
            return reverse_lazy('archive:classification_list')
        messages.success(request, 'Classificazione eliminata con successo.')
        return super().delete(request, *args, **kwargs)


class ClassificationTreeDataView(DetailView):
    """API JSON per dati albero (usata da jsTree o AJAX)."""
    model = Classification

    def get(self, request, *args, **kwargs):
        classification = self.get_object()
        children = classification.children.select_related('parent').order_by('code', 'name')

        child_data = []
        for child in children:
            child_data.append({
                'id': child.pk,
                'text': f"{child.code or ''} - {child.name}",
                'code': child.code or '',
                'name': child.name,
                'has_children': child.children.exists(),
                'unit_count': child.units.count(),
            })

        return JsonResponse({
            'id': classification.pk,
            'code': classification.code or '',
            'name': classification.name,
            'description': classification.description or '',
            'children': child_data,
        })


class ClassificationUnitsView(DetailView):
    """Lista unità classificate con una specifica classificazione."""
    model = Classification
    template_name = 'archive/classification_units.html'
    context_object_name = 'classification'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['units'] = self.object.units.select_related('fond').order_by('title')
        return context
