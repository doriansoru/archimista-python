# Piano di Migrazione Archimista - Stato Avanzamento

Il presente documento riassume l'approccio e lo stato della migrazione del software "Archimista" verso Python/Django.

## Stato Attuale: v0.50.0 COMPLETATA — Suite test completa (242 test) (2026-04-07)

### Tecnologie Utilizzate
- **Backend**: Python 3.11+ / Django 6.0.3
- **Database**: SQLite (sviluppo locale)
- **Frontend**: Bootstrap 5 + Django Templates

### Struttura Progetto (aggiornata 2026-04-03)
L'app `archive/` è stata spostata dentro `archimista_python/` per seguire le convenzioni Django:
```
python_rewrite/
├── manage.py
├── archimista_python/          ← Progetto Django
│   ├── settings.py, urls.py
│   └── archive/                ← App Django (models, views, forms, templates)
├── seed.py, *_vocabularies.py  ← Script utility
└── db.sqlite3
```

## Fasi del Piano

### Fase 1: Inizializzazione e Modellazione Base (COMPLETATA)
- Setup dell'ambiente virtuale (`venv`).
- Creazione del progetto `archimista_python` e dell'app `archive`.
- Traduzione dei modelli core: `Group`, `Fond`, `Unit`, `Creator`, `Custodian`.
- Configurazione base del Django Admin.

### Fase 2: Modelli Avanzati e Relazioni (COMPLETATA)
- Implementazione delle **Voci di Indice (`Heading`)** per persone, famiglie, enti e luoghi.
- Implementazione degli **Oggetti Digitali (`DigitalObject`)** con supporto polimorfico (`GenericForeignKey`) per allegare file a qualsiasi entità.
- Creazione delle tabelle di relazione molti-a-molti (`Rel*`) tra i modelli principali.
- Aggiornamento dello script `seed.py` per testare le nuove relazioni.

### Fase 3: Interfaccia Utente (CRUD) e Navigazione (COMPLETATA)
- Aggiunta di campi gerarchici `parent` in `Fond` e `Unit` per navigazione nativa.
- Creazione di **Maschere di Inserimento (`forms.py`)** personalizzate.
- Sviluppo di viste CRUD complete (Creazione, Modifica, Cancellazione) lato utente.
- Restyling grafico delle liste e del dettaglio fondi con Bootstrap 5.
- Aggiunta modelli `Institution` e `Source`.

### Fase 4: Biografie, Eventi e Classificazione (COMPLETATA)
- **Biografie ed Eventi**: Porting dei modelli `BiogHist` e `Event` con supporto polimorfico.
- **Classificazione (Titolario)**: Implementazione dello schema gerarchico di classificazione (`Classification`) collegato alle unità.
- **Admin Inlines**: Gestione integrata di eventi e biografie nelle schede archivistiche.

### Fase 5: Navigazione Dinamica e Schede Specialistiche (COMPLETATA)
- **Albero Archivistico**: Navigazione visuale e dinamica (`jstree`) per muoversi tra fondi e unità senza ricaricare la pagina.
- **Schede Iccd / Sc2**: Supporto per la catalogazione di beni culturali e disegni tecnici, rendendo il sistema autonomo (Standalone).
- **Dettaglio Unità**: Nuova vista per visualizzare segnature, contenuti e dati specialistici.

### Fase 6: Ricerca e Reportistica (COMPLETATA)
- **Ricerca Globale**: Implementata vista di ricerca base in `GlobalSearchView`.
- **Generazione Inventari**: Implementata esportazione PDF e DOCX in `export_utils.py`.

### Fase 41: Controllo qualità (COMPLETATA - v0.43.0)
- **Controllo qualità**: Implementata pagina "Controllo qualità" allineata a Ruby `QualityChecksController`.
- **Fond QC**: 11 controlli (denominazione, datazione, tipologia, descrizione, storia, consistenza, unità, creatori, conservatori, progetti, fonti).
- **Creator QC**: 6 controlli (tipologia, tipologia ente, denominazione, datazione, biografia, fonti).
- **Custodian QC**: 3 controlli (denominazione, macrotipologia, sedi).
- **Menu**: voce "Controllo qualità" aggiunta nel menu Strumenti.

