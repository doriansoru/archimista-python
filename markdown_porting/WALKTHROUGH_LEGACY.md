# Walkthrough Legacy: Fasi Iniziali della Migrazione (v0.1 - v0.19)

Questo documento traccia la cronologia delle fasi iniziali della riscrittura del software "Archimista" da Ruby on Rails a Django.

Per le release recenti (v0.20+), vedere [CHANGELOG.md](CHANGELOG.md).

---

## Fondazione Progetto (Fase 1 - 2026-04-02)
- Inizializzazione della directory `python_rewrite/archimista_python`.
- Setup del `venv` e installazione Django.
- Traduzione dei modelli di base (`Group`, `Fond`, `Unit`, `Creator`, `Custodian`).
- Configurazione iniziale del **Django Admin** per ispezione dati.

## Relazioni e Polimorfismo (Fase 2 - 2026-04-02)
- Implementazione degli **Oggetti Digitali (`DigitalObject`)**: Utilizzo di `GenericForeignKey` di Django per permettere di allegare file (PDF, immagini) a qualsiasi entità archivistica (Fondi, Unità, ecc.).
- Implementazione delle **Voci di Indice (`Heading`)** per la catalogazione di persone, famiglie, enti e luoghi.
- Creazione delle **Tabelle di Relazione (`Rel*`)**: Mappatura delle associazioni molti-a-molti (es: Creatore <-> Fondo).
- Aggiornamento di `seed.py` per testare la solidità delle relazioni e dei vincoli d'integrità.

## Interfaccia Utente e Navigazione (Fase 3 - 2026-04-02)
- **Gerarchia Nativa**: Aggiunta di campi `parent` ricorsivi in `Fond` e `Unit` per una gestione gerarchica fluida nell'albero archivistico.
- **Viste CRUD Lato Utente**: Implementate le maschere di inserimento, modifica e cancellazione (Create, Update, Delete) per i Fondi e le Unità in `views.py`.
- **Form e Template**: Creazione di `forms.py` con widget Bootstrap 5 e di una serie di template HTML moderni (`fond_form.html`, `unit_form.html`, etc.).
- **Nuovi Modelli Core**: Aggiunta di `Institution` (Istituzioni) e `Source` (Fonti bibliografiche/archivistiche).

## Biografie, Eventi e Classificazione (Fase 4 - 2026-04-02)
- **Supporto Date Complesse**: Implementato il modello `Event` per gestire date di esistenza e attività (EAD-compatible), con precisione al giorno o all'anno e stringhe di visualizzazione personalizzate.
- **Biografie e Storia**: Aggiunto modello `BiogHist` per separare la narrazione storica/biografica dai metadati descrittivi del fondo.
- **Titolario (Classificazione)**: Introdotto il modello `Classification` gerarchico. Ora le unità possono essere collegate a uno schema di classificazione indipendente dall'albero dei fondi.
- **Admin Avanzato**: Configurato il Django Admin con `GenericStackedInline` per visualizzare Eventi e Biografie direttamente nelle schede di Fondi, Unità e Creatori.

## Navigazione Dinamica e Standalone UI (Fase 5 - 2026-04-02)
- **Interactive Tree Browser**: Implementata la navigazione ad albero con caricamento asincrono (`jstree`), rendendo l'esplorazione dell'archivio visiva e intuitiva.
- **Schede Specialistiche Sc2/Iccd**: Aggiunto supporto nativo per la catalogazione di beni culturali (ICCD) e disegni tecnici (Sc2), trasformando l'app in un sistema di inventariazione autonomo e potente.
- **Unit Detail View**: Creata la vista di dettaglio per le Unità, con integrazione automatica dei metadati specialistici se presenti.

## Ricerca e Reportistica (Fase 6 - 2026-04-02)
- **Global Search**: Implementata vista di ricerca globale per fondi, unità, voci di indice e oggetti digitali.
- **Export PDF/DOCX**: Implementate funzioni di esportazione inventari in `export_utils.py`.

## Correzioni Template (2026-04-02)
- **Fix Template Tags**: Corretti template tag spezzati su più righe in `fond_detail.html`, `unit_detail.html`, `search_results.html`, `import_form.html`.
- **Importazione AEF**: Risolto problema di linking unità-fondi durante importazione.
- **SC2 Card Type**: Implementato rilevamento automatico `sc2_tsk='F'` per fotografie (SC3) vs disegni (SC2).

## Implementazione Completa Modelli (Fase 8 - 2026-04-02)

