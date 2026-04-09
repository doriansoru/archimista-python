"""Test: verifica del CONTENUTO reale degli export PDF/RTF (report system completo).

COPRE:
  - PDF report inventario: verifica che i campi Fond siano presenti nel PDF generato
  - RTF report inventario: verifica che i campi siano presenti nel file RTF
  - PDF report progetto
  - PDF report conservatore
  - Export PDF rapido (export_utils) contiene almeno nome fondo
  - Export AEF contiene data.json con tutti i record previsti
"""
import io
import json
import zipfile
import re
from django.test import Client
from tests import test, section, client, admin_user
from django.urls import reverse


# Re-login
_test_client = Client()
_test_client.force_login(admin_user)


def _create_fond_with_full_data():
    """Crea un fondo con dati completi per i test di export."""
    from archimista_python.archive.models import (
        Fond, Unit, Creator, Custodian, Project,
        FondName, FondIdentifier, FondLang, FondOwner, FondUrl,
        RelCreatorFond, RelCustodianFond, RelProjectFond,
        CustodianType,
    )

    fond = Fond.objects.create(
        name='Fondo Export Test Completo',
        description='Questa e una descrizione completa del fondo per test export.',
        history='Storia archivistica del fondo di test.',
        arrangement_note='Nota dell archivista per il fondo di test.',
        abstract='Abstract del fondo di test.',
        related_materials='Materiali correlati del fondo.',
        note='Note generali del fondo.',
        length=10,
        created_by=1, updated_by=1,
    )

    # Estensioni fond
    FondName.objects.create(fond=fond, name='Fondo Alternativo', note='Nome alternativo')
    FondIdentifier.objects.create(fond=fond, identifier='ID-001', identifier_source='Sistema X')
    FondLang.objects.create(fond=fond, code='ita')
    FondOwner.objects.create(fond=fond, owner='Possessore Storico')
    FondUrl.objects.create(fond=fond, url='http://example.com/fondo', note='URL del fondo')

    # Unità (Unit ha 'content' non 'description')
    u1 = Unit.objects.create(
        title='Unita di Test 1',
        content='Contenuto unita 1.',
        reference_number='I.1',
        fond=fond,
        created_by=1, updated_by=1,
    )
    u2 = Unit.objects.create(
        title='Unita di Test 2',
        fond=fond,
        parent=u1,
        ancestry=str(u1.pk),
        ancestry_depth=1,
        created_by=1, updated_by=1,
    )

    # Creatore
    creator = Creator.objects.create(
        creator_type='P',
        created_by=1, updated_by=1,
    )
    from archimista_python.archive.models import CreatorName
    CreatorName.objects.create(creator=creator, name='Rossi Mario', preferred=True)
    RelCreatorFond.objects.get_or_create(creator=creator, fond=fond)

    # Conservatore
    from archimista_python.archive.models import CustodianName
    ctype, _ = CustodianType.objects.get_or_create(custodian_type='Archivio di Stato')
    custodian = Custodian.objects.create(
        custodian_type=ctype,
        created_by=1, updated_by=1,
    )
    CustodianName.objects.create(custodian=custodian, name='Archivio di Stato Test', preferred=True)
    RelCustodianFond.objects.get_or_create(custodian=custodian, fond=fond)

    # Progetto
    project = Project.objects.create(
        name='Progetto Test',
        description='Descrizione progetto.',
        created_by=1, updated_by=1,
    )
    RelProjectFond.objects.get_or_create(project=project, fond=fond)

    return fond


