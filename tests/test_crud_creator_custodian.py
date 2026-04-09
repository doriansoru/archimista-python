"""Test: CRUD Creator e Custodian."""
from tests import test, section, client
from django.urls import reverse


def run():
    section("6c. Creator CRUD")

    def _run_creator_crud():
        from archimista_python.archive.models import Creator, CreatorCorporateType
        corp_type = CreatorCorporateType.objects.create(corporate_type='Ente test CRUD')
        creator = Creator.objects.create(
            creator_type='P', creator_corporate_type=corp_type,
            published=False, created_by=1, updated_by=1,
        )
        resp = client.get(reverse('archive:creator_list'))
        assert resp.status_code == 200, f"Creator list failed: {resp.status_code}"
        resp = client.get(reverse('archive:creator_detail', args=[creator.pk]))
        assert resp.status_code == 200, f"Creator detail failed: {resp.status_code}"
        resp = client.get(reverse('archive:creator_update', args=[creator.pk]))
        assert resp.status_code == 200, f"Creator update GET failed: {resp.status_code}"
        resp = client.get(reverse('archive:creator_delete', args=[creator.pk]))
        assert resp.status_code == 200, f"Creator delete confirm failed: {resp.status_code}"
    test("Creator: list, detail, update, delete confirm", _run_creator_crud)

    section("6d. Custodian CRUD")

    def _run_custodian_crud():
        from archimista_python.archive.models import Custodian, CustodianType
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='Archivio test')
        resp = client.post(reverse('archive:custodian_create'), {
            'custodian_type': ctype.pk, 'published': False,
            'name': 'Conservatore Test', 'note': '',
            'custodian_names-TOTAL_FORMS': '0', 'custodian_names-INITIAL_FORMS': '0', 'custodian_names-MIN_NUM_FORMS': '0', 'custodian_names-MAX_NUM_FORMS': '1000',
            'custodian_identifiers-TOTAL_FORMS': '0', 'custodian_identifiers-INITIAL_FORMS': '0', 'custodian_identifiers-MIN_NUM_FORMS': '0', 'custodian_identifiers-MAX_NUM_FORMS': '1000',
            'custodian_contacts-TOTAL_FORMS': '0', 'custodian_contacts-INITIAL_FORMS': '0', 'custodian_contacts-MIN_NUM_FORMS': '0', 'custodian_contacts-MAX_NUM_FORMS': '1000',
            'custodian_buildings-TOTAL_FORMS': '0', 'custodian_buildings-INITIAL_FORMS': '0', 'custodian_buildings-MIN_NUM_FORMS': '0', 'custodian_buildings-MAX_NUM_FORMS': '1000',
            'custodian_owners-TOTAL_FORMS': '0', 'custodian_owners-INITIAL_FORMS': '0', 'custodian_owners-MIN_NUM_FORMS': '0', 'custodian_owners-MAX_NUM_FORMS': '1000',
            'custodian_urls-TOTAL_FORMS': '0', 'custodian_urls-INITIAL_FORMS': '0', 'custodian_urls-MIN_NUM_FORMS': '0', 'custodian_urls-MAX_NUM_FORMS': '1000',
            'custodian_editors-TOTAL_FORMS': '0', 'custodian_editors-INITIAL_FORMS': '0', 'custodian_editors-MIN_NUM_FORMS': '0', 'custodian_editors-MAX_NUM_FORMS': '1000',
            'rel_custodian_sources-TOTAL_FORMS': '0', 'rel_custodian_sources-INITIAL_FORMS': '0', 'rel_custodian_sources-MIN_NUM_FORMS': '0', 'rel_custodian_sources-MAX_NUM_FORMS': '1000',
            'rel_custodian_fonds-TOTAL_FORMS': '0', 'rel_custodian_fonds-INITIAL_FORMS': '0', 'rel_custodian_fonds-MIN_NUM_FORMS': '0', 'rel_custodian_fonds-MAX_NUM_FORMS': '1000',
        }, follow=True)
        if resp.status_code != 200:
            raise AssertionError(f"Custodian create failed: {resp.status_code}")
        custodian = Custodian.objects.order_by('-pk').first()
        assert custodian is not None, "Custodian non creato"
        resp = client.get(reverse('archive:custodian_list'))
        assert resp.status_code == 200, f"Custodian list failed: {resp.status_code}"
        resp = client.get(reverse('archive:custodian_detail', args=[custodian.pk]))
        assert resp.status_code == 200, f"Custodian detail failed: {resp.status_code}"
        resp = client.get(reverse('archive:custodian_update', args=[custodian.pk]))
        assert resp.status_code == 200, f"Custodian update GET failed: {resp.status_code}"
        resp = client.get(reverse('archive:custodian_delete', args=[custodian.pk]))
        assert resp.status_code == 200, f"Custodian delete confirm failed: {resp.status_code}"
    test("Custodian: create, list, detail, update, delete confirm", _run_custodian_crud)
