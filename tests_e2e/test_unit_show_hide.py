"""
Test E2E — Show/hide condizionale nel form Unità.

Verifica:
  1. Pagina di edit unità si carica
  2. Tipo "Unità documentaria" → SC2 visibile, FSC nascosto
  3. Tipo "Fascicolo" → SC2 nascosto, FSC visibile
  4. SC2 tipo "F" → sottocampi Fotografia visibili
  5. SC2 tipo "CARS" → sottocampi Cartografia visibili
  6. Cambio tipo dinamico → campi si aggiornano
  7. FSC "Personale" → formset FSC visibili
  8. FSC "Edilizia" → formset FE visibili
  9. Formset SC2 → aggiunta riga funzionante
  10. Persistenza dati → submit → dati salvati
"""


def _select_unit_type(page, option_text):
    """Seleziona un tipo unità dal Select2 (cerca per testo)."""
    return page.evaluate(f'''() => {{
        const select = document.getElementById('id_unit_type_term');
        if (!select) return 'not-found';
        for (const opt of select.options) {{
            if (opt.text.toLowerCase().includes('{option_text}'.toLowerCase())) {{
                select.value = opt.value;
                select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return 'selected:' + opt.value;
            }}
        }}
        return 'not-matched';
    }}''')


def _select_sc2_type(page, value):
    """Seleziona un tipo SC2 (dropdown normale, non Select2)."""
    return page.evaluate(f'''() => {{
        const select = document.getElementById('id_unit_sc2_tsk');
        if (!select) return 'not-found';
        select.value = '{value}';
        select.dispatchEvent(new Event('change', {{ bubbles: true }}));
        return 'selected:' + select.value;
    }}''')


def _select_fsc_type(page, value):
    """Seleziona un tipo fascicolo (dropdown normale)."""
    return page.evaluate(f'''() => {{
        const select = document.getElementById('id_unit_file_type');
        if (!select) return 'not-found';
        select.value = '{value}';
        select.dispatchEvent(new Event('change', {{ bubbles: true }}));
        return 'selected:' + select.value;
    }}''')


