#!/usr/bin/env python
"""
Test server-side di Archimista Python/Django — v0.51.0+

Scheletro runner — importa ed esegue tutti i moduli in tests/.
I test effettivi sono in tests/test_*.py

COPRE (323+ test in 23+ moduli):
  1. Import moduli, URL, widgets, forms, templates
  2. CRUD Fond, Unit, Creator, Custodian
  3. CRUD 9 entità di servizio (Source, Project, Institution, Heading, Anagraphic, DocumentForm, Editor, Classification, DigitalObject)
  4. API albero (tree data, manipulation, trash)
  5. Gerarchia unità (move_up, move_down), classificazione di massa
  6. Export PDF/RTF/AEF/CSV con validazione contenuto
  7. Report, Quality checks, Import AEF con file reale, Autenticazione
  8. Proprietà/metodi modelli, ricerca globale/avanzata
  9. DigitalObject CRUD completo (upload, validazione, nested)
  10. Form validation (11 form)
  11. Seed scripts (vocabularies, source_types, admin_user)
  12. Formset annidati SC2, File upload, Edge case data, Large data
  13. AEF round-trip, Export content validation

NOTA: I test E2E (JavaScript/browser) sono in tests_e2e/ e si lanciano con pytest.
      Usa run_all_tests.py per eseguire tutto insieme.
"""

from tests import run_all

if __name__ == '__main__':
    run_all()
