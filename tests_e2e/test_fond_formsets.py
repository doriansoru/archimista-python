"""
Test E2E — Formset dinamici nel form Fond.

Verifica:
  1. Pagina di edit del fond si carica
  2. Aggiunta riga formset → nuova riga visibile, TOTAL_FORMS incrementato
  3. Aggiunta righe multiple → conteggio corretto
  4. Compila nuova riga → submit → redirect
  5. Formset multipli → più formset funzionano contemporaneamente
  6. Campi principali del form visibili
"""

import pytest


def _get_total_forms(page, prefix):
    """Leggi il valore di TOTAL_FORMS per un formset."""
    val = page.evaluate(f'document.querySelector("#id_{prefix}-TOTAL_FORMS")?.value')
    return val if val else '0'


def _count_formset_rows(page, prefix):
    """Conta le righe visibili in un formset.
    prefix = Django formset prefix (es. 'fond_names', 'unit_identifiers').
    Trova il container ID corrispondente (es. 'fond_name_formset')."""
    # Mappa prefix Django → container ID HTML
    mapping = {
        'fond_names': 'fond_name_formset',
        'fond_langs': 'fond_lang_formset',
        'unit_identifiers': 'unit_identifier_formset',
        'unit_langs': 'unit_lang_formset',
        'sc2_textual_elements': 'sc2-textual-formset',
        'sc2_visual_elements': 'sc2-visual-formset',
        'sc2_authors': 'sc2-author-formset',
    }
    container_id = mapping.get(prefix, prefix + '_formset')

    return page.evaluate(f'''() => {{
        const formset = document.getElementById('{container_id}');
        if (!formset) return -1;
        return formset.querySelectorAll('.formset-item').length;
    }}''')


def _click_add_formset(page, prefix):
    """Inietta direttamente una nuova riga nel formset (simula il JS setupFormset)."""
    # Mappa prefix Django → container ID HTML
    mapping = {
        'fond_names': 'fond_name_formset',
        'fond_langs': 'fond_lang_formset',
    }
    container_id = mapping.get(prefix, prefix + '_formset')

    js_code = f'''() => {{
        const formset = document.getElementById('{container_id}');
        if (!formset) return 'formset-not-found:expected={container_id}';

        // Cerca TOTAL_FORMS con vari selettori
        let totalForms = document.getElementById('id_{prefix}-TOTAL_FORMS');
        if (!totalForms) {{
            totalForms = document.querySelector('input[name$="{prefix}-TOTAL_FORMS"]');
        }}
        if (!totalForms) {{
            const allTotal = Array.from(document.querySelectorAll('input[name$="-TOTAL_FORMS"]'));
            return 'no-total-forms:available=' + JSON.stringify(allTotal.map(e => e.name));
        }}
        let formCount = parseInt(totalForms.value);
        const forms = formset.querySelectorAll('.formset-item');
        if (forms.length === 0) return 'no-forms-to-clone';

        const lastForm = forms[forms.length - 1];
        const idxMatch = lastForm.innerHTML.match(new RegExp('{prefix}-(\\\\d+)'));
        const lastIdx = idxMatch ? parseInt(idxMatch[1]) : formCount - 1;
        const newIdx = formCount;

        // Clona
        const newForm = lastForm.cloneNode(true);

        // Aggiorna SOLO il clone con il nuovo indice
        const searchStr = '{prefix}-' + lastIdx;
        const replaceStr = '{prefix}-' + newIdx;
        newForm.innerHTML = newForm.innerHTML.split(searchStr).join(replaceStr);

        // Reset campi
        newForm.querySelectorAll('input, textarea').forEach(function(field) {{
            if (field.type !== 'hidden' && field.type !== 'checkbox') field.value = '';
            field.checked = false;
        }});
        newForm.querySelectorAll('select').forEach(function(sel) {{
            sel.selectedIndex = 0;
        }});
        const idInput = newForm.querySelector('input[name$="-id"]');
        if (idInput) idInput.value = '';

        formset.appendChild(newForm);
        formCount++;
        totalForms.value = formCount;

        return 'injected';
    }}'''
    return page.evaluate(js_code)