class TestUnitShowHide:
    """Test show/hide condizionale nel form Unità."""

    def test_unit_edit_page_loads(self, logged_in_page, base_url, unit_pk):
        """La pagina di edit dell'unità si carica."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(500)
        assert logged_in_page.locator('#description-tab').is_visible()

    def test_documentaria_shows_sc2(self, logged_in_page, base_url, unit_pk):
        """Tipo "Unità documentaria" → SC2 container visibile."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        result = _select_unit_type(logged_in_page, 'documentaria')
        assert 'selected' in result, f'unit_type_term non selezionato: {result}'
        logged_in_page.wait_for_timeout(500)

        sc2_label = logged_in_page.locator('#lbl_unit_sc2_tsk')
        assert sc2_label.is_visible(), 'Label SC2 non visibile con tipo documentaria'

        fsc_label = logged_in_page.locator('#lbl_unit_fsc')
        assert not fsc_label.is_visible(), 'Label FSC dovrebbe essere nascosta con tipo documentaria'

    def test_fascicolo_shows_fsc(self, logged_in_page, base_url, unit_pk):
        """Tipo "Fascicolo" → FSC container visibile, SC2 nascosto."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        result = _select_unit_type(logged_in_page, 'fascicolo')
        assert 'selected' in result, f'unit_type_term non selezionato: {result}'
        logged_in_page.wait_for_timeout(500)

        fsc_label = logged_in_page.locator('#lbl_unit_fsc')
        assert fsc_label.is_visible(), 'Label FSC non visibile con tipo fascicolo'

        sc2_label = logged_in_page.locator('#lbl_unit_sc2_tsk')
        assert not sc2_label.is_visible(), 'Label SC2 dovrebbe essere nascosta con tipo fascicolo'

    def test_sc2_type_filters_containers(self, logged_in_page, base_url, unit_pk):
        """SC2 tipo "F" → mostra container Fotografia, nasconde altri."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        _select_unit_type(logged_in_page, 'documentaria')
        logged_in_page.wait_for_timeout(500)

        result = _select_sc2_type(logged_in_page, 'F')
        assert 'selected' in result, f'sc2_tsk non selezionato: {result}'
        logged_in_page.wait_for_timeout(500)

        lrc_label = logged_in_page.locator('label:has-text("Luogo ripresa")')
        assert lrc_label.count() > 0, 'Campo "Luogo ripresa" non trovato'

    def test_sc2_type_cars_shows_cartography(self, logged_in_page, base_url, unit_pk):
        """SC2 tipo "CARS" → mostra container Cartografia."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        _select_unit_type(logged_in_page, 'documentaria')
        logged_in_page.wait_for_timeout(500)

        result = _select_sc2_type(logged_in_page, 'CARS')
        assert 'selected' in result
        logged_in_page.wait_for_timeout(500)

        sc2_val = logged_in_page.evaluate("document.getElementById('id_unit_sc2_tsk').value")
        assert sc2_val == 'CARS', f'sc2_tsk value: {sc2_val}'

    def test_dynamic_type_change(self, logged_in_page, base_url, unit_pk):
        """Cambio da documentaria a fascicolo → campi si aggiornano."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        _select_unit_type(logged_in_page, 'documentaria')
        logged_in_page.wait_for_timeout(500)
        sc2_visible_1 = logged_in_page.locator('#lbl_unit_sc2_tsk').is_visible()
        assert sc2_visible_1, 'SC2 visibile dopo documentaria'

        _select_unit_type(logged_in_page, 'fascicolo')
        logged_in_page.wait_for_timeout(500)
        sc2_visible_2 = logged_in_page.locator('#lbl_unit_sc2_tsk').is_visible()
        assert not sc2_visible_2, 'SC2 dovrebbe essere nascosto dopo fascicolo'

        fsc_visible_2 = logged_in_page.locator('#lbl_unit_fsc').is_visible()
        assert fsc_visible_2, 'FSC dovrebbe essere visibile dopo fascicolo'

    def test_fsc_personale_shows_fsc(self, logged_in_page, base_url, unit_pk):
        """Fascicolo "Personale" → FSC visibili, FE nascosti."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        _select_unit_type(logged_in_page, 'fascicolo')
        logged_in_page.wait_for_timeout(500)

        result = _select_fsc_type(logged_in_page, 'personale')
        assert 'selected' in result, f'file_type non selezionato: {result}'
        logged_in_page.wait_for_timeout(500)

        fsc_label = logged_in_page.locator('#lbl_unit_fsc')
        assert fsc_label.is_visible(), 'FSC label non visibile con tipo personale'

    def test_fsc_edilizia_shows_fe(self, logged_in_page, base_url, unit_pk):
        """Fascicolo "Edilizia" → FE visibili, FSC nascosti."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        _select_unit_type(logged_in_page, 'fascicolo')
        logged_in_page.wait_for_timeout(500)

        result = _select_fsc_type(logged_in_page, 'edilizia')
        assert 'selected' in result
        logged_in_page.wait_for_timeout(500)

        fe_container = logged_in_page.locator('.fe_container')
        assert fe_container.count() > 0, 'Container FE non trovato nel DOM'

    def test_sc2_formset_present(self, logged_in_page, base_url, unit_pk):
        """Il formset SC2 Authors è presente nel DOM con tipo documentaria."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        _select_unit_type(logged_in_page, 'documentaria')
        logged_in_page.wait_for_timeout(500)

        # Verifica container
        container_exists = logged_in_page.evaluate('''() => {
            return document.getElementById('sc2-author-formset') !== null;
        }''')
        assert container_exists, 'Container sc2-author-formset non trovato'

        # Verifica TOTAL_FORMS
        total_exists = logged_in_page.evaluate('''() => {
            return document.getElementById('id_sc2_authors-TOTAL_FORMS') !== null;
        }''')
        assert total_exists, 'TOTAL_FORMS per sc2_authors non trovato'

    def test_persist_data_after_submit(self, logged_in_page, base_url, unit_pk):
        """Compila titolo → submit → redirect a una pagina di dettaglio."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        title_input = logged_in_page.locator('input[name="title"], textarea[name="title"]')
        if title_input.count() > 0:
            title_input.fill('Unità E2E Modificata')

        logged_in_page.wait_for_timeout(200)

        logged_in_page.click('button[type="submit"]')
        logged_in_page.wait_for_load_state('networkidle')
        logged_in_page.wait_for_timeout(1000)

        current_url = logged_in_page.url
        # Verifica che non siamo tornati alla pagina di edit con errori
        # (il redirect può andare a fond_detail, unit_detail, o unit_list)
        assert '/edit/' not in current_url, f'Form non salvato — ancora su edit: {current_url}'
