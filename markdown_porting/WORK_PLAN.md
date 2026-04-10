# Piano di Lavoro — Stato Aggiornato (2026-04-10)

## ✅ Fase 10: Installer Windows Standalone (.exe) (COMPLETATA v0.55.0)

### 10a. Launcher intelligente (`archimista_launcher.py`)
- Entry point unificato per sviluppo e bundle PyInstaller
- Rilevamento primo avvio tramite marker `first_run.done`
- Setup guidato al primo avvio:
  1. `manage.py migrate --no-input`
  2. `seed_vocabularies.py`
  3. `seed_source_types.py`
  4. **Domanda interattiva:** vuoi i dati di esempio? (S/n)
  5. Creazione utente admin con password casuale (12 caratteri)
  6. Salvataggio credenziali in `admin_credentials.txt`
  7. `manage.py runserver 127.0.0.1:8000` + apertura browser
- Avvii successivi: salta setup, avvia direttamente il server
- PyInstaller-aware: rileva `sys.frozen` e adatta `BASE_DIR`

### 10b. PyInstaller build (`archimista.spec` + `build_installer.bat`)
- **archimista.spec:**
  - 80+ hidden imports (Django, select2, lxml, Pillow, reportlab, weasyprint, python-docx)
  - Data files: 68 template HTML, migrazioni, file statici, seed scripts, manage.py
  - Esclusioni: playwright, pytest, test suite (non necessari a runtime)
  - Output: one-dir build in `dist\archimista\`
- **build_installer.bat:**
  - Verifica ambiente Python/Django
  - Installa PyInstaller via pip
  - Esegue `collectstatic --no-input --clear`
  - Build con `pyinstaller --clean archimista.spec`

### 10c. Inno Setup installer (`archimista_installer.iss`)
- Installer Windows professionale con wizard moderno
- Lingue: italiano e inglese
- Shortcut: menu Start (sempre), desktop (opzionale), quick launch (opzionale)
- Crea directory `media/` e `staticfiles/` post-installazione
- Compressione LZMA2/ultra64
- Lancio opzionale dell'applicazione post-installazione
- Output: `output\Archimista-Setup-0.55.0.exe`

### 10d. Script di build automatizzati
- **`build_all.bat`:** orchestratore one-click
  - Esegue Stage 1 (PyInstaller)
  - Auto-detect Inno Setup (PATH o percorsi di default)
  - Esegue Stage 2 (iscc.exe)
  - Verifica output
- **`requirements-build.txt`:** dipendenze di build minime (PyInstaller + hooks-contrib)

### 10e. Modifiche a `settings.py`
- **`BASE_DIR` detection:** quando `sys.frozen` è True, usa la directory dell'eseguibile
- **`STATIC_ROOT`:** aggiunto `BASE_DIR / 'staticfiles'` per collectstatic
- **`SECRET_KEY`:** leggibile da `DJANGO_SECRET_KEY` env var
- **`DEBUG`:** leggibile da `DJANGO_DEBUG` env var

### 10f. Documentazione
- **`INSTALLER_BUILD.md`:** guida completa al processo di build, troubleshooting, personalizzazione (icona, porta, code-signing)
- **`README.md`:** nuova sezione "Installer Windows (.exe)" con istruzioni e tabella file
- **`CHANGELOG.md`:** voce v0.55.0 dettagliata
- **`COMPLETION_STATUS.md`:** sezione 27 "Pacchettizzazione Windows" + riga summary

### 10g. Risultato
| Artefatto | Descrizione |
|-----------|-------------|
| `dist\archimista\` | Bundle PyInstaller (testabile direttamente) |
| `output\Archimista-Setup-0.55.0.exe` | Installer Windows finale |

**Dimensione stimata:** 150-300 MB
**Nota:** L'installer NON richiede Python installato sul sistema target.

## ✅ Fase 9: Refactor AEF, Export XML, Select2 ibrido (COMPLETATA v0.53.0 → v0.54.0)

### 9a. Refactor AEF Exporter (1161 → 8 moduli)
- `aef_exporter/` package con 10 moduli separati
- `aef_exporter.py` originale → thin compatibility shim (2 righe)
- Ogni modulo 45-300 righe, testabile singolarmente
- Zero regressioni: export AEF funziona come prima (22 record, 12 modelli)

### 9b. Export XML — SAN, EAD, METS
- **CAT-SAN**: namespace `http://san.mibac.it/cat-import/`, `catRecord` per ogni entità
- **EAD3/EAC-CPF/SCONS2**: namespace EAD3, EAC-CPF, SCONS2 corretti
- **METS**: envelope SAN + METS per oggetti digitali
- 4 checkbox nel form export (come Ruby): oggetti digitali, entità correlate, SAN, EAD
- Mutual exclusion identica a Ruby (JS nel template)