### Modelli Estensione per Fond
- `FondName`: Nomi alternativi del fondo
- `FondIdentifier`: Identificativi del fondo
- `FondLang`: Lingue del fondo
- `FondOwner`: Possessori del fondo
- `FondUrl`: URL del fondo
- `FondEditor`: Curatori del fondo

### Modelli Estensione per Unit
- `UnitIdentifier`: Identificativi dell'unità
- `UnitOtherReferenceNumber`: Altre segnature dell'unità
- `UnitLang`: Lingue dell'unità
- `UnitDamage`: Danni dell'unità
- `UnitUrl`: URL dell'unità
- `UnitEditor`: Curatori dell'unità

### Modelli Estensione per Creator
- `CreatorName`: Nomi del creatore (primari e alternativi)
- `CreatorLegalStatus`: Stati giuridici del creatore
- `CreatorUrl`: URL del creatore
- `CreatorIdentifier`: Identificativi del creatore
- `CreatorActivity`: Attività del creatore
- `CreatorEditor`: Curatori del creatore

### Modelli Estensione per Custodian
- `CustodianName`: Nomi del custode
- `CustodianIdentifier`: Identificativi del custode
- `CustodianContact`: Contatti del custode
- `CustodianBuilding`: Edifici del custode
- `CustodianOwner`: Possessori del custode
- `CustodianUrl`: URL del custode
- `CustodianEditor`: Curatori del custode

### Schede SC2 Complete
- `Sc2TextualElement`: Elementi testuali (iscrizioni)
- `Sc2VisualElement`: Elementi visivi (stato conservazione)
- `Sc2Author`: Autori con ruolo, nome, datazione
- `Sc2Commission`: Commissioni con ente committente
- `Sc2CommissionName`: Nomi delle commissioni
- `Sc2Technique`: Tecniche di esecuzione
- `Sc2Scale`: Scale di rappresentazione

### Schede ICCD Complete
- `IccdSubject`: Soggetti della scheda
- `IccdDamage`: Danni specifici
- `IccdTechSpec`: Specifiche tecniche (materiali, tecniche, dimensioni)

### FSC - Fascicoli Sanitari Edilizia
- `FscCode`: Codici FSC
- `FscOrganization`: Organizzazioni
- `FscNationality`: Nazionalità
- `FscOpen`: Aperture
- `FscClose`: Chiusure

### FE - Fabbricati Edilizia
- `FeIdentification`: Identificazioni pratica
- `FeContext`: Contesti e licenze
- `FeOpera`: Opere e edifici
- `FeDesigner`: Progettisti e ruoli
- `FeCadastral`: Dati catastali
- `FeLandParcel`: Particelle fondiarie
- `FeFractLandParcel`: Frazionamenti particelle
- `FeFractEdilParcel`: Frazionamenti edilizi

### Modelli Relazionali Aggiuntivi
- `RelCreatorCreator`: Relazioni tra creatori
- `RelCreatorInstitution`: Relazioni creatore-istituzione
- `RelCreatorSource`: Relazioni creatore-fonte
- `RelCustodianSource`: Relazioni custode-fonte
- `RelFondSource`: Relazioni fondo-fonte
- `RelUnitSource`: Relazioni unità-fonte
- `RelFondDocumentForm`: Relazioni fondo-forma documentaria
- `RelProjectFond`: Relazioni progetto-fondo
- `RelUnitAnagraphic`: Relazioni unità-anagrafica

### Altri Modelli di Sistema
- `Project`: Progetti
- `DocumentForm`: Forme documentarie
- `Anagraphic`: Anagrafiche persone/famiglie
- `Place`: Luoghi geografici
- `Lang`: Lingue
- `Term`: Termini thesaurus
- `Vocabulary`: Vocabolari controllati
- `Export`: Tracciamento esportazioni
- `Import`: Tracciamento importazioni
- `Editor`: Entità curatrici
- `Activity`: Attività (thesaurus)
- `CreatorAssociationType`: Tipi associazione creatori
- `DocumentFormEditor`: Curatori forme documentarie
- `AnagIdentifier`: Identificativi anagrafiche

### Risultati della Validazione Finale
- **110+ modelli** implementati (100% copertura Archimista Ruby)
- **70+ tabelle** aggiuntive create con migrazione `0009_lang_activity_anagraphic_anagidentifier_and_more.py`
- **100% compatibilità** importazione AEF garantita
- **Django Admin** configurato con inlines per tutti i modelli correlati
- **System Check**: Nessun errore rilevato (`python manage.py check`)

