"""Test: CRUD Fond — list, create, detail, update, delete."""
from tests import test, section, client
from django.urls import reverse


def run():
    section("6a. Fond CRUD")

    def _test_fond_list():
        resp = client.get(reverse('archive:fond_list'))
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    def _test_fond_create():
        resp = client.post(reverse('archive:fond_create'), {
            'name': 'Fondo Test', 'fond_type_term': '', 'published': False,
        }, follow=True)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        from archimista_python.archive.models import Fond
        fond = Fond.objects.filter(name='Fondo Test').first()
        assert fond is not None, "Fondo non creato"

    def _test_fond_detail():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.filter(name='Fondo Test').first()
        assert fond is not None
        resp = client.get(reverse('archive:fond_detail', args=[fond.pk]))
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        assert b'Fondo Test' in resp.content, "Nome fondo non nella response"

    def _test_fond_update():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.filter(name='Fondo Test').first()
        assert fond is not None
        resp = client.get(reverse('archive:fond_update', args=[fond.pk]))
        assert resp.status_code == 200

        resp = client.post(reverse('archive:fond_update', args=[fond.pk]), {
            'name': 'Fondo Test Modificato', 'fond_type_term': '', 'published': False,
            'fond_name-TOTAL_FORMS': '1', 'fond_name-INITIAL_FORMS': '0', 'fond_name-MIN_NUM_FORMS': '0', 'fond_name-MAX_NUM_FORMS': '1000',
            'fond_identifier-TOTAL_FORMS': '1', 'fond_identifier-INITIAL_FORMS': '0', 'fond_identifier-MIN_NUM_FORMS': '0', 'fond_identifier-MAX_NUM_FORMS': '1000',
            'fond_lang-TOTAL_FORMS': '1', 'fond_lang-INITIAL_FORMS': '0', 'fond_lang-MIN_NUM_FORMS': '0', 'fond_lang-MAX_NUM_FORMS': '1000',
            'fond_owner-TOTAL_FORMS': '1', 'fond_owner-INITIAL_FORMS': '0', 'fond_owner-MIN_NUM_FORMS': '0', 'fond_owner-MAX_NUM_FORMS': '1000',
            'fond_url-TOTAL_FORMS': '1', 'fond_url-INITIAL_FORMS': '0', 'fond_url-MIN_NUM_FORMS': '0', 'fond_url-MAX_NUM_FORMS': '1000',
            'fond_editor-TOTAL_FORMS': '1', 'fond_editor-INITIAL_FORMS': '0', 'fond_editor-MIN_NUM_FORMS': '0', 'fond_editor-MAX_NUM_FORMS': '1000',
            'rel_fond_heading-TOTAL_FORMS': '1', 'rel_fond_heading-INITIAL_FORMS': '0', 'rel_fond_heading-MIN_NUM_FORMS': '0', 'rel_fond_heading-MAX_NUM_FORMS': '1000',
            'rel_fond_source-TOTAL_FORMS': '1', 'rel_fond_source-INITIAL_FORMS': '0', 'rel_fond_source-MIN_NUM_FORMS': '0', 'rel_fond_source-MAX_NUM_FORMS': '1000',
            'rel_fond_document-TOTAL_FORMS': '1', 'rel_fond_document-INITIAL_FORMS': '0', 'rel_fond_document-MIN_NUM_FORMS': '0', 'rel_fond_document-MAX_NUM_FORMS': '1000',
        }, follow=True)
        assert resp.status_code == 200
        fond.refresh_from_db()
        assert fond.name == 'Fondo Test Modificato', f"Nome non aggiornato: {fond.name}"

    def _test_fond_delete():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if fond:
            resp = client.get(reverse('archive:fond_delete', args=[fond.pk]))
            assert resp.status_code == 200, f"Fond delete confirm failed: {resp.status_code}"

    def _run_fond_crud():
        _test_fond_list()
        _test_fond_create()
        _test_fond_detail()
        _test_fond_update()
        _test_fond_delete()

    test("Fond: list, create, detail, update, delete confirm", _run_fond_crud)