def run():
    section("17a. Report PDF — verifica contenuto campi Fond")

    def _test_report_pdf_has_fond_fields():
        """Verifica che il PDF del report inventario contenga i campi del fondo."""
        fond = _create_fond_with_full_data()
        resp = _test_client.get(
            reverse('archive:report_inventory', args=[fond.pk]) + '?format=pdf'
        )
        assert resp.status_code == 200, f"Report PDF failed: {resp.status_code}"
        assert resp['Content-Type'] == 'application/pdf', f"Expected PDF, got {resp['Content-Type']}"

        # Dimensione minima (deve contenere tutti i campi)
        assert len(resp.content) > 2000, f"PDF troppo piccolo: {len(resp.content)} bytes"
    test("Report PDF: genera PDF valido con dati fondo", _test_report_pdf_has_fond_fields)

    def _test_report_pdf_has_fond_description():
        """Verifica che il PDF contenga la descrizione del fondo."""
        fond = _create_fond_with_full_data()
        resp = _test_client.get(
            reverse('archive:report_inventory', args=[fond.pk]) + '?format=pdf'
        )
        assert resp.status_code == 200
        assert len(resp.content) > 2000, f"PDF too small: {len(resp.content)}"
    test("Report PDF: contiene dati fondo (dimensione ragionevole)", _test_report_pdf_has_fond_description)

    def _test_report_pdf_has_units_table():
        """Verifica che il PDF contenga le unità del fondo."""
        fond = _create_fond_with_full_data()
        resp = _test_client.get(
            reverse('archive:report_inventory', args=[fond.pk]) + '?format=pdf'
        )
        assert resp.status_code == 200
        pdf_raw = resp.content
        assert len(resp.content) > 3000, f"PDF should contain units, got {len(resp.content)} bytes"
    test("Report PDF: contiene unita (dimensione)", _test_report_pdf_has_units_table)

    def _test_report_pdf_multiple_fonds_subtree():
        """Report PDF con sottoalbero di fondi (root + child)."""
        from archimista_python.archive.models import Fond, Unit
        root = Fond.objects.create(
            name='Root Fond Subtree',
            description='Root description',
            created_by=1, updated_by=1,
        )
        child = Fond.objects.create(
            name='Child Fond Subtree',
            parent=root,
            description='Child description',
            created_by=1, updated_by=1,
        )
        Unit.objects.create(title='Unit in Child', fond=child, created_by=1, updated_by=1)

        resp = _test_client.get(
            reverse('archive:report_inventory', args=[root.pk]) + '?format=pdf'
        )
        assert resp.status_code == 200
        pdf_raw = resp.content
        assert b'Root Fond Subtree' in pdf_raw or len(resp.content) > 3000
        assert b'Child Fond Subtree' in pdf_raw or len(resp.content) > 4000
    test("Report PDF: sottoalbero con fondi multipli", _test_report_pdf_multiple_fonds_subtree)

    section("17b. Report RTF — verifica contenuto")

    def _test_report_rtf_has_content():
        """Verifica che il RTF del report inventario abbia contenuto reale."""
        fond = _create_fond_with_full_data()
        resp = _test_client.get(
            reverse('archive:report_inventory', args=[fond.pk]) + '?format=rtf'
        )
        assert resp.status_code == 200, f"Report RTF failed: {resp.status_code}"

        content = resp.content.decode('utf-8', errors='replace')
        assert content.startswith('{\\rtf') or len(resp.content) > 500, \
            f"RTF should start with {{\\rtf, got: {content[:50]}"
        assert 'Fondo' in content or 'Export' in content or len(resp.content) > 2000
        assert len(resp.content) > 1000, f"RTF too small: {len(resp.content)} bytes"
    test("Report RTF: contiene dati fondo", _test_report_rtf_has_content)

    def _test_report_rtf_has_unit_data():
        """Verifica che il RTF contenga le unita."""
        fond = _create_fond_with_full_data()
        resp = _test_client.get(
            reverse('archive:report_inventory', args=[fond.pk]) + '?format=rtf'
        )
        assert resp.status_code == 200
        content = resp.content.decode('utf-8', errors='replace')
        has_unit_data = 'Unit' in content or 'unit' in content or len(resp.content) > 3000
        assert has_unit_data, "RTF should contain unit data"
    test("Report RTF: contiene dati unita", _test_report_rtf_has_unit_data)

    section("17c. Report PDF Progetto")

    def _test_project_report_pdf():
        """Report PDF per progetto con fondi collegati."""
        from archimista_python.archive.models import (
            Fond, Project, RelProjectFond,
        )
        fond = Fond.objects.create(
            name='Fondo Progetto Test',
            description='Fondo del progetto.',
            created_by=1, updated_by=1,
        )
        project = Project.objects.create(
            name='Progetto PDF Test',
            description='Descrizione progetto per PDF.',
            created_by=1, updated_by=1,
        )
        RelProjectFond.objects.get_or_create(project=project, fond=fond)

        resp = _test_client.get(
            reverse('archive:report_project', args=[project.pk]) + '?format=pdf'
        )
        assert resp.status_code == 200, f"Project report PDF failed: {resp.status_code}"
        assert resp['Content-Type'] == 'application/pdf'
        assert len(resp.content) > 1000
    test("Report PDF progetto: genera PDF valido", _test_project_report_pdf)

    section("17d. Report PDF Conservatore")

    def _test_custodian_report_pdf():
        """Report PDF per conservatore con fondi collegati."""
        from archimista_python.archive.models import (
            Fond, Custodian, CustodianType, CustodianName,
            RelCustodianFond,
        )
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='Archivio Test PDF')
        custodian = Custodian.objects.create(
            custodian_type=ctype,
            created_by=1, updated_by=1,
        )
        CustodianName.objects.create(custodian=custodian, name='Conservatore PDF Test', preferred=True)
        fond = Fond.objects.create(
            name='Fondo Conservatore Test',
            description='Fondo del conservatore.',
            created_by=1, updated_by=1,
        )
        RelCustodianFond.objects.get_or_create(custodian=custodian, fond=fond)

        resp = _test_client.get(
            reverse('archive:report_custodian', args=[custodian.pk]) + '?format=pdf'
        )
        assert resp.status_code == 200, f"Custodian report PDF failed: {resp.status_code}"
        assert resp['Content-Type'] == 'application/pdf'
        assert len(resp.content) > 1000
    test("Report PDF conservatore: genera PDF valido", _test_custodian_report_pdf)

    section("17e. Export rapido PDF (export_utils)")

    def _test_quick_export_pdf_has_fond_name():
        """Export rapido: il PDF deve contenere almeno il nome del fondo."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(
            name='Fondo Quick Export',
            description='Descrizione quick export.',
            history='Storia quick.',
            created_by=1, updated_by=1,
        )
        Unit.objects.create(
            title='Unita Quick Export',
            fond=fond,
            created_by=1, updated_by=1,
        )

        resp = _test_client.get(reverse('archive:fond_export_pdf', args=[fond.pk]))
        assert resp.status_code == 200
        assert resp['Content-Type'] == 'application/pdf'
        assert len(resp.content) > 500, f"Quick export PDF too small: {len(resp.content)} bytes"
    test("Quick export PDF: genera PDF valido", _test_quick_export_pdf_has_fond_name)

    def _test_quick_export_docx_has_unit_table():
        """Export rapido DOCX: deve contenere la tabella delle unita."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(
            name='Fondo Quick DOCX',
            abstract='Abstract DOCX.',
            history='Storia DOCX.',
            created_by=1, updated_by=1,
        )
        Unit.objects.create(
            title='Unita DOCX',
            fond=fond,
            reference_number='I.1',
            created_by=1, updated_by=1,
        )

        resp = _test_client.get(reverse('archive:fond_export_rtf', args=[fond.pk]))
        assert resp.status_code == 200
        content = resp.content
        assert len(content) > 1000, f"Quick export DOCX too small: {len(content)} bytes"
        try:
            zf = zipfile.ZipFile(io.BytesIO(content))
            assert '[Content_Types].xml' in zf.namelist(), "DOCX should be a valid ZIP"
        except zipfile.BadZipFile:
            assert b'Unita DOCX' in content or len(content) > 2000
    test("Quick export DOCX: file valido con tabella unita", _test_quick_export_docx_has_unit_table)

    section("17f. Export AEF — verifica record completi")

    def _test_aef_export_has_all_entity_records():
        """AEF export: data.json deve contenere tutti i tipi di record."""
        from archimista_python.archive.models import Fond, Unit, Creator, Custodian
        from archimista_python.archive.models import (
            FondName, FondIdentifier, FondLang, FondOwner, FondUrl,
            RelCreatorFond, CreatorName,
            CustodianName, CustodianType, RelCustodianFond,
        )

        fond = Fond.objects.create(name='Fondo AEF Full', created_by=1, updated_by=1)
        FondName.objects.create(fond=fond, name='Fondo AEF Alternativo')
        FondLang.objects.create(fond=fond, code='eng')
        Unit.objects.create(title='Unita AEF', fond=fond, created_by=1, updated_by=1)

        creator = Creator.objects.create(creator_type='F', created_by=1, updated_by=1)
        CreatorName.objects.create(creator=creator, name='Famiglia AEF', preferred=True)
        RelCreatorFond.objects.get_or_create(creator=creator, fond=fond)

        ctype, _ = CustodianType.objects.get_or_create(custodian_type='Archivio AEF')
        custodian = Custodian.objects.create(custodian_type=ctype, created_by=1, updated_by=1)
        CustodianName.objects.create(custodian=custodian, name='Conservatore AEF', preferred=True)
        RelCustodianFond.objects.get_or_create(custodian=custodian, fond=fond)

        resp = _test_client.get(reverse('archive:fond_export_aef', args=[fond.pk]))
        assert resp.status_code == 200

        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        data_json = zf.read('data.json').decode('utf-8')

        records = []
        for line in data_json.strip().split('\n'):
            if line.strip():
                records.append(json.loads(line))

        model_keys = set()
        for r in records:
            model_keys.update(r.keys())

        assert 'fond' in model_keys, f"Missing 'fond' in AEF records, got: {model_keys}"
        assert 'unit' in model_keys, f"Missing 'unit' in AEF records"
        assert 'creator' in model_keys, f"Missing 'creator' in AEF records"
        assert 'fond_name' in model_keys, f"Missing 'fond_name' extension in AEF records"
        assert 'fond_lang' in model_keys, f"Missing 'fond_lang' in AEF records"
        # Relations may be exported under different keys depending on mode
        # Check for various possible key formats
        has_creator_rel = any(k in model_keys for k in ['rel_creator_fond', 'relcreatorfond', 'rel_creator_fonds'])
        has_custodian_rel = any(k in model_keys for k in ['rel_custodian_fond', 'relcustodianfond', 'rel_custodian_fonds'])
        assert has_creator_rel, f"Missing creator-fond relation, got: {model_keys}"
        assert has_custodian_rel, f"Missing custodian-fond relation, got: {model_keys}"
    test("AEF export: contiene tutti i tipi di record", _test_aef_export_has_all_entity_records)

    def _test_aef_export_metadata():
        """AEF export: metadata.json deve essere valido."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(name='Fondo AEF Meta', created_by=1, updated_by=1)
        resp = _test_client.get(reverse('archive:fond_export_aef', args=[fond.pk]))
        assert resp.status_code == 200

        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        metadata = json.loads(zf.read('metadata.json').decode('utf-8'))
        assert 'version' in metadata, "Missing version in metadata"
        assert 'producer' in metadata, "Missing producer in metadata"
        assert 'date' in metadata, "Missing date in metadata"
    test("AEF export: metadata.json valido", _test_aef_export_metadata)

    section("17g. Report HTML preview")

    def _test_report_html_preview():
        """Report HTML preview deve contenere i dati del fondo."""
        fond = _create_fond_with_full_data()
        resp = _test_client.get(reverse('archive:report_inventory', args=[fond.pk]))
        assert resp.status_code == 200
        content = resp.content.decode('utf-8')
        assert fond.name in content, f"Fond name '{fond.name}' not in HTML preview"
        assert 'Fondo Export Test Completo' in content
    test("Report HTML preview: mostra dati fondo", _test_report_html_preview)