---

## Rilascio v0.13.0 - Allineamento Interfaccia a Archimista Ruby (2026-04-02)

### Cosa è stato fatto nella Fase 11

#### 1. Form Unità - Riorganizzazione completata

**Nuove sezioni (allineate ad Archimista Ruby):**
- **Descrizione**: Titolo, contenuto, contesto, identificazione, identificativi alternativi, altre segnature, lingue
- **Descrizione fisica**: Tipo supporto, descrizione fisica, stato conservazione, danni
- **Accesso**: Condizioni accesso/uso con note
- **Fonti**: RelUnitSource, RelUnitHeading, RelUnitAnagraphic
- **Compilatori**: UnitEditor formset inline
- **Schede Speciali**: SC2, ICCD, FSC, FE (già esistenti)

#### 2. Form Fondi - Riorganizzazione completata

**Nuove sezioni (allineate ad Archimista Ruby):**
- **Descrizione**: Nome fondo, tipologia, estensione, abstract, descrizione, storia, nomi alternativi, identificativi, lingue
- **Altre informazioni**: Materiali correlati, tipo materiali, note, possessori, URL
- **Accesso**: Condizioni accesso/uso/conservazione, tipo descrizione
- **Relazioni**: Voci di indice, forme documentarie
- **Fonti**: RelFondSource
- **Compilatori**: FondEditor

#### 3. Formset Inline Aggiunti

**Per Unità:**
- `UnitIdentifierFormSet` - Identificativi dell'unità
- `UnitOtherReferenceNumberFormSet` - Altre segnature
- `UnitLangFormSet` - Lingue dell'unità
- `UnitDamageFormSet` - Danni
- `UnitUrlFormSet` - URL
- `UnitEditorFormSet` - Compilatori
- `RelUnitHeadingFormSet` - Voci di indice
- `RelUnitSourceFormSet` - Fonti
- `RelUnitAnagraphicFormSet` - Anagrafiche

#### 4. JavaScript per Formset Dinamici

- Funzione generica `setupFormset()` per gestire tutti i formset
- Pulsanti "Aggiungi" per ogni formset inline
- Clonazione corretta delle righe con aggiornamento indici
- Aggiornamento automatico `TOTAL_FORMS`

**Formset con JavaScript dinamico:**
- Fond: `fond_name`, `fond_identifier`, `fond_lang`, `fond_owner`, `fond_url`, `fond_editor`, `rel_fond_heading`, `rel_fond_source`, `rel_fond_document`
- Unit: `unit_identifier`, `unit_other_reference_number`, `unit_lang`, `unit_damage`, `unit_editor`, `rel_unit_heading`, `rel_unit_source`, `rel_unit_anagraphic`

#### 5. File Modificati

**forms.py:**
- Aggiunti form per tutte le estensioni Unità
- Aggiunti formset inline per relazioni Unità

**views.py:**
- Aggiornata `UnitUpdateView` con tutti i formset per estensioni
- Salvataggio automatico in transazione atomica

**templates:**
- `unit_form.html` - Completamente riscritto con 6 tab
- `fond_form.html` - Completamente riscritto con 6 tab

### Risultati della Validazione
- `python manage.py check` - Nessun errore
- `python manage.py migrate` - Migrazioni applicate
- `python manage.py runserver` - Server si avvia correttamente

---

## Rilascio v0.14.0 - Allineamento Vocabolari a Archimista Ruby (2026-04-02)

### Cosa è stato fatto nella Fase 12

#### 1. Problema Riscontrato
- I vocabolari Python avevano termini generici non allineati a Ruby
- Ruby usa termini specifici italiani (es. "lacune", "rottura delle cuciture")
- L'import AEF salvava valori che non corrispondevano ai vocabolari Python

#### 2. Fonte dei Vocabolari Ruby
```
/home/srbntt/Documenti/ProgrammiInformatici/archimista/db/seeds/
├── vocabularies.json    # 30 vocabolari definiti
└── terms.json           # 200+ termini con vocabulary_id
```

**Mappatura vocabulary_id → nome:**
- `12` → `units.preservation` (ottimo, buono, discreto, mediocre, cattivo, pessimo)
- `13` → `units.unit_type` (registro, fascicolo, unità documentaria)
- `14` → `unit_damages.code` (23 termini, incluso "lacune", "rottura delle cuciture")
- `22` → `units.physical_type` (21 termini: busta, cartella, fascicolo, ecc.)
- `23` → `units.medium` (carta, pergamena, carta telata, cartoncino, pellicola)

