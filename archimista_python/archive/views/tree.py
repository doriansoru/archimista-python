from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from archimista_python.archive.models import Fond, Unit


def tree_data(request):
    """Restituisce i nodi radice: i Fondi che non hanno un genitore."""
    fonds = Fond.objects.filter(parent__isnull=True, trashed=False).order_by('position')
    data = [
        {
            'id': f'fond_{f.id}',
            'text': f.name or 'Senza nome',
            'children': True,
            'type': 'fond',
            'data': {'is_root': True}
        } for f in fonds
    ]
    return JsonResponse(data, safe=False)


def tree_children(request, node_id):
    """Restituisce i figli di un determinato nodo (Fondo o Unità)."""
    try:
        prefix, pk = node_id.split('_')
        data = []

        if prefix == 'fond':
            fond = get_object_or_404(Fond, pk=pk)
            # Sottofondi/Serie (non trashed)
            for f in fond.children.filter(trashed=False).order_by('position'):
                data.append({
                    'id': f'fond_{f.id}',
                    'text': f.name or 'Senza nome',
                    'children': True,
                    'type': 'fond',
                    'data': {'is_root': f.parent is None}
                })
            # Unità radice collegate a questo fondo/serie
            for u in Unit.objects.filter(fond=fond, parent__isnull=True).order_by('position'):
                data.append({
                    'id': f'unit_{u.id}',
                    'text': u.title or 'Senza titolo',
                    'children': u.children.exists(),
                    'type': 'unit'
                })

        elif prefix == 'unit':
            unit = get_object_or_404(Unit, pk=pk)
            for u in unit.children.all().order_by('position'):
                data.append({
                    'id': f'unit_{u.id}',
                    'text': u.title or 'Senza titolo',
                    'children': u.children.exists(),
                    'type': 'unit'
                })

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def tree_children_fonds_only(request, node_id):
    """Restituisce solo i figli Fonds di un nodo (per classificazione).
    Ruby: il tree di classificazione mostra solo i fondi/serie, non le unità.
    """
    try:
        prefix, pk = node_id.split('_')
        data = []

        if prefix == 'fond':
            fond = get_object_or_404(Fond, pk=pk)
            # Solo sottofondi/Serie (no unità)
            for f in fond.children.filter(trashed=False).order_by('position'):
                data.append({
                    'id': f'fond_{f.id}',
                    'text': f.name or 'Senza nome',
                    'children': True,
                    'type': 'fond',
                    'data': {'is_root': f.parent is None}
                })

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# =============================================================================
# Tree Manipulation API (porting da Ruby fonds_controller.rb)
# =============================================================================

@require_http_methods(["POST"])
@csrf_exempt
def tree_create_node(request):
    """Crea un nuovo nodo fondo/serie sotto un genitore selezionato.
    Ruby: POST /fonds/ con fond[parent_id] e fond[name]
    """
    import json
    try:
        data = json.loads(request.body) if request.body else request.POST
        parent_id = data.get('parent_id')
        name = data.get('name', '').strip()

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Nome obbligatorio'}, status=400)

        with transaction.atomic():
            if parent_id:
                parent = get_object_or_404(Fond, pk=parent_id)
                # Calcola la posizione: max position tra i figli + 1
                max_pos = parent.children.aggregate(
                    models.Max('position')
                )['position__max'] or 0
                fond = Fond.objects.create(
                    name=name,
                    parent=parent,
                    position=max_pos + 1,
                    ancestry_depth=1 if parent.ancestry_depth is None else parent.ancestry_depth + 1,
                    created_by=1,
                    updated_by=1,
                )
                # Aggiorna ancestry
                parent_ancestry = parent.ancestry or ''
                fond.ancestry = f"{parent_ancestry}/{parent.id}" if parent_ancestry else str(parent.id)
                fond.save(update_fields=['ancestry'])
            else:
                # Nodo root
                max_pos = Fond.objects.filter(parent__isnull=True).aggregate(
                    models.Max('position')
                )['position__max'] or 0
                fond = Fond.objects.create(
                    name=name,
                    position=max_pos + 1,
                    ancestry_depth=0,
                    created_by=1,
                    updated_by=1,
                )

            return JsonResponse({
                'status': 'success',
                'id': fond.id,
                'value': fond.name,
                'node': {
                    'id': f'fond_{fond.id}',
                    'text': fond.name,
                    'children': False,
                    'type': 'fond',
                    'data': {'is_root': fond.parent is None}
                }
            })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_http_methods(["PUT", "POST"])
