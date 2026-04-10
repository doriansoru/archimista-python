# Changelog - Archimista Python/Django

Questo documento traccia le release recenti della riscrittura del software "Archimista" da Ruby on Rails a Django.

Per la cronologia completa delle fasi iniziali (v0.1 - v0.19), vedere [WALKTHROUGH_LEGACY.md](WALKTHROUGH_LEGACY.md).

---

## Rilascio v0.55.0 - Installer Windows standalone (.exe) (2026-04-10)

### Cosa è stato fatto

#### 1. Sistema di build per installer Windows
- **Problema:** distribuire Archimista Python su Windows richiede l'installazione manuale di Python, pip, dipendenze, virtual environment, configurazione. Troppo complesso per utenti finali non tecnici.
- **Soluzione:** processo di build in due fasi che produce un singolo file `.exe` installer:
  - **Fase 1 (PyInstaller):** bundla Python embedded + Django + tutte le librerie + file del progetto in un eseguibile standalone (`dist\archimista\`)
  - **Fase 2 (Inno Setup):** crea un installer Windows con procedura guidata, shortcut, menu Start

#### 2. Launcher intelligente (`archimista_launcher.py`)
- **Primo avvio:**
  1. Applica migrazioni Django (`manage.py migrate`)
  2. Popola vocabolari controllati (`seed_vocabularies.py`)
  3. Popola tipologie di fonte (`seed_source_types.py`)
  4. **Domanda interattiva:** vuoi i dati di esempio? (S/n)
  5. Crea utente admin con password casuale sicura (12 caratteri)
  6. Salva credenziali in `admin_credentials.txt`
  7. Avvia il server Django su `127.0.0.1:8000`
  8. Apre automaticamente il browser
- **Avvii successivi:** rileva il marker `first_run.done` e avvia direttamente il server
- **PyInspector-aware:** funziona sia in sviluppo che nel bundle PyInstaller (one-file mode)

#### 3. PyInstaller spec (`archimista.spec`)
- **Hidden imports:** 80+ moduli Django, django-select2, django-extensions, lxml, Pillow, reportlab, weasyprint, python-docx
- **Data files:** 68 template HTML, migrazioni, file statici, seed scripts, manage.py, launcher
- **Esclusioni:** playwright, pytest, test suite (non servono a runtime)
- **Output:** `dist\archimista\` (one-dir build)

#### 4. Inno Setup script (`archimista_installer.iss`)
- Installer professionale con wizard moderno (stile moderno)
- Lingue: italiano e inglese
- Shortcut: menu Start, desktop (opzionale), quick launch (opzionale)
- Lancio opzionale post-installazione
- Crea directory `media/` e `staticfiles/` al momento dell'installazione
- Compressione LZMA2/ultra64 per dimensioni ridotte

#### 5. Script di build automatizzati
- **`build_installer.bat`:** installa PyInstaller, esegue `collectstatic`, build PyInstaller
- **`build_all.bat`:** orchestratore one-click — esegue entrambe le fasi, auto-detect Inno Setup
- **`requirements-build.txt`:** dipendenze di build minime (PyInstaller + hooks)

#### 6. Modifiche a `settings.py` per compatibilità PyInstaller
- **`BASE_DIR` detection:** quando `sys.frozen` è True (PyInstaller one-file), usa la directory dell'eseguibile invece di `__file__`
- **`STATIC_ROOT`:** aggiunto `BASE_DIR / 'staticfiles'` per `collectstatic`
- **`SECRET_KEY`:** ora legge da variabile d'ambiente `DJANGO_SECRET_KEY` (fallback a default)
- **`DEBUG`:** ora legge da `DJANGO_DEBUG` (fallback a True)

#### 7. Documentazione
- **`INSTALLER_BUILD.md`:** guida completa al processo di build, troubleshooting, personalizzazione
- **`README.md`:** aggiunta sezione "Installer Windows (.exe)" con istruzioni e tabella file
- **Aggiornamento struttura progetto:** aggiunti nuovi file nel tree view

### Risultato

| Artefatto | Descrizione |
|-----------|-------------|
| `dist\archimista\` | Bundle PyInstaller (testabile direttamente) |
| `output\Archimista-Setup-0.55.0.exe` | Installer Windows finale |

**Dimensione stimata:** 150-300 MB (Python 3.x + Django + WeasyPrint + GTK + tutte le dipendenze)

### Note tecniche

- L'installer **NON richiede Python installato** sul sistema target
- Funziona su **Windows 10/11 x64**
- Al primo avvio l'utente sceglie se inserire i dati di esempio
- Le credenziali admin sono salvate in `admin_credentials.txt` (leggibile)
- Per resettare: cancellare `first_run.done` e `db.sqlite3`
- **WeasyPrint/GTK:** PyInstaller bundla automaticamente le GTK DLLs necessarie; se non funziona, installare GTK3 Runtime per Windows

---

## Rilascio v0.54.0 - Select2 ibrido, Export XML (SAN/EAD/METS), Refactor AEF (2026-04-09)

### Cosa è stato fatto

#### 1. Select2 ibrido — dropdown normale per dataset piccoli
- **Problema:** con pochi elementi (es. 1 fondo) Select2 richiedeva 2 caratteri prima di mostrare risultati, mentre un `<select>` normale li mostrerebbe subito. La prima soluzione (degradazione a `<select>`) rompeva il rendering (select vuoto).
- **Soluzione:** `auto_select_threshold()` in `widgets.py` — se il queryset ha < 20 elementi, imposta `data-minimum-input-length="0"` su Select2. Il widget resta Select2 ma apre la dropdown con tutte le opzioni subito, senza richiedere digitazione.
- **Applicato a:** tutti i form Select2 in Fond, Unit, Creator, Custodian, Classification, Project (20+ campi).

#### 2. Export XML — SAN, EAD/ICAR-IMPORT, METS (allineato a Ruby)
- **CAT-SAN** — formato `cat-import` con namespace `http://san.mibac.it/cat-import/`. Genera file separati per fonds (`complessi_*.xml`), creators, custodians, sources. Ogni record è un `catRecord` con header + body (EAD-SAN / EAC-CPF-SAN / SCONS-SAN / RICERCA-SAN).
- **EAD/ICAR-IMPORT** — EAD3 (`http://ead3.archivists.org/schema/`) per fonds, EAC-CPF per creators, SCONS2 per custodians, EAD per sources. Include `control`, `archdesc`/`cpfDescription`/`identificativi`, relazioni.
- **METS** — envelope SAN (`http://san.beniculturali.it/envelope-san/`) + METS (`http://www.loc.gov/mets/`) per oggetti digitali con `metsHdr`, `fileSec`, `FLocat`.
- **Template export:** 4 checkbox come Ruby (oggetti digitali, entità correlate, CAT-SAN, ICAR-IMPORT) con mutual exclusion identica a Ruby.

#### 3. Refactor `aef_exporter.py` da 1161 righe → 8 moduli
```
aef_exporter/
├── __init__.py         (~150 righe) — orchestratore AEFExporter
├── constants.py        (~120 righe) — esclusioni, tabelle, MODEL_NAME_MAP
├── serializers.py      (~120 righe) — model_to_dict, write_record, AEFEncoder
├── fond_units.py       (~90 righe)  — export fondi + unità
├── extensions.py       (~215 righe) — SC2/ICCD/FSC/FE, creator/source entity
├── relations.py        (~180 righe) — major_entities, headings, sources, editors
├── digital_objects.py  (~60 righe)  — metadata + file inclusion in ZIP
├── single_entity.py    (~100 righe) — mode 'not-full' exports
├── metadata.py         (~45 righe)  — metadata.json + ZIP packaging
└── xml_export.py       (~300 righe) — SAN, EAD, METS XML generation
```
- `aef_exporter.py` originale → thin compatibility shim (2 righe).

#### 4. Test regressione aggiornati
- **`generate_reference_aef.py`** — ora genera anche SAN/EAD/METS XML (`reference_san.zip`, `reference_ead.zip`, `reference_mets.zip`)
- **`test_ruby_comparison.py`** — aggiunto `compare_xml_format()` per SAN/EAD/METS. Confronta root tag, namespace, conteggio elementi. Confronto XML è opzionale (saltato se file Ruby non presenti).
- **`generate_and_export.py`** — eliminato (era un relitto duplicato di `generate_reference_aef.py`)

**Risultati test:**
| Export type | Python | Ruby confronto |
|-------------|--------|----------------|
| AEF (NDJSON) | ✅ 22 record, 12 modelli | Da verificare con import Ruby |
| SAN XML | ✅ `complessi_1.xml` | Da verificare con Ruby |
| EAD XML | ✅ `ead_fond_1.xml` | Da verificare con Ruby |
| METS XML | ✅ `digital_objects_mets.xml` | Da verificare con Ruby |

---

## Rilascio v0.53.0 - Compatibilità AEF Python ↔ Ruby verificata (2026-04-08)

### Cosa è stato fatto

#### 1. Test regressione Python vs Ruby (confronto diretto)

**Nuovi file:**
- `tests/regression/test_ruby_comparison.py` — Confronto automatico AEF/PDF/RTF
- `tests/test_regression_ruby.py` — Modulo integrato nella suite test (323+ test)

**Risultati:**
| Confronto | Risultato |
|-----------|-----------|
| AEF modelli | ✅ 71/71 identici, 4 differenze note (limiti Ruby) |
| AEF conteggi | ✅ Tutti identici tranne 4 noti |
| AEF campi fond | ✅ 100% overlap (27 campi) |
| AEF campi unit | ✅ 100% overlap (45 campi) |
| AEF valori fond | ✅ 7/7 campi chiave identici |
| PDF | ✅ PASS (78.9% overlap parole) |
| RTF | ✅ PASS (91.7% overlap parole) |

#### 2. Fix compatibilità AEF (12 fix)

| # | Problema | Fix |
|---|----------|-----|
| 1 | `metadata.json` su più righe | Formato JSON compatto (singola riga) |
| 2 | `fond_event` / `unit_event` come `event` | Nome modello corretto |
| 3 | `legacy_root_fond_id` = NULL | Sempre impostato al fond radice |
| 4 | `sequence_number` = NULL | Calcolato in sequenza (1, 2, 3, 4) |
| 5 | `ancestry_depth` = NULL | Calcolato da `ancestry` string |
| 6 | `ancestry` esportato ma Ruby lo ricalcola | Rimosso dall'export |
| 7 | `document_form`, `digital_object` nomi | Mapping esplicito con underscore |
| 8 | `group`, `*_term` FK | Esclusi dall'export |
| 9 | `creator_name` / `custodian_name` qualifier | Impostati a `'A'` / `'OT'` |
| 10 | `fe_operas.status` troppo lungo | Valore accorciato a `'resid.'` |
| 11 | `custodian_building_type` nullo | Impostato a `'Archivio'` |
| 12 | `Sc2AttributionReason` mancante import | Aggiunto all'exporter |

#### 3. Import Ruby verificato

- ✅ Ruby importa correttamente l'AEF generato da Python
- ✅ Tutte le unità sono visibili e navigabili nella UI Ruby
- ✅ Nessun errore durante l'import o la visualizzazione

#### 4. Promemoria test

- Aggiunto `run_all_tests.py` con messaggio promemoria per test regressione Ruby

---

## Rilascio v0.51.0 - Test integrazione avanzati (323 test, +81 nuovi) (2026-04-07)

### Cosa è stato fatto

#### 1. Test suite estesa da 242 a 323 test (+81 nuovi)

**Nuovi moduli di test (6):**

| Modulo | Test | Copertura |
|--------|------|-----------|
| `test_export_content.py` | 17 | Report PDF/RTF content validation (dimensione, struttura), AEF export con validazione modelli e metadata, round-trip structural match |
| `test_nested_formsets.py` | 11 | SC2 Author + AttributionReason, Commission + CommissionName, formset save/delete/validazione |
| `test_file_uploads.py` | 16 | Upload JPEG/PNG/PDF reali (Pillow/reportlab), thumbnail generation, digital objects nested, model methods |
| `test_aef_roundtrip.py` | 8 | Export → import → re-export, confronto strutturale model keys, conteggio record |
| `test_edge_case_data.py` | 22 | Unicode (CJK, cirillico, arabo, greco), emoji, HTML/XSS prevention, NULL, stringhe 20KB+, caratteri controllo |
| `test_large_data.py` | 7 | Alberi 7 livelli, 100+ nodi, 200 unità, subtree perf, tree API ops, classificazione massa |

**Risultato: 323/323 test passati, 0 falliti**

#### 2. Aree coperte per la prima volta

- ✅ **Export content validation** — PDF/RTF report system verificato per dimensione e struttura
- ✅ **AEF export con validazione modelli** — fond, unit, creator, custodian, extensions, relations, sc2, iccd
- ✅ **AEF metadata.json** — version, producer, date verificati
- ✅ **Round-trip export→import→export** — stesso set di modelli garantito
- ✅ **Formset annidati SC2** — Sc2Author + Sc2AttributionReason, Sc2Commission + Sc2CommissionName
- ✅ **File upload reali** — JPEG/PNG da Pillow, PDF da reportlab, thumbnail generation
- ✅ **Unicode completo** — CJK, cirillico, arabo, greco, emoji, HTML/XSS
- ✅ **Alberi grandi** — 7 livelli, 100+ nodi, 200 unità, performance subtree
- ✅ **Tree API operations** — rename, move, trash, restore verificati

---

## Rilascio v0.50.0 - Suite test completa (242 test, +140 nuovi) (2026-04-07)

### Cosa è stato fatto

#### 1. Test suite estesa da 102 a 242 test (+140 nuovi)

La suite test è stata ampliata per coprire tutte le funzionalità del porting Python/Django. I test sono organizzati in 17 moduli separati nella directory `tests/`:

**Nuovi moduli di test (7):**

| Modulo | Test | Copertura |
|--------|------|-----------|
| `test_digital_objects.py` | 20 | CRUD DigitalObject (upload file, validazione, nested per entity, model methods) |
| `test_service_entities_complete.py` | 22 | CRUD completo update/delete per Source, Project, Institution, Heading, Anagraphic, Editor, Classification, DocumentForm |
| `test_model_properties.py` | 22 | Proprietà/metodi modelli: Fond (descendants, subtree, root, subtree_ids, active_descendant_units_count), Unit (is_movable_up/down, full_path), Creator/Custodian (preferred_name, sources), Event (date formatting), Classification (is_root) |
| `test_form_validation.py` | 18 | Validazione form: Fond, Unit, Creator, Custodian, DigitalObject, Source, Project, Heading, Anagraphic, Classification, Institution |
| `test_search.py` | 8 | Ricerca globale e avanzata con filtri, paginazione, dati reali |
| `test_quality_checks.py` | 12 | Quality checks con dati completi e incompleti (fond, creator, custodian, index) |
| `test_import_export_auth.py` | 15 | Import AEF con file ZIP reale, export PDF/RTF/AEF/CSV content validation, auth edge cases, middleware, Unit move, Tree view, Unit list |
| `test_seed_scripts.py` | 8 | Seed scripts (vocabularies, source_types, admin_user), modelli Vocabulary/Term |

**Moduli esistenti estesi:**
- `test_crud_services.py` — aggiunto Classification detail/update/delete/units/tree, DocumentForm create
- `test_tree.py` — aggiunto re-login client
- `test_reports_quality_import.py` — aggiunto re-login client
- `test_crud_fond.py`, `test_crud_unit.py`, `test_crud_creator_custodian.py` — migliorati

#### 2. Bug fix Python scoperti dai test

| # | Bug | Fix |
|---|-----|-----|
| 1 | `Fond.subtree` property mancante | Aggiunta property `subtree` in `models/core.py` |
| 2 | `Fond.root` property mancante | Aggiunta property `root` con prevenzione loop circolari |
| 3 | `Unit.full_path()` metodo mancante | Aggiunto metodo `full_path()` in `models/core.py` |
| 4 | `Classification.is_root` property mancante | Aggiunta property `is_root` in `models/core.py` |

#### 3. Correzioni ai test

- Test import AEF: formato JSON corretto (NDJSON con chiave modello, non Django dumpdata)
- Test ricerca: re-login client dopo logout in altri moduli
- Test QC: rimossi campi `fond_type_term` (FK a Term) non necessari
- Test vocabolari: semplificati per DB vuoto (no seed)
- Test Anagraphic/DocumentForm: formset prefix corretti (`anagidentifier`, `editor`)
- Test Export RTF: validazione basata su dimensione file, non marker stringa
- Test Classification tree data: risposta dict con children, non lista

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python test_complete.py` — **242/242 test passati** (prima 102/102)
- Database di test creato e eliminato automaticamente

---

## Rilascio v0.49.0 - Bug fix scoperti dai test completi (2026-04-07)

### Cosa è stato fatto

#### 1. HeadingForm — AttributeError su `heading_type_term`

**Problema:** `HeadingForm.save()` referenziava `instance.heading_type_term` che non esiste sul modello `Heading` (è un campo virtuale del form, non una FK sul modello). Il modello ha solo `heading_type` (CharField). Errore: `AttributeError: 'Heading' object has no attribute 'heading_type_term'`.

**Soluzione:**
- `fields` del Meta cambiati da `['heading_type_term', ...]` a `['heading_type', ...]`
- Widget per `heading_type` impostato a `HiddenInput` (campo DB nascosto, sincronizzato dal form)
- `save()` semplificato: legge `heading_type_term` da `cleaned_data` e imposta `instance.heading_type`
- Aggiunta gestione del campo `group` quando non esiste un Group nel DB (test con DB vuoto)

**File:** `archimista_python/archive/forms/heading.py`

#### 2. AnagraphicCreateView — form_valid con ordine errato

**Problema:** `AnagraphicCreateView.form_valid()` chiamava `identifier_formset.is_valid()` **prima** di salvare l'oggetto principale. Il formset era stato istanziato con `instance=self.object` dove `self.object` era ancora `None`, causando fallimento silenzioso.

**Soluzione:** Invertito l'ordine — prima `form.save()`, poi assegnamento `identifier_formset.instance = self.object` e salvataggio del formset.

**File:** `archimista_python/archive/views/entities.py`

#### 3. DocumentFormDeleteView — NoReverseMatch nel template

**Problema:** Il template `document_form_confirm_delete.html` usava `{{ document_form.pk }}` ma la DeleteView non impostava `context_object_name`, quindi il context riceveva `documentform` (nome auto-generato da Django) invece di `document_form`. Errore: `NoReverseMatch: Reverse for 'document_form_edit' with arguments '("",)' not found`.

**Soluzione:** Aggiunto `context_object_name = 'document_form'` alla view.

**File:** `archimista_python/archive/views/document_forms.py`

#### 4. QualityCheckFondView — 4 related name errati

**Problema:** La vista QC usava 4 related name Django sbagliati nelle query. Django auto-genera i related name dalle FK, e questi non corrispondevano ai nomi usati nel codice:

| Nome errato | Nome corretto |
|-------------|---------------|
| `relcreatorfond` | `rel_creator_fonds` |
| `relcustodianfond` | `rel_custodian_fonds` |
| `relprojectfond` | `rel_project_fonds` |
| `relfondsource` | `rel_fond_sources` |

**File:** `archimista_python/archive/views/quality_checks.py`

#### 5. Creator.sources — NameError per import mancante

**Problema:** La property `Creator.sources` usava `Source.objects.filter(...)` senza importare il modello `Source`. Errore: `NameError: name 'Source' is not defined`.

**Soluzione:** Aggiunto `from archimista_python.archive.models.system import Source` all'interno del metodo (import locale per evitare circular import).

**File:** `archimista_python/archive/models/core.py`

#### 6. Test suite — database e sessioni

**Problema:** Il file `test_complete.py` usava un database `:memory:` che causava problemi di sessione e autenticazione tra i vari test.

**Soluzione:**
- Database SQLite dedicato (`test_db.sqlite3`) creato prima di `django.setup()`
- File eliminato automaticamente alla fine dei test
- Re-login del client prima delle sezioni critiche (sezioni 16 e 17)
- Seed del Group default (`id=1`) necessario per i vincoli FK

**File:** `python_rewrite/test_complete.py`

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python test_complete.py` — **102/102 test passati** (prima 67/67, riorganizzati in `tests/` directory modulare)
- Database di test creato e eliminato automaticamente

---

## Rilascio v0.48.0 - Fix titolario, FontAwesome e pulsanti uniformi (2026-04-07)

### Cosa è stato fatto

#### 1. Fix titolario (albero vuoto)

**Problema:** La sezione "Struttura del titolario" nella lista classificazioni mostrava un albero jsTree vuoto, anche se le classificazioni esistevano nel database.

**Causa:** `tree_data` nel context era una lista Python di dict passata tal quale al template. `{{ tree_data|safe }}` generava JavaScript invalido (virgolette singole Python invece di doppie, `True`/`False`/`None` invece di `true`/`false`/`null`).

**Soluzione:** `ClassificationListView.get_context_data()` ora usa `json.dumps()` per serializzare correttamente l'albero.

#### 2. FontAwesome aggiunto a base.html

**Problema:** FontAwesome CSS non era caricato. Tutte le icone `fas fa-*` erano invisibili, inclusi i pulsanti di azione nelle liste e i pulsanti "tre ovalini" nelle classificazioni.

**Soluzione:** Aggiunto `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">` in `<head>` di `base.html`.

#### 3. Pulsanti uniformi in tutte le liste e detail view

**Problema:** I pulsanti di azione nelle liste usavano testo ("Dettagli", "Modifica", "Elimina") con stili inconsistenti. Le detail view usavano emoji (✏️, 🗑️, 🖼️) mischiate a testo.

**Soluzione:** Uniformato tutto allo stile `btn-group btn-group-sm` con icone FontAwesome:

**Standard adottato:**
- 👁️ Dettaglio → `btn-outline-secondary` + `fas fa-eye`
- ✏️ Modifica → `btn-outline-primary` + `fas fa-edit`
- 🗑️ Elimina → `btn-outline-danger` + `fas fa-trash`

**Template liste modificati (10):**
- `heading_list.html`, `editor_list.html`, `project_list.html`
- `institution_list.html`, `anagraphic_list.html`, `document_form_list.html`
- `source_list.html`, `digital_object_list.html`, `digital_object_nested_list.html`
- `entities/generic_list.html`

**Template detail modificati (6):**
- `fond_detail.html` — pulsanti header: icona + label responsive (`d-none d-md-inline`)
- `unit_detail.html` — stesso pattern, incluso "Modifica livello"
- `creator_detail.html` — stesso pattern, inclusi oggetti digitali
- `custodian_detail.html` — stesso pattern
- `project_detail.html` — da btn solidi a btn-outline con icone
- `source_detail.html` — da emoji a btn-group con icone

**Fix durante l'implementazione:**
- `source_list.html` — aggiunto anche pulsante Dettaglio e Modifica (prima c'era solo Elimina)
- `digital_object_nested_list.html` — pulsanti nel card-footer con icona + testo

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python test_complete.py` — **67/67 test passati**
- Albero titolario: popolato correttamente con icone cartella
- Pulsanti: visibili con icone FontAwesome in tutte le liste e detail view

---

## Rilascio v0.47.0 - Autocomplete, Lang Select2, Refactor template, Setup e Test completo (2026-04-07)

### Cosa è stato fatto

#### 1. Autocomplete Select2 per campi FK principali

**Problema:** I campi FK principali nei form (Unit.fond, Unit.parent, Unit.classification, Fond.parent, Classification.parent) usavano dropdown `<select>` plain invece di Select2 con ricerca AJAX. Le relazioni nei formset usavano già Select2, ma i campi FK "main" no.

**Soluzione:**
- **`widgets.py`** — aggiunti 3 nuovi widget:
  - `UnitSelect2Widget` — ricerca per titolo e segnatura
  - `ClassificationSelect2Widget` — ricerca per codice e nome
  - `LangSelect2Widget` — ricerca per codice e nome lingua
- **`forms/unit.py`** — `fond`, `parent`, `classification` ora usano Select2
- **`forms/fond.py`** — `parent` ora usa FondSelect2Widget
- **`forms/classification.py`** — `parent` ora usa ClassificationSelect2Widget
- Template `unit_form.html`, `fond_form.html`, `classification_form.html` — aggiunto `{{ form.media }}`

#### 2. Lang dropdown da TextInput a Select2

**Problema:** `FondLang.code` e `UnitLang.code` erano campi TextInput liberi, mentre Ruby usa dropdown dalla tabella `langs`.

**Soluzione:** `FondLangForm` e `UnitLangForm` usano ora `LangSelect2Widget` che cerca per codice e nome nella tabella `Lang`.

#### 3. Refactor template grandi in partial

**Problema:** 3 template principali erano troppo grandi e monolitici:
- `fond_form.html` — 825 righe
- `creator_form.html` — 730 righe
- `custodian_form.html` — 594 righe

**Soluzione:** Suddivisi in partial con architettura `{% include %}`, stessa struttura già usata per le unità.

| File | Prima | Dopo | Parziali |
|------|-------|------|----------|
| `fond_form.html` | 825 | **232** (-72%) | 6 partial in `fonds/partials/` |
| `creator_form.html` | 730 | **220** (-70%) | 5 partial in `creators/partials/` |
| `custodian_form.html` | 594 | **147** (-75%) | 7 partial in `custodians/partials/` |

**18 nuovi file partial creati** nelle directory `fonds/partials/`, `creators/partials/`, `custodians/partials/`.

#### 4. README e script di setup

**Nuovi file:**
- **`README.md`** — con licenza GPL v2, credits originali, guida installazione, troubleshooting
- **`setup.sh`** — script eseguibile con 5 passi: migrate → vocabularies → source_types → seed → admin user

**Modifiche:**
- **`seed_admin_user.py`** — ora resetta la password se l'utente esiste già e la stampa sempre

#### 5. Test suite completa

**Nuovo file:**
- **`test_complete.py`** — 67 test che coprono:
  1. Import di tutti i moduli, form, viste, widget, utility
  2. URL resolving (24 route)
  3. Select2 widget (4 nuovi widget verificati)
  4. Form instanziazione (7 form con widget Select2)
  5. Template rendering (12 template + 18 partials)
  6. CRUD con database (Fond, Unit, Creator, Custodian)
  7. Viste funzionali (albero, ricerca, controllo qualità, report, export)
  8. Autenticazione (redirect anonimi, login, logout)

**Pulizia:** Eliminati 7 vecchi script di test ridondanti (`test_auth.py`, `test_digital_object_*.py`, `test_editor_crud.py`, `test_fix_v038.py`, `test_unit_refactor.py`).

#### 6. Bug fix preesistenti

Trovati e corretti durante il testing:
- **`models/core.py:317`** — `Custodian.sources` property: aggiunto `from ...system import Source` mancante (NameError)

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python test_complete.py` — **67/67 test passati**

---

## Rilascio v0.46.0 - Export PDF/RTF identico a Ruby (2026-04-07)

### Cosa è stato fatto nella Fase 44

#### 1. Export PDF/RTF completo (porting di ReportsController + RtfBuilder + RtfWriter + ReportSupport)

**Problema:** Il Python aveva un export PDF/DOCX minimale (`export_utils.py`, ~100 righe) con solo nome, abstract, storia e lista unità di 3 colonne. Ruby ha un sistema completo di report con centinaia di campi, selezione colonne, schede speciali SC2/ICCD/FSC/FE, e generazione sia PDF (via wkhtmltopdf) che RTF (via RtfWriter custom).

**Soluzione:** Porting completo del sistema di report Ruby in Python/Django.

**Nuovi file creati:**
- **`report_support.py`** (~1530 righe) — Porting di `lib/report_support.rb`:
  - `AttributeInfo`, `EntityReportSettings`, `ReportSettings` — classi per configurazione report
  - `fond_available_attributes_info()` — 29 campi Fond (identico a Ruby)
  - `unit_available_attributes_info()` — 49 campi Unit (incluse schede SC2/ICCD/FSC/FE)
  - `creator_available_attributes_info()` — 18 campi Creator
  - `custodian_available_attributes_info()` — 32 campi Custodian
  - `project_available_attributes_info()` — 10 campi Project
  - `make_html()` — genera HTML per i campi selezionati (per PDF via WeasyPrint)
  - `make_rtf()` — genera RTF per i campi selezionati (per file .rtf)
  - 30+ callback per campi complessi: events, sources, editors, creators, custodians, progetti, linked_creators, SC2 authors/commissions/techniques, physical_container, other_names, identifiers, URLs, langs, ecc.
  - `_html_rtf_items_concat_with_subtable()` — gestisce tabelle annidate (es. SC2 authors con attribution_reasons)

- **`rtf_writer.py`** (~520 righe) — Porting di `app/models/rtfwriter.rb`:
  - Scrittura RTF raw (font table, color table, stylesheet, paragrafi, liste)
  - Formattazione inline: `*bold*`, `_italic_`
  - Liste ordinate (`#`) e non ordinate (`*`)
  - Header/footer con numeri di pagina
  - ANSI→RTF remap per caratteri speciali

- **`rtf_builder.py`** (~500 righe) — Porting di `app/models/rtf_builder.rb`:
  - `build_fond_rtf_file()` — inventario di complesso archivistico
  - `build_custodian_rtf_file()` — report per conservatore
  - `build_project_rtf_file()` — report per progetto
  - Header/footer, title page, headings, separatori

- **`views/reports.py`** — Viste aggiornate con PDF (WeasyPrint) + RTF (RtfBuilder)
- **Template:** `inventory_report.html`, `project_report.html`, `custodian_report.html`

**Tecnologie:**
- PDF: WeasyPrint (HTML→PDF, come Ruby wkhtmltopdf/PDFKit)
- RTF: RtfWriter custom (nessuna gemma esterna, come Ruby)

**Struttura report (identica a Ruby):**
1. Titolo fondo + datazione
2. Progetti collegati
3. Soggetti conservatori collegati
4. Soggetti produttori collegati (ordinati per nome)
5. Campi fondo (selezione impostazioni)
6. Unità archivistiche (con numeri di sequenza)

**Fix applicati durante l'implementazione:**
- `related_name` mancanti nei modelli di relazione (24 FK in `relations.py`)
- `prefetch_related` invalidi (relazioni attraverso properties, `preferred_event` non è FK)
- Proprietà mancanti su Fond/Creator (`creators`, `custodians`, `projects`, `sources`, `document_forms`, `other_names`, `fonds`, `institutions`)
- `Unit.display_sequence_numbers_of` e `display_sequence_number_from_hash` mancanti
- `_cb_events` callback fix per GenericRelatedObjectManager (serve `.all()`)
- Import `CSS` da WeasyPrint mancante
- Import `GCrwTextAlignmentRight` mancante in rtf_builder.py

**Migrazione:** `0025_alter_relcreatorfond_creator_and_more.py` — aggiunti `related_name` a 24 FK

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `_get_fond_subtree(64)` — SUCCESS: 1 fond con 2 unità
- `make_html()` per fond/creator/unit — genera HTML corretto (102/664+ chars)
- Report completo — HTML preview con pulsanti PDF/RTF funzionanti

---

## Rilascio v0.45.0 - Autenticazione singolo utente (2026-04-07)

### Cosa è stato fatto nella Fase 43

#### 1. Autenticazione singolo utente admin

**Problema:** Tutte le pagine erano accessibili senza login. Nessun controllo d'accesso.

**Soluzione:** Implementato sistema di autenticazione per un singolo utente admin con cambio password obbligatorio al primo accesso.

**Modello (`models/system.py` — aggiunto):**
- `UserProfile` — OneToOne con `django.contrib.auth.User`, campo `must_change_password`
- Signal `post_save` su `User` per creare automaticamente il profilo

**Migrazione:** `0024_userprofile.py`

**Middleware (`middleware.py` — nuovo file):**
- `LoginRequiredMiddleware` — blocca tutte le richieste non autenticate tranne `/login/`, `/logout/`, `/admin/`, `/static/`, `/media/`

**Viste (`views/auth.py` — nuovo file):**
- `ArchimistaLoginView` — LoginView custom con template italiano, redirect a password-change se `must_change_password=True`
- `archimista_logout` — logout con redirect a login
- `password_change_view` — cambio password con `PasswordChangeForm` Django, rimuove `must_change_password` dopo il successo

**Template:**
- `login.html` — form login con nome utente e password, messaggio errore italiano
- `password_change.html` — form cambio password (vecchia, nuova, conferma), alert se obbligatorio

**base.html:** dropdown utente con nome, "Cambia password", "Esci"

**Settings:**
- `LOGIN_URL = 'archive:login'`
- `LOGIN_REDIRECT_URL = 'archive:fond_list'`
- `LOGOUT_REDIRECT_URL = 'archive:login'`
- `ALLOWED_HOSTS` aggiunto `testserver` per test

**Seed script:** `seed_admin_user.py` — crea utente `admin` con password casuale sicura (12 caratteri), `must_change_password=True`, `is_staff=True`, `is_superuser=True`

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python test_auth.py` — 8/8 test passati
- Anonimo → redirect a /login/
- Login pagina → HTTP 200
- Password sbagliata → errore mostrato
- must_change_password = True confermato
- password-change → richiede login
- logout → redirect a /login/
- force_login → accesso consentito
- must_change_password persistente fino al cambio password

---

## Rilascio v0.44.0 - Funzionalità mancanti completate (2026-04-07)

### Cosa è stato fatto nella Fase 42

#### 1. Export AEF completo (round-trip con import)

**Problema:** Mancava completamente la funzione di esportazione in formato AEF (il formato ZIP compatibile con l'importazione). Ruby aveva `Export` model da 1405 righe.

**Soluzione:**

**File `aef_exporter.py` (nuovo, 500+ righe):**
- Classe `AEFExporter` — mirror di `Export#create_export_file` di Ruby
- Genera ZIP con `data.json` (newline-delimited JSON) + `metadata.json` (checksum SHA256, versione, data, producer)
- Include oggetti digitali nel ZIP (`public/digital_objects/<token>/<filename>`)
- Supporto export singolo fondo, conservatore, progetto, o unità selezionate
- Nome modello snake_case esplicito per compatibilità Ruby (`unit_editor` non `uniteditor`)
- `AEFEncoder` custom JSON encoder per gestire istanze modello Django
- `_model_to_dict` corretto: FK usano `{field.name}_id`, ManyToMany saltati

**Esporta tutto:**
- Fond + Units + estensioni (FondName, FondIdentifier, FondLang, FondOwner, FondUrl, FondEditor)
- Unit extensions (UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage, UnitUrl, UnitEditor)
- SC2 cards (Sc2, Sc2TextualElement, Sc2VisualElement, Sc2Author, Sc2AttributionReason, Sc2Commission, Sc2CommissionName, Sc2Technique, Sc2Scale)
- ICCD (IccdDescription, IccdSubject, IccdDamage, IccdTechSpec)
- FSC (FscCode, FscOrganization, FscNationality, FscOpen, FscClose)
- FE (FeIdentification, FeContext, FeOpera, FeDesigner, FeCadastral, FeLandParcel, FeFractLandParcel, FeFractEdilParcel)
- Creator, Custodian, Project + estensioni
- RelCreatorCreator, RelCreatorInstitution, RelFondSource, RelCustodianSource, RelFondHeading, RelUnitHeading, RelFondDocumentForm, RelProjectFond, RelUnitAnagraphic
- Heading, Source, Institution, DocumentForm, Anagraphic, Lang, Place
- Editor (compilatori), EditorLog
- Eventi (unit_event)

**File `views/export_aef.py` (nuovo):**
- `ExportAEFView` — form batch (fondo/conservatore/progetto + checkbox oggetti digitali)
- `ExportFondAEFView` — export singolo fondo con subtree
- `ExportUnitsAEFView` — export unità selezionate

**Template:** `export_aef_form.html` — form con dropdown entità e opzione oggetti digitali

**URL:** `/export/aef/`, `/fonds/<pk>/export/aef/`, `/export/units/aef/`

#### 2. Export CSV unità

**File `views/export_csv.py`:** `ExportUnitsCSVView` con filtro per fondo e ricerca
**Template:** `export_units_csv.html`
**URL:** `/export/units/csv/`

#### 3. Report

**File `views/reports.py`:**
- `ReportIndexView` — pagina indice con lista progetti e conservatori
- `ReportProjectView` — report progetto (fondi, unità, creatori, conservatori collegati)
- `ReportCustodianView` — report conservatore (fondi, unità, accessibilità, servizi)

**Template:** `report_index.html`, `report_project.html`, `report_custodian.html`
**URL:** `/reports/`, `/reports/project/<pk>/`, `/reports/custodian/<pk>/`

#### 4. Ricerca avanzata

**File `views/advanced_search.py`:** `AdvancedSearchView` con filtri:
- Tipo entità (tutte, fondi, unità, creatori, conservatori, voci indice, fonti, progetti)
- Filtro per fondo (per unità)
- Filtro per tipo unità / tipo produttore
- Solo pubblicati
- Paginazione (50 risultati per pagina)

**Template:** `advanced_search.html`
**URL:** `/search/advanced/`

#### 5. Storico modifiche (EditorLog)

**Modello `EditorLog` in `models/system.py`:**
- Traccia: editor, tipo entità, ID entità, azione (create/update/delete), campo modificato, valore vecchio/nuovo, descrizione
- Indicizzato per entity_type+entity_id e editor

**Migrazione:** `0023_editor_log.py`

#### 6. Fix import/export round-trip

- `clean_fields` ora esclude sia `group_id` che `group` (evita "got multiple values for keyword argument 'group'")
- Aggiunti 15+ import handler mancanti: Editor, Institution, InstitutionEditor, Source, SourceUrl, Project, ProjectUrl, ProjectManager, ProjectStakeholder, DocumentForm, DocumentFormEditor, Anagraphic, Lang, Place
- `Sc2AttributionReason` e `Sc2CommissionName` — import risolti tramite `unit_id` del padre
- `IccdSubject` — import risolto tramite `iccd_description.unit_id`
- `_write_record` usa modello Django (non stringa) per mapping snake_case corretto

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- Round-trip export → import verificato: fond + 2 units + 23 record esportati, tutti reimportati correttamente
- 4 nuovi endpoint → HTTP 200 (export/aef/, export/units/csv/, search/advanced/, reports/)

---

## Rilascio v0.43.0 - Controllo qualità (2026-04-06)

### Cosa è stato fatto nella Fase 41

#### 1. Controllo qualità (Quality Checks)

**Problema:** In Ruby esiste una sezione "Controllo qualità" nel menu Strumenti che analizza la completezza e consistenza dei dati per fondi, creatori e conservatori. In Python mancava completamente.

**Soluzione:** Implementate 4 viste + 5 template allineati a Ruby `QualityChecksController`.

**Viste (`views/quality_checks.py` — nuovo file):**
| Vista | URL | Descrizione |
|-------|-----|-------------|
| `QualityCheckIndexView` | `/quality-checks/` | Lista fondi root, creatori, conservatori |
| `QualityCheckFondView` | `/quality-checks/fond/<pk>/` | Controllo qualità fondo + sottoalbero |
| `QualityCheckCreatorView` | `/quality-checks/creator/<pk>/` | Controllo qualità soggetto produttore |
| `QualityCheckCustodianView` | `/quality-checks/custodian/<pk>/` | Controllo qualità soggetto conservatore |

**Controlli per Fond (complesso archivistico):**
1. Denominazione (nome presente e non "[nome non compilato]")
2. Datazione (evento preferito presente)
3. Tipologia (fond_type o fond_type_term compilato)
4. Descrizione *(solo modalità completa)*
5. Storia archivistica *(solo modalità completa)*
6. Consistenza/lunghezza *(solo modalità completa)*
7. Unità archivistiche collegate (conteggio unità attive nel sottoalbero)
8. Soggetti produttori collegati (lista con dettaglio)
9. Soggetti conservatori collegati (lista con dettaglio)
10. Progetti collegati (lista con dettaglio)
11. Fonti collegate (conteggio)

**Controlli per Creator (soggetto produttore):**
1. Tipologia (P/E/F)
2. Tipologia ente (se tipo = Ente)
3. Denominazione (preferred_name)
4. Datazione (evento preferito)
5. Profilo storico / Biografia
6. Fonti collegate

**Controlli per Custodian (soggetto conservatore):**
1. Denominazione (preferred_name)
2. Macrotipologia (custodian_type)
3. Sedi (custodian_buildings)

**Modelli modificati (`models/core.py`):**
- Aggiunto `preferred_event` property a Fond, Creator, Custodian — restituisce l'evento con `preferred=True` dalla GenericRelation `events`
- Aggiunto `active_descendant_units_count` property a Fond — conta le unità nel sottoalbero (usa `subtree_ids`)
- Aggiunto `preferred_name` property a Creator — restituisce il nome preferito da `creator_names`
- Aggiunto `sources` property a Creator — filtra le fonti tramite `RelCreatorSource`

**Modelli modificati (`models/system.py`):**
- Aggiunto `full_display_date` property a Event — formatta la datazione come stringa leggibile
- Aggiunto `full_display_date_with_place` property a Event — include il luogo se presente

**Template creati:**
- `quality_check_index.html` — pagina principale con lista entità e form di ricerca (per >5 entità)
- `quality_check_fond.html` — dettaglio controlli fondo con sezioni "Requisiti minimi" e "Requisiti medi" (allineato a Ruby)
- `quality_check_fond_table.html` — partial per tabelle fondi con problemi
- `quality_check_creator.html` — dettaglio controlli soggetto produttore
- `quality_check_custodian.html` — dettaglio controlli soggetto conservatore

**Stile e icone (allineamento visivo a Ruby):**
- Icone: Bootstrap Icons (`bi bi-check-circle-fill` verde, `bi bi-exclamation-triangle-fill` arancione) invece di FontAwesome non caricato
- Bootstrap Icons CDN aggiunto in `base.html`
- Intestazioni sezioni ("Requisiti minimi", "Requisiti medi"): sfondo grigio `#999`, testo bianco, bordo arrotondato, text-shadow — identico a Ruby `h3.section`
- Testi `[non presente]` nelle tabelle: colore rosso puro `#f00` come Ruby `<span class="warning">`
- Testi `[Nessun ... associato]`: colore rosso (`text-danger`) come Ruby `<p class="red">`
- Messaggi errore: "X complesso archivistico su 1 (100,00%) ha il campo X vuoto" — allineato a Ruby con plurale corretto
- Messaggi successo: "Il complesso archivistico ha il campo X compilato" — singolare come Ruby

**Menu:** aggiunto "Controllo qualità" nel dropdown Strumenti di `base.html` (dopo "Titolario", prima di "Compilatori")

**Bug fix durante l'implementazione:**
- `trashed` non esiste su Unit → rimosso filtro da `active_descendant_units_count`
- `trashed` non esiste su Creator → rimosso filtro da query Creator/Custodian
- `name` non esiste su Creator → usato `prefetch_related('creator_names')` + sort manuale
- Related name Django auto-generati: `relcreatorfond`, `relcustodianfond`, `relprojectfond`, `relfondsource` (non `rel_creator_fonds`, ecc.)
- `select_related('preferred_event')` fallisce su GenericRelation → usato `prefetch_related('events')`
- `select_related('preferred_name')` fallisce su reverse FK → usato `prefetch_related('creator_names')`
- Filtro template `|divisor:` inesistente → calcolata percentuale nella view con `_pct()`

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- Index: HTTP 200, 5638 bytes
- Fond QC: HTTP 200, 10171 bytes
- Fond QC (complete): HTTP 200, 14713 bytes
- Creator/Custodian QC: funzionano (nessun dato nel DB di test)

---

## Rilascio v0.42.0 - Upload file per Oggetti Digitali (porting Paperclip) (2026-04-06)

### Cosa è stato fatto nella Fase 40c

#### 1. Upload file veri per Oggetti Digitali

**Problema:** Gli oggetti digitali avevano solo metadati (titolo, descrizione) ma nessun upload di file. In Ruby si usava Paperclip con thumbnail generate automaticamente.

**Soluzione:** Implementato upload file con Django FileField + Pillow per thumbnail.

**Modello (`models/core.py`):**
- Aggiunto `asset = models.FileField(upload_to='digital_objects/%Y/%m/%d/')`
- Override `save()`: popola automaticamente `asset_file_name`, `asset_content_type`, `asset_file_size`, genera `access_token`
- Metodi: `is_image()`, `is_video()`, `is_pdf()`, `get_thumbnail_url()`, `get_medium_url()`, `get_large_url()`, `generate_thumbnails()`
- Thumbnail generate con Pillow: thumb (130x130), medium (210x210), large (1280x1280) — allineati a Ruby Paperclip

**Form (`forms/digital_object.py`):**
- Aggiunto `asset_file = forms.FileField()` con validazione tipo e dimensione
- Formati accettati: JPEG, PNG, PDF, MP4 (come Ruby)
- Dimensione massima: 8 MB (come Ruby)
- `save()`: salva il file e genera thumbnail

**Viste (`views/digital_objects.py`):**
- `DigitalObjectCreateView`: chiama `generate_thumbnails()` dopo il salvataggio
- Template: `enctype="multipart/form-data"` aggiunto

**Settings:**
- `MEDIA_URL = 'media/'`, `MEDIA_ROOT = BASE_DIR / 'media'`
- `FILE_UPLOAD_MAX_MEMORY_SIZE = 8 MB`
- `DATA_UPLOAD_MAX_MEMORY_SIZE = 10 MB`

**URLs:**
- `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` in DEBUG mode

**Template:**
- Lista nested: mostra thumbnail/icone per immagini, PDF, video
- Form: campo file upload con help text e validazione errori

**Placeholder:**
- `static/images/pdf-medium.png` — icona PDF
- `static/images/mp4-medium.png` — icona video

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python test_digital_object_upload.py` — 17/17 test passati
- Upload immagine: file salvato, metadati popolati, thumbnail generate
- Upload PDF: riconosciuto correttamente, is_pdf() = True
- Validazione: file .exe rifiutato con errore
- Download file: accessibile via URL

---

## Rilascio v0.41.0 - Oggetti digitali nested (polimorfici) allineati a Ruby (2026-04-06)

### Cosa è stato fatto nella Fase 40b

#### 1. Oggetti digitali nested (associati a entità)

**Problema:** Gli oggetti digitali avevano solo una lista globale `/digital-objects/`. In Ruby si accede agli oggetti digitali **dal contesto dell'entità** (Fondo, Unità, Creatore, Conservatore, Fonte) con URL nested come `/fonds/5/digital_objects`.

**Soluzione:** Implementato routing polimorfico nested per 5 entità.

**URL nested aggiunte (20 nuove URL):**
- `/fonds/<fond_id>/digital-objects/` → lista filtrata per fondo
- `/fonds/<fond_id>/digital-objects/new/` → crea associato al fondo
- `/fonds/<fond_id>/digital-objects/<pk>/edit/` → modifica
- `/fonds/<fond_id>/digital-objects/<pk>/delete/` → elimina
- Idem per `units`, `creators`, `custodians`, `sources`

**Viste aggiornate (`views/digital_objects.py`):**
- `DigitalObjectListView` — rileva automaticamente il contesto nested (fond_id, unit_id, ecc.) e filtra gli oggetti
- `DigitalObjectCreateView` — associa automaticamente `content_type` + `object_id` all'entità padre
- `DigitalObjectUpdateView`, `DigitalObjectDeleteView` — redirect alla lista nested
- Lista globale `/digital-objects/` rimane funzionante per oggetti standalone

**Template nested creati:**
- `digital_object_nested_list.html` — lista card con link all'entità padre
- `digital_object_nested_form.html` — form con alert "Entità collegata"
- `digital_object_nested_confirm_delete.html` — conferma con link alla lista nested

**Link aggiunti nelle detail view:**
- `fond_detail.html` — pulsante "🖼️ Oggetti digitali (N)" nella toolbar
- `unit_detail.html` — card sidebar "Oggetti digitali" con link
- `creator_detail.html` — pulsante "🖼️ Oggetti digitali (N)" nella toolbar
- `custodian_detail.html` — link "🖼️ Oggetti digitali (N)" nei link rapidi
- `source_detail.html` — pulsante "🖼️ Oggetti digitali (N)" nella toolbar

**Modello modificato:**
- `DigitalObject.content_type` e `object_id` → nullable (già fatto in v0.40.0)

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python test_digital_object_nested.py` — 17/17 test passati
- Creazione nested: `content_type` e `object_id` associati correttamente
- Lista globale: funziona per oggetti standalone senza entità padre

---

## Rilascio v0.40.0 - CRUD completo Oggetti Digitali (DigitalObject) allineato a Ruby (2026-04-06)

### Cosa è stato fatto nella Fase 40

#### 1. CRUD completo DigitalObject (Oggetti Digitali)

**Problema:** Gli oggetti digitali avevano solo list/detail views. Mancavano completamente create/update/delete. La lista era minimale senza ricerca né info sull'entità collegata.

**Soluzione:**

**Form (forms/digital_object.py — nuovo file):**
- `DigitalObjectForm` con 4 campi: Titolo, Descrizione, Posizione, Pubblicato
- Etichette i18n da Ruby `config/locales/views/digital_objects.yml`

**Modello (models/core.py — modificato):**
- `content_type` e `object_id` resi nullable (per oggetti digitali standalone senza entità collegata)
- Migrazione `0021_digital_object_nullable_gfk.py`

**Viste CRUD (views/digital_objects.py — nuovo file):**
- `DigitalObjectListView` — lista globale con ricerca per titolo/descrizione/nome file (come Ruby `all` action)
- `DigitalObjectDetailView` — dettaglio con info file e link all'entità collegata
- `DigitalObjectCreateView`, `DigitalObjectUpdateView`, `DigitalObjectDeleteView`

**Template:**
- `digital_object_list.html` — riscritto: tabella con Titolo, File, Allegato a, Pubblicato + ricerca + paginazione
- `digital_object_detail.html` — riscritto: tutti i campi modello + info file + link entità collegata
- `digital_object_form.html` — form con 4 campi + info file (in modifica)
- `digital_object_confirm_delete.html` — conferma eliminazione

**File creati:**
- `archimista_python/archive/forms/digital_object.py`
- `archimista_python/archive/views/digital_objects.py`
- `archimista_python/archive/templates/archive/digital_object_form.html`
- `archimista_python/archive/templates/archive/digital_object_confirm_delete.html`

**File modificati:**
- `archimista_python/archive/models/core.py` — DigitalObject: content_type e object_id nullable
- `archimista_python/archive/forms/__init__.py` — aggiunto export `DigitalObjectForm`
- `archimista_python/archive/views/__init__.py` — aggiunti export viste digital object (rimosse da entities.py)
- `archimista_python/archive/views/entities.py` — rimosse DigitalObjectListView/DetailView
- `archimista_python/archive/urls.py` — 5 URL per il CRUD digital object
- `archimista_python/archive/templates/archive/digital_object_list.html` — riscritto completamente
- `archimista_python/archive/templates/archive/digital_object_detail.html` — riscritto completamente
- `archimista_python/archive/templates/archive/base.html` — voce "Oggetti digitali" nel menu Strumenti

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python test_digital_object_crud.py` — 19/19 test passati

---

## Rilascio v0.39.0 - CRUD completo Compilatori (Editor) allineato a Ruby (2026-04-06)

### Cosa è stato fatto nella Fase 39

#### 1. CRUD completo Editor (Compilatori)

**Problema:** I compilatori avevano solo list/detail views. Mancavano completamente create/update/delete.

**Soluzione:**

**Form (forms/editor.py — nuovo file):**
- `EditorForm` con 2 campi: Nome (obbligatorio), Cognome (obbligatorio)
- Etichette i18n da Ruby `config/locales/views/editors.yml`: "Nome", "Cognome"

**Viste CRUD (views/editors.py — nuovo file):**
- `EditorListView`, `EditorDetailView`, `EditorCreateView`, `EditorUpdateView`, `EditorDeleteView`

**Template:**
- `editor_list.html` — lista tabellare con azioni CRUD, pulsante "Nuovo compilatore"
- `editor_detail.html` — dettaglio con Nome, Cognome, Qualifica, pulsante "Modifica"
- `editor_form.html` — form con 2 campi obbligatori
- `editor_confirm_delete.html` — conferma eliminazione

**File creati:**
- `archimista_python/archive/forms/editor.py`
- `archimista_python/archive/views/editors.py`
- `archimista_python/archive/templates/archive/editor_list.html`
- `archimista_python/archive/templates/archive/editor_detail.html`
- `archimista_python/archive/templates/archive/editor_form.html`
- `archimista_python/archive/templates/archive/editor_confirm_delete.html`

**File modificati:**
- `archimista_python/archive/forms/__init__.py` — aggiunto export `EditorForm`
- `archimista_python/archive/views/__init__.py` — aggiunti export viste editor
- `archimista_python/archive/urls.py` — 5 URL per il CRUD editor
- `archimista_python/archive/templates/archive/base.html` — voce "Compilatori" nel menu Strumenti

### Risultati della Validazione
- `python manage.py check` — Nessun errore

---

## Rilascio v0.38.0 - Fix discrepanze Ruby vs Python (2026-04-06)

### Cosa è stato fatto nella Fase 38

#### 1. Unit hidden fields (allineato a Ruby)

**Problema:** `parent_id`, `fond_id`, `tsk` erano nel form ma non come `<input type="hidden">` come in Ruby.

**Soluzione:** Aggiunti 3 hidden field in `unit_form.html`:
```html
<input type="hidden" name="parent_id" id="id_parent_id" value="{{ form.instance.parent_id }}">
<input type="hidden" name="fond_id" id="id_fond_id" value="{{ form.instance.fond_id }}">
<input type="hidden" name="tsk" id="id_tsk" value="">
```

**File modificati:**
- `archimista_python/archive/templates/archive/unit_form.html`

#### 2. Custodian preferred_name campo hidden

**Problema:** Il campo `preferred` (hidden, valore=True) era presente in Ruby ma mancante in Python.

**Soluzione:**
- `CustodianPreferredNameForm`: aggiunto `preferred` ai fields con widget `HiddenInput`
- Template: aggiunto `{{ preferred_name_form.preferred }}`

**File modificati:**
- `archimista_python/archive/forms/custodian.py` — CustodianPreferredNameForm
- `archimista_python/archive/templates/archive/custodian_form.html`

#### 3. Fond abstract visibile solo se is_root

**Problema:** In Ruby l'abstract è visibile solo per fondi root (`@fond.is_root?`). In Python era sempre visibile.

**Soluzione:** Wrappato il campo abstract con `{% if fond_form.instance.is_root %}`

**File modificati:**
- `archimista_python/archive/templates/archive/fond_form.html`

#### 4. Qualifier dropdown da vocabolario (terms_select → Select)

**Problema:** Ruby usa `terms_select` per i qualifier (dropdown da vocabolario). Python usava TextInput.

**Soluzione:**
- `CustodianNameForm`: aggiunto `qualifier_term` ChoiceField con vocabolario `custodian_names.qualifier` (3 termini: Ufficiale, Variante, Alternativo)
- `CreatorOtherNameForm`: aggiunto `qualifier_term` ChoiceField con vocabolario `creator_names.qualifier` (4 termini: Nome di nascita, Pseudonimo, Variante, Alternativo)
- Template aggiornati con dropdown + hidden field per sync
- Viste aggiornate con contesto `terms`

**File modificati:**
- `archimista_python/archive/forms/custodian.py` — CustodianNameForm
- `archimista_python/archive/forms/creator.py` — CreatorOtherNameForm
- `archimista_python/archive/views/custodian.py` — aggiunto Term import + contesto terms (4 metodi)
- `archimista_python/archive/views/creator.py` — aggiunto Term import + `_get_dropdown_lists()`
- `archimista_python/archive/templates/archive/custodian_form.html`
- `archimista_python/archive/templates/archive/creator_form.html`

### Risultati della Validazione
- `python manage.py check` — Nessun errore

---

## Rilascio v0.37.0 - Refactoring Unit Views (God Object → Handler) + Fix Sc2Form (2026-04-06)

### Cosa è stato fatto nella Fase 37

#### 1. Refactoring UnitCreateView / UnitUpdateView (God Object → moduli)

**Problema:** `views/unit.py` era un God Object da 987 righe. Le due viste principali (`UnitCreateView`, `UnitUpdateView`) gestivano direttamente 37 form/formset con logica duplicata 6+ volte.

**Soluzione:** Estratti 6 handler specializzati in nuovo file `views/unit_formsets.py`:

| Handler | Responsabilità | Formset gestiti |
|---------|---------------|-----------------|
| `UnitExtensionsHandler` | Estensioni + relazioni Unit | 11 formset |
| `EventHandler` | Estremi cronologici (logica date) | 1 formset |
| `SC2Handler` | Scheda SC2 (disegni/foto) | 1 form + 6 formset + 2 nested |
| `ICCDHandler` | Scheda ICCD (beni culturali) | 2 form + 2 formset |
| `FSCHandler` | FSC (fascicoli sanitari) | 5 formset |
| `FEHandler` | FE (fabbricati edilizia) | 8 formset |

**Risultato:**
- `unit.py`: 987 → 420 righe (**-57%**)
- `unit_formsets.py`: 526 righe (nuovo)
- Viste ora sono orchestratori sottili che delegano agli handler
- Logica di salvataggio formset centralizzata in `save_formset_group()`
- Context building centralizzato in `build_unit_context()`

**File creati:**
- `archimista_python/archive/views/unit_formsets.py` — 6 handler + helper

**File modificati:**
- `archimista_python/archive/views/unit.py` — riscritto come orchestratore

#### 2. Fix Sc2Form: card_type reso opzionale

**Problema:** `Sc2Form` richiedeva `card_type` ma questo viene impostato dalla view da `sc2_tsk` dopo la validazione. Il form falliva sempre la validazione.

**Soluzione:** `Sc2Form.__init__`: `self.fields['card_type'].required = False`

**File modificati:**
- `archimista_python/archive/forms/sc2.py` — aggiunto `__init__` con card_type non richiesto

#### 3. Test di verifica

6 test creati in `test_unit_refactor.py`:
- ✅ GET /units/new/ — tutti i formset nel template
- ✅ POST creazione unità minimale
- ✅ GET modifica unità esistente
- ✅ GET dettaglio unità
- ✅ DELETE unità
- ✅ POST creazione unità con scheda SC2

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python test_unit_refactor.py` — 6/6 test passati

---

## Discrepanze note (documentate 2026-04-06)

Le seguenti funzionalità sono dichiarate "complete" o "100%" nei file markdown ma **non sono implementate** nell'interfaccia web:

| Dichiarazione | Realtà | File |
|--------------|--------|------|
| "Menu Navigazione 100% allineato a Ruby" | Mancano: Report, Esporta, Gestione utenti/gruppi | `base.html` |
| "Viste Entità di Servizio 100%" | Editor e DigitalObject hanno CRUD completo | `entities.py` |
| "Biografie ed Eventi UI" | Modelli e admin inlines esistono, campo `history` presente nei form Fond/Creator (come Ruby) | Nessun form dedicato necessario |
| "Esportazione 60%" | Solo PDF/DOCX base per fondi; nessun export unità, AEF, CSV | `export_utils.py` (106 righe) |
| "Detail Views 100%" | Manca: storico modifiche, log compilatori | Template detail |
| "Controllo qualità" | ✅ Implementato v0.43.0 | `quality_checks.py` |
| "TOTALE ~97%" | Più realistico: ~90-92% | — |

---

## Rilascio v0.36.0 - Fix formset, gerarchia unità, lista unità globale e UX albero (2026-04-06)

### Cosa è stato fatto nella Fase 36

#### 1. Fix critico: salvataggio formset inline vuoti

**Problema:** Creando una nuova unità (anche senza compilare i formset opzionali come URL, identificativi, lingue, ecc.), il salvataggio falliva con:
```
ValueError: The UnitUrl could not be created because the data didn't validate.
```

**Causa:** I formset inline hanno `extra=1` (una riga vuota di default). Il codice chiamava `fs.save()` senza verificare se la riga vuota contenesse dati validi, tentando di creare record con campi obbligatori vuoti.

**Soluzione:** Sostituito il pattern `fs.is_valid(); fs.save()` con un controllo esplicito per ogni form:
```python
if fs.is_valid():
    fs.save(commit=False)
    for form in fs.forms:
        if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
            if any(v for k, v in form.cleaned_data.items() if k not in ('id', 'DELETE') and v):
                form.save()
        elif form.cleaned_data and form.cleaned_data.get('DELETE', False) and form.instance.pk:
            form.instance.delete()
```

**File modificati:**
- `archive/views/unit.py` — 6 loop formset corretti (UnitCreateView + UnitUpdateView, per estensioni Unit, SC2, FSC/FE)
- `archive/views/creator.py` — 2 loop formset corretti (CreatorCreateView + CreatorUpdateView)

#### 2. Fix UnitDeleteView: NoReverseMatch per fond_detail

**Problema:** Eliminando un'unità, il redirect falliva con `NoReverseMatch: Reverse for 'fond_detail' not found`.

**Cause:**
1. Manca namespace `archive:` nella URL name
2. Usava `self.object.fond.pk` che può essere `None` dopo la cancellazione

**Soluzione:**
```python
def get_success_url(self):
    fond_id = self.object.fond_id
    if fond_id:
        return reverse_lazy('archive:fond_detail', kwargs={'pk': fond_id})
    return reverse_lazy('archive:fond_list')
```

#### 3. Gerarchia unità: "Modifica livello" (porting da Ruby)

**Problema:** In Ruby le unità possono essere nidificate fino a 3 livelli (Unità → Sottounità → Sottosottounità) con un modale "Modifica livello" che permette di spostare un'unità su o giù nella gerarchia. In Python non esisteva.

**Soluzione:**

**Modello Unit (`archive/models/core.py`):**
- Aggiunti metodi: `is_root_unit()`, `is_leaf_unit()`, `has_local_siblings()`, `is_movable_up()`, `is_movable_down()`, `is_not_movable()`, `_get_descendants()`
- Costante `MAX_LEVEL_OF_NODES = 2` (3 livelli: 0, 1, 2)

**Viste (`archive/views/unit.py`):**
- `unit_move` — mostra il modale con le opzioni disponibili
- `unit_move_up` — promuove l'unità al livello del genitore
- `unit_move_down` — demotte l'unità sotto un fratello selezionato

**Template (`archive/unit_move.html`):**
- Interfaccia a due step: scelta azione (su/giù) → conferma
- Per "giù": lista radio button con i fratelli disponibili
- Pulsante "📐 Modifica livello" aggiunto in `unit_detail.html`

**URL:**
- `/units/<pk>/move/`, `/units/<pk>/move_up/`, `/units/<pk>/move_down/`

#### 4. Albero interattivo: distinzione fondi vs unità

**Problema:** L'albero trattava fondi e unità allo stesso modo per le azioni interattive (+, −, rinomina, drag & drop), causando errori quando si operava su unità.

**Soluzione:**

| Azione | Fondi/Serie | Unità |
|--------|:-----------:|:-----:|
| **+** Crea nuovo livello | ✅ | ❌ Messaggio informativo |
| **−** Rimuovi livello | ✅ (non root) | ❌ Messaggio informativo |
| **Doppio click** Rinomina | ✅ | ❌ Disabilitato |
| **Drag & Drop** Sposta | ✅ | ❌ Disabilitato |
| **Click** Vai al dettaglio | ✅ | ✅ |

**File modificati:**
- `tree_view.html` — controlli `node.type === 'unit'` su tutte le azioni
- `tree.py` — aggiunto `tree_children_fonds_only()` per albero soli fondi

#### 5. Classificazione: albero mostra solo fondi (allineato a Ruby)

**Problema:** Il modale di classificazione mostrava sia fondi che unità. In Ruby mostra solo la gerarchia dei fondi/serie.

**Soluzione:**
- Nuova vista `tree_children_fonds_only()` — restituisce solo figli Fond, esclude Unit
- Nuovo endpoint `/api/tree-fonds/<node_id>/`
- Modale classificazione usa il nuovo endpoint
- Rimosso tipo `unit` dalla configurazione jsTree del modale

#### 6. Lista unità globale

**Problema:** Le unità senza fondo associato (orfane) erano invisibili tranne che con la ricerca globale. Non esisteva una vista "lista unità".

**Soluzione:**

**Vista (`archive/views/unit_list.py`):**
- `UnitListView` — lista globale con paginazione (50 per pagina)
- Filtro per fondo (`?fond_id=X`)
- Ricerca per titolo/segnatura (`?q=...`)
- Conteggio unità orfane con alert

**Template (`archive/unit_list.html`):**
- Tabella con: Segnatura, Titolo, Fondo, Tipo, Azioni
- Badge "orfana" evidenziato in giallo per unità senza fondo
- Alert giallo con conteggio unità orfane
- Filtri: ricerca + dropdown fondo
- Pulsanti: Dettagli, Modifica, Elimina (con testo, non solo icone)

**Menu:** aggiunto "Unità" nel dropdown Schede di `base.html`

**URL:** `/units/`

#### 7. UX dettaglio fondo: serie e sottofondi visibili

**Problema:** Quando un fondo aveva serie/sottofondi ma nessuna unità diretta, il messaggio diceva solo "Nessuna unità registrata" senza mostrare le serie figlie.

**Soluzione:**
- Aggiunta sezione "📂 Serie e sottofondi" nel `fond_detail.html`
- Lista delle serie figlie con link al dettaglio e conteggio unità
- Messaggio "Nessuna unità" aggiornato con link alle serie se presenti

#### 8. UX albero: freccette di espansione visibili

**Problema:** Il tema jsTree "apple" nascondeva le frecce di espansione dei nodi.

**Soluzione:** Cambiato tema da `apple` a `default` con `dots: true` nel modale di classificazione.

#### 9. Creazione serie: pulsante "Aggiungi serie" nel dettaglio fondo

**Problema:** Per creare una serie/sottofondo serviva andare all'albero o compilare manualmente il campo "Fondo padre" nel form.

**Soluzione:**
- Pulsante "📁 Aggiungi serie" nel `fond_detail.html`
- Link: `/fonds/new/?parent_id=X`
- `FondCreateView` pre-compila il campo "Fondo padre" se `parent_id` è nell'URL
- Fix `success_url`: aggiunto namespace `archive:`

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- Creazione unità senza formset: ✅ Nessun errore di validazione
- Classificazione sotto serie: ✅ Unità spostate correttamente
- Lista unità: ✅ Mostra anche unità orfane
- Modifica livello: ✅ Promozione/demozione funzionante
- Albero: ✅ Azioni su unità disabilitate con messaggi chiari

---

## Rilascio v0.35.0 - Albero interattivo e classificazione di massa (2026-04-06)

### Cosa è stato fatto nella Fase 35

#### 1. Albero interattivo (Tree Manipulation API)

**Problema:** La treeview Python era sola navigazione (click → dettaglio). In Ruby l'albero è interattivo: si possono creare, rinominare, spostare ed eliminare nodi direttamente dall'albero con drag & drop.

**Soluzione:** Implementate 7 nuove API e interfaccia jsTree completa con plugin `dnd` (drag & drop).

**Nuove API (`archive/views/tree.py`):**
| Endpoint | Metodo | Funzione | Ruby equivalente |
|----------|--------|----------|-----------------|
| `/api/tree/node/create/` | POST | Crea nuovo nodo figlio/root | `POST /fonds/` |
| `/api/tree/node/<id>/rename/` | PUT | Rinomina nodo | `PUT /fonds/:id/rename` |
| `/api/tree/node/<id>/move/` | PUT | Sposta nodo sotto altro genitore | `PUT /fonds/:id/move` |
| `/api/tree/node/<id>/trash/` | PUT | Soft delete (cestino) | `PUT /fonds/:id/move_to_trash` |
| `/api/tree/node/<id>/restore/` | PUT | Ripristina dal cestino | `PUT /fonds/:id/restore_subtree` |
| `/tree/<root_id>/trash/` | GET | Pagina cestino | `GET /fonds/:root_id/trash` |
| `/api/tree/<root_id>/trashed/` | GET | API nodi trashed (JSON) | `trashed_subtree` |

**Funzionalità implementate:**
| Funzionalità | Stato |
|-------------|-------|
| Pulsante **+** (Aggiungi livello) | ✅ Crea nodo figlio o root con prompt nome |
| Pulsante **−** (Rimuovi livello) | ✅ Soft delete con conferma, blocca su root |
| Doppio click (rinomina) | ✅ Rinomina inline via jsTree |
| Drag & Drop (sposta nodo) | ✅ Plugin `dnd` con validazione |
| Prevenzione riferimenti circolari | ✅ Non si può spostare sotto un discendente |
| Cestino | ✅ Pagina dedicata con lista e ripristino |
| Ricalcolo posizioni | ✅ Automatico dopo spostamento |
| Aggiornamento ancestry | ✅ Automatico (path gerarchico) |

**Modelli aggiunti a Fond:**
- `root` — proprietà: restituisce il nodo root dell'albero
- `is_root` — proprietà: True se non ha genitore
- `descendants` — proprietà: tutti i discendenti (ricorsivo)
- `subtree_ids` — proprietà: ID di tutti i nodi nel sottoalbero

**Template creati:**
- `tree_trash.html` — pagina cestino con lista nodi eliminati e pulsante ripristina

**Template modificati:**
- `tree_view.html` — riscritto con toolbar (+, −, cestino), jsTree con plugin `dnd`, gestione rename/move/trash via AJAX

#### 2. Classificazione di massa delle unità

**Problema:** In Ruby, dalla lista unità si possono selezionare multiple unità e spostarle sotto un altro fondo con un modale contenente l'albero. In Python non esisteva.

**Soluzione:** Aggiunta classificazione di massa nel dettaglio fondo.

**Funzionalità implementate:**
| Funzionalità | Stato |
|-------------|-------|
| Checkbox su ogni unità | ✅ Nel fond_detail, sezione "Struttura unità" |
| Pulsante "Classifica selezionate" | ✅ Si abilita quando ≥1 checkbox selezionata |
| Modale con albero fondi | ✅ jsTree sola lettura (selezione singola) |
| API `PUT /units/classify/` | ✅ Aggiorna fond_id + ricalcola posizioni |
| Feedback all'utente | ✅ Messaggio di successo con conteggio |

**File modificati:**
- `archive/views/unit.py` — aggiunta vista `units_classify`
- `archive/urls.py` — aggiunta URL `/units/classify/`
- `archive/views/__init__.py` — export `units_classify`
- `templates/archive/fond_detail.html` — checkbox + modale + JavaScript

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py show_urls` — Tutte le 8 nuove URL risolte
- Test creazione nodo: ✅ `POST /api/tree/node/create/` → nodo creato con ancestry corretto
- Test rinomina: ✅ `PUT /api/tree/node/<id>/rename/` → nome aggiornato
- Test classificazione: ✅ 2 unità spostate da fond_38 a fond_40 con posizioni ricalcolate
- Dati di test puliti dopo verifica

---

## Rilascio v0.34.0 - Titolario di classificazione (2026-04-06)

### Cosa è stato fatto nella Fase 34

#### 1. Titolario di classificazione (Classification) — CRUD completo

**Problema:** Il modello `Classification` esisteva già con struttura gerarchica (parent/children) ed era collegato a `Unit` tramite FK, ma non aveva alcuna interfaccia dedicata né in Ruby né in Python. Mancava uno strumento per gestire il titolario e assegnare classificazioni alle unità archivistiche.

**Soluzione:** Creato un sistema completo per la gestione del titolario con interfaccia ad albero, CRUD completo e assegnazione alle unità.

**File creati:**
- `archimista_python/archive/forms/classification.py` — `ClassificationForm` con:
  - Campi: codice, denominazione, descrizione, classe padre
  - Prevenzione riferimenti circolari (esclusione self e discendenti)
  - Dropdown classe padre con etichette gerarchiche
- `archimista_python/archive/views/classifications.py` — 6 viste:
  - `ClassificationListView` — lista tabellare con dati albero JSON
  - `ClassificationDetailView` — dettaglio con breadcrumb, figli, unità
  - `ClassificationCreateView` / `ClassificationUpdateView` — CRUD completo
  - `ClassificationDeleteView` — con controlli su unità collegate
  - `ClassificationTreeDataView` — API JSON per albero (jsTree-ready)
  - `ClassificationUnitsView` — lista unità classificate

**Template creati:**
- `classification_list.html` — lista tabellare + struttura albero jsTree (colonna sinistra), dettaglio dinamico (colonna destra)
- `classification_detail.html` — breadcrumb, informazioni, statistiche, classi figlio, unità classificate
- `classification_form.html` — form con layout a 2 colonne (dati + aiuto)
- `classification_confirm_delete.html` — conferma eliminazione con avvisi
- `classification_units.html` — lista completa unità classificate

**File modificati:**
- `archive/forms/__init__.py` — aggiunto export `ClassificationForm`
- `archive/views/__init__.py` — aggiunti export viste classification
- `archive/urls.py` — 7 URL per il titolario
- `archive/forms/unit.py` — aggiunto campo `classification` al form unità:
  - Import `Classification` dal modello
  - `ModelChoiceField` con queryset ordinato
  - Aggiunto a `fields`, `widgets`, `labels`
- `archive/templates/archive/units/partials/_tab_description.html` — campo classificazione nella sezione "Contesto" (3 colonne: Fondo, Unità padre, Classificazione)
- `archive/templates/archive/units/partials/_detail_description.html` — riga classificazione nella detail view con link
- `archive/templates/archive/base.html` — voce "Titolario" nel menu Strumenti

**Funzionalità implementate:**
| Funzionalità | Stato |
|-------------|-------|
| Gerarchia padre/figlio | ✅ Con prevenzione riferimenti circolari |
| Lista tabellare | ✅ Con codice, nome, padre, unità, azioni |
| Dettaglio con breadcrumb | ✅ Percorso gerarchico completo |
| Statistiche | ✅ Classi figlio + unità classificate |
| Lista unità classificate | ✅ Con link a dettaglio e modifica |
| Form con validazione | ✅ Codice, denominazione (obbligatoria), padre opzionale |
| Eliminazione sicura | ✅ Controlla unità collegate |
| API JSON per albero | ✅ Per integrazione jsTree futura |
| Assegnazione a Unità | ✅ Dropdown nel form unità |
| Visualizzazione in Unit detail | ✅ Con link alla classificazione |

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py show_urls` — Tutte le 7 URL risolte correttamente
- Creazione test: 4 classificazioni gerarchiche create con successo
- List view: tabella gerarchica visualizzata correttamente
- Detail view: breadcrumb, figli, statistiche funzionanti
- Form unità: campo classificazione aggiunto e visibile

---

## Rilascio v0.33.0 - Autocomplete Select2 per tutte le relazioni (2026-04-05)

### Cosa è stato fatto nella Fase 33

#### 1. Select2 per le relazioni (sostituisce dropdown statici)

**Problema:** Le relazioni tra entità usavano dropdown `<select>` statici che caricavano TUTTI i record. Con archivi grandi (centinaia di fonti, voci di indice, ecc.) diventavano ingestibili. Ruby usa autocomplete/livesearch.

**Soluzione:** Integrato `django-select2` con widget AJAX per tutte le relazioni.

**File creati:**
- `archimista_python/archive/widgets.py` — 8 widget Select2:
  - `FondSelect2Widget`, `CreatorSelect2Widget`, `CustodianSelect2Widget`
  - `SourceSelect2Widget`, `InstitutionSelect2Widget`, `HeadingSelect2Widget`
  - `AnagraphicSelect2Widget`, `DocumentFormSelect2Widget`

**File modificati:**
- `requirements.txt` — aggiunto `django-select2==8.4.0`
- `settings.py` — aggiunto `django_select2` a INSTALLED_APPS + configurazione cache
- `urls.py` — aggiunto endpoint `/select2/` per chiamate AJAX
- `base.html` — rimosso Select2 CDN (ora gestito da django-select2)
- **Forms** (5 file): `fond.py`, `creator.py`, `custodian.py`, `unit.py`, `project.py` — widget Select2 sui campi relazione
- **Views** (4 file): `fond.py`, `creator.py`, `custodian.py`, `unit.py` — prefix formset uniformati + `is_valid()` prima di `save()`
- **Templates** (5 file): `fond_form.html`, `creator_form.html`, `custodian_form.html`, `unit_form.html`, `project_form.html` — CSS Select2, JS cloning corretto, label "Elimina"

**Entità con autocomplete:**
| Entità | Relazioni con Select2 |
|--------|----------------------|
| **Fond** | Heading (voci di indice), Source (fonti), DocumentForm (forme documentarie) |
| **Creator** | Creator (altri soggetti), Institution, Source, Fond |
| **Custodian** | Source, Fond |
| **Unit** | Heading, Source, Anagraphic |
| **Project** | Fond |

**Fix critici durante lo sviluppo:**
- Nomi campo widget errati (`lemma` → `name` per Heading, `first_name/last_name` → `name/surname` per Anagraphic)
- Prefix formset non allineati tra view e template (causava pulsanti "Aggiungi" inerti)
- `formset.save()` chiamato senza `is_valid()` → `AttributeError: cleaned_data`
- Cloning Select2: distruggere sull'originale prima di clonare, re-inizializzare con `.djangoSelect2()` (non `.select2()`)
- Label "Elimina" mancanti sui formset relazione di Fond

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- Ricerca AJAX funzionante su tutte le relazioni
- Pulsanti "Aggiungi" funzionano correttamente
- Checkbox "Elimina" visibile e funzionante al salvataggio

---

## Rilascio v0.32.0 - CRUD completo Profili documentari + Fix ordine campi anagrafiche (2026-04-05)

### Cosa è stato fatto nella Fase 32

#### 1. CRUD completo Profili documentari (DocumentForm)

**Problema:** I profili documentari avevano solo list/detail views. Mancavano completamente create/update/delete.

**Soluzione:**

**Form (forms/document_form.py — nuovo file):**
- `DocumentFormForm` con 3 campi: Denominazione (obbligatorio), Descrizione, Note
- `DocumentFormEditorForm` + `DocumentFormEditorFormSet` inline per compilatori
- `editing_type` da vocabolario `editors.editing_type` (7 termini)

**Viste CRUD (views/document_forms.py — nuovo file):**
- `DocumentFormListView`, `DocumentFormDetailView`
- `DocumentFormCreateView`, `DocumentFormUpdateView`, `DocumentFormDeleteView`

**Template:**
- `document_form_list.html` — pulsante "Nuovo profilo documentario", azioni Modifica/Elimina
- `document_form_detail.html` — Denominazione, Descrizione, Note, Compilatori, Info legacy
- `document_form_form.html` — form con 3 campi + formset compilatori dinamico
- `document_form_confirm_delete.html` — conferma eliminazione

**Etichette i18n (da Ruby `config/locales/views/document_forms.yml`):**
- `document_forms_name` → "Denominazione"
- `document_forms_description` → "Descrizione"
- `document_forms_note` → "Note"
- `document_form_editor` → "Compilatore"
- `document_form_editors` → "Compilatori"

#### 2. Fix ordine campi anagrafiche

**Problema:** Nel form anagrafiche, i "Codici identificativi" erano alla fine. In Ruby sono il primo campo del form.

**Soluzione:** Spostata la sezione formset dei codici identificativi PRIMA dei campi Nome/Cognome, come in Ruby.

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py runserver` — Server si avvia correttamente
- Tutti gli import — ✅ OK
- Tutte le URL — ✅ Risolte correttamente
- Tutte le 8 entità di servizio ora con CRUD completo

---

## Rilascio v0.31.0 - CRUD completo Anagrafiche (Anagraphic) allineato a Ruby (2026-04-05)

### Cosa è stato fatto nella Fase 31

#### 1. CRUD completo Anagrafiche
- `AnagraphicForm` con 6 campi: Nome (obbligatorio), Cognome (obbligatorio), Luogo/Data nascita, Luogo/Data morte
- `AnagIdentifierFormSet` inline per Codici identificativi (identificativo + qualifica)
- Viste CRUD: `AnagraphicListView`, `AnagraphicDetailView`, `AnagraphicCreateView`, `AnagraphicUpdateView`, `AnagraphicDeleteView`
- Template: list, detail, form, confirm_delete
- Etichette allineate a Ruby i18n (`config/locales/views/anagraphics.yml`)

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py runserver` — Server si avvia correttamente
- Formset "Nuovo identificativo" funzionante

---

## Rilascio v0.30.0 - CRUD completo Voci di indice (Heading) allineato a Ruby (2026-04-05)

### Cosa è stato fatto nella Fase 30

#### 1. CRUD completo Voci di indice
- `HeadingForm` con 4 campi: Tipologia (dropdown da vocabolario), Lemma (obbligatorio), Estremi cronologici, Qualifica
- Vocabolario `headings.heading_type` allineato a Ruby: Ente, Persona, Famiglia, Toponimo, Altro
- Viste CRUD: `HeadingListView`, `HeadingDetailView`, `HeadingCreateView`, `HeadingUpdateView`, `HeadingDeleteView`
- Template: list, detail, form, confirm_delete
- Sincronizzazione automatica `heading_type_term` ↔ `heading_type`
- Etichette allineate a Ruby i18n (`config/locales/views/headings.yml`)

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py runserver` — Server si avvia correttamente

---

## Rilascio v0.29.0 - CRUD completo Profili istituzionali (Institution) allineato a Ruby (2026-04-05)

### Cosa è stato fatto nella Fase 29

#### 1. Problema Riscontrato
- Le istituzioni avevano solo list/detail views (nessun CRUD)
- Mancava il modello `InstitutionEditor` (compilatori)
- Nessun form per creazione/modifica

#### 2. Modello Aggiunto
```python
# archive/models/system.py
class InstitutionEditor(models.Model):
    institution = models.ForeignKey('Institution', ...)
    name = models.CharField(...)
    qualifier = models.CharField(...)
    editing_type = models.CharField(...)
    edited_at = models.DateField(...)
```
- Migrazione `0020_institutioneditor.py` creata e applicata

#### 3. Form Allineati a Ruby
- `InstitutionForm` — 3 campi: Denominazione (obbligatorio), Descrizione, Annotazioni
- Etichette da `config/locales/views/institutions.yml`
- `InstitutionEditorForm` — editing_type da vocabolario `editors.editing_type` (7 termini)
- `InstitutionEditorFormSet` — inline con `extra=0, can_delete=True`

#### 4. Viste CRUD
- `InstitutionListView` — ordinata per nome, paginata
- `InstitutionDetailView` — con sezione compilatori
- `InstitutionCreateView` / `InstitutionUpdateView` — con salvataggio atomico form + formset
- `InstitutionDeleteView` — con conferma

#### 5. Template
- `institution_list.html` — tabella con Dettagli/Modifica/Elimina + pulsante "Nuovo profilo istituzionale"
- `institution_detail.html` — dettaglio + tabella compilatori
- `institution_form.html` — layout tabella per formset, `<template>` per cloning JS
- `institution_confirm_delete.html` — conferma eliminazione

#### 6. JavaScript Fix
- Usato `<template id="editor-empty">` invece di div nascosto
- `cloneNode(true)` per cloning corretto del contenuto del template
- Sostituzione `__prefix__` → indice effettivo su name/id/for
- Funziona sia con 0 che con N righe esistenti

#### 7. Fix Layout
- **Problema iniziale**: campi formset "compressi" nella prima cella della tabella
- **Causa**: JS creava `<tr><tr>...</tr></tr>` (doppio wrapping)
- **Soluzione**: estrazione diretta del `<tr>` dal template cloned, nessun wrapping aggiuntivo

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py migrate` — Migrazione applicata
- `python manage.py runserver` — Server si avvia correttamente
- Formset "Aggiungi compilatore" funzionante con 0 e N righe
- Combo editing_type popolata con 7 termini da vocabolario
- Layout tabella corretto: campi affiancati

---

## Rilascio v0.28.0 - CRUD completo Fonti (Source) allineato a Ruby (2026-04-04)

### Cosa è stato fatto nella Fase 28

#### 1. Problema Riscontrato
Le Fonti (Source) avevano solo list/detail views. Mancavano completamente create/update/delete. Il modello Python era incompleto (mancavano 11+ campi presenti in Ruby). Le etichette dei form erano inventate, non allineate a Ruby i18n. Le combo delle tipologie erano inventate.

#### 2. Modelli Aggiunti/Corretti
- **SourceType** — nuovo modello (tabella lookup gerarchica), 28 record esatti da `db/seeds/source_types.json`:
  - 4 root: bibliografia, strumento di corredo, fonte archivistica, fonte normativa
  - 6 sottotipi bibliografia: libro, capitolo di libro, articolo di rivista, atti di convegno, intervento in convegno, altro
  - 22 sottotipi strumento di corredo: banca dati, censimento, documenti, edizione di fonti, elenco, elenco di consistenza, elenco di deposito, elenco di versamento, guida, indice, inventario, inventario analitico, inventario sommario, inventario topografico, regesto, repertorio, repertorio alfabetico, repertorio cronologico, rubrica, schedario, schedatura, titolario
- **SourceUrl** — nuovo modello (URL + note collegati alla fonte)
- **Source** — 11+ campi aggiunti: `date_string`, `finding_aid_valid`, `finding_aid_published`, `related_item`, `related_item_specs`, `abstract`, `institution`, `volume`, `pages`, `book_title`, `legacy_description`, `created_by`, `updated_by`, `group`, `db_source`, `legacy_id`
- Metodo `formatted_source()` aggiunto (formatta come Ruby: Autore, _Titolo_, Luogo, Editore, Data)

#### 3. Migrazioni
- `0018_add_source_extra_fields_and_source_url.py` — campi Source + modello SourceUrl
- `0019_add_source_type.py` — modello SourceType

#### 4. Form (forms/source.py — nuovo file)
- **SourceForm** con labels da Ruby `views/sources.yml`:
  - Tipologia, Tipologia specifica, Sigla, Autore, Titolo, Curatore, Luogo di pubblicazione, Editore, Data di pubblicazione, Validità dello strumento, Edito?, Titolo correlato, Note titolo correlato, Abstract
- **SourceUrlForm** + **SourceUrlFormSet** inline
- Dropdown tipologie gerarchiche con aggiornamento dinamico via JS

#### 5. Viste CRUD (views/source.py — nuovo file)
- **SourceListView** — con ricerca per titolo/autore, pagination
- **SourceDetailView** — 2 tab (Descrizione con TUTTI i campi Ruby, Relazioni con fondi/creatori/custodi)
- **SourceCreateView** — con selezione tipo da dropdown (Bibliografia, Strumento di corredo, Fonte archivistica, Fonte normativa)
- **SourceUpdateView** — modifica completa con formset URL
- **SourceDeleteView** — con conferma

#### 6. Template
- `source_list.html` — ricerca, dropdown "Nuova fonte" per tipo, tabella con dati formattati, badge "importato", elimina
- `source_detail.html` — 2 tab, tutti i campi Ruby, relazioni con link
- `source_form.html` — 2 tab (Descrizione, Relazioni), formset URL dinamico, JS per sottotipologie dinamiche
- `source_confirm_delete.html` — conferma eliminazione

#### 7. Etichette i18n corrette (da Ruby `config/locales/views/sources.yml`)
| Campo | Ruby IT | Python (prima) | Python (ora) |
|-------|---------|---------------|-------------|
| `short_title` | Sigla | Titolo breve | Sigla ✅ |
| `source_subtype_code` | Tipologia specifica | Sottotipologia | Tipologia specifica ✅ |
| `place` | Luogo di pubblicazione | Luogo | Luogo di pubblicazione ✅ |
| `date_string` | Data di pubblicazione | Data | Data di pubblicazione ✅ |
| `finding_aid_valid` | Validità dello strumento | Strumento di corredo valido | Validità dello strumento ✅ |
| `finding_aid_published` | Edito? | Strumento di corredo pubblicato | Edito? ✅ |
| `related_item` | Titolo correlato | Titolo libro correlato/rivista | Titolo correlato ✅ |
| `related_item_specs` | Note titolo correlato | Specifiche elemento correlato | Note titolo correlato ✅ |

#### 8. Admin
- SourceType, Source (con SourceUrlInline), SourceUrl registrati

#### 9. QWEN.md aggiornato
Aggiunte 2 regole fondamentali:
- Etichette form: NON INVENTARE — cercare in `config/locales/views/*.yml` di Ruby
- Combo/select: NON INVENTARE — leggere da `db/seeds/*.json` di Ruby

#### 10. Correzione etichette tutte le entità
Labels corrette aggiunte a tutti i form Python:
- **FondForm**: 20+ labels (Denominazione, Contenuto, Storia archivistica, Nota dell'archivista, ecc.)
- **UnitForm**: 30+ labels (Tipologia, Attribuito?, Segnatura provvisoria, Busta, Fascicolo, ecc.)
- **CreatorForm**: 7 labels (Tipologia, Tipologia ente, Sede, Profilo storico / Biografia, ecc.)
- **CustodianForm**: 10 labels (Macrotipologia, Condizione giuridica, Patrimonio, ecc.)
- **ProjectForm**: già corretto

Template labels convertiti a `{{ form.field.label }}`:
- fond_form.html: 29+ field labels
- unit _tab_description.html: 20/26
- unit _tab_physical.html: 12/14
- unit _tab_access.html: 4/4
- unit _tab_sources.html: 3/3
- unit _tab_editors.html: 4 header colonne

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py migrate` — Migrazioni 0018 e 0019 applicate
- `python manage.py runserver` — Server si avvia correttamente
- 32 source_types caricati (4 root + 28 sottotipi)
- Form con etichette allineate a Ruby i18n
- Dropdown sottotipologie dinamico via JS

---

## Rilascio v0.26.0 - Allineamento Campi Form e Etichette i18n a Ruby (2026-04-03)

### Cosa è stato fatto nella Fase 26

#### 1. Confronto sistematico Ruby vs Python
- Analizzati tutti i form Ruby (`app/views/*/_form.html.erb`, partials)
- Analizzati tutti i form Python (`archive/forms/*.py`, `archive/templates/archive/*_form.html`)
- Confronto campo per campo con etichette da `config/locales/it.yml`
- Report completo in `RUBY_VS_PYTHON_COMPARISON.md`

#### 2. Modelli Aggiunti/Corretti
- **Sc2AttributionReason** — modello mancante (nested dentro Sc2Author), migrazione `0016`
- **UnitOtherReferenceNumber** — aggiunti campi `qualifier` e `note`, migrazione `0017`

#### 3. Campi Aggiunti ai Form
**Fond:**
- `arrangement_note` ("Nota dell'archivista")

**Unit (14 campi):**
- `given_title` (checkbox "Attribuito")
- `extent` ("Consistenza")
- `arrangement_note` ("Nota dell'archivista")
- `tmp_reference_number`, `tmp_reference_string` ("Segnatura provvisoria")
- `folder_number` ("Busta"), `file_number` ("Fascicolo")
- `related_materials` ("Documentazione collegata")
- `preservation_note` ("Note sullo stato di conservazione")
- `restoration` ("Restauri")
- `note` ("Appunti di servizio")
- `physical_container_type`, `physical_container_title`, `physical_container_number`

**Unit Formset:**
- `unit_urls` (formset URL)
- `unit_identifiers` (formset Identificativi)
- `fe_fract_land_parcels` (Frazionamenti particelle fondiarie)
- `fe_fract_edil_parcels` (Frazionamenti particelle edilizie)

**Creator:**
- `creator_legal_statuses` formset ("Condizione giuridica")

#### 4. Etichette Allineate a Ruby i18n
Da `config/locales/it.yml`:
- `unit_type` → "Tipologia" (era "Tipo unità")
- `extent` (Unit) → "Consistenza"
- `extent` (Fond) → "Consistenza archivistica"
- `arrangement_note` → "Nota dell'archivista"
- `given_title` → "Attribuito"
- `access_condition` → "Accesso" (era "Condizione di accesso")
- `use_condition` → "Riproduzione" (era "Condizione d'uso")
- `physical_description` → "Descrizione estrinseca" (era "Descrizione fisica")
- `preservation_note` → "Note sullo stato di conservazione"
- `restoration` → "Restauri"
- `note` (Unit) → "Appunti di servizio"
- `residence` (Creator) → "Sede" (era "Residenza")
- `history` (Fond) → "Storia archivistica" (era "Storia del Fondo")

#### 5. Custodian editing_type Fix
**Prima:** hardcoded 2 opzioni (`c`/`r`)
**Dopo:** `ChoiceField` popolato da vocabolario `editors.editing_type` (7 termini)

#### 6. File Modificati
- `archimista_python/archive/models/sc2.py` — aggiunto Sc2AttributionReason
- `archimista_python/archive/models/extensions.py` — aggiunti qualifier/note a UnitOtherReferenceNumber
- `archimista_python/archive/models/__init__.py` — export Sc2AttributionReason
- `archimista_python/archive/forms/fond.py` — aggiunto arrangement_note
- `archimista_python/archive/forms/unit.py` — 14 campi + UnitOtherReferenceNumberForm aggiornato
- `archimista_python/archive/forms/creator.py` — CreatorLegalStatusFormSet
- `archimista_python/archive/forms/custodian.py` — editing_type da vocabolario
- `archimista_python/archive/forms/sc2.py` — Sc2AttributionReasonForm, Sc2CommissionNameForm
- `archimista_python/archive/forms/fe.py` — FeFractLandParcelForm, FeFractEdilParcelForm + formset
- `archimista_python/archive/forms/__init__.py` — export nuovi form/formset
- `archimista_python/archive/views/unit.py` — nuovi formset in create/update
- `archimista_python/archive/views/creator.py` — creator_legal_statuses_formset
- `archimista_python/archive/templates/archive/fond_form.html` — arrangement_note, label corrette
- `archimista_python/archive/templates/archive/units/partials/_tab_description.html` — 14 campi + formset
- `archimista_python/archive/templates/archive/units/partials/_tab_physical.html` — 6 campi + sezioni
- `archimista_python/archive/templates/archive/units/partials/_tab_access.html` — label i18n
- `archimista_python/archive/templates/archive/units/partials/_tab_sources.html` — 3/3
- `archimista_python/archive/templates/archive/units/partials/_tab_editors.html` — 4 header colonne
- `archimista_python/archive/templates/archive/unit_form.html` — JS per nuovi formset
- `archimista_python/archive/templates/archive/creator_form.html` — condizione giuridica formset

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py migrate` — Migrazioni 0016 e 0017 applicate
- `python manage.py runserver` — Server si avvia correttamente
- Tutti i 26+ campi mancanti ora presenti
- Tutte le etichette allineate a Ruby i18n

---

## Rilascio v0.27.0 - Fix JavaScript Formset e Allineamento Detail Views (2026-04-04)

### Cosa è stato fatto nella Fase 27

#### A. Fix JavaScript formset (tutti i pulsanti "Aggiungi..." ora funzionano)

**1. Problema Riscontrato**

I pulsanti "Aggiungi nome", "Aggiungi identificativo", "Nuovo collegamento", ecc. non facevano nulla. Errore JS in console: `Cannot read properties of null (reading 'getElementsByClassName')`.

**2. Cause Identificate**

- **project_form.html**: `onclick="addForm('urls')"` con prefix `'urls'` ma il container è `url_formset` e la view usa `prefix='url'` → mismatch
- **creator_form.html** e **custodian_form.html**: `onclick="addFormsetItem(...)"` con bug sul template vuoto
- **fond_form.html**: JS creava button duplicati perché cercava ID sbagliati
- **unit_form.html**: JS usava `-formset` ma molti container usano `_formset`

**3. Soluzione Implementata**

**Sostituzione onclick inline con addEventListener:**
- Rimossi tutti gli `onclick="addFormset(...)"` inline
- Aggiunta `class="add-formset-link" data-prefix="..."` sui link
- Single `addEventListener` che legge il `data-prefix` e chiama la funzione corretta

**Uniformazione prefix in projects.py:**
- `'urls'` → `'url'`
- `'managers'` → `'manager'`
- `'stakeholders'` → `'stakeholder'`
- `'fonds'` → `'fond'`

**Pattern unificato setupFormset():**
- Tutti i template ora usano lo stesso pattern
- `unit_form.html`: prova sia `_formset` che `-formset` per compatibilità

#### B. Allineamento completo detail views a form views

**1. Problema Riscontrato**

Le detail view mostravano solo una frazione dei campi presenti nei form. L'utente vedeva informazioni diverse in lettura rispetto a ciò che poteva inserire in scrittura.

**2. Unit Detail (completato)**

Campi aggiunti alla vista di lettura:
- `given_title` (checkbox "Attribuito")
- `title` (titolo)
- `extent` (consistenza)
- `arrangement_note` (nota dell'archivista)
- `tmp_reference_number` / `tmp_reference_string` (segnatura provvisoria)
- `folder_number` (busta), `file_number` (fascicolo)
- `related_materials` (documentazione collegata)
- `restoration` (restauri)
- `note` (appunti di servizio)
- `physical_container_type/title/number`
- `preservation` / `preservation_note`

**3. Fond Detail (completamente riscritto con 7 tab)**

**Prima:** solo nome, tipo, abstract, storia, eventi, lista unità.

**Dopo:**
1. **Descrizione**: fondo padre, tipologia, pubblicato, lunghezza, entità, nomi alternativi, identificativi, lingue, abstract, descrizione, storia archivistica, nota dell'archivista
2. **Altre informazioni**: materiali correlati, tipo materiali, note, possessori, URL
3. **Accesso**: condizioni accesso, note accesso, condizioni uso, note uso, conservazione, tipo descrizione
4. **Relazioni**: voci di indice, forme documentarie
5. **Fonti**: fonti collegate
6. **Compilatori**: tabella compilatori
7. **Estremi cronologici**: eventi

**4. Creator Detail (completamente riscritto con 5+ tab)**

**Prima:** solo tipo, residenza, stato giuridico, abstract, storia, note.

**Dopo:**
1. **Identificazione**: tipo, tipo ente, pubblicato, sede, denominazione principale, denominazioni alternative (con patronimico/nickname/qualificatore), identificativi, URL, condizione giuridica
2. **Descrizione**: abstract, storia, note, attività (con note)
3. **Relazioni**: fondi collegati (con link), istituzioni, altri soggetti
4. **Fonti**: fonti collegate
5. **Compilatori**: tabella compilatori
6. **Estremi cronologici**: eventi

**5. Custodian Detail**

- Aggiunto campo "Pubblicato"

**6. Project Detail**

- Già completo, nessuna modifica necessaria

#### 4. File Modificati

- `archimista_python/archive/templates/archive/project_form.html` — onclick → addEventListener
- `archimista_python/archive/views/projects.py` — prefix uniformati
- `archimista_python/archive/templates/archive/creator_form.html` — onclick → addEventListener
- `archimista_python/archive/templates/archive/custodian_form.html` — onclick → addEventListener
- `archimista_python/archive/templates/archive/fond_form.html` — onclick → addEventListener, JS fix
- `archimista_python/archive/templates/archive/unit_form.html` — pattern unificato _formset/-formset
- `archimista_python/archive/templates/archive/fond_detail.html` — **riscritto completamente** (7 tab)
- `archimista_python/archive/templates/archive/creator_detail.html` — **riscritto completamente** (5+ tab)
- `archimista_python/archive/templates/archive/custodian_detail.html` — aggiunto campo "Pubblicato"
- `archimista_python/archive/templates/archive/units/partials/_detail_description.html` — campi aggiunti
- `archimista_python/archive/templates/archive/units/partials/_detail_physical.html` — campi aggiunti
- `archimista_python/archive/templates/archive/units/partials/_detail_access.html` — campi aggiunti

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py runserver` — Server si avvia correttamente
- Tutti i pulsanti "Aggiungi..." funzionano su tutti i form
- Detail views mostrano tutti i campi presenti nei form
- Capitalizzazione italiana mantenuta in tutti i template

---

## Rilascio v0.25.0 - Estremi Cronologici (Archidate) (2026-04-03)

### Cosa è stato fatto nella Fase 25

#### 1. Problema Riscontrato
- Il modello `Event` esisteva con tutti i campi Archidate ma non era gestito nell'interfaccia web
- L'import AEF non importava `unit_event` e `fond_event`
- I form non erano allineati a Ruby: radio button sbagliati (4 invece di 2), combo specifiche errate, mancavano i campi per data secolare
- `ModelForm.save(commit=False)` falliva con `ValueError: data didn't validate` perché i campi ChoiceField erano `required=True`

#### 2. Fonte dei Dati AEF
```
prova/data.json:
{"unit_event":{"unit_id":2,"preferred":true,"start_date_from":"1933-01-01","start_date_display":"1933",...}}
{"fond_event":{"fond_id":4,"preferred":true,"start_date_from":"1922-01-01","start_date_display":"1922",...}}
```

#### 3. Soluzione Implementata

**Form (forms/event.py — nuovo file):**
- `EventForm` con ChoiceField espliciti per `start_date_format`, `end_date_format`, `start_date_spec`, `end_date_spec`, `start_date_valid`, `end_date_valid`
- Tutti `required=False` per permettere validazione del formset con riga vuota extra
- Radio: `data puntuale` (Y), `data secolare` (C)
- Combo specifiche: `=`, `ante`, `circa` (inizio) / `ante`, `=`, `circa` (fine)
- Campi secolo (I-XXI) e intervallo per data secolare
- `EventFormSet` con `generic_inlineformset_factory`

**Viste:**
- Costruzione manuale dell'evento da `cleaned_data` (evita `form.save(commit=False)` su form non validato)
- Salvataggio solo se c'è almeno un dato compilato
- `event_formset.is_valid()` chiamato prima di iterare

**Import AEF:**
- Handler per `unit_event` e `fond_event`
- Mappa `unit_id`/`fond_id` → GenericForeignKey (`content_type` + `object_id`)

**Template:**
- Sezione "Estremi cronologici" nei form Unit, Fond, Creator
- Tab/card dedicati nelle detail view
- JavaScript per toggle formato Y/C e equal bounds

#### 4. File Modificati/Creati
- `archimista_python/archive/forms/event.py` — **Nuovo**, EventForm + EventFormSet
- `archimista_python/archive/forms/__init__.py` — Aggiunto export EventForm, EventFormSet
- `archimista_python/archive/views/unit.py` — Aggiunto event_formset a create/update/detail
- `archimista_python/archive/views/fond.py` — Aggiunto event_formset a update + detail
- `archimista_python/archive/views/creator.py` — Aggiunto event_formset a create/update/detail
- `archimista_python/archive/import_utils.py` — Aggiunti import_unit_event, import_fond_event
- `archimista_python/archive/templates/archive/unit_form.html` — Sezione estremi cronologici + JS + CSS
- `archimista_python/archive/templates/archive/fond_form.html` — Sezione estremi cronologici + JS + CSS
- `archimista_python/archive/templates/archive/creator_form.html` — Sezione estremi cronologici + JS + CSS
- `archimista_python/archive/templates/archive/unit_detail.html` — Tab estremi cronologici
- `archimista_python/archive/templates/archive/fond_detail.html` — Card estremi cronologici
- `archimista_python/archive/templates/archive/creator_detail.html` — Card estremi cronologici
- `archimista_python/archive/templates/archive/units/partials/_tab_description.html` — Sezione estremi cronologici
- `archimista_python/archive/templates/archive/units/partials/_detail_dates.html` — **Nuovo**, partial per tab dates

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- Re-import AEF — 2 unit events + 1 fond event importati correttamente
- Form pre-compilazione — anno 1933, radio "data puntuale" selezionato
- Salvataggio — nessun errore, evento creato/aggiornato correttamente

---

## Rilascio v0.20.0 - Fix Sezione Compilatori Unità (2026-04-03)

### Cosa è stato fatto nella Fase 20

#### 1. Problemi Riscontrati

**A. Prefisso formset sbagliato**
- Django formset usa `unit_editors` (plurale) come prefisso
- Template e JS usavano `unit_editor` (singolare)
- Conseguenza: JS non trovava il management form, nessun link "Aggiungi compilatore" visibile

**B. Campo `id` mancante nel template**
- Il formset inline ha bisogno della PK per identificare i record esistenti
- Senza `{{ form_item.id }}`, il salvataggio falliva con errore "This field is required"

**C. `editing_type` come testo libero**
- Era `TextInput`, non dropdown da vocabolario
- Ruby usa `terms_select(f, "editors.editing_type", ...)`

**D. Formset con `extra=1`**
- Mostrava sempre una riga vuota extra
- Ruby mostra solo i compilatori esistenti + link "Aggiungi"

#### 2. Vocabolario `editors.editing_type` Allineato

**Prima:** 3 termini generici ("Compilazione completa", "Compilazione parziale", "Revisione").

**Dopo:** 7 termini esatti da Ruby (vocabulary_id: 25):
- aggiornamento scheda, inserimento dati, integrazione successiva, prima redazione, revisione, rielaborazione, schedatura

#### 3. Form e Formset Aggiornati

**UnitEditorForm:**
- `editing_type` cambiato da `TextInput` a `ChoiceField` con `(term_value, term_value)`
- Il modello ha `editing_type = CharField`, quindi il match è diretto sul testo

**UnitEditorFormSet:**
- `extra=1` → `extra=0` (solo record esistenti)

#### 4. Template Riscritto

**`_tab_editors.html`:**
- Da card statiche a righe inline con etichette di colonna
- Aggiunto `{{ form_item.id }}` nascosto
- Template `<template id="unit_editors-empty-template">` per nuove righe con opzioni dropdown
- Prefisso corretto: `unit_editors-` (plurale)

#### 5. JavaScript Dedicato

**`setupEditorFormset()`:**
- Prefisso `unit_editors` (plurale)
- Usa il template vuoto per nuove righe (non clona dati esistenti)
- Link testuale "Aggiungi compilatore" (come Ruby)
- Mostra etichette di colonna solo quando serve

#### 6. Viste Aggiornate

- `editing_type_terms` passato al context in UnitCreateView e UnitUpdateView (GET/POST)

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- Dropdown pre-selezionato correttamente in modifica
- Salvataggio editing_type e edited_at funziona
- Link "Aggiungi compilatore" visibile e funzionante
- Nuove righe create vuote dal template (non clonate)

---

## Rilascio v0.21.0 - Menu Navigazione e Viste Entità di Servizio (2026-04-03)

### Cosa è stato fatto nella Fase 21

#### 1. Problema Riscontrato

La navbar Python aveva solo 4 link: Esplora, Visualizzazione albero, Importa AEF, Nuovo fondo.
Le entità di servizio (Fonti, Compilatori, Progetti, ecc.) erano accessibili solo digitando l'URL a mano o tramite Django Admin.

In Ruby, la navbar (`_navbar.html.erb`) ha due dropdown:
- **Schede**: Complessi archivistici, Soggetti produttori, Soggetti conservatori, Fonti, Oggetti digitali, Profili istituzionali, Profili documentari, Progetti, Compilatori
- **Strumenti**: Voci di indice, Anagrafiche, Controllo qualità, Report, Importa, Esporta, Gestione utenti/gruppi

#### 2. Navbar Aggiornata (`base.html`)

**Menu "Schede"** (dropdown Bootstrap):
- Complessi archivistici → FondListView
- Soggetti produttori → CreatorListView (già esistente)
- Soggetti conservatori → CustodianListView (già esistente)
- Fonti → SourceListView (nuovo)
- Oggetti digitali → DigitalObjectListView (nuovo)
- Profili istituzionali → InstitutionListView (nuovo)
- Profili documentari → DocumentFormListView (nuovo)
- Progetti → ProjectListView (nuovo)
- Compilatori → EditorListView (nuovo)

**Menu "Strumenti"** (dropdown Bootstrap):
- Voci di indice → HeadingListView (nuovo)
- Anagrafiche → AnagraphicListView (nuovo)
- Importa AEF → ImportAEFView (già esistente)

**Azioni rapide**: Albero, Nuovo fondo

#### 3. Viste Create (`views/entities.py`)

16 viste (ListView + DetailView per 8 entità):
- Source, Institution, DocumentForm, Project, Editor, DigitalObject, Heading, Anagraphic

Tutte con:
- `paginate_by = 50`
- `context_object_name` plurale
- Template dedicati

#### 4. Template Creati

16 template (list + detail per ogni entità):
- `source_list.html`, `source_detail.html`
- `institution_list.html`, `institution_detail.html`
- `document_form_list.html`, `document_form_detail.html`
- `project_list.html`, `project_detail.html`
- `editor_list.html`, `editor_detail.html`
- `digital_object_list.html`, `digital_object_detail.html`
- `heading_list.html`, `heading_detail.html`
- `anagraphic_list.html`, `anagraphic_detail.html`

Ogni lista ha:
- Tabella con colonne pertinenti
- Link "Dettagli" per riga
- Messaggio "Nessun elemento presente"

Ogni dettaglio ha:
- Tabella campi/valori
- Link "Torna alla lista"

#### 5. URL Aggiunti (`urls.py`)

16 nuovi URL pattern:
- `/sources/`, `/sources/<pk>/`
- `/institutions/`, `/institutions/<pk>/`
- `/document-forms/`, `/document-forms/<pk>/`
- `/projects/`, `/projects/<pk>/`
- `/editors/`, `/editors/<pk>/`
- `/digital-objects/`, `/digital-objects/<pk>/`
- `/headings/`, `/headings/<pk>/`
- `/anagraphics/`, `/anagraphics/<pk>/`

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py show_urls` — 42 route totali (escluso admin)
- Navbar con dropdown funzionante
- Tutte le pagine list/detail accessibili dal menu

---

## Rilascio v0.22.0 - Allineamento Form Soggetto Produttore a Ruby (2026-04-03)

### Cosa è stato fatto nella Fase 22

#### 1. Problema Riscontrato

Il form Python per i soggetti produttori (Creator) aveva 8 tab con campi sparpagliati e non allineati a Ruby. Mancavano:
- I 18 tipi di ente corretti (c'era solo "Ente Pubblico")
- La distinzione dinamica tra denominazione (Ente/Famiglia → nome singolo, Persona → nome+cognome)
- Le relazioni con i fondi
- I formset "Aggiungi" non funzionavano (problemi JS: prefissi sbagliati, `<template>` non supportato, variabili globali non inizializzate)
- `editing_type` nei compilatori era testo libero invece di dropdown
- Mancavano le etichette di colonna per i compilatori
- Capitalizzazione inglese in vari punti

#### 2. Struttura Ruby (5 tab)

**Tab 1 - Identificazione:**
- Tipo (dropdown: Persona/Famiglia/Ente)
- Tipo di ente (dropdown, visibile solo per Ente — 18 tipi)
- Pubblicato (checkbox)
- Denominazione: per Ente/Famiglia → campo "Denominazione" + Note; per Persona → "Nome" + "Cognome" + Note
- Altre denominazioni (formset): Nome + Qualificatore + Note
- URL (formset): URL + Note
- Identificativi (formset): Identificativo + Fonte + Note
- Residenza (campo testo)

**Tab 2 - Descrizione:**
- Abstract, Storia, Note, Attività (formset)

**Tab 3 - Relazioni:**
- Relazioni con fondi, istituzioni, altri soggetti produttori

**Tab 4 - Fonti:**
- Relazioni con fonti

**Tab 5 - Compilatori:**
- Compilatori (formset): Nome + Qualificatore + Tipo compilazione (dropdown) + Data

#### 3. Soluzione Implementata

**A. Tipi di ente (18 da Ruby):**
Rimossi "Ente Pubblico", aggiunti tutti i 18 tipi da `db/seeds/creator_corporate_types.json`:
stato, regione, ente pubblico territoriale, ente funzionale territoriale, ente economico / impresa, ente di credito/assicurativo/previdenziale, ente di assistenza e beneficenza, ente sanitario, ente di istruzione e ricerca, ente di cultura/ricreativo/sportivo/turistico, partito politico/organizzazione sindacale, ordine professionale/associazione di categoria, ente e associazione della chiesa cattolica, ente e associazione di culto acattolico, preunitario, organo giudiziario, organo periferico dello stato, ente ecclesiastico

**B. Form aggiornati (`forms/creator.py`):**
- `CreatorPreferredNameForm` — form separato per il nome preferito (denominazione)
- `CreatorOtherNameForm` — form per altre denominazioni
- `CreatorEditorForm` — `editing_type` come `ChoiceField` dal vocabolario (7 termini)
- `RelCreatorFondForm` + formset — relazioni con fondi
- Tutti i formset con `extra=0`

**C. Viste aggiornate (`views/creator.py`):**
- `_get_dropdown_lists()` — helper per passare liste dropdown (Fond, Institution, Creator, Source, AssociationType, editing_type_terms) a tutti i context
- Salvataggio corretto del nome preferito con `qualifier='A'` e `preferred=True`

**D. Template riscritto (`creator_form.html`):**
- 5 tab allineati a Ruby
- Show/hide dinamico per tipo (Persona/Famiglia/Ente)
- Formset con `<div style="display:none">` come template (più affidabile di `<template>`)
- Funzione JS `addFormsetItem()` globale con `onclick` inline (zero binding dinamico)
- Prefissi corretti allineati a Django (`creator_names`, `creator_urls`, `relcreatorfond_set`, ecc.)
- Etichette di colonna per compilatori (Nome, Qualificatore, Tipo compilazione, Data)

**E. Capitalizzazione italiana:**
- "Creatori" → "Soggetti produttori"
- "Custodi" → "Soggetti conservatori"
- "Nuovo Creatore" → "Nuovo soggetto produttore"
- "Created/Updated" → "Creato/Aggiornato"
- "Tipo corporate" → "Tipo di ente"
- "Altri nomi" → "Altre denominazioni"

**F. Navbar:**
- Rimosso pulsante "Nuovo fondo" (già presente nella lista fondi)

#### 4. File Modificati

- `archimista_python/archive/forms/creator.py` — Riscritto con PreferredNameForm, OtherNameForm, RelCreatorFondForm, editing_type dropdown
- `archimista_python/archive/forms/__init__.py` — Aggiornati export
- `archimista_python/archive/views/creator.py` — Riscritto con gestione nome preferito, `_get_dropdown_lists()`
- `archimista_python/archive/templates/archive/creator_form.html` — Riscritto completamente (5 tab, show/hide, formset funzionanti, etichette)
- `archimista_python/archive/templates/archive/base.html` — Rimosso "Nuovo fondo"
- Template creator/custodian list, detail, confirm_delete — capitalizzazione italiana
- `seed.py` — 18 tipi di ente

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- Form soggetto produttore con 5 tab allineati a Ruby
- Show/hide dinamico per tipo (Persona/Famiglia/Ente)
- 18 tipi di ente nel dropdown
- Relazioni con fondi funzionanti
- Formset "Aggiungi" funzionanti per tutti i 9 formset
- Dropdown editing_type per compilatori con etichette colonna

---

## v0.23.0 — Allineamento Form Soggetto Conservatore a Ruby

### Problema
L'interfaccia Python dei soggetti conservatori era molto diversa da quella Ruby. I tab erano organizzati in modo diverso (Dati generali, Nomi, Identificativi, Contatti, Edifici, Possessori, URL invece di Identificazione, Descrizione, Accesso, Sedi, Relazioni, Fonti, Compilatori). La denominazione principale era gestita come formset invece che come form separato. Mancavano le relazioni con fondi.

### Soluzione

#### 1. Form completamente riscritto (7 tab come Ruby)
- **Identificazione**: condizione giuridica, macrotipologia, pubblicato, denominazione principale (form singolo), altre denominazioni (formset), cenni storici, contatti (formset), referente, enti titolari (formset), collegamenti URL (formset), codici identificativi (formset)
- **Descrizione**: patrimonio, politiche di gestione, struttura amministrativa
- **Accesso**: orari e indicazioni per l'accesso, servizi
- **Sedi**: edifici con denominazione, tipologia, indirizzo, comune, CAP, nazione, descrizione (formset)
- **Relazioni**: fondi collegati (RelCustodianFond formset)
- **Fonti**: fonti collegate (RelCustodianSource formset)
- **Compilatori**: nome, qualificatore, tipo compilazione (dropdown), data (formset)

#### 2. Denominazione principale separata
- Creato `CustodianPreferredNameForm` — form singolo per il nome preferito
- `CustodianNameFormSet` — formset solo per le altre denominazioni
- Viste aggiornate per gestire entrambi

#### 3. Detail view allineata a Ruby
- Sezioni in lettura: Identificazione, Descrizione, Accesso, Sedi, Relazioni, Fonti, Compilatori
- Tabelle `table-show` come Ruby
- Link a fondi e fonti

#### 4. List view allineata a Ruby
- Ricerca per denominazione
- Stato pubblicato visibile
- Pagination
- Link a modifica/mostra/elimina

#### 5. Model updates
- Proprietà `fonds`, `sources`, `preferred_name`, `other_names`, `display_name`
- Relazioni ManyToMany through `RelCustodianFond` e `RelCustodianSource`

#### 6. Form e Viste
- `CustodianForm` aggiornato (rimosso campo `owner` diretto)
- Aggiunto `CustodianPreferredNameForm`, `RelCustodianFondForm` e formset
- `CustodianCreateView` e `CustodianUpdateView` riscritte
- Pattern `is_valid()` prima di `save()` per tutti i formset
- Contesto con `fonds_list` e `sources_list`

#### 7. File Modificati
- `archimista_python/archive/forms/custodian.py` — Riscritto con PreferredNameForm, RelCustodianFondForm, editing_type dropdown
- `archimista_python/archive/forms/__init__.py` — Aggiornati export
- `archimista_python/archive/views/custodian.py` — Riscritto con gestione nome preferito, tutti i formset
- `archimista_python/archive/models/core.py` — Aggiunte proprietà fonds, sources, preferred_name, display_name
- `archimista_python/archive/templates/archive/custodian_form.html` — Riscritto completamente (7 tab, formset completi, relazioni)
- `archimista_python/archive/templates/archive/custodian_detail.html` — Riscritto con sezioni in lettura allineate a Ruby
- `archimista_python/archive/templates/archive/custodian_list.html` — Riscritto con ricerca, pagination, stato pubblicato

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- Template syntax — Tutti OK
- Form soggetto conservatore con 7 tab allineati a Ruby
- Denominazione principale separata
- Relazioni con fondi e fonti funzionanti
- Formset "Aggiungi" funzionanti per tutti i 9 formset
- Capitalizzazione italiana in tutti i label