#### 3. Soluzione Implementata
- Aggiornato `seed_vocabularies.py` con termini esatti da Ruby
- Approccio ibrido: campo testo con datalist per suggerimenti
- Compatibile con import AEF (valori testuali)

#### 4. File Modificati
- `seed_vocabularies.py` - Termini allineati a Ruby
- `archimista_python/archive/forms/unit.py` - UnitDamageForm con datalist
- `archimista_python/archive/views/unit.py` - Passa termini ai template
- `archimista_python/archive/templates/archive/unit_form.html` - Datalist per suggerimenti

#### 5. Documentazione Creata
- **VOCABOLARI_GUIDA.md** - Guida completa con elenco vocabolari e istruzioni

### Risultati della Validazione
- 30 vocabolari, 200+ termini creati
- Import AEF funziona con valori "lacune" e "rottura delle cuciture"
- Form visualizza suggerimenti dal vocabolario mentre si digita

---

## Rilascio v0.15.0 - Show/Hide Dinamico Campi SC2/FSC/FE (2026-04-03)

### Cosa è stato fatto nella Fase 13

#### 1. Problema Riscontrato
- Tutte le schede speciali (SC2, ICCD, FSC, FE) erano sempre visibili nel form unità
- In Ruby Archimista, i campi appaiono dinamicamente in base al tipo di unità selezionato
- I campi SC2 avevano sfondo giallo (`#F5F5C8`) in Ruby ma non in Python
- La tab "Schede Speciali" era separata, mentre in Ruby i campi sono integrati nei tab Descrizione/Descrizione Fisica

#### 2. Campi Aggiunti al Modello Sc2
```python
# archive/models/sc2.py
sdts = models.CharField(...)  # Rappresentazione tematica (sc2_cars)
lrd = models.CharField(...)   # Data della ripresa (sc2_f)
cmmr = models.CharField(...)  # Numero di commessa (sc2_dt)
ort = models.CharField(...)   # Orientamento (sc2_cars)
```
- Migrazione `0014_add_sc2_extra_fields.py` creata e applicata

#### 3. Form Aggiornati
**UnitForm:**
- Aggiunto `sc2_tsk` (ChoiceField: CARS, D, DT, F, S)
- Aggiunto `file_type` (ChoiceField: personale, edilizia)
- Aggiunti `fsc_name`, `fsc_surname`

**Sc2Form:**
- Aggiunti campi `sdts`, `lrd`, `cmmr`, `ort`
- Tutti i campi hanno classe CSS `sc2_field` (sfondo giallo)

#### 4. JavaScript (Porting di `units-sc.js`)
Logica a 3 livelli identica a Ruby:

```
Livello 1: unit_type
  ├─ "unità documentaria" → mostra sc2_tsk, nascondi file_type
  ├─ "fascicolo..." → mostra file_type, nascondi sc2_tsk
  └─ altro → nascondi entrambi

Livello 2a: sc2_tsk
  ├─ Vuoto → mostra physical_type, nascondi SC2
  ├─ "CARS" → mostra sc2_all + sc2_cars
  ├─ "D" → mostra sc2_all + sc2_d
  ├─ "DT" → mostra sc2_all + sc2_dt
  ├─ "F" → mostra sc2_all + sc2_f
  └─ "S" → mostra sc2_all + sc2_s

Livello 2b: file_type
  ├─ Vuoto → nascondi FSC e FE
  ├─ "personale" → mostra FSC, nascondi FE
  └─ "edilizia" → mostra FE, nascondi FSC
```

**Fix critico:** Django `ModelChoiceField` usa gli ID del database come valori delle `<option>` (es. `180`, `181`, `182`), mentre Ruby usa il testo direttamente. Le funzioni `isUnitDocumentaria()` e `isUnitFascicolo()` leggono il testo con `jqEl.find('option:selected').text()`.

#### 5. Template Riorganizzato
- **Tab Descrizione**: Tipo Unità, Scheda Speciale, Tipologia Fascicolo, FSC name/surname, container SC2, container FSC, container FE
- **Tab Descrizione Fisica**: `div_physical_type_wrapper` (tipo fisico, supporto), campi SC2 specifici, container FE (opera, progettisti, catastali, particelle)
- **Rimossa tab "Schede Speciali" separata**

