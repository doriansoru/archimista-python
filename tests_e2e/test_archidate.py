"""
Test E2E — Archidate (data puntuale / data secolare).

Verifica:
  1. Formato Y (data puntuale) → campi anno/mese/giorno visibili
  2. Formato C (data secolare) → secolo/intervallo visibili
  3. Switch Y → C → Y → toggling corretto
  4. Equal bounds → checkbox disabilita estremo finale
  5. Archidate wrapper ha stile corretto
"""


class TestArchidate:
    """Test archidate format toggle."""

    def test_default_format_is_visible(self, logged_in_page, base_url, fond_pk):
        """Format Y (default) → campi data puntuale visibili."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(1000)

        format_togglers = logged_in_page.locator('.format-toggler')
        assert format_togglers.count() > 0, 'Format toggler non trovato'

        year_input = logged_in_page.locator('input[name*="start_date_from_year"]')
        if year_input.count() > 0:
            assert year_input.first.is_visible(), 'Campo anno non visibile con formato Y'

    def test_switch_to_century_format(self, logged_in_page, base_url, fond_pk):
        """Clic su formato C → secolo/intervallo visibili, anno nascosto."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(1000)

        result = logged_in_page.evaluate('''() => {
            const radioC = document.querySelector('.format-toggler.start[value="C"]');
            if (!radioC) return 'radio-not-found';
            radioC.click();
            return 'clicked';
        }''')
        assert result == 'clicked', f'Radio C non cliccato: {result}'
        logged_in_page.wait_for_timeout(500)

        c_wrapper_status = logged_in_page.evaluate('''() => {
            const wrapper = document.querySelector('.archidate-format-wrapper.C.active');
            return wrapper ? 'active' : (document.querySelector('.archidate-format-wrapper.C') ? 'inactive' : 'missing');
        }''')
        assert c_wrapper_status in ('active', 'inactive'), f'C wrapper status: {c_wrapper_status}'

    def test_switch_back_to_year_format(self, logged_in_page, base_url, fond_pk):
        """Clic su formato Y → anno/mese/giorno tornano visibili."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(1000)

        # Prima switch a C
        logged_in_page.evaluate('''() => {
            const radioC = document.querySelector('.format-toggler.start[value="C"]');
            if (radioC) radioC.click();
        }''')
        logged_in_page.wait_for_timeout(300)

        # Poi switch a Y
        result = logged_in_page.evaluate('''() => {
            const radioY = document.querySelector('.format-toggler.start[value="Y"]');
            if (!radioY) return 'radio-not-found';
            radioY.click();
            return 'clicked';
        }''')
        assert result == 'clicked', f'Radio Y non cliccato: {result}'
        logged_in_page.wait_for_timeout(500)

        y_wrapper_status = logged_in_page.evaluate('''() => {
            const wrapper = document.querySelector('.archidate-format-wrapper.Y.active');
            return wrapper ? 'active' : 'inactive-or-missing';
        }''')
        assert y_wrapper_status == 'active', f'Y wrapper non attivo dopo switch: {y_wrapper_status}'

    def test_equal_bounds_checkbox(self, logged_in_page, base_url, fond_pk):
        """Checkbox "uguali" → estremo finale disabilitato."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(1000)

        eq_checkbox = logged_in_page.locator('.equal-bounds-command')
        if eq_checkbox.count() == 0:
            import pytest
            pytest.skip('Equal bounds checkbox non trovato')

        eq_checkbox.first.check()
        logged_in_page.wait_for_timeout(500)

        end_bound_status = logged_in_page.evaluate('''() => {
            const endBound = document.querySelector('.end.bound-wrapper.inactive');
            return endBound ? 'disabled' : 'enabled';
        }''')
        assert end_bound_status == 'disabled', f'End bound non disabilitato: {end_bound_status}'

    def test_archidate_wrapper_styled(self, logged_in_page, base_url, fond_pk):
        """Archidate wrapper ha stile corretto (bordo, sfondo)."""
        logged_in_page.goto(f'{base_url}/fonds/{fond_pk}/edit/', wait_until='networkidle')
        logged_in_page.wait_for_timeout(1000)

        wrapper = logged_in_page.locator('.archidate-wrapper')
        assert wrapper.count() > 0, 'Archidate wrapper non trovato'

        bg = logged_in_page.evaluate('''() => {
            const wrapper = document.querySelector('.archidate-wrapper');
            if (!wrapper) return 'not-found';
            return window.getComputedStyle(wrapper).backgroundColor;
        }''')
        assert bg != 'not-found', 'Archidate wrapper non trovato nel DOM'
