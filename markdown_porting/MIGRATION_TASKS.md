# Checklist dei task: Riscrittura di Archimista (Django)

## ✅ COMPLETATO - v0.50.0 (2026-04-07)

Suite test estesa a 242 test (+140 nuovi), 17 moduli in `tests/`. Copertura: CRUD completi, viste, proprietà modelli, validazione form, import AEF reale, export content validation, auth, middleware, seed scripts. 4 bug Python scoperti e corretti.

### Nuovi moduli di test
- [x] `test_digital_objects.py` — 20 test: CRUD DigitalObject (upload file, validazione, nested, model methods)
- [x] `test_service_entities_complete.py` — 22 test: CRUD update/delete per Source, Project, Institution, Heading, Anagraphic, Editor, Classification, DocumentForm
- [x] `test_model_properties.py` — 22 test: Fond (subtree, root, descendants), Unit (full_path, is_movable_up/down), Creator/Custodian (preferred_name, sources), Event, Classification
- [x] `test_form_validation.py` — 18 test: validazione Fond, Unit, Creator, Custodian, DigitalObject, Source, Project, Heading, Anagraphic, Classification, Institution
- [x] `test_search.py` — 8 test: ricerca globale e avanzata con dati reali
- [x] `test_quality_checks.py` — 12 test: QC con dati completi e incompleti
- [x] `test_import_export_auth.py` — 15 test: import AEF reale, export content validation, auth, middleware, tree/unit views
- [x] `test_seed_scripts.py` — 8 test: seed scripts, vocabolari, admin user

### Bug fix Python v0.50.0
- [x] **Fond.subtree**: property mancante → aggiunta in `models/core.py`
- [x] **Fond.root**: property mancante → aggiunta con prevenzione loop
- [x] **Unit.full_path()**: metodo mancante → aggiunto in `models/core.py`
- [x] **Classification.is_root**: property mancante → aggiunta in `models/core.py`

### Risultati
- `python manage.py check` — Nessun errore
- `python test_complete.py` — **242/242 test passati** (prima 102/102)

## ✅ COMPLETATO - v0.49.0 (2026-04-07)

Test suite riorganizzata in `tests/` directory modulare (11 file). 102/102 test passati. 6 bug scoperti e corretti.

### Bug fix v0.49.0
- [x] **HeadingForm**: `AttributeError` su `heading_type_term` → sincronizzazione corretta con `heading_type`
- [x] **AnagraphicCreateView**: formset validato prima del save → ordine invertito
- [x] **DocumentFormDeleteView**: `NoReverseMatch` → aggiunto `context_object_name`
- [x] **QualityCheckFondView**: 4 related name errati → nomi corretti
- [x] **Creator.sources**: `NameError` → import locale di `Source`
- [x] **Test suite**: DB `:memory:` instabile → file SQLite dedicato con cleanup

## ✅ COMPLETATO - v0.48.0 (2026-04-07)

Tutti i task principali sono stati completati. Fix titolario, FontAwesome, pulsanti uniformi in tutte le liste e detail view.

## Fase 1: Inizializzazione (COMPLETATA)
- [x] Creazione directory del progetto (`archimista_python`)
- [x] Setup Ambiente Virtuale (`venv`) e installazione Django
- [x] Inizializzazione progetto e app `archive`
- [x] Traduzione modelli core: Group, Fond, Unit, Creator, Custodian

## Fase 2: Modelli Avanzati e Relazioni (COMPLETATA)
- [x] Implementazione polimorfismo per `DigitalObject` (GenericForeignKey)
- [x] Creazione modelli `Heading` (Voci di Indice) e relativi test in `seed.py`
- [x] Implementazione tabelle di relazione (RelCreatorFond, RelFondHeading, ecc.)
- [x] Registrazione in Django Admin con Inlines

## Fase 3: UI CRUD e Navigazione (COMPLETATA)
- [x] Aggiunta campi `parent` per la gestione gerarchica nativa in Django
- [x] Creazione di `forms.py` per Fondi e Unità
- [x] Sviluppo viste CRUD lato utente per Fondi e Unità
- [x] Creazione template HTML moderni (Bootstrap 5)
- [x] Aggiunta modelli `Institution` e `Source`

## Fase 4: Biografie, Eventi e Classificazione (COMPLETATA)
- [x] Implementazione dei restanti modelli archivistici (Biografie, Eventi, Schemi di classificazione).
- [x] Implementazione dello schema di Classificazione (Titolario) e navigazione ad albero avanzata.

## Fase 5: UI Standalone e Schede Specialistiche (COMPLETATA)
- [x] Implementazione Navigazione ad Albero Dinamica (`jstree`)
- [x] Aggiunta campi Iccd/Sc2 (Mappe e Beni Culturali)
- [x] Vista di dettaglio Unità con metadati specialistici

## Fase 41: Controllo qualità (✅ COMPLETATA - v0.43.0)
- [x] **QualityCheckIndexView**: lista fondi root, creatori, conservatori con ricerca
- [x] **QualityCheckFondView**: 11 controlli per fondo (denominazione, datazione, tipologia, descrizione, storia, consistenza, unità, creatori, conservatori, progetti, fonti)
- [x] **QualityCheckCreatorView**: 6 controlli per soggetto produttore (tipologia, tipologia ente, denominazione, datazione, biografia, fonti)
- [x] **QualityCheckCustodianView**: 3 controlli per soggetto conservatore (denominazione, macrotipologia, sedi)
- [x] **Modelli**: aggiunti `preferred_event` a Fond/Creator/Custodian, `active_descendant_units_count` a Fond, `preferred_name` e `sources` a Creator
- [x] **Event model**: aggiunti `full_display_date` e `full_display_date_with_place`
- [x] **Template**: 5 template (index, fond, fond_table, creator, custodian)
- [x] **Menu**: voce "Controllo qualità" aggiunta nel menu Strumenti
- [x] **Test**: 5/5 view test passati (index, fond, fond complete, creator, custodian)

## Fase 6: Ricerca e Reportistica (COMPLETATA)
- [x] Motore di ricerca globale (GlobalSearchView)
- [x] Generazione Inventari Archivistici (PDF/RTF via export_utils.py)