#### 6. CSS Allineato
```css
.sc2_field { background-color: #F5F5C8; }
.fsc_organization, .fsc_nationality, .fsc_code, .fsc_open, .fsc_close { display: none; }
```

#### 7. Viste Aggiornate
- `UnitCreateView`: riscritta come `View` con GET/POST completi per tutti i formset
- `UnitUpdateView`: già completa

### Risultati della Validazione
- `python manage.py check` - Nessun errore
- `python manage.py migrate` - Migrazione applicata
- `python manage.py runserver` - Server si avvia correttamente
- 91 occorrenze di classi SC2 nel HTML renderizzato
- Tutti i container con classi modificatrici corretti (sc2_all, sc2_cars, sc2_dt, sc2_f, ecc.)

---

## Rilascio v0.16.0 - Refactor Forms/Views in Moduli (2026-04-03)

### Cosa è stato fatto nella Fase 14

#### 1. Refactor forms.py
- **Prima:** 1 file da 970 righe (`archimista_python/archive/forms.py`)
- **Dopo:** 9 moduli in `archimista_python/archive/forms/`:
  - `__init__.py` — Re-export per compatibilità
  - `fond.py` — FondForm + estensioni + formset (188 righe)
  - `unit.py` — UnitForm + estensioni + formset (223 righe)
  - `creator.py` — CreatorForm + estensioni + formset (138 righe)
  - `custodian.py` — CustodianForm + estensioni + formset (130 righe)
  - `sc2.py` — Schede SC2 (96 righe)
  - `iccd.py` — Schede ICCD (61 righe)
  - `fsc.py` — FSC (64 righe)
  - `fe.py` — FE (101 righe)

#### 2. Refactor views.py
- **Prima:** 1 file da 1.265 righe (`archimista_python/archive/views.py`)
- **Dopo:** 9 moduli in `archimista_python/archive/views/`:
  - `__init__.py` — Re-export per compatibilità
  - `fond.py` — CRUD Fondi (151 righe)
  - `unit.py` — CRUD Unità (566 righe)
  - `creator.py` — CRUD Creator (217 righe)
  - `custodian.py` — CRUD Custodian (204 righe)
  - `tree.py` — API albero archivistico (62 righe)
  - `search.py` — Ricerca globale (46 righe)
  - `export.py` — Export PDF/DOCX (25 righe)
  - `import_view.py` — Import AEF (34 righe)

#### 3. Compatibilità
- Tutti gli import esistenti funzionano grazie a `__init__.py` con re-export
- `python manage.py check` — Nessun errore
- `python manage.py runserver` — Server si avvia correttamente

### Risultati della Validazione
- **28 moduli** totali per organizzazione codice (10 models + 9 forms + 9 views)
- Compatibilità totale con codice esistente
- Nessun breaking change

---

## Rilascio v0.17.0 - Riorganizzazione Struttura Progetto (2026-04-03)

### Cosa è stato fatto nella Fase 15

#### 1. Problema Riscontrato
- La directory `archive/` era fuori da `archimista_python/`, non seguendo la convenzione Django
- Confusione tra directory del progetto (`archimista_python/`) e app (`archive/`)

#### 2. Soluzione Implementata
- Spostato `archive/` dentro `archimista_python/`
- Aggiornati 3 file di configurazione:
  - `settings.py`: `'archive'` → `'archimista_python.archive'`
  - `urls.py`: `'archive.urls'` → `'archimista_python.archive.urls'`
  - `apps.py`: `name = 'archimista_python.archive'` + `label = 'archive'`
- Aggiornati 21 file con import interni: `from archive.` → `from archimista_python.archive.`