### Fase 42: Completamento funzionale (COMPLETATA - v0.44.0)
- **Export AEF completo** — classe `AEFExporter` (500+ righe), round-trip compatibile con import, genera ZIP con data.json + metadata.json + oggetti digitali, supporta tutti i modelli e le relazioni
- **Export CSV unità** — vista con filtro per fondo e ricerca, download CSV
- **Report** — report per progetto (fondi, unità, creatori, conservatori) e per conservatore (fondi, unità, accessibilità)
- **Ricerca avanzata** — vista con filtri multipli (tipo entità, fondo, tipo unità, tipo produttore, solo pubblicati), paginazione
- **Storico modifiche** — modello `EditorLog` con tracciamento di chi ha modificato cosa e quando
- **Fix import/export** — 15+ handler import aggiunti, fix FK field names, mapping snake_case modelli

### Fase 44: Export PDF/RTF identico a Ruby (COMPLETATA - v0.46.0)
- **report_support.py** — porting di `lib/report_support.rb` (~1530 righe): 29 campi Fond, 49 Unit, 18 Creator, 32 Custodian, 10 Project
- **rtf_writer.py** — porting di `app/models/rtfwriter.rb` (~520 righe): scrittura RTF raw
- **rtf_builder.py** — porting di `app/models/rtf_builder.rb` (~500 righe): inventario, progetto, conservatore
- **views/reports.py** — viste aggiornate con PDF (WeasyPrint) + RTF (RtfBuilder)
- **Template** — `inventory_report.html`, `project_report.html`, `custodian_report.html`
- **Fix** — 24 related_name in relations.py, proprietà su Fond/Creator, Unit.display_sequence_numbers_of
- **Migrazione** — 0025_relcreatorfond (24 FK con related_name)
- **Test** — `_get_fond_subtree(64)` OK, `make_html()` OK, report completo OK

### Fase 43: Autenticazione singolo utente (COMPLETATA - v0.45.0)
- **UserProfile** — modello OneToOne con `User`, campo `must_change_password`, signal auto-creazione profilo
- **Middleware** — `LoginRequiredMiddleware` blocca tutte le richieste non autenticate (tranne login, logout, admin, static, media)
- **Login/Logout** — `ArchimistaLoginView` con template italiano, redirect forzato a password-change se `must_change_password=True`
- **Cambio password** — `PasswordChangeForm` Django, rimuove `must_change_password` dopo il successo
- **Navbar** — dropdown utente con nome, "Cambia password", "Esci"
- **Seed script** — `seed_admin_user.py` crea admin con password casuale sicura e `must_change_password=True`
- **Test** — 8/8 passati (redirect anonimi, login, errore password, cambio password, logout)

### Fase 7: Sistema di Permessi (✅ COMPLETATA - v0.45.0, singolo utente)
- **Autenticazione singolo utente**: Implementata con login/logout, cambio password obbligatorio, middleware, seed script.
- **Multi-utente con permessi granulari**: Da implementare (opzionale, futuro).

### Fase 8: Modelli Completi e Importazione Dati (COMPLETATA)
- **Modelli Completi**: Implementati tutti i 129+ modelli di Archimista Ruby, inclusi:
  - Estensioni per Fond, Unit, Creator, Custodian
  - Schede SC2, ICCD, FSC, FE complete
  - Modelli relazionali, sistema, vocabolari
  - EditorLog (v0.44.0)
- **Importazione AEF**: Tutti i handler completati (v0.44.0) — 15+ nuovi handler aggiunti
- **Export AEF**: Round-trip completo (v0.44.0)
- **Admin Completo**: Tutti i modelli registrati con inlines

### Fase 9: Standardizzazione con Vocabolari Controllati (COMPLETATA - v0.11.0)
- **77 termini** standardizzati in 11 vocabolari
- Campi a scelta per Fond e Unit implementati
- Migrazioni 0010 e 0011 create e applicate

### Fase 10: Refactor in Moduli (COMPLETATA - v0.12.0)
- **models.py** suddiviso in 10 moduli separati
- Compatibilità mantenuta con codice esistente
- Verifica: `python manage.py check` passa senza errori

### Fase 11: Allineamento Interfaccia a Archimista Ruby (COMPLETATA - v0.13.0)
- **Form Unità**: Riorganizzati con 6 tab (Descrizione, Descrizione Fisica, Accesso, Fonti, Compilatori, Schede Speciali)
- **Form Fondi**: Riorganizzati con 6 tab (Descrizione, Altre Informazioni, Accesso, Relazioni, Fonti, Compilatori)
- **Formset Inline**: Tutti i 18 formset per estensioni e relazioni implementati
- **JavaScript Dinamico**: Funzione generica per aggiungi/rimuovi righe in tutti i formset
- **Template**: `unit_form.html` e `fond_form.html` completamente riscritti