### 9c. Select2 ibrido
- `auto_select_threshold()` in `widgets.py` — se queryset < 20 elementi, imposta `minimum-input-length=0`
- Widget resta Select2 (non degrada a `<select>` vuoto)
- Applicato a 20+ campi FK in tutti i form

### 9d. Test regressione
- `generate_reference_aef.py` — genera ora anche SAN/EAD/METS XML
- `test_ruby_comparison.py` — aggiunto `compare_xml_format()` per SAN/EAD/METS
- `generate_and_export.py` — eliminato (relitto duplicato)

## ✅ Fase 8: Test E2E con Playwright (COMPLETATA v0.52.0 → v0.53.0)

### 8a. Infrastruttura E2E
- **Playwright + pytest-playwright** installati (Chromium headless)
- `tests_e2e/` directory con 5 moduli test + `conftest.py`
- DB E2E dedicato (`test_e2e_db.sqlite3`) — creato/eliminato automaticamente
- Server Django subprocess avviato automaticamente con settings dedicato (`e2e_settings.py`)
- Login automatico via cookie injection (sessionid da requests session)
- Seed dati: admin user, vocabolari, fond + unit, record formset, eventi archidate
- Runner unificato `run_all_tests.py` — lancia server + E2E in sequenza

### 8b. Test E2E implementati (36 test)
- `test_fond_formsets.py` (6 test) — Formset dinamici Fond: add row, multiple rows, fill+save, indipendenti, tab visibili
- `test_unit_show_hide.py` (10 test) — Show/hide condizionale: documentaria→SC2, fascicolo→FSC, SC2 tipo F/CARS, cambio dinamico, FSC personale/edilizia, SC2 formset, persistenza
- `test_unit_formsets.py` (5 test) — Presenza formset nel DOM: identificatori, lingue, SC2 textual/visual, TOTAL_FORMS coerenti
- `test_tree_operations.py` (10 test) — jsTree: load, create child, rename, toolbar, select+status, expand/collapse, create root, navigazione detail, trash, delete→trash
- `test_archidate.py` (5 test) — Data puntuale/secolare: formato Y visibile, switch C→Y→C, equal bounds, stile wrapper
- **Risultato: 36/36 test passati, 0 falliti**

### 8c. Copertura JavaScript raggiunta
| Area JavaScript | Prima | Ora |
|----------------|-------|-----|
| Show/hide SC2/FSC/FE | 0% | ✅ ~80% |
| Formset "Aggiungi riga" | 0% | ✅ ~70% |
| jsTree operazioni | 0% | ✅ ~90% |
| Archidate format toggle | 0% | ✅ ~80% |
| Login/UI flow | 0% | ✅ 100% |

## ✅ Fase 7: Test completo con copertura funzionale (COMPLETATA v0.50.0 → v0.51.0)

### 7a. Suite test estesa (102 → 242 test, +140 nuovi) — v0.50.0
- 17 moduli in directory `tests/` (prima 11)
- **7 nuovi moduli**: DigitalObject CRUD, service entity CRUD completo, model properties, form validation, ricerca, quality checks, import/export/auth
- Copertura funzionale: tutte le viste, tutti i CRUD, tutte le proprietà modelli, validazione form, import AEF reale, export con validazione contenuto, autenticazione edge cases, middleware, seed scripts
- **Risultato: 242/242 test passati**

### 7b. Test di integrazione avanzati (242 → 323 test, +81 nuovi) — v0.51.0
- 23 moduli in directory `tests/` (prima 17)
- **6 nuovi moduli**:
  - `test_export_content.py` (17 test) — verifica contenuto reale PDF/RTF del report system completo (29 campi Fond, 49 Unit), export AEF con validazione modelli, metadata.json
  - `test_nested_formsets.py` (11 test) — SC2 Author + AttributionReason annidati, Commission + CommissionName, formset save/delete/validazione
  - `test_file_uploads.py` (16 test) — Upload JPEG/PNG/PDF reali (generati con Pillow/reportlab), thumbnail generation, digital objects nested
  - `test_aef_roundtrip.py` (8 test) — Export → import → re-export, confronto strutturale model keys, conteggio record
  - `test_edge_case_data.py` (22 test) — Unicode (CJK, cirillico, arabo, greco), emoji, HTML/XSS prevention, NULL, stringhe 20KB+, caratteri di controllo
  - `test_large_data.py` (7 test) — Alberi 7 livelli, 100+ nodi, 200 unità, subtree performance, tree API operations, classificazione massa 100 unità
