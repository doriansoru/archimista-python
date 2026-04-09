"""Test: CRUD Unit — create, detail, update, delete, move, classify."""
from tests import test, section, client
from django.urls import reverse


def run():
    section("6b. Unit CRUD")

    def _run_unit_crud():
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if not fond:
            fond = Fond.objects.create(name='Unit Test Fond', created_by=1, updated_by=1)

        # Create
        resp = client.post(reverse('archive:unit_create'), {
            'title': 'Unità Test', 'fond': fond.pk, 'parent': '', 'unit_type_term': '', 'published': False,
            'unit_identifier-TOTAL_FORMS': '1', 'unit_identifier-INITIAL_FORMS': '0', 'unit_identifier-MIN_NUM_FORMS': '0', 'unit_identifier-MAX_NUM_FORMS': '1000',
            'unit_other_reference_number-TOTAL_FORMS': '1', 'unit_other_reference_number-INITIAL_FORMS': '0', 'unit_other_reference_number-MIN_NUM_FORMS': '0', 'unit_other_reference_number-MAX_NUM_FORMS': '1000',
            'unit_lang-TOTAL_FORMS': '1', 'unit_lang-INITIAL_FORMS': '0', 'unit_lang-MIN_NUM_FORMS': '0', 'unit_lang-MAX_NUM_FORMS': '1000',
            'unit_damage-TOTAL_FORMS': '1', 'unit_damage-INITIAL_FORMS': '0', 'unit_damage-MIN_NUM_FORMS': '0', 'unit_damage-MAX_NUM_FORMS': '1000',
            'unit_url-TOTAL_FORMS': '1', 'unit_url-INITIAL_FORMS': '0', 'unit_url-MIN_NUM_FORMS': '0', 'unit_url-MAX_NUM_FORMS': '1000',
            'unit_editor-TOTAL_FORMS': '1', 'unit_editor-INITIAL_FORMS': '0', 'unit_editor-MIN_NUM_FORMS': '0', 'unit_editor-MAX_NUM_FORMS': '1000',
            'rel_unit_heading-TOTAL_FORMS': '1', 'rel_unit_heading-INITIAL_FORMS': '0', 'rel_unit_heading-MIN_NUM_FORMS': '0', 'rel_unit_heading-MAX_NUM_FORMS': '1000',
            'rel_unit_source-TOTAL_FORMS': '1', 'rel_unit_source-INITIAL_FORMS': '0', 'rel_unit_source-MIN_NUM_FORMS': '0', 'rel_unit_source-MAX_NUM_FORMS': '1000',
            'rel_unit_anagraphic-TOTAL_FORMS': '1', 'rel_unit_anagraphic-INITIAL_FORMS': '0', 'rel_unit_anagraphic-MIN_NUM_FORMS': '0', 'rel_unit_anagraphic-MAX_NUM_FORMS': '1000',
            'sc2-TOTAL_FORMS': '1', 'sc2-INITIAL_FORMS': '0', 'sc2-MIN_NUM_FORMS': '0', 'sc2-MAX_NUM_FORMS': '1000',
            'sc2_textual-TOTAL_FORMS': '1', 'sc2_textual-INITIAL_FORMS': '0', 'sc2_textual-MIN_NUM_FORMS': '0', 'sc2_textual-MAX_NUM_FORMS': '1000',
            'sc2_visual-TOTAL_FORMS': '1', 'sc2_visual-INITIAL_FORMS': '0', 'sc2_visual-MIN_NUM_FORMS': '0', 'sc2_visual-MAX_NUM_FORMS': '1000',
            'sc2_author-TOTAL_FORMS': '1', 'sc2_author-INITIAL_FORMS': '0', 'sc2_author-MIN_NUM_FORMS': '0', 'sc2_author-MAX_NUM_FORMS': '1000',
            'sc2_commission-TOTAL_FORMS': '1', 'sc2_commission-INITIAL_FORMS': '0', 'sc2_commission-MIN_NUM_FORMS': '0', 'sc2_commission-MAX_NUM_FORMS': '1000',
            'sc2_technique-TOTAL_FORMS': '1', 'sc2_technique-INITIAL_FORMS': '0', 'sc2_technique-MIN_NUM_FORMS': '0', 'sc2_technique-MAX_NUM_FORMS': '1000',
            'sc2_scale-TOTAL_FORMS': '1', 'sc2_scale-INITIAL_FORMS': '0', 'sc2_scale-MIN_NUM_FORMS': '0', 'sc2_scale-MAX_NUM_FORMS': '1000',
            'iccd-TOTAL_FORMS': '1', 'iccd-INITIAL_FORMS': '0', 'iccd-MIN_NUM_FORMS': '0', 'iccd-MAX_NUM_FORMS': '1000',
            'iccd_author-TOTAL_FORMS': '1', 'iccd_author-INITIAL_FORMS': '0', 'iccd_author-MIN_NUM_FORMS': '0', 'iccd_author-MAX_NUM_FORMS': '1000',
            'iccd_subject-TOTAL_FORMS': '1', 'iccd_subject-INITIAL_FORMS': '0', 'iccd_subject-MIN_NUM_FORMS': '0', 'iccd_subject-MAX_NUM_FORMS': '1000',
            'iccd_damage-TOTAL_FORMS': '1', 'iccd_damage-INITIAL_FORMS': '0', 'iccd_damage-MIN_NUM_FORMS': '0', 'iccd_damage-MAX_NUM_FORMS': '1000',
            'iccd_tech_spec-TOTAL_FORMS': '1', 'iccd_tech_spec-INITIAL_FORMS': '0', 'iccd_tech_spec-MIN_NUM_FORMS': '0', 'iccd_tech_spec-MAX_NUM_FORMS': '1000',
            'fsc_code-TOTAL_FORMS': '1', 'fsc_code-INITIAL_FORMS': '0', 'fsc_code-MIN_NUM_FORMS': '0', 'fsc_code-MAX_NUM_FORMS': '1000',
            'fsc_organization-TOTAL_FORMS': '1', 'fsc_organization-INITIAL_FORMS': '0', 'fsc_organization-MIN_NUM_FORMS': '0', 'fsc_organization-MAX_NUM_FORMS': '1000',
            'fsc_nationality-TOTAL_FORMS': '1', 'fsc_nationality-INITIAL_FORMS': '0', 'fsc_nationality-MIN_NUM_FORMS': '0', 'fsc_nationality-MAX_NUM_FORMS': '1000',
            'fsc_open-TOTAL_FORMS': '1', 'fsc_open-INITIAL_FORMS': '0', 'fsc_open-MIN_NUM_FORMS': '0', 'fsc_open-MAX_NUM_FORMS': '1000',
            'fsc_close-TOTAL_FORMS': '1', 'fsc_close-INITIAL_FORMS': '0', 'fsc_close-MIN_NUM_FORMS': '0', 'fsc_close-MAX_NUM_FORMS': '1000',
            'fe_id-TOTAL_FORMS': '1', 'fe_id-INITIAL_FORMS': '0', 'fe_id-MIN_NUM_FORMS': '0', 'fe_id-MAX_NUM_FORMS': '1000',
            'fe_context-TOTAL_FORMS': '1', 'fe_context-INITIAL_FORMS': '0', 'fe_context-MIN_NUM_FORMS': '0', 'fe_context-MAX_NUM_FORMS': '1000',
            'fe_opera-TOTAL_FORMS': '1', 'fe_opera-INITIAL_FORMS': '0', 'fe_opera-MIN_NUM_FORMS': '0', 'fe_opera-MAX_NUM_FORMS': '1000',
            'fe_designer-TOTAL_FORMS': '1', 'fe_designer-INITIAL_FORMS': '0', 'fe_designer-MIN_NUM_FORMS': '0', 'fe_designer-MAX_NUM_FORMS': '1000',
            'fe_cadastral-TOTAL_FORMS': '1', 'fe_cadastral-INITIAL_FORMS': '0', 'fe_cadastral-MIN_NUM_FORMS': '0', 'fe_cadastral-MAX_NUM_FORMS': '1000',
            'fe_land-TOTAL_FORMS': '1', 'fe_land-INITIAL_FORMS': '0', 'fe_land-MIN_NUM_FORMS': '0', 'fe_land-MAX_NUM_FORMS': '1000',
            'fe_fract_land-TOTAL_FORMS': '1', 'fe_fract_land-INITIAL_FORMS': '0', 'fe_fract_land-MIN_NUM_FORMS': '0', 'fe_fract_land-MAX_NUM_FORMS': '1000',
            'fe_fract_edil-TOTAL_FORMS': '1', 'fe_fract_edil-INITIAL_FORMS': '0', 'fe_fract_edil-MIN_NUM_FORMS': '0', 'fe_fract_edil-MAX_NUM_FORMS': '1000',
        }, follow=True)
        assert resp.status_code == 200, f"Unit create failed: {resp.status_code}"

        unit = Unit.objects.filter(title='Unità Test').first()
        assert unit is not None, "Unità non creata"

        # Detail
        resp = client.get(reverse('archive:unit_detail', args=[unit.pk]))
        assert resp.status_code == 200, f"Unit detail failed: {resp.status_code}"

        # Update
        resp = client.get(reverse('archive:unit_update', args=[unit.pk]))
        assert resp.status_code == 200, f"Unit update GET failed: {resp.status_code}"

        # Delete
        resp = client.get(reverse('archive:unit_delete', args=[unit.pk]))
        assert resp.status_code == 200, f"Unit delete confirm failed: {resp.status_code}"

    test("Unit: create, detail, update, delete confirm", _run_unit_crud)

    # Unit move_up / move_down
    section("  6b1. Gerarchia unità (move_up, move_down)")

    def _test_unit_move_up():
        from archimista_python.archive.models import Unit, Fond
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if not fond:
            fond = Fond.objects.create(name='Move Test Fond', created_by=1, updated_by=1)
        parent = Unit.objects.create(title='Parent Unit', fond=fond, created_by=1, updated_by=1)
        child = Unit.objects.create(
            title='Child Unit', fond=fond, parent=parent,
            ancestry=str(parent.pk), ancestry_depth=1, created_by=1, updated_by=1,
        )
        resp = client.post(reverse('archive:unit_move_up', args=[child.pk]), follow=True)
        assert resp.status_code == 200, f"Unit move_up failed: {resp.status_code}"
        child.refresh_from_db()
        assert child.parent is None, f"Expected parent=None after move_up, got {child.parent_id}"
    test("Unit: move_up (promozione)", _test_unit_move_up)

    def _test_unit_move_down():
        from archimista_python.archive.models import Unit, Fond
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if not fond:
            fond = Fond.objects.create(name='Move Down Fond', created_by=1, updated_by=1)
        root_unit = Unit.objects.create(title='Root Unit', fond=fond, created_by=1, updated_by=1)
        sibling = Unit.objects.create(
            title='Sibling Unit', fond=fond, parent=root_unit,
            ancestry=str(root_unit.pk), ancestry_depth=1, created_by=1, updated_by=1,
        )
        resp = client.post(reverse('archive:unit_move_down', args=[root_unit.pk]), {
            'new_parent_id': sibling.pk,
        }, follow=True)
        assert resp.status_code == 200, f"Unit move_down failed: {resp.status_code}"
        root_unit.refresh_from_db()
        assert root_unit.parent_id == sibling.pk, f"Expected parent={sibling.pk}, got {root_unit.parent_id}"
    test("Unit: move_down (demotion)", _test_unit_move_down)

    # Classificazione di massa
    section("  6b2. Classificazione di massa")

    def _test_units_classify():
        import json
        from archimista_python.archive.models import Unit, Fond
        unit = Unit.objects.filter(title='Unità Test').first()
        if unit and unit.fond:
            resp = client.put(
                reverse('archive:units_classify'),
                data=json.dumps({'record_ids': [unit.pk], 'new_fond_id': unit.fond.pk}),
                content_type='application/json',
            )
            assert resp.status_code == 200, f"Units classify failed: {resp.status_code}"
            data = resp.json()
            assert data['status'] == 'success', f"Units classify error: {data.get('message')}"
        else:
            from tests import skip
            skip("Units classify (no unit/fond)", "Nessuna unità con fondo")
    test("Unit: classify API", _test_units_classify)