### Fase 12: Allineamento Vocabolari a Archimista Ruby (COMPLETATA - v0.14.0)
- **30 vocabolari**, 200+ termini da `db/seeds/terms.json`
- Approccio ibrido: campo testo con datalist per suggerimenti
- Compatibile con import AEF

### Fase 13: Show/Hide Dinamico Campi SC2/FSC/FE (COMPLETATA - v0.15.0)
- **Logica a 3 livelli** identica a Ruby `units-sc.js`:
  - `unit_type` → mostra/nasconde `sc2_tsk` o `file_type`
  - `sc2_tsk` → mostra/nasconde container SC2 specifici (CARS, D, DT, F, S)
  - `file_type` → mostra/nasconde FSC o FE
- **Campi SC2 aggiunti**: `sdts`, `lrd`, `cmmr`, `ort`
- **CSS**: sfondo giallo `#F5F5C8` per campi SC2 (identico a Ruby)
- **Template riorganizzato**: SC2/FSC/FE integrati nei tab Descrizione e Descrizione Fisica
- **UnitCreateView**: riscritta come View con GET/POST completi
- **Fix critico**: `isUnitDocumentaria()` e `isUnitFascicolo()` leggono il testo dell'opzione (non il DB ID)

## Conteggio Modelli

| Categoria | Ruby (originale) | Django (port) | Stato |
|-----------|-----------------|---------------|-------|
| Modelli principali | ~40 | ~40 | ✅ Completo |
| Modelli estensione | ~70 | ~70 | ✅ Completo |
| Modelli relazionali | ~15 | ~15 | ✅ Completo |
| **TOTALE** | **~129** | **~129** | **✅ 100%** |

## Stato di Avanzamento per Area

| Area | Completamento | Note |
|------|---------------|------|
| Database/Modelli | 100% | Tutti i 129+ modelli implementati (incluso EditorLog) |
| Import Dati | 100% | AEF compatibile — tutti i handler completati (v0.44.0) |
| Export AEF | 100% | Round-trip completo (v0.44.0) |
| Export CSV | 100% | Export unità con filtri (v0.44.0) |
| Export PDF/RTF | 100% | Report inventario completo identico a Ruby (v0.46.0) |
| Report | 100% | Report inventario (fond), progetto, conservatore — PDF + RTF (v0.46.0) |
| Ricerca Avanzata | 100% | Filtri multipli, paginazione (v0.44.0) |
| Admin Django | 100% | Tutti i modelli registrati |
| Interfaccia Form | 100% | Show/hide dinamico allineato Ruby (v0.15.0) |
| Formset Inline | 100% | 18 formset implementati |
| JavaScript Dinamico | 100% | Show/hide SC2/FSC/FE + formset buttons (v0.27.0) |
| Detail Views | 100% | Fond/Creator/Unit/Custodian allineate a Ruby (v0.27.0) |
| Albero Interattivo | 100% | +, −, rinomina, drag & drop, cestino (v0.36.0) |
| Classificazione di Massa | 100% | Checkbox + modale albero + sposta (v0.35.0) |
| Gerarchia Unità | 100% | Modifica livello (su/giù), 3 livelli max (v0.36.0) |
| Lista Unità Globale | 100% | Con filtro, ricerca, alert orfane (v0.36.0) |
| Refactoring Unit Views | 100% | God Object → 6 handler (v0.37.0) |
| Controllo Qualità | 100% | Fond, Creator, Custodian (v0.43.0) |
| Storico Modifiche | 100% | EditorLog model (v0.44.0) |
| Autenticazione Singolo Utente | 100% | Login/logout, cambio password obbligatorio, middleware, seed script (v0.45.0) |
| Permessi Multi-utente | 0% | Opzionale, futuro |
| **TOTALE** | **100%** | Completato — autenticazione singolo utente inclusa (v0.45.0) |

## Istruzioni per la ripresa del lavoro
1. Verificare l'attivazione del `venv` in `python_rewrite/venv`.
2. Eseguire `python manage.py runserver` per testare l'interfaccia corrente.
3. Consultare `COMPLETION_STATUS.md` per lo stato dettagliato di ogni componente.
4. Eseguire `python test_complete.py` per verificare che tutto funzioni (242 test).

**Stato:** Il porting è COMPLETATO (v0.50.0). Tutte le funzionalità core sono implementate, testate (242/242 test) e documentate. Pulsanti uniformi con icone FontAwesome in tutte le liste e detail view. Titolario funzionante con albero jsTree popolato. Suite test completa copre: CRUD, viste, proprietà modelli, validazione form, import AEF reale, export content validation, autenticazione, middleware, seed scripts.
