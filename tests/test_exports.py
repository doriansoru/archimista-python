"""Test: export (PDF, RTF, AEF, CSV) e ricerca."""
from tests import test, section, client
from django.urls import reverse


def run():
    section("14. Export fond (PDF, RTF, AEF)")

    def _test_fond_export_pdf():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if fond:
            resp = client.get(reverse('archive:fond_export_pdf', args=[fond.pk]))
            assert resp.status_code == 200
            assert resp['Content-Type'] == 'application/pdf'
    test("Fond: export PDF", _test_fond_export_pdf)

    def _test_fond_export_rtf():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if fond:
            resp = client.get(reverse('archive:fond_export_rtf', args=[fond.pk]))
            assert resp.status_code == 200
    test("Fond: export RTF", _test_fond_export_rtf)

    def _test_fond_export_aef():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if fond:
            resp = client.get(reverse('archive:fond_export_aef', args=[fond.pk]))
            assert resp.status_code == 200
    test("Fond: export AEF", _test_fond_export_aef)

    section("15. Export AEF batch")

    def _test_export_aef_form():
        resp = client.get(reverse('archive:export_aef'))
        assert resp.status_code == 200
    test("Export AEF: form", _test_export_aef_form)

    def _test_export_units_aef():
        resp = client.post(reverse('archive:export_units_aef'), {}, follow=True)
        assert resp.status_code == 200
    test("Export: batch units AEF (POST)", _test_export_units_aef)

    def _test_export_csv():
        resp = client.get(reverse('archive:export_units_csv'))
        assert resp.status_code == 200
    test("Export CSV: form", _test_export_csv)

    section("16. Ricerca")

    def _test_advanced_search():
        resp = client.get(reverse('archive:advanced_search'))
        assert resp.status_code == 200
    test("Ricerca avanzata", _test_advanced_search)

    def _test_global_search():
        resp = client.get(reverse('archive:search') + '?q=Test')
        assert resp.status_code == 200
    test("Ricerca globale", _test_global_search)
