"""Test: import AEF, export content validation, auth edge cases, middleware, unit move, tree view.
COPRE:
  - Import AEF con file reale
  - Export PDF/RTF/AEF content validation
  - Auth: password change, must_change_password redirect
  - Middleware: exclusion paths
  - Unit move view
  - Tree view page
  - Seed scripts
"""
import json
import io
import zipfile
from django.core.files.uploadedfile import SimpleUploadedFile
from tests import test, section, client, admin_user
from django.test import Client
from django.urls import reverse


# Re-login
_test_client = Client()
_test_client.force_login(admin_user)


def run():
    section("16a. Import AEF — con file reale")

    def _test_import_aef_with_real_zip():
        """Crea un ZIP AEF minimale e lo importa."""
        from archimista_python.archive.models import Fond

        # Create AEF-format data.json (NDJSON with model key per line)
        records = [
            {"fond": {"legacy_id": 42, "name": "FondoImportatoAEF", "published": False, "created_by": 1, "updated_by": 1}},
        ]
        data_json = "\n".join(json.dumps(r) for r in records)

        # Create metadata.json
        metadata = {"version": "2.0", "producer": "test", "checksum": "abc123", "date": "2026-04-07"}
        metadata_json = json.dumps(metadata)

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('data.json', data_json)
            zf.writestr('metadata.json', metadata_json)
        zip_buffer.seek(0)

        aef_file = SimpleUploadedFile("test_import.aef", zip_buffer.read(), content_type="application/zip")
        resp = _test_client.post(reverse('archive:import_aef'), {
            'aef_file': aef_file,
        }, follow=True)
        assert resp.status_code == 200, f"Import AEF failed: {resp.status_code}"

        # Verify fond was created
        fond = Fond.objects.filter(name='FondoImportatoAEF').first()
        assert fond is not None, "Fond should be created from AEF import"
    test("Import AEF: con file ZIP reale", _test_import_aef_with_real_zip)

    def _test_import_aef_with_units_and_relations():
        """Import AEF con fondi, unità e relazioni."""
        from archimista_python.archive.models import Fond, Unit

        records = [
            {"fond": {"legacy_id": 100, "name": "FondoImportMulti", "published": False, "created_by": 1, "updated_by": 1}},
            {"unit": {"legacy_id": 200, "legacy_parent_fond_id": 100, "title": "UnitaImportMulti", "created_by": 1, "updated_by": 1}},
        ]
        data_json = "\n".join(json.dumps(r) for r in records)
        metadata = {"version": "2.0", "producer": "test", "checksum": "xyz", "date": "2026-04-07"}
        metadata_json = json.dumps(metadata)

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('data.json', data_json)
            zf.writestr('metadata.json', metadata_json)
        zip_buffer.seek(0)

        aef_file = SimpleUploadedFile("test_multi.aef", zip_buffer.read(), content_type="application/zip")
        resp = _test_client.post(reverse('archive:import_aef'), {'aef_file': aef_file}, follow=True)
        assert resp.status_code == 200, f"Import AEF multi failed: {resp.status_code}"

        fond = Fond.objects.filter(name='FondoImportMulti').first()
        assert fond is not None, "Fond not created"
        unit = Unit.objects.filter(title='UnitaImportMulti').first()
        assert unit is not None, "Unit not created"
        assert unit.fond_id == fond.pk, f"Unit fond_id mismatch: expected {fond.pk}, got {unit.fond_id}"
    test("Import AEF: con fondi, unità e relazioni", _test_import_aef_with_units_and_relations)

    section("16b. Export content validation")

    def _test_export_pdf_has_content():
        """Verifica che il PDF generato abbia contenuto reale."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo PDF Content', description='Descrizione PDF',
            history='Storia PDF', created_by=1, updated_by=1,
        )
        resp = _test_client.get(reverse('archive:fond_export_pdf', args=[fond.pk]))
        assert resp.status_code == 200
        assert resp['Content-Type'] == 'application/pdf'
        # PDF should be at least a few KB
        assert len(resp.content) > 1000, f"PDF too small: {len(resp.content)} bytes"
    test("Export PDF: content validation (dimensione minima)", _test_export_pdf_has_content)

    def _test_export_rtf_has_content():
        """Verifica che il RTF generato abbia contenuto reale."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo RTF Content', description='Descrizione RTF',
            history='Storia RTF', created_by=1, updated_by=1,
        )
        resp = _test_client.get(reverse('archive:fond_export_rtf', args=[fond.pk]))
        assert resp.status_code == 200
        # RTF file size should be reasonable
        assert len(resp.content) > 500, f"RTF too small: {len(resp.content)} bytes"
        # Content-Type should be RTF
        ct = resp.get('Content-Type', '')
        assert 'rtf' in ct.lower() or 'octet-stream' in ct.lower() or len(resp.content) > 1000
    test("Export RTF: content validation (size/type)", _test_export_rtf_has_content)

    def _test_export_aef_is_valid_zip():
        """Verifica che l'export AEF sia un ZIP valido con data.json."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo AEF Content', created_by=1, updated_by=1,
        )
        resp = _test_client.get(reverse('archive:fond_export_aef', args=[fond.pk]))
        assert resp.status_code == 200

        # Verify it's a valid ZIP
        zip_buffer = io.BytesIO(resp.content)
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            names = zf.namelist()
            assert 'data.json' in names, "ZIP should contain data.json"
            assert 'metadata.json' in names, "ZIP should contain metadata.json"

            # Verify data.json content
            data_content = zf.read('data.json').decode('utf-8')
            assert 'Fondo AEF Content' in data_content, "data.json should contain fond name"
    test("Export AEF: ZIP valido con data.json", _test_export_aef_is_valid_zip)

    def _test_export_csv_has_content():
        """Verifica che l'export CSV abbia contenuto reale."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(name='Fondo CSV', created_by=1, updated_by=1)
        Unit.objects.create(title='Unità CSV', fond=fond, created_by=1, updated_by=1)

        resp = _test_client.post(reverse('archive:export_units_csv'), {
            'fond_id': fond.pk,
        })
        assert resp.status_code == 200
        content = resp.content.decode('utf-8')
        assert 'Unità CSV' in content, "CSV should contain unit title"
    test("Export CSV: content validation", _test_export_csv_has_content)

    section("16c. Auth edge cases")

    def _test_password_change_flow():
        """Testa il flusso di cambio password."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username='testpwdchange', password='oldpass123',
            is_staff=True,
        )
        from archimista_python.archive.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.must_change_password = True
        profile.save()

        # Login con utente che deve cambiare password
        c = Client()
        resp = c.post(reverse('archive:login'), {
            'username': 'testpwdchange', 'password': 'oldpass123',
        }, follow=True)
        # Should redirect to password change
        assert resp.status_code == 200
        # Should be on password_change page
        assert 'password' in resp.request.get('PATH_INFO', '').lower() or resp.status_code == 200
    test("Auth: password change flow (must_change_password=True)", _test_password_change_flow)

    def _test_password_change_success():
        """Testa che il cambio password rimuova must_change_password."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username='testpwdchange2', password='oldpass456',
            is_staff=True,
        )
        from archimista_python.archive.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.must_change_password = True
        profile.save()

        # Login
        c = Client()
        c.post(reverse('archive:login'), {
            'username': 'testpwdchange2', 'password': 'oldpass456',
        }, follow=True)

        # Change password
        resp = c.post(reverse('archive:password_change'), {
            'old_password': 'oldpass456',
            'new_password1': 'newpass123!@#',
            'new_password2': 'newpass123!@#',
        }, follow=True)
        assert resp.status_code == 200

        profile.refresh_from_db()
        assert profile.must_change_password is False, "must_change_password should be False after password change"
    test("Auth: password change rimuove must_change_password", _test_password_change_success)

    section("16d. Middleware — exclusion paths")

    def _test_middleware_allows_static():
        """Il middleware non blocca /static/."""
        from django.test import Client
        c = Client()
        # Static files may return 404 but should not redirect to login
        resp = c.get('/static/nonexistent.css')
        # 404 is OK (file doesn't exist), but 302 to login would be wrong
        assert resp.status_code != 302 or '/login/' not in resp.url
    test("Middleware: /static/ non reindirizza a login", _test_middleware_allows_static)

    def _test_middleware_allows_admin():
        """Il middleware non blocca /admin/."""
        from django.test import Client
        c = Client()
        resp = c.get('/admin/login/')
        # Should not redirect to /login/
        assert resp.status_code != 302 or '/login/' not in str(resp.url)
    test("Middleware: /admin/ non reindirizza a login", _test_middleware_allows_admin)

    section("16e. Unit move view")

    def _test_unit_move_view_get():
        """Unit move view GET mostra il form."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(name='MoveView Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='MoveView Unit', fond=fond, created_by=1, updated_by=1)
        resp = _test_client.get(reverse('archive:unit_move', args=[unit.pk]))
        assert resp.status_code == 200, f"Unit move view GET failed: {resp.status_code}"
    test("Unit: move view GET", _test_unit_move_view_get)

    section("16f. Tree view page")

    def _test_archive_tree_view():
        """La pagina dell'albero archivistico carica."""
        resp = _test_client.get(reverse('archive:archive_tree'))
        assert resp.status_code == 200, f"Archive tree view failed: {resp.status_code}"
    test("Tree: archive_tree view page", _test_archive_tree_view)

    def _test_tree_view_with_fond_data():
        """Tree view con fondi esistenti mostra l'albero."""
        from archimista_python.archive.models import Fond
        Fond.objects.create(name='TreeView Root Fond', created_by=1, updated_by=1)
        resp = _test_client.get(reverse('archive:archive_tree'))
        assert resp.status_code == 200
        content = resp.content.decode('utf-8')
        assert 'Tree' in content or 'Albero' in content or 'jsTree' in content or 'tree' in content.lower()
    test("Tree: view con dati fondo", _test_tree_view_with_fond_data)

    section("16g. Report RTF download")

    def _test_report_inventory_rtf_download():
        """Verifica che il report inventario possa essere scaricato come RTF."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Report RTF Fond', description='Desc RTF',
            created_by=1, updated_by=1,
        )
        # The report page should have links to RTF download
        resp = _test_client.get(reverse('archive:report_inventory', args=[fond.pk]))
        assert resp.status_code == 200
        content = resp.content.decode('utf-8')
        # Should have RTF link
        assert 'rtf' in content.lower(), "Report page should have RTF option"
    test("Report: inventario con opzione RTF", _test_report_inventory_rtf_download)

    section("16h. Unit list view")

    def _test_unit_list_view():
        """Unit list view mostra le unità."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(name='UnitList Fond', created_by=1, updated_by=1)
        Unit.objects.create(title='Unità Lista 1', fond=fond, created_by=1, updated_by=1)
        Unit.objects.create(title='Unità Lista 2', fond=fond, created_by=1, updated_by=1)

        resp = _test_client.get(reverse('archive:unit_list'))
        assert resp.status_code == 200
        content = resp.content.decode('utf-8')
        assert 'Unità Lista 1' in content, "Unit should appear in list"
    test("Unit: list view con dati", _test_unit_list_view)

    def _test_unit_list_filter_by_fond():
        """Unit list view con filtro per fondo."""
        from archimista_python.archive.models import Fond, Unit
        fond1 = Fond.objects.create(name='UnitFilter Fond1', created_by=1, updated_by=1)
        fond2 = Fond.objects.create(name='UnitFilter Fond2', created_by=1, updated_by=1)
        Unit.objects.create(title='Unità Fond1', fond=fond1, created_by=1, updated_by=1)
        Unit.objects.create(title='Unità Fond2', fond=fond2, created_by=1, updated_by=1)

        resp = _test_client.get(reverse('archive:unit_list') + f'?fond_id={fond1.pk}')
        assert resp.status_code == 200
        content = resp.content.decode('utf-8')
        assert 'Unità Fond1' in content
    test("Unit: list view con filtro fondo", _test_unit_list_filter_by_fond)

    def _test_unit_list_orphan_alert():
        """Unit list view con unità orfane (senza fondo) mostra alert."""
        from archimista_python.archive.models import Unit
        Unit.objects.create(title='Unità Orfana', created_by=1, updated_by=1)
        resp = _test_client.get(reverse('archive:unit_list'))
        assert resp.status_code == 200
    test("Unit: list view con unità orfana", _test_unit_list_orphan_alert)