@csrf_exempt
def tree_rename_node(request, fond_id):
    """Rinomina un nodo fondo/serie.
    Ruby: PUT /fonds/:id/rename
    """
    import json
    try:
        fond = get_object_or_404(Fond, pk=fond_id)
        data = json.loads(request.body) if request.body else request.POST
        new_name = data.get('name', '').strip()

        if not new_name:
            return JsonResponse({'status': 'error', 'message': 'Nome obbligatorio'}, status=400)

        fond.name = new_name
        fond.updated_by = 1
        fond.save()

        return JsonResponse({
            'status': 'success',
            'node': {k: v for k, v in fond.__dict__.items() if not k.startswith('_')}
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_http_methods(["PUT", "POST"])
@csrf_exempt
def tree_move_node(request, fond_id):
    """Sposta un fondo sotto un nuovo genitore.
    Ruby: PUT /fonds/:id/move con new_parent_id e new_position
    """
    import json
    try:
        fond = get_object_or_404(Fond, pk=fond_id)
        data = json.loads(request.body) if request.body else request.POST
        new_parent_id = data.get('new_parent_id')
        new_position = int(data.get('new_position', 0))

        # Prevenire riferimenti circolari
        if new_parent_id:
            new_parent = get_object_or_404(Fond, pk=new_parent_id)
            # Controlla che il nuovo genitore non sia un discendente
            if fond.id == new_parent_id:
                return JsonResponse({'status': 'error', 'message': 'Non puoi spostare un nodo su se stesso'}, status=400)
            # Controlla se new_parent_id è un discendente di fond
            descendant_ids = set(_get_all_descendant_ids(fond.id))
            if new_parent_id in descendant_ids:
                return JsonResponse({'status': 'error', 'message': 'Non puoi spostare un nodo sotto un suo discendente'}, status=400)
        else:
            new_parent = None

        with transaction.atomic():
            old_parent = fond.parent
            old_position = fond.position

            # Aggiorna parent e position
            fond.parent = new_parent
            fond.position = new_position

            # Aggiorna ancestry
            if new_parent:
                parent_ancestry = new_parent.ancestry or ''
                fond.ancestry = f"{parent_ancestry}/{new_parent.id}" if parent_ancestry else str(new_parent.id)
                fond.ancestry_depth = (new_parent.ancestry_depth or 0) + 1
            else:
                fond.ancestry = None
                fond.ancestry_depth = 0

            fond.save()

            # Ricalcola posizioni del vecchio genitore
            if old_parent:
                _reorder_siblings(old_parent.id)

            # Ricalcola posizioni del nuovo genitore
            if new_parent:
                _reorder_siblings(new_parent.id)

            # Aggiorna units_count per i fondi coinvolti
            _update_units_count(fond.id)
            if old_parent:
                _update_units_count(old_parent.id)
            if new_parent:
                _update_units_count(new_parent.id)

            return JsonResponse({
                'status': 'success',
                'node': {k: v for k, v in fond.__dict__.items() if not k.startswith('_')}
            })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_http_methods(["PUT", "POST"])
@csrf_exempt
def tree_move_to_trash(request, fond_id):
    """Soft delete: sposta nel cestino un fondo e i suoi discendenti.
    Ruby: PUT /fonds/:id/move_to_trash
    """
    try:
        fond = get_object_or_404(Fond, pk=fond_id)

        if fond.parent is None and fond.children.filter(trashed=False).exists():
            # È un root con figli: marca tutti i discendenti come trashed
            _trash_subtree(fond)
        else:
            fond.trashed = True
            if fond.parent:
                fond.trashed_ancestor_id = fond.root.id if fond.root else fond.id
            fond.save()

        # Aggiorna units_count
        _update_units_count(fond.id)
        if fond.parent:
            _update_units_count(fond.parent.id)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def tree_trash_view(request, root_id):
    """Mostra i fondi eliminati (cestino).
    Ruby: GET /fonds/:root_id/trash
    """
    root_fond = get_object_or_404(Fond, pk=root_id)
    trashed_roots = root_fond.descendants.filter(
        trashed=True,
        parent__isnull=False  # solo i "root" trashed (figli diretti del root che sono stati trashed)
    ).order_by('-updated_at')

    # Se il root stesso ha figli trashed diretti
    trashed_children = root_fond.children.filter(trashed=True).order_by('-updated_at')

    return render(request, 'archive/tree_trash.html', {
        'root_fond': root_fond,
        'trashed_fonds': trashed_children,
    })


@require_http_methods(["PUT", "POST"])
@csrf_exempt
def tree_restore_subtree(request, fond_id):
    """Ripristina un fondo eliminato e i suoi discendenti.
    Ruby: PUT /fonds/:id/restore_subtree
    """
    try:
        fond = get_object_or_404(Fond, pk=fond_id)

        with transaction.atomic():
            # Ripristina questo fondo
            fond.trashed = False
            fond.trashed_ancestor_id = None
            fond.save()

            # Ripristina tutti i discendenti
            descendants = fond.descendants
            descendants.update(trashed=False, trashed_ancestor_id=None)

        # Se è una richiesta form (dal template HTML), redirect
        if 'application/json' not in request.headers.get('Content-Type', ''):
            from django.shortcuts import redirect
            return redirect('archive:archive_tree')

        return JsonResponse({'status': 'success', 'redirect': f'/archive/fonds/{fond.root.id}/'})
    except Exception as e:
        if 'application/json' not in request.headers.get('Content-Type', ''):
            from django.shortcuts import redirect
            return redirect('archive:tree_trash', root_id=fond.root.id if fond.root else fond_id)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def tree_trashed_children(request, root_id):
    """API JSON per i figli trashed di un root fond.
    Ruby: trashed_subtree action
    """
    root_fond = get_object_or_404(Fond, pk=root_id)
    trashed = root_fond.children.filter(trashed=True).order_by('-updated_at')

    def _to_jstree(fond):
        node = {
            'id': f'fond_{fond.id}',
            'text': fond.name or 'Senza nome',
            'children': fond.children.filter(trashed=True).exists(),
            'type': 'fond',
            'data': {'is_root': False, 'trashed': True, 'updated_at': fond.updated_at.strftime('%Y-%m-%d %H:%M') if fond.updated_at else ''}
        }
        return node

    data = [_to_jstree(f) for f in trashed]
    return JsonResponse(data, safe=False)


# =============================================================================
# Helper functions
# =============================================================================

from django.db.models import Max, Count, Q
import django.db.models as models


def _get_all_descendant_ids(fond_id, seen=None):
    """Restituisce tutti gli ID dei discendenti di un fondo (ricorsivo)."""
    if seen is None:
        seen = set()
    children = Fond.objects.filter(parent_id=fond_id).values_list('id', flat=True)
    for child_id in children:
        if child_id not in seen:
            seen.add(child_id)
            _get_all_descendant_ids(child_id, seen)
    return list(seen)


def _trash_subtree(fond):
    """Marca come trashed un fondo e tutti i suoi discendenti."""
    fond.trashed = True
    if fond.parent:
        fond.trashed_ancestor_id = fond.root.id if fond.root else fond.id
    fond.save()
    for child in fond.children.filter(trashed=False):
        _trash_subtree(child)


def _reorder_siblings(parent_id):
    """Ricalcola la posizione dei figli di un genitore in ordine sequenziale."""
    children = Fond.objects.filter(parent_id=parent_id).order_by('position')
    for i, child in enumerate(children, 1):
        if child.position != i:
            child.position = i
            child.save(update_fields=['position'])


def _update_units_count(fond_id):
    """Aggiorna il conteggio delle unità per un fondo e i suoi antenati."""
    fond = Fond.objects.get(pk=fond_id)
    # Conta le unità dirette + quelle dei discendenti non trashed
    descendant_ids = [fond_id] + _get_all_descendant_ids(fond_id)
    count = Unit.objects.filter(
        fond_id__in=descendant_ids,
        fond__trashed=False
    ).count()
    fond.units_count = count
    fond.save(update_fields=['units_count'])


def archive_tree_view(request):
    """Pagina principale per la navigazione visuale dell'archivio."""
    # Prendi il primo root fond (se esiste)
    root_fond = Fond.objects.filter(parent__isnull=True, trashed=False).first()
    return render(request, 'archive/tree_view.html', {
        'root_fond': root_fond,
    })


