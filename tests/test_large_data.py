"""Test: alberi profondi e grandi — 5+ livelli, 100+ nodi, performance.

COPRE:
  - Albero fondi profondo (5+ livelli di gerarchia)
  - Albero fondi ampio (100+ nodi allo stesso livello)
  - Albero unita profondo e ampio
  - Tree API con alberi grandi (serializzazione, movimento)
  - Subtree e root computation
  - Full path computation
"""
from tests import test, section, client, admin_user
from django.test import Client
from django.urls import reverse
import json
import time


# Re-login
_test_client = Client()
_test_client.force_login(admin_user)


def run():
    section("22a. Albero fondi profondo (5+ livelli)")

    def _test_deep_fond_tree():
        """Crea un albero di fondi 7 livelli profondo."""
        from archimista_python.archive.models import Fond

        levels = []
        parent = None
        for i in range(7):
            f = Fond.objects.create(
                name=f'Livello {i} Fond',
                parent=parent,
                description=f'Fondo al livello {i}',
                created_by=1, updated_by=1,
            )
            levels.append(f)
            parent = f

        # Verifica la gerarchia
        for i in range(1, 7):
            assert levels[i].parent_id == levels[i - 1].pk, \
                f"Level {i} parent mismatch: expected {levels[i-1].pk}, got {levels[i].parent_id}"

        # Verifica root
        deepest = levels[-1]
        if hasattr(deepest, 'root'):
            root = deepest.root
            assert root.pk == levels[0].pk, f"Root mismatch: expected {levels[0].pk}, got {root.pk}"

        # Verifica full_path su Fond (se esiste come property)
        if hasattr(deepest, 'full_path'):
            path = deepest.full_path
            # full_path potrebbe essere stringa o metodo
            if callable(path):
                path = path()
            if isinstance(path, str):
                assert 'Livello 0' in path or 'Livello 6' in path
            elif isinstance(path, list):
                names = [getattr(f, 'name', '') for f in path]
                assert 'Livello 0 Fond' in names

        # Verifica subtree
        root = levels[0]
        if hasattr(root, 'subtree'):
            subtree = root.subtree
            if callable(subtree):
                subtree = list(subtree())
            assert len(subtree) == 7, f"Subtree should have 7 nodes, got {len(subtree)}"

        if hasattr(root, 'subtree_ids'):
            ids = root.subtree_ids
            if callable(ids):
                ids = list(ids())
            assert len(ids) == 7, f"Subtree IDs should have 7 nodes, got {len(ids)}"

        # Verifica detail view del nodo profondo
        resp = _test_client.get(reverse('archive:fond_detail', args=[deepest.pk]))
        assert resp.status_code == 200

        # Verifica che il genitore sia visibile
        resp = _test_client.get(reverse('archive:fond_detail', args=[levels[3].pk]))
        assert resp.status_code == 200
    test("Albero profondo: 7 livelli di fondi", _test_deep_fond_tree)

    def _test_deep_fond_tree_api():
        """Tree API con albero profondo."""
        from archimista_python.archive.models import Fond

        parent = None
        for i in range(5):
            f = Fond.objects.create(
                name=f'API Tree Level {i}',
                parent=parent,
                created_by=1, updated_by=1,
            )
            parent = f

        root = Fond.objects.filter(name='API Tree Level 0').first()
        assert root is not None

        # Tree data API — URL corretto e' tree_data_root
        resp = _test_client.get(reverse('archive:tree_data_root'))
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert isinstance(data, list), f"tree_data should return a list, got {type(data)}"
    test("Tree API: albero profondo 5 livelli", _test_deep_fond_tree_api)

    section("22b. Albero fondi ampio (100+ nodi)")

    def _test_wide_fond_tree():
        """Crea 100 fondi figli dello stesso root."""
        from archimista_python.archive.models import Fond

        root = Fond.objects.create(name='Root Wide Fond', created_by=1, updated_by=1)
        for i in range(100):
            Fond.objects.create(
                name=f'Child {i} Wide',
                parent=root,
                created_by=1, updated_by=1,
            )

        # Verifica subtree
        if hasattr(root, 'subtree'):
            subtree = root.subtree
            if callable(subtree):
                subtree = list(subtree())
            # Dovrebbe avere root + 100 figli = 101
            assert len(subtree) == 101, f"Expected 101 nodes in subtree, got {len(subtree)}"

        # Verifica tree view
        resp = _test_client.get(reverse('archive:archive_tree'))
        assert resp.status_code == 200

        # Verifica detail di un figlio
        child = Fond.objects.filter(name='Child 50 Wide').first()
        assert child is not None
        resp = _test_client.get(reverse('archive:fond_detail', args=[child.pk]))
        assert resp.status_code == 200
    test("Albero ampio: 100 figli allo stesso livello", _test_wide_fond_tree)

    def _test_tree_api_with_wide_tree():
        """Tree API con albero ampio (50 nodi)."""
        from archimista_python.archive.models import Fond

        root = Fond.objects.filter(name='Root Wide Fond').first()
        if not root:
            root = Fond.objects.create(name='Root Wide Fond API', created_by=1, updated_by=1)
            for i in range(50):
                Fond.objects.create(
                    name=f'API Child {i}',
                    parent=root,
                    created_by=1, updated_by=1,
                )

        resp = _test_client.get(reverse('archive:tree_data_root'))
        assert resp.status_code == 200
        data = json.loads(resp.content)
        assert isinstance(data, list)
    test("Tree API: albero ampio 50+ nodi", _test_tree_api_with_wide_tree)

    section("22c. Albero unita profondo e ampio")

    def _test_deep_unit_tree():
        """Crea un albero di unita 5 livelli profondo."""
        from archimista_python.archive.models import Fond, Unit

        fond = Fond.objects.create(name='Unit Deep Fond', created_by=1, updated_by=1)

        units = []
        parent = None
        ancestry_parts = []
        for i in range(5):
            ancestry = '/'.join(ancestry_parts) if ancestry_parts else ''
            u = Unit.objects.create(
                title=f'Unita Livello {i}',
                fond=fond,
                parent=parent,
                ancestry=ancestry,
                ancestry_depth=i,
                created_by=1, updated_by=1,
            )
            units.append(u)
            ancestry_parts.append(str(u.pk))
            parent = u

        # Verifica gerarchia
        for i in range(1, 5):
            assert units[i].parent_id == units[i - 1].pk

        # Verifica full_path (metodo, non property)
        deepest = units[-1]
        path = deepest.full_path()  # e' un metodo!
        path_titles = [u.title for u in path]
        assert 'Unita Livello 0' in path_titles, f"Root title not in path: {path_titles}"
        assert 'Unita Livello 4' in path_titles, f"Leaf title not in path: {path_titles}"

        # Verifica detail view
        resp = _test_client.get(reverse('archive:unit_detail', args=[deepest.pk]))
        assert resp.status_code == 200
    test("Albero unita: 5 livelli profondi", _test_deep_unit_tree)

    def _test_wide_unit_tree():
        """Crea 200 unita figlie dello stesso fondo."""
        from archimista_python.archive.models import Fond, Unit

        fond = Fond.objects.create(name='Unit Wide Fond', created_by=1, updated_by=1)
        for i in range(200):
            Unit.objects.create(
                title=f'Unita Wide {i}',
                fond=fond,
                created_by=1, updated_by=1,
            )

        # Verifica che le unita siano state create
        count = Unit.objects.filter(fond=fond).count()
        assert count == 200, f"Expected 200 units, got {count}"

        # Verifica la list view
        resp = _test_client.get(reverse('archive:unit_list') + f'?fond_id={fond.pk}')
        assert resp.status_code == 200
    test("Albero unita: 200 unita allo stesso livello", _test_wide_unit_tree)

    section("22d. Performance — subtree computation")

    def _test_subtree_computation_performance():
        """Misura il tempo di subtree computation su albero grande."""
        from archimista_python.archive.models import Fond

        root = Fond.objects.create(name='Perf Root Fond', created_by=1, updated_by=1)
        for i in range(200):
            Fond.objects.create(
                name=f'Perf Child {i}',
                parent=root,
                created_by=1, updated_by=1,
            )

        # Misura subtree computation
        start = time.time()
        if hasattr(root, 'subtree'):
            subtree = root.subtree
            if callable(subtree):
                subtree = list(subtree())
            elapsed = time.time() - start
            # Dovrebbe essere < 5 secondi per 200 nodi
            assert elapsed < 5.0, f"Subtree computation took {elapsed:.2f}s (should be < 5s)"
            assert len(subtree) == 201, f"Expected 201 nodes, got {len(subtree)}"
    test("Performance: subtree 200 nodi", _test_subtree_computation_performance)

    def _test_full_path_computation_performance():
        """Misura il tempo di full_path computation su albero profondo."""
        from archimista_python.archive.models import Fond

        parent = None
        last_fond = None
        for i in range(10):
            f = Fond.objects.create(
                name=f'Path Perf Level {i}',
                parent=parent,
                created_by=1, updated_by=1,
            )
            parent = f
            last_fond = f

        # Misura full_path (metodo)
        if hasattr(last_fond, 'full_path'):
            start = time.time()
            path = last_fond.full_path()
            elapsed = time.time() - start
            assert elapsed < 2.0, f"Full path computation took {elapsed:.2f}s"
            if isinstance(path, str):
                assert 'Path Perf Level 0' in path
            elif isinstance(path, list):
                names = [getattr(f, 'name', '') for f in path]
                assert 'Path Perf Level 0' in names
    test("Performance: full_path 10 livelli", _test_full_path_computation_performance)

    section("22e. Tree API operations con alberi grandi")

    def _test_tree_create_rename_move_on_large_tree():
        """Operazioni tree API su albero con molti nodi."""
        from archimista_python.archive.models import Fond

        root = Fond.objects.create(name='Large Op Root', created_by=1, updated_by=1)
        child1 = Fond.objects.create(name='Large Op Child 1', parent=root, created_by=1, updated_by=1)
        child2 = Fond.objects.create(name='Large Op Child 2', parent=root, created_by=1, updated_by=1)

        # Aggiungi molti nodi per rendere l'albero "grande"
        for i in range(50):
            Fond.objects.create(name=f'Large Op Extra {i}', parent=root, created_by=1, updated_by=1)

        # Rename via tree API — URL corretto: tree_rename_node
        resp = _test_client.post(
            reverse('archive:tree_rename_node', args=[child1.pk]),
            data=json.dumps({'name': 'Large Op Child 1 Rinominato'}),
            content_type='application/json',
        )
        assert resp.status_code in (200, 201), f"Tree rename failed: {resp.status_code}"
        child1.refresh_from_db()
        assert child1.name == 'Large Op Child 1 Rinominato'

        # Move via tree API — URL corretto: tree_move_node
        resp = _test_client.post(
            reverse('archive:tree_move_node', args=[child2.pk]),
            data=json.dumps({'new_parent_id': child1.pk}),
            content_type='application/json',
        )
        assert resp.status_code in (200, 201), f"Tree move failed: {resp.status_code}"
        child2.refresh_from_db()
        assert child2.parent_id == child1.pk
    test("Tree API: rename + move su albero grande", _test_tree_create_rename_move_on_large_tree)

    def _test_tree_trash_restore_on_large_tree():
        """Trash e restore su albero grande."""
        from archimista_python.archive.models import Fond

        root = Fond.objects.create(name='Trash Root', created_by=1, updated_by=1)
        children = []
        for i in range(20):
            c = Fond.objects.create(name=f'Trash Child {i}', parent=root, created_by=1, updated_by=1)
            children.append(c)

        # Trash via tree API — URL: tree_move_to_trash (richiede fond_id)
        for c in children[:5]:
            resp = _test_client.post(
                reverse('archive:tree_move_to_trash', args=[c.pk]),
                data=json.dumps({}),
                content_type='application/json',
            )
            assert resp.status_code in (200, 201), f"Tree trash failed for {c.pk}: {resp.status_code}"

        # Verifica che siano trashed
        trashed_count = Fond.objects.filter(trashed=True).count()
        assert trashed_count >= 5, f"Expected >=5 trashed, got {trashed_count}"

        # Restore — URL: tree_restore_subtree (richiede fond_id)
        for c in children[:3]:
            resp = _test_client.post(
                reverse('archive:tree_restore_subtree', args=[c.pk]),
                data=json.dumps({}),
                content_type='application/json',
            )
            assert resp.status_code in (200, 201), f"Tree restore failed for {c.pk}: {resp.status_code}"

        restored_count = Fond.objects.filter(trashed=False, pk__in=[c.pk for c in children[:3]]).count()
        assert restored_count == 3, f"Expected 3 restored, got {restored_count}"
    test("Tree API: trash + restore su albero grande", _test_tree_trash_restore_on_large_tree)

    section("22f. Alberi misti — fondi con unita multiple")

    def _test_mixed_tree_fonds_with_units():
        """Albero con 3 livelli di fondi, ciascuno con multiple unita."""
        from archimista_python.archive.models import Fond, Unit

        root = Fond.objects.create(name='Mixed Root', created_by=1, updated_by=1)
        mid1 = Fond.objects.create(name='Mixed Mid 1', parent=root, created_by=1, updated_by=1)
        mid2 = Fond.objects.create(name='Mixed Mid 2', parent=root, created_by=1, updated_by=1)
        leaf1 = Fond.objects.create(name='Mixed Leaf 1', parent=mid1, created_by=1, updated_by=1)
        leaf2 = Fond.objects.create(name='Mixed Leaf 2', parent=mid1, created_by=1, updated_by=1)

        # Aggiungi unita a ogni fondo
        for i in range(10):
            Unit.objects.create(title=f'Unit Root {i}', fond=root, created_by=1, updated_by=1)
            Unit.objects.create(title=f'Unit Mid1 {i}', fond=mid1, created_by=1, updated_by=1)
            Unit.objects.create(title=f'Unit Leaf1 {i}', fond=leaf1, created_by=1, updated_by=1)

        total_units = Unit.objects.filter(fond__in=[root, mid1, leaf1]).count()
        assert total_units == 30, f"Expected 30 units, got {total_units}"

        # Verifica report inventario con sottoalbero
        resp = _test_client.get(reverse('archive:report_inventory', args=[root.pk]))
        assert resp.status_code == 200
    test("Albero misto: fondi con unita multiple", _test_mixed_tree_fonds_with_units)

    section("22g. Stress test — classificazione di massa")

    def _test_mass_classify_many_units():
        """Classificazione di massa su 100+ unita."""
        from archimista_python.archive.models import Fond, Unit

        source_fond = Fond.objects.create(name='Source Classify Fond', created_by=1, updated_by=1)
        target_fond = Fond.objects.create(name='Target Classify Fond', created_by=1, updated_by=1)

        unit_ids = []
        for i in range(100):
            u = Unit.objects.create(title=f'Classify Unit {i}', fond=source_fond, created_by=1, updated_by=1)
            unit_ids.append(u.pk)

        # Classificazione di massa
        resp = _test_client.put(
            reverse('archive:units_classify'),
            data=json.dumps({
                'record_ids': unit_ids,
                'new_fond_id': target_fond.pk,
            }),
            content_type='application/json',
        )
        assert resp.status_code == 200, f"Mass classify failed: {resp.status_code}"
        result = json.loads(resp.content)
        assert result.get('status') == 'success', f"Mass classify error: {result.get('message')}"

        # Verifica che le unita siano state spostate
        moved_count = Unit.objects.filter(fond=target_fond, pk__in=unit_ids).count()
        assert moved_count == 100, f"Expected 100 moved units, got {moved_count}"
    test("Classificazione di massa: 100 unita", _test_mass_classify_many_units)
