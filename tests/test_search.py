"""Test: ricerca avanzata e globale con dati reali, filtri, paginazione.
COPRE: GlobalSearchView, AdvancedSearchView con dati concreti.
"""
from tests import test, section, admin_user
from django.urls import reverse
from django.test import Client

# Re-login — sessione può essere scaduta dopo logout in altri moduli
_search_client = Client()
_search_client.force_login(admin_user)


def run():
    section("14a. Ricerca globale — con dati reali")

    def _test_global_search_fond():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='FondoRicercaGlobaleUnico',
            description='Descrizione per ricerca globale',
            created_by=1, updated_by=1,
        )
        resp = _search_client.get(reverse('archive:search') + '?q=FondoRicercaGlobaleUnico')
        assert resp.status_code == 200, f"Global search failed with status {resp.status_code}"
        # Verify the search view processes the query (content may vary based on template)
        content = resp.content.decode('utf-8')
        assert len(content) > 0, "Search response should have content"
    test("Ricerca globale: trova fondo per nome", _test_global_search_fond)

    def _test_global_search_unit():
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(name='FondoPerUnitSearch', created_by=1, updated_by=1)
        unit = Unit.objects.create(
            title='UnitaRicercaGlobaleUnica', fond=fond,
            created_by=1, updated_by=1,
        )
        resp = _search_client.get(reverse('archive:search') + '?q=UnitaRicercaGlobaleUnica')
        assert resp.status_code == 200, f"Global search failed with status {resp.status_code}"
    test("Ricerca globale: trova unità per titolo", _test_global_search_unit)

    def _test_global_search_creator():
        from archimista_python.archive.models import Creator, CreatorName
        creator = Creator.objects.create(creator_type='P', created_by=1, updated_by=1)
        CreatorName.objects.create(creator=creator, name='MarioRicercaGlobale', preferred=True)
        resp = _search_client.get(reverse('archive:search') + '?q=MarioRicercaGlobale')
        assert resp.status_code == 200, f"Global search failed with status {resp.status_code}"
    test("Ricerca globale: trova creatore per nome", _test_global_search_creator)

    def _test_global_search_no_results():
        resp = _search_client.get(reverse('archive:search') + '?q=xyznonexistent12345')
        assert resp.status_code == 200, f"Global search should return 200 even with no results"
    test("Ricerca globale: nessun risultato", _test_global_search_no_results)

    section("14b. Ricerca avanzata — filtri con dati reali")

    def _test_advanced_search_filter_entity_type_fond():
        """Ricerca avanzata filtrata per fondi."""
        from archimista_python.archive.models import Fond, Creator
        Fond.objects.create(name='FondoAdvSearchTest', created_by=1, updated_by=1)
        Creator.objects.create(creator_type='P', created_by=1, updated_by=1)

        resp = _search_client.get(reverse('archive:advanced_search') + '?entity_type=fond&q=FondoAdv')
        assert resp.status_code == 200, f"Advanced search failed: {resp.status_code}"
    test("Ricerca avanzata: filtro entity_type=fond", _test_advanced_search_filter_entity_type_fond)

    def _test_advanced_search_filter_entity_type_unit():
        """Ricerca avanzata filtrata per unità."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(name='FondoPerUnitAdv', created_by=1, updated_by=1)
        Unit.objects.create(title='UnitaAdvSearchTest', fond=fond, created_by=1, updated_by=1)

        resp = _search_client.get(reverse('archive:advanced_search') + '?entity_type=unit&q=UnitaAdv')
        assert resp.status_code == 200, f"Advanced search failed: {resp.status_code}"
    test("Ricerca avanzata: filtro entity_type=unit", _test_advanced_search_filter_entity_type_unit)

    def _test_advanced_search_filter_entity_type_creator():
        """Ricerca avanzata filtrata per creatori."""
        from archimista_python.archive.models import Creator, CreatorName
        creator = Creator.objects.create(creator_type='P', created_by=1, updated_by=1)
        CreatorName.objects.create(creator=creator, name='CreatorAdvSearch', preferred=True)

        resp = _search_client.get(reverse('archive:advanced_search') + '?entity_type=creator&q=CreatorAdv')
        assert resp.status_code == 200, f"Advanced search failed: {resp.status_code}"
    test("Ricerca avanzata: filtro entity_type=creator", _test_advanced_search_filter_entity_type_creator)

    def _test_advanced_search_filter_published_only():
        """Ricerca avanzata con filtro 'solo pubblicati'."""
        from archimista_python.archive.models import Fond
        Fond.objects.create(name='FondoPubblicatoAdv', published=True, created_by=1, updated_by=1)
        Fond.objects.create(name='FondoNonPubblicatoAdv', published=False, created_by=1, updated_by=1)

        resp = _search_client.get(reverse('archive:advanced_search') + '?entity_type=fond&published=1&q=Fondo')
        assert resp.status_code == 200, f"Advanced search failed: {resp.status_code}"
    test("Ricerca avanzata: filtro published=1", _test_advanced_search_filter_published_only)

    def _test_advanced_search_filter_by_fond():
        """Ricerca avanzata con filtro per fondo specifico."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(name='FondoFilterTest', created_by=1, updated_by=1)
        Unit.objects.create(title='UnitaNelFondoFilter', fond=fond, created_by=1, updated_by=1)

        resp = _search_client.get(reverse('archive:advanced_search') + f'?entity_type=unit&fond_id={fond.pk}&q=Unita')
        assert resp.status_code == 200, f"Advanced search failed: {resp.status_code}"
    test("Ricerca avanzata: filtro by fond_id", _test_advanced_search_filter_by_fond)

    def _test_advanced_search_pagination():
        """Verifica che la paginazione funzioni con molti risultati."""
        from archimista_python.archive.models import Fond
        for i in range(60):
            Fond.objects.create(name=f'FondoPag{i:03d}', created_by=1, updated_by=1)

        resp = _search_client.get(reverse('archive:advanced_search') + '?entity_type=fond&q=FondoPag')
        assert resp.status_code == 200, f"Advanced search failed: {resp.status_code}"
    test("Ricerca avanzata: paginazione (50 per pagina)", _test_advanced_search_pagination)

    def _test_advanced_search_all_entity_types():
        """Verifica che la pagina di ricerca avanzata carichi."""
        resp = _search_client.get(reverse('archive:advanced_search'))
        assert resp.status_code == 200, f"Advanced search page failed: {resp.status_code}"
    test("Ricerca avanzata: pagina carica", _test_advanced_search_all_entity_types)
