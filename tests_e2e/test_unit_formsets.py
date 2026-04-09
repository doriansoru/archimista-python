"""
Test E2E — Formset nel form Unità.

Verifica che i formset siano presenti nel DOM e che il TOTAL_FORMS
esista per ogni tipo di formset.
"""


def _total_forms_exists(page, prefix):
    """Verifica che l'input TOTAL_FORMS esista per un formset."""
    return page.evaluate(f'''() => {{
        const el = document.getElementById('id_{prefix}-TOTAL_FORMS')
                || document.querySelector('input[name$="{prefix}-TOTAL_FORMS"]');
        return el !== null;
    }}''')


def _formset_container_exists(page, container_id):
    """Verifica che il container del formset esista nel DOM."""
    return page.evaluate(f'''() => {{
        return document.getElementById('{container_id}') !== null;
    }}''')


def _count_formset_rows(page, container_id):
    """Conta le righe formset-item nel container."""
    return page.evaluate(f'''() => {{
        const container = document.getElementById('{container_id}');
        if (!container) return -1;
        return container.querySelectorAll('.formset-item').length;
    }}''')


class TestUnitFormsets:
    """Verifica presenza formset nel form Unità."""

    def test_unit_identifier_formset_present(self, logged_in_page, base_url, unit_pk):
        """Il formset identificatori è presente nel DOM."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        assert _formset_container_exists(logged_in_page, 'unit_identifier_formset'), (
            'Container unit_identifier_formset non trovato nel DOM'
        )
        assert _total_forms_exists(logged_in_page, 'unit_identifiers'), (
            'TOTAL_FORMS per unit_identifiers non trovato'
        )

    def test_unit_lang_formset_present(self, logged_in_page, base_url, unit_pk):
        """Il formset lingue è presente nel DOM."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        assert _formset_container_exists(logged_in_page, 'unit_lang_formset'), (
            'Container unit_lang_formset non trovato nel DOM'
        )
        assert _total_forms_exists(logged_in_page, 'unit_langs'), (
            'TOTAL_FORMS per unit_langs non trovato'
        )

    def test_sc2_textual_formset_present(self, logged_in_page, base_url, unit_pk):
        """Il formset SC2 textual è presente nel DOM (visibile con tipo documentaria)."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        # Mostra SC2
        logged_in_page.evaluate('''() => {
            const select = document.getElementById('id_unit_type_term');
            if (select) {
                for (const opt of select.options) {
                    if (opt.text.toLowerCase().includes('documentaria')) {
                        select.value = opt.value;
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                        break;
                    }
                }
            }
        }''')
        logged_in_page.wait_for_timeout(500)

        assert _formset_container_exists(logged_in_page, 'sc2-textual-formset'), (
            'Container sc2-textual-formset non trovato nel DOM dopo aver selezionato documentaria'
        )
        assert _total_forms_exists(logged_in_page, 'sc2_textual_elements'), (
            'TOTAL_FORMS per sc2_textual_elements non trovato'
        )

    def test_sc2_visual_formset_present(self, logged_in_page, base_url, unit_pk):
        """Il formset SC2 visual è presente nel DOM (visibile con tipo documentaria)."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        # Mostra SC2
        logged_in_page.evaluate('''() => {
            const select = document.getElementById('id_unit_type_term');
            if (select) {
                for (const opt of select.options) {
                    if (opt.text.toLowerCase().includes('documentaria')) {
                        select.value = opt.value;
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                        break;
                    }
                }
            }
        }''')
        logged_in_page.wait_for_timeout(500)

        assert _formset_container_exists(logged_in_page, 'sc2-visual-formset'), (
            'Container sc2-visual-formset non trovato nel DOM dopo aver selezionato documentaria'
        )
        assert _total_forms_exists(logged_in_page, 'sc2_visual_elements'), (
            'TOTAL_FORMS per sc2_visual_elements non trovato'
        )

    def test_total_forms_consistent(self, logged_in_page, base_url, unit_pk):
        """TOTAL_FORMS value corrisponde al numero di formset-item nel DOM."""
        logged_in_page.goto(f'{base_url}/units/{unit_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(800)

        # Verifica che TOTAL_FORMS sia un numero coerente con le righe visibili
        # per il formset identificatori
        total_raw = logged_in_page.evaluate('''() => {
            const el = document.getElementById('id_unit_identifiers-TOTAL_FORMS');
            return el ? el.value : null;
        }''')
        if total_raw is not None:
            total_val = int(total_raw)
            rows = _count_formset_rows(logged_in_page, 'unit_identifier_formset')
            assert rows >= 0, 'Container formset non trovato'
            assert total_val == rows, f'TOTAL_FORMS ({total_val}) != righe ({rows})'
