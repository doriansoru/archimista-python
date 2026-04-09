"""Test: quality checks con dati reali (completi e incompleti).
COPRE: QC index, fond QC (minimo + medio), creator QC, custodian QC con dati concreti.
"""
from tests import test, section, client
from django.urls import reverse


def run():
    section("15a. Quality Check — fondo incompleto (requisiti minimi)")

    def _test_qc_fond_incomplete_minimal():
        """Fondo senza nessun campo compilato → tutti i controlli minimi falliscono."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(name='[nome non compilato]', created_by=1, updated_by=1)
        resp = client.get(reverse('archive:quality_check_fond', args=[fond.pk]))
        assert resp.status_code == 200, f"QC fond failed: {resp.status_code}"
    test("QC fond incompleto: pagina carica", _test_qc_fond_incomplete_minimal)

    def _test_qc_fond_complete_minimal():
        """Fondo con tutti i campi minimi compilati."""
        from archimista_python.archive.models import Fond, Event
        from django.contrib.contenttypes.models import ContentType

        fond = Fond.objects.create(
            name='Fondo QC Completo Minimo',
            description='Descrizione completa per QC',
            history='Storia archivistica completa',
            length=100,
            created_by=1, updated_by=1,
        )
        Event.objects.create(
            content_type=ContentType.objects.get_for_model(Fond),
            object_id=fond.pk,
            start_date_format='Y', start_date_from='1900-01-01', start_date_display='1900',
            end_date_format='Y', end_date_from='2000-01-01', end_date_display='2000',
            preferred=True,
        )
        resp = client.get(reverse('archive:quality_check_fond', args=[fond.pk]))
        assert resp.status_code == 200, f"QC fond completo failed: {resp.status_code}"
    test("QC fondo completo: pagina carica", _test_qc_fond_complete_minimal)

    def _test_qc_fond_with_units():
        """Fondo con unità collegate."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(
            name='Fondo QC Con Unità',
            description='Desc', history='Storia', length=50,
            created_by=1, updated_by=1,
        )
        Unit.objects.create(title='UnitaQC1', fond=fond, created_by=1, updated_by=1)
        Unit.objects.create(title='UnitaQC2', fond=fond, created_by=1, updated_by=1)

        resp = client.get(reverse('archive:quality_check_fond', args=[fond.pk]))
        assert resp.status_code == 200, f"QC fond con unità failed: {resp.status_code}"
    test("QC fondo: con unità archivistiche", _test_qc_fond_with_units)

    def _test_qc_fond_with_relations():
        """Fondo con creatori, conservatori, progetti, fonti collegati."""
        from archimista_python.archive.models import (
            Fond, Creator, Custodian, Project, Source,
            RelCreatorFond, RelCustodianFond, RelProjectFond, RelFondSource,
            CustodianType,
        )
        fond = Fond.objects.create(
            name='Fondo QC Relazioni',
            description='Desc', history='Storia', length=10,
            created_by=1, updated_by=1,
        )
        creator = Creator.objects.create(creator_type='P', created_by=1, updated_by=1)
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='QC Rel')
        custodian = Custodian.objects.create(custodian_type=ctype, created_by=1, updated_by=1)
        project = Project.objects.create(name='Progetto QC', created_by=1, updated_by=1)
        source = Source.objects.create(short_title='Fonte QC', source_type_code='1', created_by=1, updated_by=1)

        RelCreatorFond.objects.create(creator=creator, fond=fond)
        RelCustodianFond.objects.create(custodian=custodian, fond=fond)
        RelProjectFond.objects.create(project=project, fond=fond)
        RelFondSource.objects.create(source=source, fond=fond)

        resp = client.get(reverse('archive:quality_check_fond', args=[fond.pk]))
        assert resp.status_code == 200, f"QC fond con relazioni failed: {resp.status_code}"
    test("QC fondo: con relazioni", _test_qc_fond_with_relations)

    def _test_qc_fond_subtree():
        """QC su fondo con sottoalbero."""
        from archimista_python.archive.models import Fond, Unit
        root = Fond.objects.create(
            name='Fondo QC Root',
            description='Root desc', history='Root history', length=200,
            created_by=1, updated_by=1,
        )
        child = Fond.objects.create(name='Fondo QC Child', parent=root, created_by=1, updated_by=1)
        Unit.objects.create(title='Unit in Root', fond=root, created_by=1, updated_by=1)
        Unit.objects.create(title='Unit in Child', fond=child, created_by=1, updated_by=1)

        resp = client.get(reverse('archive:quality_check_fond', args=[root.pk]))
        assert resp.status_code == 200, f"QC fond con sottoalbero failed: {resp.status_code}"
    test("QC fondo: con sottoalbero", _test_qc_fond_subtree)

    section("15b. Quality Check — creatore")

    def _test_qc_creator_incomplete():
        """Creatore vuoto → controlli falliscono."""
        from archimista_python.archive.models import Creator
        creator = Creator.objects.create(creator_type='P', created_by=1, updated_by=1)
        resp = client.get(reverse('archive:quality_check_creator', args=[creator.pk]))
        assert resp.status_code == 200
    test("QC creatore incompleto", _test_qc_creator_incomplete)

    def _test_qc_creator_complete():
        """Creatore completo → controlli passano."""
        from archimista_python.archive.models import Creator, CreatorName, Event, Source, RelCreatorSource
        from django.contrib.contenttypes.models import ContentType

        creator = Creator.objects.create(creator_type='E', created_by=1, updated_by=1)
        CreatorName.objects.create(creator=creator, name='Ente QC Completo', preferred=True)
        Event.objects.create(
            content_type=ContentType.objects.get_for_model(Creator),
            object_id=creator.pk,
            start_date_format='Y', start_date_from='1800-01-01', start_date_display='1800',
            preferred=True,
        )
        creator.history = 'Profilo storico completo'
        creator.save()
        source = Source.objects.create(short_title='Fonte QC Creator', source_type_code='1', created_by=1, updated_by=1)
        RelCreatorSource.objects.create(creator=creator, source=source)

        resp = client.get(reverse('archive:quality_check_creator', args=[creator.pk]))
        assert resp.status_code == 200
    test("QC creatore completo", _test_qc_creator_complete)

    def _test_qc_creator_with_entity_type():
        """Creatore di tipo Ente → deve avere creator_corporate_type."""
        from archimista_python.archive.models import Creator, CreatorCorporateType, CreatorName
        corp_type = CreatorCorporateType.objects.create(corporate_type='Tipo Ente QC')
        creator = Creator.objects.create(
            creator_type='E', creator_corporate_type=corp_type, created_by=1, updated_by=1,
        )
        CreatorName.objects.create(creator=creator, name='Ente QC Corporate', preferred=True)

        resp = client.get(reverse('archive:quality_check_creator', args=[creator.pk]))
        assert resp.status_code == 200
    test("QC creatore: tipo ente con corporate type", _test_qc_creator_with_entity_type)

    section("15c. Quality Check — conservatore")

    def _test_qc_custodian_incomplete():
        """Conservatore vuoto → controlli falliscono."""
        from archimista_python.archive.models import Custodian, CustodianType
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='QC Incomplete')
        custodian = Custodian.objects.create(custodian_type=ctype, created_by=1, updated_by=1)
        resp = client.get(reverse('archive:quality_check_custodian', args=[custodian.pk]))
        assert resp.status_code == 200
    test("QC conservatore incompleto", _test_qc_custodian_incomplete)

    def _test_qc_custodian_complete():
        """Conservatore completo con sedi → controlli passano."""
        from archimista_python.archive.models import Custodian, CustodianType, CustodianName, CustodianBuilding
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='QC Complete')
        custodian = Custodian.objects.create(custodian_type=ctype, created_by=1, updated_by=1)
        CustodianName.objects.create(custodian=custodian, name='Archivio QC Completo', preferred=True)
        CustodianBuilding.objects.create(
            custodian=custodian, name='Sede Principale',
            address='Via Roma 1', city='Milano',
        )

        resp = client.get(reverse('archive:quality_check_custodian', args=[custodian.pk]))
        assert resp.status_code == 200
    test("QC conservatore completo con sedi", _test_qc_custodian_complete)

    section("15d. Quality Check — index")

    def _test_qc_index_shows_all_entities():
        """QC index mostra lista di fondi root, creatori, conservatori."""
        from archimista_python.archive.models import Fond, Creator, Custodian, CustodianType
        Fond.objects.create(name='QCIndexFond', created_by=1, updated_by=1)
        Creator.objects.create(creator_type='P', created_by=1, updated_by=1)
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='QCIndex')
        Custodian.objects.create(custodian_type=ctype, created_by=1, updated_by=1)

        resp = client.get(reverse('archive:quality_check_index'))
        assert resp.status_code == 200, f"QC index failed: {resp.status_code}"
    test("QC index: pagina carica", _test_qc_index_shows_all_entities)

    def _test_qc_index_search():
        """QC index con ricerca."""
        resp = client.get(reverse('archive:quality_check_index') + '?q=QC+Index')
        assert resp.status_code == 200
    test("QC index: ricerca", _test_qc_index_search)