## Fase 48: Fix titolario, FontAwesome, pulsanti uniformi (✅ COMPLETATA - v0.48.0)
- [x] **Fix titolario**: `tree_data` serializzato con `json.dumps()` (era Python list → JS invalido)
- [x] **FontAwesome CDN**: aggiunto in `base.html` (tutte le icone `fas fa-*` ora visibili)
- [x] **Pulsanti liste (10 template)**: `btn-group btn-group-sm` con icone invece di testo
  - heading_list, editor_list, project_list, institution_list, anagraphic_list, document_form_list, source_list, digital_object_list, digital_object_nested_list, generic_list
- [x] **Pulsanti detail (6 template)**: da emoji a icona + label responsive
  - fond_detail, unit_detail, creator_detail, custodian_detail, project_detail, source_detail
- [x] **Source list**: aggiunti pulsanti Dettaglio e Modifica (prima solo Elimina)

## Fase 47: Autocomplete, Refactor, Setup, Test completo (✅ COMPLETATA - v0.47.0)
- [x] **Select2 per FK principali**: Unit.fond, Unit.parent, Unit.classification, Fond.parent, Classification.parent
- [x] **Nuovi widget**: UnitSelect2Widget, ClassificationSelect2Widget, LangSelect2Widget
- [x] **Lang Select2**: FondLangForm.code, UnitLangForm.code (da TextInput a Select2)
- [x] **Refactor fond_form.html**: 825 → 232 righe (-72%), 6 partial in `fonds/partials/`
- [x] **Refactor creator_form.html**: 730 → 220 righe (-70%), 5 partial in `creators/partials/`
- [x] **Refactor custodian_form.html**: 594 → 147 righe (-75%), 7 partial in `custodians/partials/`
- [x] **README.md**: licenza GPL v2, credits, guida installazione, troubleshooting
- [x] **setup.sh**: script eseguibile con 5 passi (migrate, vocabularies, source_types, seed, admin)
- [x] **seed_admin_user.py**: reset password se utente esiste già
- [x] **test_complete.py**: 67 test — import, URL, widget, form, template, CRUD, viste funzionali, auth
- [x] **Pulizia test vecchi**: eliminati 7 script ridondanti
- [x] **Bug fix**: `Custodian.sources` NameError (import Source mancante)

## Fase 44: Export PDF/RTF completo (✅ COMPLETATA - v0.46.0)
- [x] **report_support.py** — porting di `lib/report_support.rb` (~1530 righe)
  - [x] `AttributeInfo`, `EntityReportSettings`, `ReportSettings`
  - [x] `fond_available_attributes_info()` — 29 campi Fond
  - [x] `unit_available_attributes_info()` — 49 campi Unit (incluse schede SC2/ICCD/FSC/FE)
  - [x] `creator_available_attributes_info()` — 18 campi Creator
  - [x] `custodian_available_attributes_info()` — 32 campi Custodian
  - [x] `project_available_attributes_info()` — 10 campi Project
  - [x] `make_html()` — genera HTML per PDF via WeasyPrint
  - [x] `make_rtf()` — genera RTF per file .rtf
  - [x] 30+ callback: events, sources, editors, creators, custodians, progetti, SC2, ICCD, FSC, FE, ecc.
- [x] **rtf_writer.py** — porting di `app/models/rtfwriter.rb` (~520 righe)
- [x] **rtf_builder.py** — porting di `app/models/rtf_builder.rb` (~500 righe)
- [x] **views/reports.py** — viste con PDF (WeasyPrint) + RTF (RtfBuilder)
- [x] **Template** — `inventory_report.html`, `project_report.html`, `custodian_report.html`
- [x] **Fix** — 24 related_name in relations.py, proprietà su Fond/Creator, Unit methods
- [x] **Migrazione** — 0025_relcreatorfond (24 FK con related_name)
- [x] **Test** — tutti verificati

## Fase 43: Autenticazione singolo utente (✅ COMPLETATA - v0.45.0)
- [x] **UserProfile model** con `must_change_password` flag
- [x] **LoginRequiredMiddleware** — tutte le pagine richiedono autenticazione
- [x] **ArchimistaLoginView** — login con template italiano, redirect forzato a password-change
- [x] **password_change_view** — cambio password con `PasswordChangeForm` Django
- [x] **archimista_logout** — logout con redirect a login
- [x] **Template**: `login.html`, `password_change.html`
- [x] **base.html** — dropdown utente con nome, "Cambia password", "Esci"
- [x] **Seed script**: `seed_admin_user.py` — crea admin con password casuale e `must_change_password=True`
- [x] **Settings**: `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` configurati
- [x] **Test**: 8/8 passati — redirect anonimi, login, errore password, cambio password, logout
- [ ] Implementazione multi-utente con permessi per gruppo (opzionale, futuro)
- [ ] Mapping avanzato campi ICCD

## Fase 34: Titolario di Classificazione UI (COMPLETATA - v0.34.0)
- [x] **Form Classification**: ClassificationForm con codice, denominazione, descrizione, classe padre
- [x] **Prevenzione riferimenti circolari**: esclusione self e discendenti dal dropdown padre
- [x] **Viste CRUD**: ClassificationListView, ClassificationDetailView, ClassificationCreateView, ClassificationUpdateView, ClassificationDeleteView
- [x] **Viste aggiuntive**: ClassificationTreeDataView (API JSON), ClassificationUnitsView (lista unità)
- [x] **Template**: classification_list.html, classification_detail.html, classification_form.html, classification_confirm_delete.html, classification_units.html
- [x] **URL**: 7 URL configurate (/classifications/, /classifications/new/, /classifications/<pk>/, ecc.)
- [x] **Assegnazione a Unità**: campo classification aggiunto al form unità (sezione Contesto)
- [x] **Visualizzazione in Unit detail**: riga classificazione con link
- [x] **Menu navigazione**: voce "Titolario" aggiunta nel menu Strumenti
- [x] **Test**: 4 classificazioni gerarchiche create e verificate