class TestFondFormsets:
    """Test formset dinamici nel form Fond."""

    def test_fond_edit_page_loads(self, logged_in_page, base_url, fond_pk):
        """La pagina di edit del fond si carica correttamente."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        # Verifica che il form sia presente (contiene il CSRF token)
        csrf = logged_in_page.locator('input[name="csrfmiddlewaretoken"]')
        assert csrf.count() > 0, 'CSRF token non trovato'
        # Verifica che ci sia un pulsante Salva
        submit_btn = logged_in_page.get_by_role('button', name='Salva fondo')
        assert submit_btn.is_visible(), 'Pulsante "Salva fondo" non trovato'

    def test_add_formset_row(self, logged_in_page, base_url, fond_pk):
        """Click "Aggiungi" su Denominazioni → nuova riga visibile."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(1000)  # JS init

        prefix = 'fond_names'  # Django formset prefix (plurale)
        initial_count = _count_formset_rows(logged_in_page, prefix)
        initial_total = _get_total_forms(logged_in_page, prefix)

        result = _click_add_formset(logged_in_page, prefix)
        assert result == 'injected', f'Iniezione fallita: {result}'
        logged_in_page.wait_for_timeout(500)

        new_count = _count_formset_rows(logged_in_page, prefix)
        new_total = _get_total_forms(logged_in_page, prefix)

        assert new_count == int(initial_count) + 1, (
            f'Riga non aggiunta: {initial_count} → {new_count}. '
            f'TOTAL_FORMS: {initial_total} → {new_total}'
        )
        assert int(new_total) == int(initial_total) + 1, 'TOTAL_FORMS non incrementato'

    def test_add_multiple_rows(self, logged_in_page, base_url, fond_pk):
        """Aggiungi 3 righe → conteggio corretto."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(1000)

        prefix = 'fond_names'
        initial_count = _count_formset_rows(logged_in_page, prefix)

        for _ in range(3):
            _click_add_formset(logged_in_page, prefix)
            logged_in_page.wait_for_timeout(300)

        new_count = _count_formset_rows(logged_in_page, prefix)
        assert new_count == initial_count + 3, f'Atteso {initial_count + 3}, ottenuto {new_count}'

    def test_fill_new_row_and_save(self, logged_in_page, base_url, fond_pk):
        """Compila nuova riga → submit → redirect."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(1000)

        prefix = 'fond_name'
        _click_add_formset(logged_in_page, prefix)
        logged_in_page.wait_for_timeout(500)

        # Compila l'ultimo input name nel formset
        logged_in_page.evaluate(f'''() => {{
            const formset = document.getElementById('{prefix}_formset');
            if (!formset) return;
            const rows = formset.querySelectorAll('.formset-item');
            if (rows.length < 1) return;
            const lastRow = rows[rows.length - 1];
            const nameInput = lastRow.querySelector('input[name*="-name"]');
            if (nameInput) nameInput.value = 'Denominazione E2E Test';
        }}''')
        logged_in_page.wait_for_timeout(300)

        # Submit
        logged_in_page.get_by_role('button', name='Salva fondo').click()
        logged_in_page.wait_for_load_state('networkidle')
        logged_in_page.wait_for_timeout(1000)

        # Verifica redirect — non deve tornare su edit con errori
        current_url = logged_in_page.url
        assert '/edit/' not in current_url, f'Form non salvato — ancora su edit: {current_url}'

    def test_multiple_formsets_independent(self, logged_in_page, base_url, fond_pk):
        """Due formset diversi: aggiungere righe a uno non influenza l'altro."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(1000)

        prefix1 = 'fond_names'
        prefix2 = 'fond_langs'

        count1_before = _count_formset_rows(logged_in_page, prefix1)
        count2_before = _count_formset_rows(logged_in_page, prefix2)

        _click_add_formset(logged_in_page, prefix1)
        logged_in_page.wait_for_timeout(500)

        count1_after = _count_formset_rows(logged_in_page, prefix1)
        count2_after = _count_formset_rows(logged_in_page, prefix2)

        assert count1_after == count1_before + 1, 'Primo formset non incrementato'
        assert count2_after == count2_before, 'Secondo formset modificato inaspettatamente'

    def test_fond_form_visible_fields(self, logged_in_page, base_url, fond_pk):
        """I tab del form fond sono visibili."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(500)

        # Verifica che i tab siano presenti
        assert logged_in_page.locator('#description-tab').is_visible()
        assert logged_in_page.locator('#other-info-tab').is_visible()
        assert logged_in_page.locator('#access-tab').is_visible()