- **Risultato: 323/323 test passati, 0 falliti**

### 7c. TOTALE test dopo Fase 8 (v0.52.0)
- **Server-side:** 323 test (23 moduli in `tests/`)
- **E2E browser:** 36 test (5 moduli in `tests_e2e/`)
- **TOTALE: 359/359 test passati, 0 falliti**
- **Copertura stimata app:** ~92-95% (era ~85-90% a v0.51.0, ~65-70% a v0.51.0)

### 7d. Bug Python scoperti e corretti

| # | Bug | Fix |
|---|-----|-----|
| 1 | `Fond.subtree` mancante | Aggiunta property in `models/core.py` |
| 2 | `Fond.root` mancante | Aggiunta property con prevenzione loop |
| 3 | `Unit.full_path()` mancante | Aggiunto metodo in `models/core.py` |
| 4 | `Classification.is_root` mancante | Aggiunta property in `models/core.py` |

## ✅ Fase 6: Bug fix test-driven (COMPLETATA v0.49.0)

### 6a. Test suite estesa e riorganizzata (67 → 102 test modulari)
- Directory `tests/` con 11 moduli separati
- `test_complete.py` ridotto a scheletro runner
- Database SQLite dedicato (`test_db.sqlite3`) creato/eliminato automaticamente
- Seed Group default per vincoli FK
- Re-login client prima sezioni critiche (tree, QC)
- CRUD completi per 9 entità di servizio
- API albero (create, rename, move, trash, restore)
- Gerarchia unità, classificazione di massa
- Export PDF/RTF/AEF, report, QC individuali
- **Risultato: 102/102 test passati**

### 6b. Bug corretti (scoperti dai test)

| # | Bug | Fix |
|---|-----|-----|
| 1 | `HeadingForm.save()` → `AttributeError` su `heading_type_term` | `forms/heading.py`: sincronizzazione corretta con `heading_type` CharField |
| 2 | `AnagraphicCreateView` — formset validato prima del save | `views/entities.py`: ordine invertito (save prima, formset dopo) |
| 3 | `DocumentFormDeleteView` → `NoReverseMatch` | `views/document_forms.py`: aggiunto `context_object_name` |
| 4 | `QualityCheckFondView` — 4 related name errati | `views/quality_checks.py`: `rel_creator_fonds`, `rel_custodian_fonds`, `rel_project_fonds`, `rel_fond_sources` |
| 5 | `Creator.sources` → `NameError` | `models/core.py`: aggiunto import locale di `Source` |
| 6 | Test DB `:memory:` — sessione instabile | `test_complete.py`: file SQLite dedicato con cleanup |

## ✅ Fase 1: README + setup script (COMPLETATA v0.47.0)
- README.md con licenza GPL v2, credits, installazione, troubleshooting
- setup.sh con 5 passi
- seed_admin_user.py: reset password se utente esiste

## ✅ Fase 2: Autocomplete + Lang dropdowns (COMPLETATA v0.47.0)

### 2a. Select2 per campi FK principali ✅
- `UnitForm.fond` → FondSelect2Widget
- `UnitForm.parent` → UnitSelect2Widget
- `UnitForm.classification` → ClassificationSelect2Widget
- `FondForm.parent` → FondSelect2Widget
- `ClassificationForm.parent` → ClassificationSelect2Widget

### 2b. Lang Select2 ✅
- `FondLangForm.code` → LangSelect2Widget
- `UnitLangForm.code` → LangSelect2Widget

### Nuovi widget creati
- `UnitSelect2Widget` (cerca per titolo, segnatura)
- `ClassificationSelect2Widget` (cerca per codice, nome)
- `LangSelect2Widget` (cerca per codice, nome)

## ✅ Fase 3a: Refactor template grandi (COMPLETATA v0.47.0)

| File | Prima | Dopo | Parziali |
|------|-------|------|----------|
| fond_form.html | 825 righe | 232 (-72%) | 6 partial |
| creator_form.html | 730 righe | 220 (-70%) | 5 partial |
| custodian_form.html | 594 righe | 147 (-75%) | 7 partial |

