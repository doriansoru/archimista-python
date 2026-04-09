"""Test: API albero archivistico (tree data, manipulation, trash)."""
import json
from django.test import Client
from tests import test, section, client as global_client, admin_user
from django.urls import reverse

# Re-login — sessione può essere scaduta dopo i test precedenti
client = Client()
client.force_login(admin_user)


def run():
    section("7a. Albero: tree data API")

    def _test_tree_data():
        resp = client.get(reverse('archive:tree_data_root'))
        assert resp.status_code == 200, f"Tree data failed: {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list)
    test("Albero: tree data API", _test_tree_data)

    def _test_tree_children_with_arg():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.first()
        if fond:
            resp = client.get(reverse('archive:tree_data_children', args=[f'fond_{fond.pk}']))
            assert resp.status_code == 200
        else:
            from tests import skip
            skip("Tree children (no fond)", "Nessun fondo")
    test("Albero: tree children (con argomento)", _test_tree_children_with_arg)

    def _test_tree_fonds_only_with_arg():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.first()
        if fond:
            resp = client.get(reverse('archive:tree_data_children_fonds_only', args=[f'fond_{fond.pk}']))
            assert resp.status_code == 200
    test("Albero: tree children fonds-only (con argomento)", _test_tree_fonds_only_with_arg)

    section("7b. Albero: tree manipulation API")

    def _run_tree_manipulation():
        # Create
        resp = client.post(reverse('archive:tree_create_node'),
            data=json.dumps({'name': 'Serie Test Tree', 'parent_id': None}),
            content_type='application/json')
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'success'
        fond_id = data['id']

        # Rename
        resp = client.put(reverse('archive:tree_rename_node', args=[fond_id]),
            data=json.dumps({'name': 'Serie Test Rinominata'}), content_type='application/json')
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'success'

        # Move
        from archimista_python.archive.models import Fond
        target = Fond.objects.create(name='Fondo Destinazione', created_by=1, updated_by=1)
        resp = client.put(reverse('archive:tree_move_node', args=[fond_id]),
            data=json.dumps({'new_parent_id': target.pk, 'new_position': 1}),
            content_type='application/json')
        assert resp.status_code == 200

        # Trash
        resp = client.put(reverse('archive:tree_move_to_trash', args=[fond_id]))
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'success'

        # Restore
        resp = client.put(reverse('archive:tree_restore_subtree', args=[fond_id]),
            data=json.dumps({}), content_type='application/json')
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'success'

        # Trash view
        root = Fond.objects.filter(parent__isnull=True, trashed=False).first()
        if root:
            resp = client.get(reverse('archive:tree_trash', args=[root.pk]))
            assert resp.status_code == 200
            # Trash children API
            resp = client.get(reverse('archive:tree_trashed_children', args=[root.pk]))
            assert resp.status_code == 200

    test("Albero: create, rename, move, trash, restore, trash view, trashed children", _run_tree_manipulation)