## Fase 35: Albero Interattivo e Classificazione di Massa (COMPLETATA - v0.35.0)
- [x] **Tree Manipulation API**: 7 nuovi endpoint (create, rename, move, trash, restore, trash view, trashed children API)
- [x] **Albero interattivo**: pulsanti +/−, rinomina con doppio click, drag & drop (plugin jsTree `dnd`)
- [x] **Prevenzione riferimenti circolari**: non si può spostare un nodo sotto un suo discendente
- [x] **Cestino**: pagina dedicata con lista nodi eliminati e pulsante ripristino
- [x] **Proprietà Fond aggiuntive**: root, is_root, descendants, subtree_ids
- [x] **Classificazione di massa**: checkbox unità nel fond_detail + pulsante "Classifica selezionate"
- [x] **Modale con albero**: jsTree sola lettura per selezione fondo destinazione
- [x] **API units_classify**: PUT /units/classify/ con record_ids + new_fond_id
- [x] **Test**: creazione nodo, rinomina, classificazione — tutti verificati

## Fase 36: Fix Formset, Gerarchia Unità, Lista Unità Globale e UX Albero (COMPLETATA - v0.36.0)
- [x] **Fix formset inline vuoti**: sostituito `fs.is_valid(); fs.save()` con controllo esplicito per ogni form (salva solo se c'è almeno un campo compilato) — unit.py (6 loop), creator.py (2 loop)
- [x] **Fix UnitDeleteView**: aggiunto namespace `archive:` e fallback a `fond_list` se `fond_id` è None
- [x] **Gerarchia unità "Modifica livello"**: 3 nuovi endpoint (move, move_up, move_down), modello Unit con metodi is_movable_up/down, template unit_move.html
- [x] **Albero: distinzione fondi vs unità**: azioni +/−/rinomina/dnd disabilitate su unità con messaggi informativi
- [x] **Classificazione: albero soli fondi**: nuovo endpoint `tree_children_fonds_only`, modale usa solo fondi/serie (allineato a Ruby)
- [x] **Lista unità globale**: UnitListView con paginazione, filtro per fondo, ricerca, alert unità orfane
- [x] **UX dettaglio fondo**: sezione "Serie e sottofondi" con link e conteggio unità
- [x] **UX albero**: tema jsTree da "apple" a "default" con frecce di espansione visibili
- [x] **Creazione serie**: pulsante "Aggiungi serie" nel fond_detail, FondCreateView pre-compila parent_id da URL

## Fase 8: Modelli Completi e Importazione Dati (COMPLETATA)
- [x] **Modelli Estensione Fond**: FondName, FondIdentifier, FondLang, FondOwner, FondUrl, FondEditor
- [x] **Modelli Estensione Unit**: UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage, UnitUrl, UnitEditor
- [x] **Modelli Estensione Creator**: CreatorName, CreatorLegalStatus, CreatorUrl, CreatorIdentifier, CreatorActivity, CreatorEditor
- [x] **Modelli Estensione Custodian**: CustodianName, CustodianIdentifier, CustodianContact, CustodianBuilding, CustodianOwner, CustodianUrl, CustodianEditor
- [x] **Schede SC2 Complete**: Sc2TextualElement, Sc2VisualElement, Sc2Author, Sc2Commission, Sc2CommissionName, Sc2Technique, Sc2Scale
- [x] **Schede ICCD Complete**: IccdSubject, IccdDamage, IccdTechSpec
- [x] **FSC (Fascicoli Sanitari Edilizia)**: FscCode, FscOrganization, FscNationality, FscOpen, FscClose
- [x] **FE (Fabbricati Edilizia)**: FeIdentification, FeContext, FeOpera, FeDesigner, FeCadastral, FeLandParcel, FeFractLandParcel, FeFractEdilParcel
- [x] **Modelli Relazionali**: RelCreatorCreator, RelCreatorInstitution, RelCreatorSource, RelCustodianSource, RelFondSource, RelUnitSource, RelFondDocumentForm, RelProjectFond, RelUnitAnagraphic
- [x] **Altri Modelli**: Project, DocumentForm, Anagraphic, Place, Lang, Term, Vocabulary, Export, Import, Editor, Activity, DocumentFormEditor, AnagIdentifier, CreatorAssociationType
- [x] **Migrazioni**: Creato e applicato migration per tutti i nuovi modelli
- [x] **Admin**: Registrati tutti i modelli in Django Admin con inlines appropriati
- [x] **Import Utils**: Aggiornato AEFImporter per gestire tutti i nuovi modelli
- [x] **Forms**: Creati tutti i form per le schede specialistiche
- [x] **Viste**: UnitUpdateView completa con tutte le schede
- [x] **Template**: unit_form.html con tab per tutte le schede
- [x] **Fond UpdateView**: Implementata con tutti i formset per estensioni
- [x] **Creator CRUD**: Viste complete con formset per tutte le estensioni
- [x] **Custodian CRUD**: Viste complete con formset per tutte le estensioni

## Fase 9: Standardizzazione con Vocabolari Controllati (COMPLETATA - v0.11.0)
- [x] **Popolare Vocabulary e Term**: 77 termini standardizzati in 11 vocabolari
- [x] **Aggiornare Modelli**: FK verso `Term` per campi standardizzati
- [x] **Aggiornare Form**: `ModelChoiceField` con widget Select
- [x] **Migrazioni**: Create e applicate migrazioni 0010 e 0011

## Fase 10: Refactor in Moduli (COMPLETATA - v0.12.0)
- [x] **Creare directory models/**: 10 moduli separati
- [x] **Compatibilità**: __init__.py espone tutti i modelli
- [x] **Verifica**: `python manage.py check` passa senza errori

## Fase 11: Allineamento Interfaccia a Archimista Ruby (COMPLETATA - v0.13.0)

### A. Riorganizzazione Form Unità ✅ COMPLETATA

**Sezioni implementate:**

1. **Descrizione** ✅
   - [x] Titolo, Contenuto, Contesto (Fondo, Unità Padre)
   - [x] Identificazione (Tipo unità, Segnatura)
   - [x] Identificativi alternativi (formset inline `UnitIdentifier`)
   - [x] Altre segnature (formset inline `UnitOtherReferenceNumber`)
   - [x] Lingue (formset inline `UnitLang`)

2. **Descrizione fisica** ✅
   - [x] Tipo supporto, Descrizione fisica, Stato conservazione
   - [x] Danni (formset inline `UnitDamage`)

3. **Accesso** ✅
   - [x] Condizione accesso/uso (dropdown da vocabolario)
   - [x] Nota accesso/uso (textarea)

4. **Fonti** ✅
   - [x] RelUnitSource, RelUnitHeading, RelUnitAnagraphic (formset inline)

5. **Compilatori** ✅
   - [x] UnitEditor formset inline

6. **Schede Speciali** ✅
   - [x] SC2, ICCD, FSC, FE (già esistenti)

### B. Riorganizzazione Form Fondi ✅ COMPLETATA

**Sezioni implementate:**

1. **Descrizione** ✅
   - [x] Nome fondo, Tipologia, Estensione, Abstract, Descrizione, Storia
   - [x] Nomi alternativi, Identificativi, Lingue (formset inline)

2. **Altre informazioni** ✅
   - [x] Materiali correlati, Tipo materiali, Note
   - [x] Possessori, URL (formset inline)

3. **Accesso** ✅
   - [x] Condizioni accesso/uso/conservazione (dropdown)
   - [x] Tipo descrizione (dropdown)

4. **Relazioni** ✅
   - [x] Voci di indice, Forme documentarie (formset inline)

5. **Fonti** ✅
   - [x] Fonti (formset inline `RelFondSource`)

6. **Compilatori** ✅
   - [x] Curatori (formset inline `FondEditor`)

### C. Viste di Dettaglio ✅ COMPLETATE (v0.18.0, v0.27.0)

- [x] Unit Detail View con tutte le sezioni in lettura (v0.18.0)
- [x] Fond Detail View con tutte le sezioni in lettura (v0.27.0)
- [x] Breadcrumb di navigazione migliorato
- [x] Link "Modifica" per ogni sezione
- [ ] Storico modifiche e log compilatori — **ANCORA DA FARE**

### D. Formset Inline ✅ COMPLETATI

**Per Unità:**
- [x] UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage, UnitUrl, UnitEditor
- [x] RelUnitSource, RelUnitHeading, RelUnitAnagraphic

**Per Fondi:**
- [x] FondName, FondIdentifier, FondLang, FondOwner, FondUrl, FondEditor
- [x] RelFondSource, RelFondHeading, RelFondDocumentForm

**Per Creator e Custodian:**
- [x] Tutti i formset già esistenti (v0.10.0)

### E. JavaScript e UI Dinamica ✅ COMPLETATA

- [x] Funzione generica `setupFormset()` per tutti i formset
- [x] Pulsanti "Aggiungi" per ogni formset inline
- [x] Clonazione corretta delle righe con aggiornamento indici
- [x] Aggiornamento automatico `TOTAL_FORMS`
- [x] Autocomplete per ForeignKey (select2) — ✅ COMPLETATO v0.33.0
- [ ] Validazione lato client - DA FARE

### F. Template Riscritti ✅ COMPLETATI

- [x] `unit_form.html` - 6 tab (Descrizione, Descrizione Fisica, Accesso, Fonti, Compilatori, Schede Speciali)
- [x] `fond_form.html` - 6 tab (Descrizione, Altre Informazioni, Accesso, Relazioni, Fonti, Compilatori)
- [x] `unit_detail.html` - ✅ Aggiornato v0.18.0 (tutte le schede in lettura)
- [x] `fond_detail.html` - ✅ Aggiornato v0.27.0 (7 tab completi)

---

## Fase 13: Show/Hide Dinamico Campi SC2/FSC/FE (COMPLETATA - v0.15.0)

### A. Logica Show/Hide (identica a Ruby units-sc.js) ✅ COMPLETATA

**Livello 1 - unit_type:**
- [x] "unità documentaria" → mostra sc2_tsk, nascondi file_type
- [x] "fascicolo o altra unità complessa" → mostra file_type, nascondi sc2_tsk
- [x] altro → nascondi entrambi

**Livello 2a - sc2_tsk (Scheda Speciale):**
- [x] Vuoto → mostra physical_type, nascondi SC2
- [x] "CARS" → mostra sc2_all + sc2_cars
- [x] "D" → mostra sc2_all + sc2_d
- [x] "DT" → mostra sc2_all + sc2_dt
- [x] "F" → mostra sc2_all + sc2_f
- [x] "S" → mostra sc2_all + sc2_s

**Livello 2b - file_type (Tipologia Fascicolo):**
- [x] Vuoto → nascondi FSC e FE
- [x] "personale" → mostra FSC, nascondi FE
- [x] "edilizia" → mostra FE, nascondi FSC

### B. CSS Allineato a Ruby ✅ COMPLETATO
- [x] `.sc2_field` → sfondo giallo `#F5F5C8`
- [x] `.sc2_container` con classi modificatrici (sc2_all, sc2_cars, sc2_d, sc2_dt, sc2_f, sc2_s)
- [x] `.fsc_container`, `.fe_container` con display:none iniziale per sub-container

### C. JavaScript (porting units-sc.js) ✅ COMPLETATO
- [x] `isUnitDocumentaria()` - legge testo opzione (non DB ID)
- [x] `isUnitFascicolo()` - legge testo opzione (non DB ID)
- [x] `unitTypeChange()` - livello 1
- [x] `sc2TskChange()` - livello 2a
- [x] `fscChange()` - livello 2b
- [x] `hideAndClean()`, `fscHideAndClean()`, `feHideAndClean()`
- [x] `showAndBuild()`

### D. Campi Modello Sc2 ✅ COMPLETATO
- [x] `sdts` (Rappresentazione tematica) - sc2_cars
- [x] `lrd` (Data della ripresa) - sc2_f
- [x] `cmmr` (Numero di commessa) - sc2_dt
- [x] `ort` (Orientamento) - sc2_cars
- [x] Migrazione `0014_add_sc2_extra_fields.py`

### E. Form e Viste ✅ COMPLETATO
- [x] `UnitForm` con sc2_tsk, file_type, fsc_name, fsc_surname
- [x] `Sc2Form` con tutti i campi + classe sc2_field
- [x] `UnitCreateView` riscritta come View
- [x] Template riorganizzato (SC2/FSC/FE nei tab Descrizione e Descrizione Fisica)

---

## Fase 14: Refactor in Moduli Forms/Views (✅ COMPLETATA - v0.16.0)
- [x] Refactor forms.py in moduli separati (archimista_python/archive/forms/) — 9 moduli
- [x] Refactor views.py in moduli separati (archimista_python/archive/views/) — 9 moduli
- [ ] Refactor admin.py in moduli separati (archimista_python/archive/admin/)
- [x] ~~Autocomplete per relazioni (Select2)~~ — ✅ COMPLETATO v0.33.0
- [ ] Validazione JavaScript lato client
- [ ] Upload oggetti digitali diretto
- [ ] Export AEF completo

---

## Fase 18: Fix Sincronizzazione Campi e Refactoring Template (✅ COMPLETATA - v0.18.0)
- [x] Fix sincronizzazione `unit_type_term` ↔ `unit_type` (pre-selezione dropdown in modifica)
- [x] Fix sincronizzazione `sc2_tsk` ↔ `card_type` (mappatura SC3→F, salvataggio corretto)
- [x] Unit Detail View completamente riscritta (tutte le schede in lettura con tab)
- [x] Template spezzati in partial (14 file in `templates/archive/units/partials/`)
- [x] Correzione capitalizzazione italiana in tutti i template
- [x] Script `fix_sc2_card_types.py` per aggiornare record esistenti

---

### Fase 26: Allineamento Campi Form e Etichette i18n a Ruby (✅ COMPLETATA - v0.26.0)

**Problema:** I form Python mancavano di 26+ campi presenti nelle maschere Ruby. Le etichette non erano sempre allineate a i18n Ruby.

**Soluzione:**

#### A. Modelli aggiunti/corretti
- `Sc2AttributionReason` — modello mancante (nested dentro Sc2Author)
- `UnitOtherReferenceNumber` — aggiunti campi `qualifier` e `note`
- Migrazioni `0016` e `0017` create e applicate

#### B. Campi aggiunti ai form
- **Fond**: `arrangement_note` ("Nota dell'archivista")
- **Unit**: 14 campi — `given_title`, `extent`, `arrangement_note`, `tmp_reference_number`, `tmp_reference_string`, `folder_number`, `file_number`, `related_materials`, `preservation_note`, `restoration`, `note`, `physical_container_type/title/number`
- **Unit formset**: `unit_urls`, `unit_identifiers`, `fe_fract_land_parcels`, `fe_fract_edil_parcels`
- **Creator**: `creator_legal_statuses` formset
- **Custodian**: `editing_type` da vocabolario (7 termini) invece di hardcoded

#### C. Etichette allineate a Ruby i18n
- `unit_type` → "Tipologia", `extent` → "Consistenza", `given_title` → "Attribuito"
- `arrangement_note` → "Nota dell'archivista", `physical_description` → "Descrizione estrinseca"
- `access_condition` → "Accesso", `use_condition` → "Riproduzione"
- `residence` → "Sede", `history` (Fond) → "Storia archivistica"
- E tutte le altre da `config/locales/it.yml`

**Priorità:** ALTA - Completato ✅

---

#### Fase 27: Fix JavaScript Formset e Allineamento Detail Views (✅ COMPLETATA - v0.27.0)

**Problema A:** I pulsanti "Aggiungi nome", "Aggiungi identificativo", "Nuovo collegamento", ecc. non facevano nulla. Errore JS: `Cannot read properties of null (reading 'getElementsByClassName')`.

**Cause:**
1. `project_form.html`: `onclick="addForm('urls')"` con prefix `'urls'` ma container `url_formset` e view usa `prefix='url'` → mismatch
2. `creator_form.html` e `custodian_form.html`: `onclick="addFormsetItem(...)"` con bug su template vuoto
3. `fond_form.html`: JS creava button duplicati perché cercava ID sbagliati
4. `unit_form.html`: JS usava `-formset` ma molti container usano `_formset`

**Soluzione:**
- Sostituiti tutti gli `onclick` inline con `class="add-formset-link" data-prefix="..."` + `addEventListener`
- Uniformati i prefix nella view `projects.py`: `'urls'`→`'url'`, `'managers'`→`'manager'`, `'stakeholders'`→`'stakeholder'`, `'fonds'`→`'fond'`
- Unificato il pattern `setupFormset()` in tutti i template
- `unit_form.html`: ora prova sia `_formset` che `-formset`

**Problema B:** Le detail view mostravano solo una frazione dei campi presenti nei form.

**Unit Detail** (completato):
- Aggiunti: `given_title`, `title`, `extent`, `arrangement_note`, `tmp_reference_number/string`, `folder_number`, `file_number`, `related_materials`, `restoration`, `note`, `physical_container_type/title/number`, `preservation`, `preservation_note`

**Fond Detail** (completamente riscritto con 7 tab):
- Prima: solo nome, tipo, abstract, storia, eventi, lista unità
- Dopo: 1.Descrizione, 2.Altre informazioni, 3.Accesso, 4.Relazioni, 5.Fonti, 6.Compilatori, 7.Estremi cronologici

**Creator Detail** (completamente riscritto con 5+ tab):
- Prima: solo tipo, residenza, stato giuridico, abstract, storia, note
- Dopo: 1.Identificazione, 2.Descrizione, 3.Relazioni, 4.Fonti, 5.Compilatori, Estremi cronologici

**Custodian Detail**:
- Aggiunto campo "Pubblicato"

**File modificati:**
- `archimista_python/archive/templates/archive/project_form.html`
- `archimista_python/archive/views/projects.py`
- `archimista_python/archive/templates/archive/creator_form.html`
- `archimista_python/archive/templates/archive/custodian_form.html`
- `archimista_python/archive/templates/archive/fond_form.html`
- `archimista_python/archive/templates/archive/unit_form.html`
- `archimista_python/archive/templates/archive/fond_detail.html` (riscritto)
- `archimista_python/archive/templates/archive/creator_detail.html` (riscritto)
- `archimista_python/archive/templates/archive/custodian_detail.html`
- `archimista_python/archive/templates/archive/units/partials/_detail_description.html`
- `archimista_python/archive/templates/archive/units/partials/_detail_physical.html`
- `archimista_python/archive/templates/archive/units/partials/_detail_access.html`

**Priorità:** ALTA - Completato ✅

---

#### Fase 29: CRUD completo Profili istituzionali (Institution) allineato a Ruby (✅ COMPLETATA - v0.29.0)

**Problema:** Istituzioni avevano solo list/detail views. Mancava il modello InstitutionEditor. Nessun form CRUD.

**Soluzione:**

##### A. Modello aggiunto
- `InstitutionEditor` — FK a Institution, campi: name, qualifier, editing_type, edited_at
- Migrazione `0020_institutioneditor.py` creata e applicata

##### B. Form allineati a Ruby
- `InstitutionForm` — 3 campi: Denominazione (obbligatorio), Descrizione, Annotazioni
- `InstitutionEditorForm` — 4 campi + editing_type da vocabolario `editors.editing_type` (7 termini)
- `InstitutionEditorFormSet` — inline formset con `extra=0, can_delete=True`

##### C. Viste CRUD
- `InstitutionListView` — lista ordinata per nome
- `InstitutionDetailView` — dettaglio con sezione compilatori
- `InstitutionCreateView` — creazione con formset
- `InstitutionUpdateView` — modifica con formset
- `InstitutionDeleteView` — conferma eliminazione

##### D. Template
- `institution_list.html` — tabella con azioni: Dettagli, Modifica, Elimina + pulsante "Nuovo"
- `institution_detail.html` — dettaglio + tabella compilatori
- `institution_form.html` — form con layout tabella per formset, `<template>` per cloning JS
- `institution_confirm_delete.html` — conferma eliminazione

##### E. JavaScript
- Formset usa `<template id="editor-empty">` per cloning corretto
- `cloneNode(true)` + sostituzione `__prefix__` → indice effettivo
- Funziona sia con 0 che con N righe esistenti

**File modificati/creati:**
- `archimista_python/archive/models/system.py` — aggiunto InstitutionEditor
- `archimista_python/archive/models/__init__.py` — esportato InstitutionEditor
- `archimista_python/archive/forms/institution.py` — nuovo, 3 form + formset
- `archimista_python/archive/forms/__init__.py` — aggiunti export
- `archimista_python/archive/views/institutions.py` — nuovo, 5 viste CRUD
- `archimista_python/archive/views/__init__.py` — aggiornati import
- `archimista_python/archive/urls.py` — aggiunte 3 URL (create, edit, delete)
- `archimista_python/archive/templates/archive/institution_form.html` — nuovo
- `archimista_python/archive/templates/archive/institution_confirm_delete.html` — nuovo
- `archimista_python/archive/templates/archive/institution_list.html` — aggiornato
- `archimista_python/archive/templates/archive/institution_detail.html` — aggiornato
- `archimista_python/archive/migrations/0020_institutioneditor.py` — creata e applicata

**Priorità:** ALTA - Completato ✅

---

## Riepilogo Finale

| Fase | Stato | Note |
|------|-------|------|
| Fase 1 | ✅ COMPLETATA | Modelli base |
| Fase 2 | ✅ COMPLETATA | Relazioni e polimorfismo |
| Fase 3 | ✅ COMPLETATA | UI CRUD e navigazione |
| Fase 4 | ✅ COMPLETATA | Biografie, eventi, classificazione |
| Fase 5 | ✅ COMPLETATA | Navigazione dinamica e schede speciali |
| Fase 6 | ✅ COMPLETATA | Ricerca ed esportazione |
| Fase 7 | ⏸️ SOSPESA | Permessi (non prioritario) |
| Fase 8 | ✅ COMPLETATA | **Tutti i modelli Archimista** |
| Fase 9 | ✅ COMPLETATA | **Vocabolari controllati** |
| Fase 10 | ✅ COMPLETATA | **Refactor in moduli** |
| Fase 11 | ✅ COMPLETATA | **Allineamento interfaccia** |
| Fase 12 | ✅ COMPLETATA | **Vocabolari allineati Ruby** |
| Fase 13 | ✅ COMPLETATA | **Show/Hide dinamico SC2/FSC/FE** |
| Fase 14 | ✅ COMPLETATA | **Refactor forms/views in moduli** |
| Fase 15 | ✅ COMPLETATA | **Riorganizzazione struttura progetto** |
| Fase 18 | ✅ COMPLETATA | **Fix sincronizzazione campi, Unit Detail, refactoring template** |
| Fase 19 | ✅ COMPLETATA | **Allineamento vocabolari a Ruby, fix formset, fix modello Term** |
| Fase 20 | ✅ COMPLETATA | **Fix sezione compilatori unità: prefisso formset, campo id, dropdown editing_type, link aggiungi** |
| Fase 21 | ✅ COMPLETATA | **Menu navigazione completo, viste list/detail per tutte le entità di servizio** |
| Fase 22 | ✅ COMPLETATA | **Allineamento form soggetto produttore a Ruby: 5 tab corretti, show/hide dinamico, capitalizzazione italiana** |
| Fase 23 | ✅ COMPLETATA | **Allineamento form soggetto conservatore a Ruby: 7 tab corretti, formset completi, relazioni con fondi/fonti, capitalizzazione italiana** |
| Fase 24 | ✅ COMPLETATA | **Allineamento form progetto a Ruby: CRUD completo, 3 tab, formset, vocabolari sincronizzati** |
| Fase 25 | ✅ COMPLETATA | **Estremi cronologici: form, import AEF, detail** |
| Fase 26 | ✅ COMPLETATA | **Allineamento campi form vs Ruby + etichette i18n** |
| Fase 27 | ✅ COMPLETATA | **Fix JavaScript formset buttons + allineamento completo detail views a Ruby** |
| Fase 28 | ✅ COMPLETATA | **CRUD completo Fonti (Source) allineato a Ruby: modelli, form, viste, template** |
| Fase 29 | ✅ COMPLETATA | **CRUD completo Profili istituzionali (Institution) allineato a Ruby: modello, form, viste, template** |
| Fase 30 | ✅ COMPLETATA | **CRUD completo Voci di indice (Heading) allineato a Ruby: form, viste, template, vocabolario corretto** |
| Fase 31 | ✅ COMPLETATA | **CRUD completo Anagrafiche (Anagraphic) allineato a Ruby: form, viste, template** |
| Fase 32 | ✅ COMPLETATA | **CRUD completo Profili documentari (DocumentForm) allineato a Ruby: form, viste, template, fix ordine campi anagrafiche** |
| Fase 33 | ✅ COMPLETATA | **Autocomplete Select2 per tutte le relazioni: widget AJAX, cloning corretto, label Elimina, prefix formset uniformati** |
| Fase 34 | ✅ COMPLETATA | **Titolario di classificazione: CRUD completo, assegnazione a unità, interfaccia gerarchica** |
| Fase 35 | ✅ COMPLETATA | **Albero interattivo (+, −, rinomina, drag & drop, cestino) + classificazione di massa unità** |
| Fase 36 | ✅ COMPLETATA | **Fix formset vuoti, gerarchia unità (Modifica livello), lista unità globale, UX albero e dettaglio fondo** |
| Fase 37 | ✅ COMPLETATA | **Refactoring Unit Views: God Object (987 righe) → 6 handler (420 righe, -57%). Fix Sc2Form card_type** |
| Fase 38 | ✅ COMPLETATA | **Fix discrepanze Ruby vs Python: hidden fields Unit, Custodian preferred_name, Fond abstract is_root, qualifier dropdown** |
| Fase 39 | ✅ COMPLETATA | **CRUD completo Compilatori (Editor): form, viste, template, menu. 6/8 entità di servizio con CRUD completo** |
| Fase 40 | ✅ COMPLETATA | **CRUD completo Oggetti Digitali (DigitalObject): form, viste, template, menu, ricerca. 8/8 entità di servizio con CRUD completo** |
| Fase 40b | ✅ COMPLETATA | **Oggetti digitali nested polimorfici: 20 URL per 5 entità, associazione automatica, link nelle detail view** |
| Fase 40c | ✅ COMPLETATA | **Upload file per Oggetti Digitali: FileField, Pillow thumbnail, validazione tipo/dimensione, 8MB max** |
| Fase 41 | ✅ COMPLETATA | **Controllo qualità: 4 viste, 5 template, 11+ controlli per fondo, 6 per creatore, 3 per conservatore, menu Strumenti** |
| Fase 42 | ✅ COMPLETATA | **Completamento funzionale: Export AEF round-trip, CSV unità, Report, Ricerca avanzata, Storico modifiche** |
| Fase 43 | ✅ COMPLETATA | **Autenticazione singolo utente: UserProfile, login/logout, cambio password obbligatorio, middleware, seed script, 8/8 test** |
| Fase 47 | ✅ COMPLETATA | **Autocomplete Select2 FK, Lang Select2, Refactor template, README, setup.sh, test 67/67, bug fix** |
| Fase 48 | ✅ COMPLETATA | **Fix titolario (json.dumps), FontAwesome CDN, pulsanti uniformi (10 liste + 6 detail), source list migliorata** |

### Fase 24: Allineamento Form Progetto a Ruby (✅ COMPLETATA - v0.24.0)

**Problema:** L'interfaccia Python dei progetti era limitata alla sola lettura (list/detail) e non era allineata all'originale per quanto riguarda etichette e opzioni dei vocabolari.

**Soluzione:**

#### A. Ristrutturazione completa del form (3 tab come Ruby)
1. **Identificazione**: Denominazione, Tipologia d'intervento (dropdown), pubblicato (checkbox), Anno d'inizio/fine (dropdown), Status (dropdown), Descrizione, Annotazioni, Collegamenti (formset ProjectUrl)
2. **Responsabilità**: Responsabili (formset ProjectManager), Soggetti coinvolti (formset ProjectStakeholder) con qualificatori esatti da Ruby.
3. **Relazioni**: Fondi collegati (RelProjectFond formset)

#### B. Sincronizzazione "maniacale" dei vocabolari
- Implementata funzione `sync_terms` in `seed_vocabularies.py` per eliminare termini estranei e garantire che `projects.project_type`, `projects.status`, `project_managers.qualifier` e `project_stakeholders.qualifier` contengano **solo ed esclusivamente** i termini presenti in Archimista Ruby.

#### C. Detail e List views aggiornate
- Detail view con sezioni: Identificazione, Responsabilità, Relazioni.
- List view con etichette allineate e azioni CRUD.

**Priorità:** ALTA - Completato ✅

---

### Fase 25: Estremi Cronologici (Archidate) (✅ COMPLETATA - v0.25.0)

**Problema:** Gli estremi cronologici erano nel modello `Event` ma non gestiti nell'interfaccia web. L'import AEF non importava gli eventi. I form non erano allineati a Ruby.

**Soluzione:**

#### A. Form allineati a Ruby
- 2 radio: `data puntuale` (Y), `data secolare` (C)
- Combo specifiche: `=`, `ante`, `circa` (inizio) / `ante`, `=`, `circa` (fine)
- Combo validità: `certa`, `incerta`, `attribuita`, `incerta e attribuita`
- Data puntuale: anno, mese, giorno
- Data secolare: secolo (I-XXI), intervallo (inizio, fine, metà, ecc.)
- Equal bounds: checkbox "Uguale all'estremo iniziale"

#### B. Import AEF eventi
- Handler per `unit_event` e `fond_event`
- GenericForeignKey: `content_type` + `object_id`

#### C. Detail view
- Unit: tab dedicato, Fond: card, Creator: card

#### D. Fix salvataggio
- Costruzione manuale evento da `cleaned_data` (evita errore `ModelForm.save(commit=False)` su form non validato)

**Priorità:** ALTA - Completato ✅

---

## Conteggio Totale Modelli

- **125+ modelli** implementati (100% copertura rispetto ad Archimista Ruby)
- **70+ tabelle** aggiuntive create con migrazioni
- **100% compatibilità** importazione AEF
- **77 termini** standardizzati in 11 vocabolari
- **18 formset inline** per estensioni e relazioni
- **28 moduli** per organizzazione codice (10 models + 9 forms + 9 views)

---

## Cosa Manca per Equivalenza Completa

### Alta Priorità (essenziali per equivalenza con Archimista)
1. ✅ ~~Modelli completi~~ (FATTO)
2. ✅ ~~Migrazioni~~ (FATTO)
3. ✅ ~~Import AEF completo~~ (FATTO)
4. ✅ ~~Vocabolari controllati~~ (FATTO)
5. ✅ ~~Interfaccia allineata a Archimista Ruby~~ (FATTO - v0.13.0)
6. ✅ ~~Show/Hide dinamico SC2/FSC/FE~~ (FATTO - v0.15.0)
7. ✅ ~~Refactor forms/views in moduli~~ (FATTO - v0.16.0)
8. ✅ ~~Unit Detail View completa~~ (FATTO - v0.18.0)
9. ✅ ~~Sincronizzazione campi form~~ (FATTO - v0.18.0)
10. ✅ ~~Refactoring template in partial~~ (FATTO - v0.18.0)
11. ✅ ~~Allineamento vocabolari a Ruby~~ (FATTO - v0.19.0)
12. ✅ ~~Fix formset is_valid/save~~ (FATTO - v0.19.0)
13. ✅ ~~Fix modello Term.__str__~~ (FATTO - v0.19.0)
14. ✅ ~~Fix sezione compilatori unità~~ (FATTO - v0.20.0)
15. ✅ ~~Menu navigazione + viste entità di servizio~~ (FATTO - v0.21.0)
16. ✅ ~~Allineamento form soggetto produttore a Ruby~~ (FATTO - v0.22.0)
17. ✅ ~~Allineamento form soggetto conservatore a Ruby~~ (FATTO - v0.23.0)
18. ✅ ~~Allineamento form progetto a Ruby (CRUD completo)~~ (FATTO - v0.24.0)
19. ✅ ~~Estremi cronologici (form, import AEF, detail)~~ (FATTO - v0.25.0)
20. ✅ ~~Confronto e allineamento campi form vs Ruby + etichette i18n~~ (FATTO - v0.26.0)
21. ✅ ~~Fix JavaScript formset buttons + allineamento detail views~~ (FATTO - v0.27.0)
22. ✅ ~~CRUD completo Fonti (Source)~~ (FATTO - v0.28.0)
23. ✅ ~~CRUD completo Profili istituzionali (Institution)~~ (FATTO - v0.29.0)
24. ✅ ~~CRUD completo Voci di indice (Heading)~~ (FATTO - v0.30.0)
25. ✅ ~~CRUD completo Anagrafiche (Anagraphic)~~ (FATTO - v0.31.0)
26. ✅ ~~CRUD completo Profili documentari (DocumentForm)~~ (FATTO - v0.32.0)
27. ✅ ~~Autocomplete Select2 per tutte le relazioni~~ (FATTO - v0.33.0)
28. ✅ ~~Titolario di classificazione UI~~ (FATTO - v0.34.0)
29. ✅ ~~Albero interattivo (+, −, rinomina, drag & drop, cestino)~~ (FATTO - v0.35.0)
30. ✅ ~~Classificazione di massa unità~~ (FATTO - v0.35.0)

### Media Priorità (importanti ma non bloccanti)
19. ✅ CRUD entità di servizio (Fonti ✅, Istituzioni ✅, Voci indice ✅, Anagrafiche ✅, Profili documentari ✅)
20. ✅ Export AEF — COMPLETATO v0.44.0
21. ✅ Upload oggetti digitali diretto — COMPLETATO v0.42.0
22. ✅ Ricerca avanzata con filtri — COMPLETATO v0.44.0
23. ✅ Autocomplete per relazioni — COMPLETATO v0.33.0
24. ✅ Gestione classificazione/titolario UI COMPLETATO v0.34.0
25. ✅ Albero interattivo e classificazione di massa COMPLETATO v0.35.0
26. ✅ Report progetto/conservatore — COMPLETATO v0.44.0
27. ✅ Export CSV unità — COMPLETATO v0.44.0
28. ✅ Storico modifiche/EditorLog — COMPLETATO v0.44.0

### Bassa Priorità (nice to have)
24. ❌ Sistema permessi (opzionale)
25. ⚠️ Miglioramenti UI/UX (opzionali)
26. ⚠️ Ottimizzazione performance (opzionali)
27. ✅ Biografie/Eventi — Modelli + formset inline completi (v0.25.0)
28. ✅ Dashboard/Statistiche — Report implementati (v0.44.0)
29. ✅ **Verifica completa campi form vs Ruby** — COMPLETATO v0.26.0 + v0.38.0

---

## Stima Lavoro Mancante

| Area | Stato | Note |
|------|-------|------|
| CRUD Editor + DigitalObject | ✅ FATTO | v0.39.0 + v0.40.0 |
| Export AEF | ✅ FATTO | v0.44.0 — round-trip completo |
| Upload oggetti digitali | ✅ FATTO | v0.42.0 — Pillow, thumbnail |
| Ricerca avanzata | ✅ FATTO | v0.44.0 — filtri multipli, paginazione |
| Autocomplete relazioni | ✅ FATTO | v0.33.0 (django-select2) |
| Gestione classificazione UI | ✅ FATTO | v0.34.0 |
| Refactoring Unit Views | ✅ FATTO | v0.37.0 (God Object → handler) |
| Sistema permessi | ❌ OPZIONALE | 20-30h, non prioritario |
| Biografie/Eventi UI | ✅ FATTO | Modelli + formset inline (v0.25.0) |
| Dashboard/Statistiche | ✅ FATTO | Report implementati (v0.44.0) |
| Menu: Controllo qualità | ✅ FATTO | v0.43.0 |
| Menu: Report, Esporta | ✅ FATTO | v0.44.0 |
| Export CSV | ✅ FATTO | v0.44.0 |
| Storico modifiche | ✅ FATTO | EditorLog model (v0.44.0) |
| **TOTALE** | **100%** | Completato — export PDF/RTF completo incluso (v0.46.0) |

**Stato attuale completamento:** 100% (modelli 100%, interfaccia core 100%, export 100%, ricerca 100%, report 100%, autenticazione singolo utente 100%, export PDF/RTF 100%).

---

## Archivio completato
*Vedi `MIGRATION_WALKTHROUGH.md` per i dettagli storici dei rilasci.*
*Vedi `COMPLETION_STATUS.md` per lo stato dettagliato di ogni componente.*
*Vedi `RUBY_VS_PYTHON_COMPARISON.md` per il confronto maschere Ruby vs Python.*
*Vedi `CHANGELOG.md` per la cronologia delle release.*