**18 nuovi partial** in `fonds/partials/`, `creators/partials/`, `custodians/partials/`.

## ✅ Fase 3b: Refactor Python (NON NECESSARIO)

Valutati `admin.py` (635 righe) e `tree.py` (414 righe):
- `admin.py` — 46 inline (3-4 righe ciascuno) + 40+ registrazioni `@admin.register`. Suddividerlo non migliora la manutenibilità.
- `tree.py` — 14 API endpoint + 4 helper. Ogni funzione ha responsabilità singola. Non è una God Object.

## ✅ Fase 4: Test completo (COMPLETATA v0.47.0, estesa v0.49.0)

- `test_complete.py` — 167 test, tutti passati (prima 67, estesi a 167 in v0.49.0)
- Eliminati 7 vecchi script di test ridondanti
- 6 bug scoperti e corretti durante l'estensione dei test (v0.49.0)

## ✅ Fase 5: Fix titolario, FontAwesome, pulsanti uniformi (COMPLETATA v0.48.0)

### 5a. Fix titolario ✅
- `tree_data` serializzato con `json.dumps()` (era Python list → JS invalido)
- Albero jsTree ora popolato correttamente

### 5b. FontAwesome CDN ✅
- Aggiunto `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">` in `base.html`
- Tutte le icone `fas fa-*` ora visibili

### 5c. Pulsanti uniformi ✅
**Standard adottato:** `btn-group btn-group-sm` con icone FontAwesome:
- 👁️ Dettaglio → `btn-outline-secondary` + `fas fa-eye`
- ✏️ Modifica → `btn-outline-primary` + `fas fa-edit`
- 🗑️ Elimina → `btn-outline-danger` + `fas fa-trash`

**Template liste modificati (10):**
- heading_list, editor_list, project_list, institution_list, anagraphic_list
- document_form_list, source_list, digital_object_list, digital_object_nested_list, generic_list

**Template detail modificati (6):**
- fond_detail, unit_detail, creator_detail, custodian_detail, project_detail, source_detail

## Bug fix preesistenti

| # | Bug | Fix | Versione |
|---|-----|-----|----------|
| 1 | `Custodian.sources` NameError | Aggiunto `from ...system import Source` in `models/core.py` | v0.47.0 |
| 2 | Titolario albero vuoto | `json.dumps()` in `ClassificationListView` | v0.48.0 |
| 3 | Icone invisibili | FontAwesome CDN aggiunto in `base.html` | v0.48.0 |
| 4 | `HeadingForm` AttributeError | Sincronizzazione corretta con `heading_type` CharField | v0.49.0 |
| 5 | `AnagraphicCreateView` ordine errato | Save prima, formset dopo | v0.49.0 |
| 6 | `DocumentFormDeleteView` NoReverseMatch | Aggiunto `context_object_name` | v0.49.0 |
| 7 | QC 4 related name errati | Nomi corretti nelle query | v0.49.0 |
| 8 | `Creator.sources` NameError | Import locale di `Source` | v0.49.0 |

## Differenze widget rimanenti (da fare in futuro)

| Entità | Campo | Ruby | Python | Impatto |
|--------|-------|------|--------|---------|
| Fond | `abstract` | Solo se is_root | Sempre visibile | Basso |
| Fond | sources | Livesearch | Dropdown Select2 | Medio |
| Fond | fond_editors editing_type | terms_select | TextInput | Medio |
| Unit | sources | Livesearch | Dropdown Select2 | Medio |
| Unit | unit_editors name | Autocomplete | TextInput | Medio |
| Unit | unit_other_reference_numbers | qualifier+note | Solo other_reference_number | Medio |
| Creator | other_names qualifier | terms_select | TextInput | Medio |
| Creator | residence | Autocomplete | Textarea | Medio |
| Creator | sources | Livesearch | Dropdown Select2 | Medio |
| Creator | relations | Autocomplete | Dropdown Select2 | Medio |
| Custodian | other_names qualifier | terms_select | TextInput | Medio |
| Custodian | contact_type | terms_select | TextInput | Medio |
| Custodian | building_type | terms_select | TextInput | Medio |
| Custodian | city/country | Autocomplete | TextInput | Medio |
| Custodian | sources | Livesearch | Dropdown Select2 | Medio |
| Custodian | relations | Autocomplete | Dropdown Select2 | Medio |
| Project | relations | Autocomplete | Dropdown Select2 | Medio |

**Nessuna di queste è bloccante.** Sono tutte differenze di UX/comodità, non di correttezza funzionale.