#### 3. Compatibilità
- `label = 'archive'` mantiene i nomi delle tabelle DB invariati
- Nessun cambiamento nel database o nelle migrazioni
- Script esterni (`seed.py`, `*_vocabularies.py`) funzionano invariati

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py runserver` — Server si avvia correttamente
- Struttura ora segue le convenzioni Django standard

---

## Rilascio v0.18.0 - Fix Sincronizzazione Campi e Refactoring Template (2026-04-03)

### Cosa è stato fatto nella Fase 18

#### 1. Fix sincronizzazione `unit_type_term` ↔ `unit_type`

**Problema:** Modificando un'unità esistente, il dropdown "Tipo unità" non era pre-selezionato.

**Soluzione:**
- `forms/unit.py` — `__init__`: se l'istanza ha `unit_type` ma non `unit_type_term`, trova il termine corrispondente
- `forms/unit.py` — `save()`: sincronizza i due campi al salvataggio
- Template: campo nascosto `<input type="hidden" name="unit_type">`

#### 2. Fix sincronizzazione `sc2_tsk` ↔ `card_type`

**Problema:** Schede esistenti con `card_type='SC3'` non venivano riconosciute dal form (che usa `'F'`).

**Soluzione:**
- `views/unit.py` — mappatura `card_type` → `sc2_tsk` (`'SC3'` → `'F'`)
- Salvataggio: `sc2_tsk` → `card_type` in entrambe le viste (create e update)
- Database: aggiornate 2 schede da `'SC3'` a `'F'`
- Template detail: gestiti entrambi i valori per retrocompatibilità

#### 3. Unit Detail View completamente riscritta

**Prima:** Template base con dati essenziali e schede minimali.

**Dopo:** 8 tab completi in lettura (Descrizione, Descrizione fisica, Accesso, Fonti, Compilatori, SC2/SC3, ICCD, FSC, FE). Tab appaiono dinamicamente solo se i dati esistono.

#### 4. Refactoring template in partial

**Prima:** `unit_form.html` 1178 righe, `unit_detail.html` 814 righe.

**Dopo:** 14 partial in `templates/archive/units/partials/`:
- 5 per il form (367 + 207 + 37 + 69 + 43 righe)
- 9 per il detail (105 + 39 + 33 + 33 + 30 + 125 + 53 + 65 + 81 righe)

**Risultato:** file principali ridotti a 279 e 110 righe (−76% e −86%).

#### 5. Correzione capitalizzazione italiana

Tutti i titoli seguono ora la regola italiana (solo prima parola maiuscola):
- "Descrizione fisica", "Accesso e utilizzo", "Tipo unità", "Stato di conservazione", "Dati catastali", ecc.

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py runserver` — Server si avvia correttamente
- Template più manutenibili e leggibili
- Pre-selezione campi corretta in modifica

---

## Rilascio v0.19.0 - Allineamento Vocabolari e Fix Critici (2026-04-03)

### Cosa è stato fatto nella Fase 19

#### 1. Fix modello `Term.__str__`

**Problema:** `__str__` restituiva `self.term` che era vuoto. Le combo apparivano senza testo.

**Soluzione:** `return self.term_value or self.term or self.term_key or str(self.pk)`

#### 2. Allineamento `units.medium` a Ruby SC2

**Prima:** 6 termini generici (carta, pergamena, carta telata, cartoncino, pellicola, altro).

**Dopo:** Campo testo con `<datalist>` filtrato per tipo SC2:
- **F (Fotografia):** 41 termini (albumina/carta, ambrotipo, dagherrotipo, gelatina bromuro d'argento/carta, stampa lambda/carta, ecc.)
- **CARS:** 8 termini
- **D:** 36 termini
- **DT:** 9 termini
- **S:** 19 termini

#### 3. Allineamento `access_condition` e `use_condition` a Ruby

**Prima:** Termini inventati ("Completamente accessibile", "Senza restrizioni").

**Dopo:** Termini esatti da Ruby:
- Accesso: liberamente accessibile, accessibile previa autorizzazione, non consultabile, parzialmente accessibile
- Uso: libera, consentita per uso studio, a pagamento, negata

#### 4. Fix `fonds.preservation`

Rimossi termini extra ("Richiede restauro"), allineato a Ruby (ottimo, buono, discreto, mediocre, cattivo, pessimo).

#### 5. Fix struttura form: `physical_type` dentro wrapper

Spostato dentro `div_physical_type_wrapper` → nascosto con SC2 (come Ruby).

#### 6. Sincronizzazione campi term per Unit e Fond

Estesa a tutti i campi: `access_condition_term`, `use_condition_term`, `preservation_term`, `physical_type_term` (Unit) + `fond_type_term`, `access_condition_term`, `use_condition_term`, `preservation_term` (Fond).

#### 7. Fix formset `is_valid()` prima di `save()`

**Problema:** `AttributeError: 'Sc2TechniqueForm' object has no attribute 'cleaned_data'`.

**Soluzione:** Tutti i formset chiamano `is_valid()` prima di `save()`, raggruppati in loop.

### Risultati della Validazione
- `python manage.py check` — Nessun errore
- `python manage.py runserver` — Server si avvia correttamente
- Combo pre-selezionate correttamente in modifica
- Supporti filtrati per tipo SC2
- Salvataggio unità senza errori
