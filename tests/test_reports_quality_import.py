"""Test: report, quality checks, import AEF, autenticazione."""
from tests import test, section, client
from django.urls import reverse


def run():
    section("16. Report")

    def _test_report_index():
        resp = client.get(reverse('archive:report_index'))
        assert resp.status_code == 200
    test("Report index", _test_report_index)

    def _test_report_inventory():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if not fond:
            fond = Fond.objects.create(name='Report Fond', created_by=1, updated_by=1)
        resp = client.get(reverse('archive:report_inventory', args=[fond.pk]))
        assert resp.status_code == 200, f"Report inventory failed: {resp.status_code}"
    test("Report: inventario fondo", _test_report_inventory)

    def _test_report_project():
        from archimista_python.archive.models import Project, Fond
        project = Project.objects.filter(name='Progetto Test').first()
        if not project:
            project = Project.objects.create(name='Report Project Test', created_by=1, updated_by=1)
        fond = Fond.objects.first()
        if fond:
            from archimista_python.archive.models import RelProjectFond
            RelProjectFond.objects.get_or_create(project=project, fond=fond)
        resp = client.get(reverse('archive:report_project', args=[project.pk]))
        assert resp.status_code == 200
    test("Report: progetto con dati collegati", _test_report_project)

    def _test_report_custodian():
        from archimista_python.archive.models import Custodian
        custodian = Custodian.objects.order_by('-pk').first()
        if custodian:
            resp = client.get(reverse('archive:report_custodian', args=[custodian.pk]))
            assert resp.status_code == 200
        else:
            from tests import skip
            skip("Report custodian (no data)", "Nessun conservatore")
    test("Report: conservatore", _test_report_custodian)

    section("17. Controlli qualità")

    def _test_quality_check_index():
        resp = client.get(reverse('archive:quality_check_index'))
        assert resp.status_code == 200
    test("Controllo qualità index", _test_quality_check_index)

    def _test_quality_check_fond():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(name='QC Test Fond', created_by=1, updated_by=1)
        resp = client.get(reverse('archive:quality_check_fond', args=[fond.pk]))
        assert resp.status_code == 200, f"Quality check fond failed: {resp.status_code}"
    test("QC: fondo individuale", _test_quality_check_fond)

    def _test_quality_check_creator():
        from archimista_python.archive.models import Creator
        cr = Creator.objects.create(creator_type='P', created_by=1, updated_by=1)
        resp = client.get(reverse('archive:quality_check_creator', args=[cr.pk]))
        assert resp.status_code == 200
    test("QC: creatore individuale", _test_quality_check_creator)

    def _test_quality_check_custodian():
        from archimista_python.archive.models import Custodian, CustodianType
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='QC Test')
        custodian = Custodian.objects.create(custodian_type=ctype, created_by=1, updated_by=1)
        resp = client.get(reverse('archive:quality_check_custodian', args=[custodian.pk]))
        assert resp.status_code == 200
    test("QC: conservatore individuale", _test_quality_check_custodian)

    section("18. Import AEF")

    def _test_import_aef_get():
        resp = client.get(reverse('archive:import_aef'))
        assert resp.status_code == 200
    test("Import AEF: form GET", _test_import_aef_get)

    section("8. Autenticazione")

    def _test_login_redirect():
        from django.test import Client as TestClient
        c2 = TestClient()
        resp = c2.get(reverse('archive:fond_list'))
        assert resp.status_code == 302
        assert '/login/' in resp.url
    test("Anonimo → redirect a login", _test_login_redirect)

    def _test_login_page():
        from django.test import Client as TestClient
        c2 = TestClient()
        resp = c2.get(reverse('archive:login'))
        assert resp.status_code == 200
    test("Pagina login HTTP 200", _test_login_page)

    def _test_logout():
        resp = client.get(reverse('archive:logout'))
        assert resp.status_code == 302
    test("Logout funziona", _test_logout)

    section("20f. Proprietà e metodi dei modelli")

    def _test_fond_properties():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.first()
        if fond:
            root = fond.root
            assert root is not None or fond.parent is None
            assert isinstance(fond.is_root, bool)
            assert isinstance(fond.subtree_ids, list)
    test("Fond: proprietà (root, is_root, subtree_ids)", _test_fond_properties)

    def _test_unit_sequence_numbers():
        from archimista_python.archive.models import Unit, Fond
        fond = Fond.objects.first()
        if fond:
            result = Unit.display_sequence_numbers_of(fond)
            assert isinstance(result, dict)
    test("Unit: display_sequence_numbers_of", _test_unit_sequence_numbers)

    def _test_event_display_date():
        from archimista_python.archive.models import Event, Fond
        from django.contrib.contenttypes.models import ContentType
        fond = Fond.objects.first()
        if fond:
            event = Event.objects.create(
                content_type=ContentType.objects.get_for_model(fond),
                object_id=fond.pk,
                start_date_format='Y', start_date_from='1900-01-01',
                start_date_display='1900', end_date_format='Y',
                end_date_from='2000-01-01', end_date_display='2000',
            )
            assert event.full_display_date is not None
            assert event.full_display_date_with_place is not None
    test("Event: full_display_date e full_display_date_with_place", _test_event_display_date)

    section("20b. Vista cestino albero con dati")

    def _test_tree_trash_with_data():
        from django.test import Client
        from tests import admin_user
        c = Client()
        c.force_login(admin_user)
        from archimista_python.archive.models import Fond
        root = Fond.objects.filter(parent__isnull=True, trashed=False).first()
        if not root:
            root = Fond.objects.create(name='Trash Root', created_by=1, updated_by=1)
        # Create a fresh child in trash
        Fond.objects.create(name='Trashed Child', parent=root, trashed=True,
                           trashed_ancestor_id=root.pk, created_by=1, updated_by=1)
        resp = c.get(reverse('archive:tree_trash', args=[root.pk]))
        assert resp.status_code == 200, f"Tree trash view failed: {resp.status_code}"
    test("Albero: vista cestino con dati", _test_tree_trash_with_data)
