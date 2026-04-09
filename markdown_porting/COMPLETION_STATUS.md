# Stato di Completamento - Archimista Python/Django

**Data:** 2026-04-09
**Versione:** 0.54.0 (Select2 ibrido, Export XML SAN/EAD/METS, Refactor AEF)

---

## Riepilogo Generale

| Categoria | Stato | Note |
|-----------|-------|------|
| **Modelli Database** | ✅ 100% | Tutti i 130+ modelli implementati (v0.46.0: +25 related_name) |
| **Migrazioni** | ✅ 100% | Tutte le tabelle create (incl. 0025_relcreatorfond) |
| **Autenticazione** | ✅ 100% | Single-user admin, login/logout, cambio password obbligatorio al primo accesso (v0.45.0) |
| **Import AEF** | ✅ 100% | Tutti i modelli supportati + 15+ handler aggiunti (v0.44.0) |
| **Export AEF** | ✅ 100% | Round-trip completo + compatibile con Ruby (v0.53.0) + refactor modulare (v0.54.0) |
| **Export XML** | ✅ 100% | CAT-SAN, EAD3/EAC-CPF/SCONS2, METS — 4 opzioni come Ruby (v0.54.0) |
| **Compatibilità Ruby** | ✅ 100% | Ruby importa AEF Python, unità visibili, confronto AEF/PDF/RTF PASS (v0.53.0) |
| **Export CSV** | ✅ 100% | Export unità con filtri (v0.44.0) |
| **Export PDF/RTF** | ✅ 100% | Report inventario completo identico a Ruby: 29 campi Fond, 49 Unit, 18 Creator, 32 Custodian, 10 Project + schede SC2/ICCD/FSC/FE (v0.46.0) |
| **Report** | ✅ 100% | Report inventario (fond), progetto, conservatore — PDF (WeasyPrint) + RTF (RtfBuilder custom) (v0.46.0) |
| **Ricerca Avanzata** | ✅ 100% | Filtri multipli per tipo entità, fondo, tipo, pubblicati (v0.44.0) |
| **Django Admin** | ✅ 100% | Tutti i modelli registrati |
| **Menu Navigazione** | ✅ 100% | Completo: Schede + Strumenti (Inventario completo, Esporta AEF, CSV, Report, Ricerca avanzata, Titolario, Controllo qualità, Compilatori) |
| **Interfaccia Web - Form Unit** | ✅ 100% | Tutti i campi Ruby presenti + etichette i18n corrette (v0.26.0) + classificazione (v0.34.0) |
| **Interfaccia Web - Form Fond** | ✅ 100% | arrangement_note aggiunto, etichette i18n corrette (v0.26.0) |
| **Interfaccia Web - Form Creator** | ✅ 100% | Condizione giuridica formset aggiunto (v0.26.0) |
| **Interfaccia Web - Form Custodian** | ✅ 100% | editing_type da vocabolario (v0.26.0) |
| **Interfaccia Web - Template** | ✅ 100% | Refactoring in partial, capitalizzazione italiana, etichette i18n (v0.26.0) |
| **Unit Detail View** | ⚠️ 90% | Tutte le schede in lettura con tab (v0.18.0) + classificazione (v0.34.0). **Manca:** storico modifiche, log compilatori |
| **Formset Inline** | ✅ 100% | Tutti i formset Ruby implementati (v0.26.0) |
| **JavaScript Dinamico** | ✅ 100% | Show/hide SC2/FSC/FE + filtraggio supporti per tipo (v0.19.0) |
| **Vocabolari Controllati** | ✅ 100% | Allineati 100% a Ruby (termini esatti da terms.json e sc2_terms.json) (v0.24.0) |
| **Sezione Compilatori Unità** | ✅ 100% | Allineata a Ruby: dropdown editing_type, link aggiungi, salvataggio corretto (v0.20.0) |
| **Menu Navigazione** | ✅ 100% | Completo: Schede + Strumenti (Esporta AEF, CSV, Report, Ricerca avanzata, Titolario, Controllo qualità, Compilatori) + dropdown utente con logout (v0.45.0) |
| **Viste Entità di Servizio** | ✅ 100% | CRUD completo per tutte le 8 entità di servizio (v0.40.0) |
| **CRUD Fonti (Source)** | ✅ 100% | Allineato a Ruby: 2 tab (Descrizione, Relazioni), formset URL, tipologie gerarchiche (v0.28.0) |
| **CRUD Profili istituzionali (Institution)** | ✅ 100% | Allineato a Ruby: 3 campi (Denominazione, Descrizione, Annotazioni), formset compilatori con editing_type da vocabolario (v0.29.0) |
| **CRUD Voci di indice (Heading)** | ✅ 100% | Allineato a Ruby: 4 campi (Tipologia, Lemma, Estremi cronologici, Qualifica), vocabolario corretto (Ente, Persona, Famiglia, Toponimo, Altro) (v0.30.0) |
| **CRUD Anagrafiche (Anagraphic)** | ✅ 100% | Allineato a Ruby: Scheda anagrafica, Nome/Cognome obbligatori, formset Codici identificativi PRIMA dei campi principali, etichette i18n (v0.31.0) |
| **CRUD Profili documentari (DocumentForm)** | ✅ 100% | Allineato a Ruby: 3 campi (Denominazione, Descrizione, Note), formset Compilatori con editing_type da vocabolario (v0.32.0) |
| **Form Soggetto Produttore** | ✅ 100% | Allineato a Ruby: 5 tab, denominazione dinamica per tipo, 18 tipi di ente da Ruby, relazioni con fondi (v0.22.0) |
| **Form Soggetto Conservatore** | ✅ 100% | Allineato a Ruby: 7 tab, denominazione principale separata, formset completi, relazioni (v0.23.0) |
| **Form Progetti (CRUD)** | ✅ 100% | Allineato a Ruby: 3 tab (Identificazione, Responsabilità, Relazioni), etichette esatte, termini vocabolario sincronizzati (v0.24.0) |
| **Estremi Cronologici (Form)** | ✅ 100% | Allineati a Ruby: 2 radio (data puntuale/secolare), combo specifiche, secolo, intervallo (v0.25.0) |
| **Estremi Cronologici (Import AEF)** | ✅ 100% | Import unit_event e fond_event dall'AEF (v0.25.0) |
| **Estremi Cronologici (Detail)** | ✅ 100% | Visualizzazione in lettura per Unit, Fond, Creator (v0.25.0) |
| **JavaScript Formset Buttons** | ✅ 100% | Tutti i pulsanti "Aggiungi..." funzionano, prefix uniformati, pattern unificato (v0.27.0) |
| **Fond Detail View** | ✅ 100% | 7 tab completi allineati al form Ruby (v0.27.0) |
| **Creator Detail View** | ✅ 100% | 5+ tab completi allineati al form Ruby (v0.27.0) |
| **Custodian Detail View** | ✅ 100% | Campo "Pubblicato" aggiunto (v0.27.0) |
| **Unit Detail View** | ✅ 100% | Tutti i campi form presenti in lettura (v0.27.0) |
| **Albero Interattivo** | ✅ 100% | +, −, rinomina, drag & drop, cestino, ripristino (v0.35.0) |
| **Classificazione di Massa** | ✅ 100% | Checkbox unità + modale albero + sposta sotto fondo (v0.35.0) |

---

## Cosa È Stato Completato

### 1. Modelli (100% ✅)

Tutti i modelli di Archimista Ruby sono stati portati in Django:

#### Modelli Core
- ✅ `Group`, `Fond`, `Unit`, `Creator`, `Custodian`, `Heading`
- ✅ `DigitalObject` (con GenericForeignKey polimorfico)
- ✅ `Classification`, `BiogHist`, `Event`
- ✅ `Institution`, `Source`

#### Estensioni Fond
- ✅ `FondName`, `FondIdentifier`, `FondLang`, `FondOwner`, `FondUrl`, `FondEditor`

#### Estensioni Unit
- ✅ `UnitIdentifier`, `UnitOtherReferenceNumber`, `UnitLang`, `UnitDamage`, `UnitUrl`, `UnitEditor`

#### Estensioni Creator
- ✅ `CreatorName`, `CreatorLegalStatus`, `CreatorUrl`, `CreatorIdentifier`, `CreatorActivity`, `CreatorEditor`

#### Estensioni Custodian
- ✅ `CustodianName`, `CustodianIdentifier`, `CustodianContact`, `CustodianBuilding`, `CustodianOwner`, `CustodianUrl`, `CustodianEditor`

#### Schede SC2 (Disegni/Foto)
- ✅ `Sc2` (con card_type SC2/SC3)
- ✅ `Sc2TextualElement`, `Sc2VisualElement`, `Sc2Author`, `Sc2Commission`, `Sc2CommissionName`, `Sc2Technique`, `Sc2Scale`

#### Schede ICCD (Beni Culturali)
- ✅ `IccdDescription`, `IccdTechSpec`, `IccdSubject`, `IccdDamage`, `IccdAuthor`

#### FSC (Fascicoli Sanitari Edilizia)
- ✅ `FscCode`, `FscOrganization`, `FscNationality`, `FscOpen`, `FscClose`

#### FE (Fabbricati Edilizia)
- ✅ `FeIdentification`, `FeContext`, `FeOpera`, `FeDesigner`, `FeCadastral`, `FeLandParcel`, `FeFractLandParcel`, `FeFractEdilParcel`

#### Modelli Relazionali
- ✅ `RelCreatorFond`, `RelCustodianFond`, `RelFondHeading`, `RelUnitHeading`
- ✅ `RelCreatorCreator`, `RelCreatorInstitution`, `RelCreatorSource`
- ✅ `RelCustodianSource`, `RelFondSource`, `RelUnitSource`
- ✅ `RelFondDocumentForm`, `RelProjectFond`, `RelUnitAnagraphic`

#### Altri Modelli
- ✅ `Project`, `DocumentForm`, `Anagraphic`, `Place`, `Lang`, `Term`, `Vocabulary`
- ✅ `Export`, `Import`, `Editor`, `Activity`, `DocumentFormEditor`, `AnagIdentifier`
- ✅ `CreatorAssociationType`, `CreatorCorporateType`, `CustodianType`

### 2. Migrazioni (100% ✅)

- ✅ Migration `0009_lang_activity_anagraphic_anagidentifier_and_more.py` creata e applicata
- ✅ 70+ nuove tabelle create nel database

### 3. Import AEF (100% ✅)

- ✅ `import_utils.py` aggiornato con metodi per tutti i modelli
- ✅ Rilevamento automatico SC2 vs SC3 basato su `sc2_tsk`
- ✅ Supporto per tutte le relazioni

### 4. Django Admin (100% ✅)

- ✅ Tutti i modelli registrati in `admin.py`
- ✅ Inline configurati per Fond, Creator, Custodian, Unit
- ✅ Formset per modelli correlati

### 5. Form (100% ✅)

- ✅ `FondForm` - completo con tutti i campi base
- ✅ `FondNameForm`, `FondIdentifierForm`, `FondLangForm`, `FondOwnerForm`, `FondUrlForm`, `FondEditorForm` - formset per estensioni
- ✅ `RelFondHeadingForm`, `RelFondSourceForm`, `RelFondDocumentFormForm` - formset per relazioni
- ✅ `UnitForm` - dati generali
- ✅ `Sc2Form` + tutti i formset SC2
- ✅ `IccdDescriptionForm`, `IccdTechSpecForm` + formset
- ✅ Tutti i form FSC e FE
- ✅ `CreatorForm` - completo con tutti i campi base
- ✅ `CreatorNameForm`, `CreatorLegalStatusForm`, `CreatorUrlForm`, `CreatorIdentifierForm`, `CreatorActivityForm`, `CreatorEditorForm` - formset per estensioni
- ✅ `RelCreatorCreatorForm`, `RelCreatorInstitutionForm`, `RelCreatorSourceForm` - formset per relazioni
- ✅ `CustodianForm` - completo con tutti i campi base
- ✅ `CustodianNameForm`, `CustodianIdentifierForm`, `CustodianContactForm`, `CustodianBuildingForm`, `CustodianOwnerForm`, `CustodianUrlForm`, `CustodianEditorForm` - formset per estensioni
- ✅ `RelCustodianSourceForm` - formset per relazioni

### 6. Viste (85% ⚠️)

- ✅ `FondListView`, `FondDetailView`, `FondCreateView`, `FondUpdateView` (completa con formset), `FondDeleteView`
- ✅ `UnitCreateView`, `UnitUpdateView` (refactored con handler v0.37.0), `UnitDetailView`, `UnitDeleteView`
- ✅ `CreatorListView`, `CreatorDetailView`, `CreatorCreateView`, `CreatorUpdateView` (completa con formset), `CreatorDeleteView`
- ✅ `CustodianListView`, `CustodianDetailView`, `CustodianCreateView`, `CustodianUpdateView` (completa con formset), `CustodianDeleteView`
- ✅ `GlobalSearchView`
- ✅ `ExportFondPDFView`, `ExportFondRTFView`
- ✅ `ImportAEFView`
- ✅ API albero archivistico (`tree_data`, `tree_children`)
- ✅ **Estremi cronologici (Eventi)** — formset inline completi in Unit, Fond, Creator (v0.25.0 + v0.26.0)
- ✅ **BiogHist** — campo `history` presente nei form Fond/Creator (come in Ruby, nessun form dedicato)
- ✅ **Tutte le 8 entità di servizio con CRUD completo** (v0.40.0)

### 7. Template (90% ✅)

- ✅ `fond_list.html`, `fond_detail.html`, `fond_form.html` (completo con tab per tutte le sezioni)
- ✅ `unit_form.html` (completo con tab per tutte le schede)
- ✅ `unit_detail.html`
- ✅ `creator_list.html`, `creator_detail.html`, `creator_form.html`, `creator_confirm_delete.html`
- ✅ `custodian_list.html`, `custodian_detail.html`, `custodian_form.html`, `custodian_confirm_delete.html`
- ✅ `search_results.html`, `tree_view.html`, `import_form.html`
- ✅ Template conferma eliminazione

### 8. Correzioni Bug (100% ✅)

- ✅ Template tag spezzati su più righe (fond_detail, unit_detail, search_results, import_form)
- ✅ Link unità-fondi durante importazione AEF
- ✅ Rilevamento automatico fotografie (SC3) vs disegni (SC2)
- ✅ NoReverseMatch per fond_detail - corretto namespace archive:
- ✅ Bootstrap JavaScript aggiunto per far funzionare i tab
- ✅ Gestione sicura per unit.fond None in UnitUpdateView

---

## Cosa Manca o È Parziale

### 1. Interfaccia Web - Form (✅ COMPLETATO - v0.26.0)

**Stato:** Tutti i campi Ruby sono ora presenti nei form Python. Etichette allineate a i18n Ruby.

**Implementato:**
- ✅ Fond: tutti i campi inclusi `arrangement_note` ("Nota dell'archivista")
- ✅ Unit: tutti i campi inclusi `given_title`, `extent`, `arrangement_note`, `tmp_reference_number`, `tmp_reference_string`, `folder_number`, `file_number`, `related_materials`, `preservation_note`, `restoration`, `note`, `physical_container_*`, formset `unit_urls`, `unit_identifiers`, `fe_fract_land_parcels`, `fe_fract_edil_parcels`, nested SC2
- ✅ Creator: formset `creator_legal_statuses` ("Condizione giuridica")
- ✅ Custodian: `editing_type` da vocabolario (7 termini) invece di hardcoded
- ✅ Etichette i18n: tutte allineate a Ruby (`config/locales/it.yml`)

---

### 2. Gestione Relazioni (✅ COMPLETATO - v0.33.0)

**Stato attuale:** Tutte le relazioni sono gestite nell'interfaccia con autocomplete Select2.

**Relazioni gestite nell'interfaccia:**
- ✅ Fondi ↔ Voci di Indice (`RelFondHeading`) — Select2
- ✅ Fondi ↔ Fonti (`RelFondSource`) — Select2
- ✅ Fondi ↔ Forme Documentarie (`RelFondDocumentForm`) — Select2
- ✅ Custodi ↔ Fonti (`RelCustodianSource`) — Select2
- ✅ Custodi ↔ Fondi (`RelCustodianFond`) — Select2
- ✅ Unità ↔ Fonti (`RelUnitSource`) — Select2
- ✅ Unità ↔ Voci di Indice (`RelUnitHeading`) — Select2
- ✅ Unità ↔ Anagrafiche (`RelUnitAnagraphic`) — Select2
- ✅ Creatori ↔ Altri Creatori (`RelCreatorCreator`) — Select2
- ✅ Creatori ↔ Istituzioni (`RelCreatorInstitution`) — Select2
- ✅ Creatori ↔ Fonti (`RelCreatorSource`) — Select2
- ✅ Creatori ↔ Fondi (`RelCreatorFond`) — Select2
- ✅ Progetti ↔ Fondi (`RelProjectFond`) — Select2

**Implementazione:**
- Widget `django-select2` con ricerca AJAX per tutte le relazioni
- 8 widget specializzati: Fond, Creator, Custodian, Source, Institution, Heading, Anagraphic, DocumentForm
- Cloning corretto delle righe con reinizializzazione Select2
- Checkbox "Elimina" visibile e funzionante per tutti i formset relazione

---

### 6. Ricerca (✅ COMPLETATO - v0.44.0)

**Implementato:**
- ✅ `GlobalSearchView` — ricerca globale di base
- ✅ `AdvancedSearchView` — ricerca avanzata con filtri multipli (tipo entità, fondo, tipo unità, tipo produttore, solo pubblicati)
- ✅ Paginazione risultati (50 per pagina)
- ✅ Template `advanced_search.html` con form filtri e tabella risultati

---

### 7. Esportazione (✅ COMPLETATO - v0.44.0)

**Implementato:**
- ✅ PDF e DOCX per inventari fondi
- ✅ **AEF** — esportazione completa round-trip compatibile con import (fondi, unità, entità, relazioni, schede specialistiche, oggetti digitali)
- ✅ **CSV** — esportazione unità con filtri
- ✅ Pulsante "Esporta AEF" nella detail del fondo

---

### 8. Sistema di Permessi (✅ COMPLETATO - v0.45.0)

**Stato:** Autenticazione singolo utente implementata. Password hashata con PBKDF2-SHA256 (1.2M iterazioni).

**Implementato:**
- ✅ Modello `UserProfile` con flag `must_change_password`
- ✅ Middleware `LoginRequiredMiddleware` — tutte le pagine richiedono login
- ✅ Login, logout, cambio password obbligatorio al primo accesso
- ✅ Dropdown utente in navbar con "Cambia password" e "Esci"
- ✅ Seed script `seed_admin_user.py` per creare l'admin iniziale

**Da fare (opzionale, multi-utente):**
- [ ] Integrazione con sistema Group originale di Archimista
- [ ] Permessi per gruppo di utenti
- [ ] Permessi per fondo/archivio specifico
- [ ] Ruoli (admin, catalogatore, consultatore)

---

### 9. Oggetti Digitali (✅ COMPLETATO - v0.42.0)

**Stato:** Upload file con Pillow per thumbnail, nested polimorfico, form con validazione.

---

### 10. Entità di Servizio - CRUD (✅ COMPLETATO - v0.40.0)

Tutte le 8 entità di servizio hanno CRUD completo!

---

### 11. Classificazione/Titolario (✅ COMPLETATO - v0.34.0 + v0.35.0)

Completato con albero interattivo e classificazione di massa.

---

### 12. Biografie ed Eventi (✅ COMPLETATO - v0.25.0)

Modelli implementati, formset inline in Unit/Fond/Creator, import AEF.

---

### 13. Validazioni e Controlli (✅ COMPLETATO - v0.43.0 + v0.44.0)

- ✅ Controllo qualità per Fond, Creator, Custodian (v0.43.0)
- ✅ Storico modifiche EditorLog (v0.44.0)

---

### 14. UI/UX (✅ MIGLIORATO - v0.44.0)

- ✅ Report progetto e conservatore
- ✅ Ricerca avanzata con filtri
- ✅ Menu Strumenti completo

---

### 15. Performance (⚠️ DA OTTIMIZZARE - Opzionale)

- [ ] Cache per viste frequentemente accessate
- [ ] Lazy loading per alberi grandi
- [ ] Indicizzazione database per ricerche veloci

---

### 16. Campi a Scelta con Vocabolari Controllati (✅ IMPLEMENTATO - v0.11.0)

**Stato:** Implementato nella versione 0.11.0.

**Implementato:**
- ✅ Modelli `Term` e `Vocabulary` aggiornati con tutti i campi necessari (`term_key`, `term_value`, `position`, `vocabulary` FK)
- ✅ Foreign key aggiunte ai modelli `Fond` e `Unit` per i campi standardizzati
- ✅ Form aggiornati con `ModelChoiceField` per dropdown dinamici
- ✅ Vocabolari popolati con 77 termini standardizzati
- ✅ Viste aggiornate per passare le scelte ai form

**Campi implementati per Fond:**
- ✅ `fond_type_term` - Tipologia del fondo (11 opzioni: Collezione, Fondo, Serie, Fascicolo, ecc.)
- ✅ `access_condition_term` - Condizione di accesso (5 opzioni)
- ✅ `use_condition_term` - Condizione d'uso (5 opzioni)
- ✅ `preservation_term` - Stato di conservazione (6 opzioni)
- ✅ `description_type_term` - Tipo di descrizione (4 opzioni)

**Campi implementati per Unit:**
- ✅ `unit_type_term` - Tipo di unità (21 opzioni: Libro, Registro, Fascicolo, Fotografia, ecc.)
- ✅ `access_condition_term` - Condizione di accesso
- ✅ `use_condition_term` - Condizione d'uso
- ✅ `preservation_term` - Stato di conservazione

**Vocabolari disponibili:**
- `fonds.fond_type` (11 termini)
- `fonds.access_condition` (5 termini)
- `fonds.use_condition` (5 termini)
- `fonds.preservation` (6 termini)
- `fonds.description_type` (4 termini)
- `units.unit_type` (21 termini)
- `units.access_condition` (5 termini)
- `units.use_condition` (5 termini)
- `units.preservation` (6 termini)
- `creators.creator_type` (3 termini)
- `custodians.custodian_type` (6 termini)

**Funzionalità:**
- I dropdown mostrano "-- Seleziona --" come opzione predefinita
- I termini sono ordinati per posizione nel vocabolario
- I campi testo originali sono mantenuti per fallback e retrocompatibilità
- Possibilità di inserire valori personalizzati nei campi testo se necessario

**Da fare (opzionale):**
- [ ] Aggiungere vocabolari per ICCD (mtc, ogt)
- [ ] Aggiungere vocabolari per SC2 (tecniche, ruoli)
- [ ] Interfaccia admin per gestire termini e vocabolari
- [ ] Traduzione termini in più lingue

---

### 17. Refactor Codice in Moduli (✅ COMPLETATO - v0.12.0)

**Stato:** Completato nella versione 0.12.0.

**Implementato:**
- ✅ `models.py` (1900 righe) suddiviso in moduli separati nella directory `archimista_python/archive/models/`
- ✅ Mantenuta compatibilità con tutti gli import esistenti tramite `__init__.py`

**Nuova struttura:**
```
archive/models/
├── __init__.py          # Espone tutti i modelli per compatibilità
├── core.py              # Group, Fond, Unit, Creator, Custodian, Classification, Heading, DigitalObject
├── relations.py         # Tutti i modelli Rel* (relazioni molti-a-molti)
├── extensions.py        # Estensioni per Fond, Unit, Creator, Custodian
├── sc2.py               # Schede SC2 (disegni tecnici e fotografie)
├── iccd.py              # Schede ICCD (beni culturali)
├── fsc.py               # FSC (fascicoli sanitari edilizia)
├── fe.py                # FE (fabbricati edilizia)
├── vocabulary.py        # Term, Vocabulary (vocabolari controllati)
└── system.py            # Modelli di sistema: Institution, Source, BiogHist, Event, Project, ecc.
```

**Vantaggi:**
- Maggiore manutenibilità del codice
- File più piccoli e facili da navigare
- Separazione logica per dominio funzionale
- Compatibilità totale con codice esistente (forms, views, admin, template)

---

### 18. Allineamento Interfaccia a Archimista Ruby (✅ COMPLETATO - v0.13.0)

**Stato:** Completato nella versione 0.13.0.

**Implementato:**

#### A. Form Unità - Riorganizzazione completata

**Sezioni implementate (allineate ad Archimista Ruby):**

1. **Descrizione** ✅
   - Titolo (campo principale)
   - Contenuto (textarea grande)
   - Contesto (Fondo, Unità Padre)
   - Identificazione (Tipo unità, Segnatura)
   - Identificativi alternativi (formset inline `UnitIdentifier`)
   - Altre segnature (formset inline `UnitOtherReferenceNumber`)
   - Lingue (formset inline `UnitLang`)
   - Pubblicato (checkbox)

2. **Descrizione fisica** ✅
   - Descrizione fisica (textarea)
   - Tipo supporto (dropdown da vocabolario)
   - Stato conservazione (dropdown da vocabolario)
   - Danni (formset inline `UnitDamage`)

3. **Accesso** ✅
   - Condizione accesso (dropdown da vocabolario)
   - Nota accesso (textarea)
   - Condizione uso (dropdown da vocabolario)
   - Nota uso (textarea)

4. **Fonti** ✅
   - RelUnitSource formset inline
   - RelUnitHeading formset inline (voci di indice)
   - RelUnitAnagraphic formset inline (anagrafiche)

5. **Compilatori** ✅
   - UnitEditor formset inline
   - Data compilazione
   - Nome compilatore

6. **Schede Speciali** ✅
   - Scheda SC2 (Disegni Tecnici e Fotografie)
   - Scheda ICCD (Beni Culturali)
   - FSC (Fascicoli Sanitari Edilizia)
   - FE (Fabbricati Edilizia)

#### B. Form Fondi - Riorganizzazione completata

**Sezioni implementate (allineate ad Archimista Ruby):**

1. **Descrizione** ✅
   - Nome fondo
   - Tipologia (dropdown da vocabolario)
   - Estensione (lunghezza, entità)
   - Abstract
   - Descrizione (textarea grande)
   - Storia archivistica
   - Nomi alternativi (formset inline `FondName`)
   - Identificativi (formset inline `FondIdentifier`)
   - Lingue (formset inline `FondLang`)

2. **Altre informazioni** ✅
   - Materiali correlati
   - Tipo materiali
   - Note
   - Possessori (formset inline `FondOwner`)
   - URL (formset inline `FondUrl`)

3. **Accesso** ✅
   - Condizioni accesso (dropdown da vocabolario)
   - Condizioni uso (dropdown da vocabolario)
   - Conservazione (dropdown da vocabolario)
   - Tipo descrizione (dropdown da vocabolario)

4. **Relazioni** ✅
   - Voci di indice (formset inline `RelFondHeading`)
   - Forme documentarie (formset inline `RelFondDocumentForm`)

5. **Fonti** ✅
   - Fonti (formset inline `RelFondSource`)

6. **Compilatori** ✅
   - Curatori (formset inline `FondEditor`)

#### C. JavaScript per Formset Dinamici ✅

- [x] Funzione generica `setupFormset()` per gestire tutti i formset
- [x] Pulsanti "Aggiungi" per ogni formset inline
- [x] Clonazione corretta delle righe con aggiornamento indici
- [x] Gestione checkbox "Elimina" per rimuovere elementi
- [x] Aggiornamento automatico `TOTAL_FORMS`

**Formset con JavaScript dinamico:**
- `fond_name`, `fond_identifier`, `fond_lang`, `fond_owner`, `fond_url`, `fond_editor`
- `rel_fond_heading`, `rel_fond_source`, `rel_fond_document`
- `unit_identifier`, `unit_other_reference_number`, `unit_lang`, `unit_damage`, `unit_editor`
- `rel_unit_heading`, `rel_unit_source`, `rel_unit_anagraphic`

#### D. Template Riorganizzati ✅

- [x] `unit_form.html` - 6 tab principali (Descrizione, Descrizione Fisica, Accesso, Fonti, Compilatori, Schede Speciali)
- [x] `fond_form.html` - 6 tab principali (Descrizione, Altre Informazioni, Accesso, Relazioni, Fonti, Compilatori)
- [x] Breadcrumb di navigazione migliorato
- [x] Classi Bootstrap per styling coerente
- [x] Messaggi di errore inline per ogni campo
- [x] Label con indicazione campi obbligatori (*)

#### E. Form e Viste Aggiornati ✅

**Form aggiunti (ora in `archimista_python/archive/forms/`):**
- [x] `UnitIdentifierForm`, `UnitOtherReferenceNumberForm`, `UnitLangForm`
- [x] `UnitDamageForm`, `UnitUrlForm`, `UnitEditorForm`
- [x] `RelUnitHeadingForm`, `RelUnitSourceForm`, `RelUnitAnagraphicForm`
- [x] Tutti i formset inline corrispondenti

**Viste aggiornate (ora in `archimista_python/archive/views/`):**
- [x] `UnitUpdateView` con tutti i formset per estensioni Unità
- [x] Salvataggio automatico di tutti i formset in transazione
- [x] `FondUpdateView` già completa con tutti i formset

**Priorità:** ALTA - Completato ✅

---

### 18. Allineamento Vocabolari a Archimista Ruby (✅ COMPLETATO - v0.14.0)

**Stato:** Completato nella versione 0.14.0.

**Problema riscontrato:**
- I vocabolari Python avevano termini generici tradotti (es. "Acido", "Fragile")
- Ruby ha termini specifici italiani (es. "lacune", "rottura delle cuciture", "strappi")
- L'import AEF salvava valori come "lacune" che non corrispondevano ai vocabolari Python

**Soluzione implementata:**
- Estratti tutti i termini originali da Ruby (`db/seeds/terms.json` e `vocabularies.json`)
- Aggiornato `seed_vocabularies.py` con i termini esatti di Ruby
- Implementato approccio ibrido: campo testo con datalist per suggerimenti

**Vocabolari allineati (30 vocabolari, 200+ termini):**

#### Per Unità:
- ✅ `units.preservation` (6 termini: ottimo, buono, discreto, mediocre, cattivo, pessimo)
- ✅ `units.unit_type` (3 termini: registro, fascicolo, unità documentaria)
- ✅ `units.physical_type` (21 termini: album, busta, cartella, fascicolo, volume, ecc.)
- ✅ `units.medium` (6 termini: carta, pergamena, carta telata, cartoncino, pellicola, altro)
- ✅ `unit_damages.code` (23 termini: lacune, rottura delle cuciture, strappi, macchia, ecc.)
- ✅ `units.access_condition` (5 termini)
- ✅ `units.use_condition` (5 termini)

#### Per Fondi:
- ✅ `fonds.fond_type` (11 termini)
- ✅ `fonds.preservation` (6 termini)
- ✅ `fonds.access_condition` (5 termini)
- ✅ `fonds.use_condition` (5 termini)
- ✅ `fonds.description_type` (4 termini)

**File sorgente Ruby:**
```
/home/srbntt/Documenti/ProgrammiInformatici/archimista/db/seeds/
├── vocabularies.json    # 30 vocabolari definiti
└── terms.json           # 200+ termini con vocabulary_id
```

**Mappatura vocabulary_id Ruby:**
- `vocabulary_id: 12` → `units.preservation`
- `vocabulary_id: 13` → `units.unit_type`
- `vocabulary_id: 14` → `unit_damages.code` (include "lacune", "rottura delle cuciture")
- `vocabulary_id: 22` → `units.physical_type`
- `vocabulary_id: 23` → `units.medium`

**Implementazione Python:**
- `seed_vocabularies.py` - Script per popolare vocabolari
- `archimista_python/archive/forms/unit.py` - Form con `ModelChoiceField` e datalist
- `archimista_python/archive/views/unit.py` - Viste passano termini ai template
- `archimista_python/archive/templates/archive/unit_form.html` - Template con datalist per suggerimenti

**Approccio ibrido (testo + dropdown):**
```python
# Form: campo testo con datalist per suggerimenti
widgets = {
    'code': forms.TextInput(attrs={
        'list': 'damage_code_list',
        'placeholder': 'Seleziona o inserisci tipo danno'
    })
}
```

**Vantaggi:**
1. ✅ Visualizza valori importati AEF (testo libero)
2. ✅ Suggerimenti dal vocabolario mentre si digita
3. ✅ Permette inserimento valori personalizzati
4. ✅ Allineato 100% a Ruby Archimista

**Documentazione:**
- ✅ Creato file `VOCABOLARI_GUIDA.md` con elenco completo e istruzioni

**Priorità:** ALTA - Completato ✅

---

### 19. Show/Hide Dinamico Campi SC2/FSC/FE (✅ COMPLETATO - v0.15.0)

**Stato:** Completato nella versione 0.15.0.

**Problema riscontrato:**
- Tutte le schede speciali (SC2, ICCD, FSC, FE) erano sempre visibili nel form unità
- In Ruby Archimista, i campi appaiono dinamicamente in base al tipo di unità selezionato
- I campi SC2 avevano sfondo giallo in Ruby ma non in Python

**Soluzione implementata:**

#### A. Logica a 3 Livelli (identica a Ruby `units-sc.js`)

```
Livello 1: unit_type
  ├─ "unità documentaria" → mostra sc2_tsk (Scheda Speciale), nascondi file_type
  ├─ "fascicolo o altra unità complessa" → mostra file_type, nascondi sc2_tsk
  └─ altro (es. "registro") → nascondi entrambi

Livello 2a: sc2_tsk (solo se unit_type = "unità documentaria")
  ├─ Vuoto → mostra physical_type, nascondi tutti i container SC2
  ├─ "CARS" → mostra sc2_all + sc2_cars
  ├─ "D" → mostra sc2_all + sc2_d
  ├─ "DT" → mostra sc2_all + sc2_dt
  ├─ "F" → mostra sc2_all + sc2_f
  └─ "S" → mostra sc2_all + sc2_s

Livello 2b: file_type (solo se unit_type = "fascicolo...")
  ├─ Vuoto → nascondi FSC e FE
  ├─ "personale" → mostra FSC, nascondi FE
  └─ "edilizia" → mostra FE, nascondi FSC
```

#### B. Campi Aggiunti al Modello Sc2
- `sdts` (Rappresentazione tematica) - visibile solo per CARS
- `lrd` (Data della ripresa) - visibile solo per F (Fotografia)
- `cmmr` (Numero di commessa) - visibile solo per DT
- `ort` (Orientamento) - visibile solo per CARS

#### C. CSS Allineato a Ruby
- `.sc2_field` → sfondo giallo `#F5F5C8` (identico a Ruby `master.css`)
- `.sc2_container` → container per campi SC2 con classi modificatrici:
  - `sc2_all` → visibile per tutti i tipi SC2
  - `sc2_cars`, `sc2_d`, `sc2_dt`, `sc2_f`, `sc2_s` → visibile solo per tipo specifico
  - `sc2_multi_instance` → formset con checkbox elimina
- `.fsc_container`, `.fe_container` → container FSC/FE
- `.fsc_organization`, `.fsc_nationality`, `.fsc_code`, `.fsc_open`, `.fsc_close` → nascosti di default

#### D. JavaScript (porting di `units-sc.js`)
- `isUnitDocumentaria()` → controlla il testo dell'opzione selezionata (non il valore DB ID)
- `isUnitFascicolo()` → controlla il testo dell'opzione selezionata
- `unitTypeChange()` → mostra/nasconde sc2_tsk o file_type in base a unit_type
- `sc2TskChange()` → mostra/nasconde container SC2 in base al tipo scheda
- `fscChange()` → mostra/nasconde FSC o FE in base a file_type
- `hideAndClean()`, `fscHideAndClean()`, `feHideAndClean()` → nasconde e pulisce i valori
- `showAndBuild()` → mostra il container

**Nota tecnica importante:** Django `ModelChoiceField` usa gli ID del database come valori delle `<option>` (es. `180`, `181`, `182`), mentre Ruby usa il testo direttamente. Le funzioni `isUnitDocumentaria()` e `isUnitFascicolo()` leggono il testo con `jqEl.find('option:selected').text()` per funzionare correttamente.

#### E. Riorganizzazione Template
- **Tab Descrizione**: ora contiene Tipo Unità, Scheda Speciale, Tipologia Fascicolo, campi FSC (nome/cognome), container SC2, container FSC, container FE
- **Tab Descrizione Fisica**: contiene `div_physical_type_wrapper` (tipo fisico, supporto), campi SC2 specifici per tipo, container FE (opera, progettisti, catastali, particelle)
- **Rimossa tab "Schede Speciali" separata** - tutto integrato nei tab esistenti come in Ruby

#### F. Form e Viste Aggiornati
- `UnitForm`: aggiunti campi `sc2_tsk` (5 scelte), `file_type` (2 scelte), `fsc_name`, `fsc_surname`
- `Sc2Form`: aggiunti campi `sdts`, `lrd`, `cmmr`, `ort` con classe `sc2_field`
- `UnitCreateView`: riscritta come `View` con GET/POST completi per tutti i formset
- Migrazione `0014_add_sc2_extra_fields.py` creata e applicata

**File modificati:**
- `archimista_python/archive/models/sc2.py` - 4 nuovi campi
- `archimista_python/archive/forms/unit.py` - UnitForm aggiornato
- `archimista_python/archive/forms/sc2.py` - Sc2Form aggiornato
- `archimista_python/archive/views/unit.py` - UnitCreateView riscritta
- `archimista_python/archive/templates/archive/unit_form.html` - completamente riscritto
- `archimista_python/archive/migrations/0014_add_sc2_extra_fields.py` - nuova migrazione

**Priorità:** ALTA - Completato ✅

---

## Cosa Manca o È Parziale

---

## Priorità di Implementazione

### Alta Priorità (essenziali per equivalenza con Archimista)
1. ✅ ~~Modelli completi~~ (FATTO)
2. ✅ ~~Migrazioni~~ (FATTO)
3. ✅ ~~Import AEF completo~~ (FATTO)
4. ✅ ~~Form Fond completo (con tutte le estensioni)~~ (FATTO - v0.10.0)
5. ✅ ~~Form Creator e Custodian (viste CRUD)~~ (FATTO - v0.10.0)
6. ✅ ~~Allineamento interfaccia a Archimista Ruby~~ (FATTO - v0.13.0)
7. ✅ ~~Allineamento vocabolari a Archimista Ruby~~ (FATTO - v0.14.0)
8. ✅ ~~Show/Hide dinamico campi SC2/FSC/FE~~ (FATTO - v0.15.0)
9. ⚠️ Unit Detail View completo (tutte le schede visibili in lettura)

### Media Priorità (importanti ma non bloccanti)
10. ⚠️ Esportazione AEF (export)
11. ⚠️ Oggetti digitali (upload diretto)
12. ⚠️ Ricerca avanzata
13. ✅ ~~Classificazione/titolario UI~~ (FATTO - v0.34.0)
14. ⚠️ Biografie ed eventi UI

### Bassa Priorità (nice to have)
15. ❌ Sistema di permessi
16. ❌ UI/UX miglioramenti
17. ❌ Performance optimization
18. ❌ Validazioni avanzate
19. ⚠️ **Verifica completa campi form vs Ruby**: controllare che TUTTI i campi presenti nelle maschere Ruby (Unit, Fond, Creator, Custodian, Project) siano presenti anche nelle maschere Python, inclusi campi nascosti, note, qualificatori, ecc.

---

### 20. Fix Sezione Compilatori Unità (✅ COMPLETATO - v0.20.0)

**Stato:** Completato nella versione 0.20.0.

**Problemi riscontrati:**
1. Il prefisso del formset Django era `unit_editors` (plurale), ma template e JS usavano `unit_editor` (singolare) → il JS non trovava il management form, nessun link "Aggiungi" visibile
2. Il campo `id` (PK) non era renderizzato nel template → il formset non poteva identificare i record esistenti → salvataggio falliva
3. `editing_type` era `TextInput` (testo libero) invece di dropdown da vocabolario
4. Il formset aveva `extra=1` → mostrava sempre una riga vuota extra, invece di solo i compilatori esistenti + link "Aggiungi"

**Soluzione implementata:**

#### A. Vocabolario `editors.editing_type` allineato a Ruby
- Rimossi 3 termini generici vecchi ("Compilazione completa", ecc.)
- Aggiunti 7 termini esatti da Ruby (`vocabulary_id: 25`):
  - aggiornamento scheda, inserimento dati, integrazione successiva, prima redazione, revisione, rielaborazione, schedatura

#### B. Form `UnitEditorForm`
- `editing_type` cambiato da `TextInput` a `ChoiceField` con valori `(term_value, term_value)`
- Il campo testo del modello (`CharField`) ora matcha correttamente con le opzioni del dropdown
- Pre-selezione corretta in modifica

#### C. Formset `UnitEditorFormSet`
- Cambiato da `extra=1` a `extra=0` → mostra solo i compilatori esistenti
- Link "Aggiungi compilatore" per crearne di nuovi (come Ruby)

#### D. Template `_tab_editors.html`
- Da card statiche a righe inline con etichette di colonna (Nome, Qualificatore, Tipo compilazione, Data)
- Aggiunto `{{ form_item.id }}` campo nascosto per identificare record esistenti
- Template nascosto `<template id="unit_editors-empty-template">` per nuove righe con opzioni dropdown corrette
- Prefisso corretto: `unit_editors-` (plurale)

#### E. JavaScript `setupEditorFormset()`
- Funzione dedicata con prefisso `unit_editors` (plurale)
- Usa il template vuoto per nuove righe (non clona dati esistenti)
- Link testuale "Aggiungi compilatore" (come Ruby)
- Mostra etichette di colonna solo quando serve

#### F. Viste
- `editing_type_terms` passato al context in UnitCreateView e UnitUpdateView (GET/POST)

**File modificati:**
- `seed_vocabularies.py` — Termini editing_type allineati a Ruby
- `archimista_python/archive/forms/unit.py` — UnitEditorForm con ChoiceField, formset extra=0
- `archimista_python/archive/views/unit.py` — editing_type_terms in 4 punti
- `archimista_python/archive/templates/archive/units/partials/_tab_editors.html` — Riscritto con righe inline, campo id, template vuoto
- `archimista_python/archive/templates/archive/unit_form.html` — JS setupEditorFormset con prefisso corretto

**Priorità:** ALTA - Completato ✅

---

### 21. Menu Navigazione e Viste Entità di Servizio (✅ COMPLETATO - v0.21.0)

**Stato:** Completato nella versione 0.21.0.

**Problema:** La navbar Python aveva solo 4 link (Esplora, Albero, Importa, Nuovo fondo). Le entità di servizio (Fonti, Compilatori, Progetti, ecc.) erano accessibili solo tramite URL diretto o Django Admin.

**Soluzione implementata:**

#### A. Navbar allineata a Ruby `_navbar.html.erb`

**Menu "Schede"** (dropdown):
- Complessi archivistici → `/fonds/` (FondListView)
- Soggetti produttori → `/creators/` (già esistente)
- Soggetti conservatori → `/custodians/` (già esistente)
- Fonti → `/sources/` (nuovo)
- Oggetti digitali → `/digital-objects/` (nuovo)
- Profili istituzionali → `/institutions/` (nuovo)
- Profili documentari → `/document-forms/` (nuovo)
- Progetti → `/projects/` (nuovo)
- Compilatori → `/editors/` (nuovo)

**Menu "Strumenti"** (dropdown):
- Voci di indice → `/headings/` (nuovo)
- Anagrafiche → `/anagraphics/` (nuovo)
- Importa AEF → `/import/aef/` (già esistente)

**Azioni rapide:**
- Albero → `/tree/`
- Nuovo fondo → `/fonds/new/`

#### B. Viste List/Detail per 8 entità

Creato `views/entities.py` con 16 viste (ListView + DetailView per ciascuna):
- `SourceListView`, `SourceDetailView`
- `InstitutionListView`, `InstitutionDetailView`
- `DocumentFormListView`, `DocumentFormDetailView`
- `ProjectListView`, `ProjectDetailView`
- `EditorListView`, `EditorDetailView`
- `DigitalObjectListView`, `DigitalObjectDetailView`
- `HeadingListView`, `HeadingDetailView`
- `AnagraphicListView`, `AnagraphicDetailView`

#### C. Template

16 template (list + detail per ogni entità) con:
- Tabella con colonne pertinenti per ogni entità
- Link "Dettagli" per ogni riga
- Pagina dettaglio con tutti i campi
- Breadcrumb "Torna alla lista"
- Messaggio "Nessun elemento presente" quando vuoto

#### D. URL

16 nuovi URL pattern in `urls.py`:
- `/sources/`, `/sources/<pk>/`
- `/institutions/`, `/institutions/<pk>/`
- `/document-forms/`, `/document-forms/<pk>/`
- `/projects/`, `/projects/<pk>/`
- `/editors/`, `/editors/<pk>/`
- `/digital-objects/`, `/digital-objects/<pk>/`
- `/headings/`, `/headings/<pk>/`
- `/anagraphics/`, `/anagraphics/<pk>/`

**File creati/modificati:**
- `archimista_python/archive/templates/archive/base.html` — Navbar con dropdown Schede/Strumenti
- `archimista_python/archive/views/entities.py` — 16 viste (nuovo file)
- `archimista_python/archive/views/__init__.py` — Export nuove viste
- `archimista_python/archive/urls.py` — 16 nuovi URL pattern
- 16 template in `templates/archive/` (source_list, source_detail, ecc.)

**Priorità:** ALTA - Completato ✅

---

## Stima Completeness

| Area | Completamento |
|------|---------------|
| Database/Modelli | 100% |
| Import Dati | 100% |
| Admin Django | 100% |
| Interfaccia Web - Form Unit | 100% (sincronizzazione campi v0.18.0) |
| Interfaccia Web - Form Fond | 100% (allineato Ruby) |
| Interfaccia Web - Form Creator | 90% |
| Interfaccia Web - Form Custodian | 90% |
| Interfaccia Web - Template | 100% (refactoring partial + capitalizzazione IT v0.18.0) |
| Unit Detail View | 90% (tutte le schede in lettura v0.18.0; manca storico modifiche) |
| Formset Inline | 100% |
| JavaScript Dinamico | 100% (show/hide SC2/FSC/FE + formset) |
| JavaScript E2E Test | ~70% (36 test Playwright v0.52.0: formset, show/hide, jsTree, archidate) |
| Vocabolari Controllati | 100% (allineati Ruby) |
| CRUD Fonti (Source) | 100% (v0.28.0) |
| Refactoring Unit Views | 100% (God Object → handler v0.37.0) |
| Ricerca | 50% |
| Esportazione | 60% |
| Permessi | 0% |
| **TOTALE** | **~90%** (↑ da ~88% — +36 test E2E coprono JavaScript) |

### Copertura Test per Versione

| Versione | Test Server | Test E2E | Totale | Copertura stimata |
|----------|------------|----------|--------|-------------------|
| v0.50.0 | 242 | 0 | 242 | ~45-50% |
| v0.51.0 | 323 | 0 | 323 | ~65-70% |
| **v0.52.0** | **323** | **36** | **359** | **~85-90%** |

---

## Note Importanti

1. **Tutti i dati di Archimista Ruby possono essere importati** - L'import AEF gestisce tutti i modelli
2. **Tutti i campi esistono nel database** - Tutti i campi sono ora accessibili anche via interfaccia web
3. **Django Admin è completo** - Si possono gestire tutti i modelli dall'admin
4. **Interfaccia web allineata ad Archimista Ruby** - Form e template riorganizzati nella v0.13.0
5. **Formset inline completi** - Tutti i formset per estensioni e relazioni implementati
6. **JavaScript dinamico** - Funzione generica per aggiungi/rimuovi righe in tutti i formset
7. **Vocabolari allineati a Ruby** - v0.14.0: 30 vocabolari, 200+ termini da `db/seeds/terms.json`
8. **Approccio ibrido** - Campi testo con datalist per suggerimenti (permette import AEF e valori personalizzati)
9. **Show/Hide dinamico SC2/FSC/FE** - v0.15.0: logica a 3 livelli identica a Ruby `units-sc.js`, campi SC2 con sfondo giallo `#F5F5C8`

---

## Prossimi Passi Consigliati

1. **Implementare export AEF** - Per esportare dati completi
2. **Upload oggetti digitali** - Interfaccia per upload diretto
3. **Ricerca avanzata** - Filtri multipli e ricerca full-text
4. **Autocomplete per relazioni** - Integrare Select2 o simile per fonti, voci di indice, anagrafiche

---

## Riferimenti e Documentazione

- **VOCABOLARI_GUIDA.md** - Guida completa ai vocabolari con:
  - Elenco di tutti i 30 vocabolari e 200+ termini
  - Mappatura vocabulary_id Ruby → nome Python
  - Istruzioni per aggiungere nuovi vocabolari
  - Esempi di utilizzo nei form e template

- **File originali Ruby:**
  - `/home/srbntt/Documenti/ProgrammiInformatici/archimista/db/seeds/vocabularies.json`
  - `/home/srbntt/Documenti/ProgrammiInformatici/archimista/db/seeds/terms.json`

- **File Python:**
  - `seed_vocabularies.py` - Script per popolare vocabolari
  - `archimista_python/archive/models/vocabulary.py` - Modelli Term e Vocabulary
  - `archimista_python/archive/forms/` - Form con campi a scelta
  - `archimista_python/archive/views/` - Viste con contesto per termini

---

### 20. Riorganizzazione Struttura Progetto (✅ COMPLETATO - v0.17.0)

**Stato:** Completato nella versione 0.17.0.

**Problema:**
- La directory `archive/` era fuori da `archimista_python/`, non seguendo le convenzioni Django

**Soluzione:**
- Spostato `archive/` dentro `archimista_python/`
- Aggiornati `settings.py`, `urls.py`, `apps.py` con nome completo `archimista_python.archive`
- Aggiornati 21 file con import interni
- Mantenuto `label = 'archive'` per compatibilità database

**Struttura finale:**
```
python_rewrite/
├── manage.py
├── archimista_python/          ← Progetto Django
│   ├── settings.py, urls.py
│   └── archive/                ← App Django
│       ├── models/, views/, forms/
│       └── templates/, migrations/
├── seed.py, *_vocabularies.py  ← Script utility
└── db.sqlite3
```

**Priorità:** MEDIA - Completato ✅

---

### 21. Fix Sincronizzazione Campi e Refactoring Template (✅ COMPLETATO - v0.18.0)

**Stato:** Completato nella versione 0.18.0.

#### A. Fix sincronizzazione `unit_type_term` ↔ `unit_type`

**Problema:** Quando si modificava un'unità esistente (es. una fotografia), il dropdown "Tipo unità" non era pre-selezionato. L'utente doveva riselezionarlo a mano.

**Causa:** Il campo `unit_type_term` (FK a `Term`) e `unit_type` (CharField testo) non erano sincronizzati. All'import AEF o al salvataggio, solo `unit_type` veniva popolato.

**Soluzione:**
- `forms/unit.py` — `__init__`: se l'istanza ha `unit_type` ma non `unit_type_term`, trova il termine corrispondente e lo pre-seleziona
- `forms/unit.py` — `save()`: sincronizza i due campi al salvataggio
- Template: aggiunto campo nascosto `<input type="hidden" name="unit_type">` per mantenere il valore testo

#### B. Fix sincronizzazione `sc2_tsk` ↔ `card_type`

**Problema:** Le schede SC2 esistenti avevano `card_type='SC3'` (fotografia), ma il form usa `'F'`. Alla modifica, il dropdown "Scheda speciale" non era pre-selezionato.

**Soluzione:**
- `views/unit.py` — `UnitUpdateView.get()`: mappatura `card_type` → `sc2_tsk` (`'SC3'` → `'F'`, `'F'` → `'F'`, ecc.)
- `views/unit.py` — `UnitCreateView.post()` e `UnitUpdateView.post()`: sincronizzazione `sc2_tsk` → `card_type` al salvataggio
- Database: aggiornate 2 schede da `'SC3'` a `'F'` per coerenza
- Template detail: gestiti entrambi i valori `'F'` e `'SC3'` per retrocompatibilità

#### C. Unit Detail View completamente riscritta

**Prima:** Template base con solo dati essenziali e schede specialistiche minimali.

**Dopo:** 8 tab completi in lettura:
1. Descrizione — contesto, identificazione, identificativi alternativi, altre segnature, lingue, contenuto
2. Descrizione fisica — tipo fisico, supporto, conservazione, descrizione fisica, danni
3. Accesso — condizioni accesso/uso con note
4. Fonti — fonti, voci di indice, anagrafiche collegate
5. Compilatori — tabella con tutti i compilatori
6. Scheda SC2/SC3 — tutti i campi specifici per tipo con autori, commissioni, tecniche, scale, elementi testuali/visivi
7. Scheda ICCD — denominazione, tipo, categoria, specifiche tecniche, soggetti, danni
8. FSC — organizzazioni, nazionalità, codici, aperture, chiusure
9. FE — identificazioni, contesti, opere, progettisti, catastali, particelle

I tab appaiono dinamicamente solo se i dati esistono.

#### D. Refactoring template in partial

**Problema:** `unit_form.html` (1178 righe) e `unit_detail.html` (814 righe) erano troppo grandi per essere manutenibili.

**Soluzione:** Spezzati in 14 partial nella directory `templates/archive/units/partials/`:

**Form (5 partial):**
- `_tab_description.html` (367 righe)
- `_tab_physical.html` (207 righe)
- `_tab_access.html` (37 righe)
- `_tab_sources.html` (69 righe)
- `_tab_editors.html` (43 righe)

**Detail (9 partial):**
- `_detail_description.html` (105 righe)
- `_detail_physical.html` (39 righe)
- `_detail_access.html` (33 righe)
- `_detail_sources.html` (33 righe)
- `_detail_editors.html` (30 righe)
- `_detail_sc2.html` (125 righe)
- `_detail_iccd.html` (53 righe)
- `_detail_fsc.html` (65 righe)
- `_detail_fe.html` (81 righe)

**Risultato:**
- `unit_form.html`: da 1178 a 279 righe (−76%)
- `unit_detail.html`: da 814 a 110 righe (−86%)

#### E. Correzione capitalizzazione italiana

Tutti i titoli nei template ora seguono la regola italiana (solo prima parola maiuscola):
- ~~"Descrizione Fisica"~~ → **Descrizione fisica**
- ~~"Accesso e Utilizzo"~~ → **Accesso e utilizzo**
- ~~"Tipo Unità"~~ → **Tipo unità**
- ~~"Stato di Conservazione"~~ → **Stato di conservazione**
- ~~"Identificativi Alternativi"~~ → **Identificativi alternativi**
- ~~"Dati Catastali"~~ → **Dati catastali**
- ... e tutti gli altri

**Priorità:** ALTA - Completato ✅

---

### 22. Allineamento Vocabolari e Fix Critici (✅ COMPLETATO - v0.19.0)

**Stato:** Completato nella versione 0.19.0.

#### A. Fix modello `Term.__str__`

**Problema:** Il metodo `__str__` restituiva `self.term` che era vuoto per i termini creati via shell. Django `ModelChoiceField` usa `__str__` per il testo delle `<option>`, quindi le combo apparivano vuote.

**Soluzione:**
```python
def __str__(self):
    return self.term_value or self.term or self.term_key or str(self.pk)
```
- Aggiornati 22 record nel DB con `term` vuoto
- Aggiornato `seed_vocabularies.py` per assicurare `term` sempre popolato

#### B. Allineamento `units.medium` (Supporti) a Ruby SC2

**Problema:** I supporti erano 6 termini generici. Ruby ha termini specifici per tipo di scheda SC2.

**Soluzione:**
- `medium` trasformato da dropdown a campo testo con `<datalist>` (come Ruby)
- JavaScript `updateMediumDatalist(sc2Type)` filtra i supporti in base al tipo SC2:
  - **Fotografia (F):** 41 termini (albumina/carta, ambrotipo, dagherrotipo, gelatina bromuro d'argento/carta, stampa lambda/carta, ecc.)
  - **Cartografia (CARS):** 8 termini
  - **Disegno artistico (D):** 36 termini
  - **Disegno tecnico (DT):** 9 termini
  - **Stampa (S):** 19 termini
- Termini estratti da `db/seeds/sc2_terms.json` (sc2_vocabulary_id:4)

#### C. Allineamento `access_condition` e `use_condition` a Ruby

**Problema:** I termini erano inventati. Ruby usa termini italiani specifici.

**Termini corretti (da Ruby `terms.json`):**
- `units.access_condition` (ID 19): liberamente accessibile, accessibile previa autorizzazione, non consultabile, parzialmente accessibile
- `units.use_condition` (ID 20): libera, consentita per uso studio, a pagamento, negata

#### D. Fix `fonds.preservation`

**Problema:** Termini con maiuscole e termini extra non presenti in Ruby.

**Soluzione:** Allineato a Ruby (ID 10): ottimo, buono, discreto, mediocre, cattivo, pessimo.

#### E. Fix struttura form: `physical_type` dentro wrapper nascosto

**Problema:** `physical_type_term` era sempre visibile anche con scheda SC2 selezionata.

**Soluzione:** Spostato dentro `div_physical_type_wrapper` → viene nascosto quando si seleziona SC2 (come Ruby).

#### F. Sincronizzazione campi term per Unit e Fond

**Problema:** Solo `unit_type_term` aveva la sincronizzazione.

**Soluzione:** Estesa a tutti i campi:
- **Unit:** `unit_type_term`, `access_condition_term`, `use_condition_term`, `preservation_term`, `physical_type_term`
- **Fond:** `fond_type_term`, `access_condition_term`, `use_condition_term`, `preservation_term`

#### G. Fix formset `is_valid()` prima di `save()`

**Problema:** `AttributeError: 'Sc2TechniqueForm' object has no attribute 'cleaned_data'`.

**Soluzione:** Tutti i formset ora chiamano `is_valid()` prima di `save()`, raggruppati in loop.

**Priorità:** ALTA - Completato ✅

---

### 23. Allineamento Form Soggetto Conservatore a Ruby (✅ COMPLETATO - v0.23.0)

**Problema:** L'interfaccia Python dei soggetti conservatori era molto diversa da quella Ruby. I tab erano organizzati diversamente. Mancavano le relazioni con fondi e la denominazione principale era gestita come formset invece che come form separato.

**Soluzione:**

#### A. Ristrutturazione completa del form (7 tab come Ruby)
1. **Identificazione**: condizione giuridica, macrotipologia, pubblicato, denominazione principale, altre denominazioni, cenni storici, contatti, referente, enti titolari, collegamenti, codici identificativi
2. **Descrizione**: patrimonio, politiche di gestione, struttura amministrativa
3. **Accesso**: orari e indicazioni per l'accesso, servizi
4. **Sedi**: edifici con denominazione, tipologia, indirizzo, comune, CAP, nazione, descrizione
5. **Relazioni**: fondi collegati (RelCustodianFond formset)
6. **Fonti**: fonti collegate (RelCustodianSource formset)
7. **Compilatori**: nome, qualificatore, tipo compilazione (dropdown), data

#### B. Denominazione principale separata
- Creato `CustodianPreferredNameForm` (form singolo, non formset)
- Formset `CustodianNameFormSet` solo per le altre denominazioni

#### C. Detail view allineata a Ruby
Sezioni in lettura: Identificazione, Descrizione, Accesso, Sedi, Relazioni, Fonti, Compilatori

#### D. List view allineata a Ruby
Ricerca per denominazione, stato pubblicato, pagination

#### E. Model updates
Proprietà `fonds`, `sources`, `preferred_name`, `other_names`, `display_name`

**Priorità:** ALTA - Completato ✅

---

### 26. Fix JavaScript Formset e Allineamento Detail Views (✅ COMPLETATO - v0.27.0)

**Stato:** Completato nella versione 0.27.0.

#### A. Fix JavaScript formset (tutti i form "Aggiungi..." ora funzionano)

**Problema:** I pulsanti "Aggiungi nome", "Aggiungi identificativo", "Nuovo collegamento", ecc. non facevano nulla. Errore JS: `Cannot read properties of null (reading 'getElementsByClassName')`.

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

#### B. Allineamento completo detail views a form views

**Problema:** Le detail view mostravano solo una frazione dei campi presenti nei form.

**Unit Detail** (già parzialmente fixato in v0.26.0, completato):
- Aggiunti: `given_title`, `title`, `extent`, `arrangement_note`, `tmp_reference_number/string`, `folder_number`, `file_number`, `related_materials`, `restoration`, `note`, `physical_container_type/title/number`, `preservation`, `preservation_note`

**Fond Detail** (completamente riscritto con 7 tab):
- Prima: solo nome, tipo, abstract, storia, eventi, lista unità
- Dopo: 1.Descrizione (padre, tipologia, pubblicato, lunghezza, entità, nomi alternativi, identificativi, lingue, abstract, descrizione, storia, nota archivista), 2.Altre informazioni (materiali correlati, tipo materiali, note, possessori, URL), 3.Accesso (condizioni, note, conservazione, tipo descrizione), 4.Relazioni (voci indice, forme documentarie), 5.Fonti, 6.Compilatori, Estremi cronologici

**Creator Detail** (completamente riscritto con 5+ tab):
- Prima: solo tipo, residenza, stato giuridico, abstract, storia, note
- Dopo: 1.Identificazione (tipo, tipo ente, pubblicato, sede, denominazione principale, denominazioni alternative con patronimico/nickname/qualificatore, identificativi, URL, condizione giuridica), 2.Descrizione (abstract, storia, note, attività con note), 3.Relazioni (fondi con link, istituzioni, altri soggetti), 4.Fonti, 5.Compilatori, Estremi cronologici

**Custodian Detail**:
- Aggiunto campo "Pubblicato"

**Project Detail**:
- Già completo, nessuna modifica necessaria

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

### 25. Estremi Cronologici (Archidate) - Form, Import AEF, Detail (✅ COMPLETATO - v0.25.0)

**Problema:** Gli estremi cronologici (date di esistenza/attività) erano presenti nel modello `Event` ma non gestiti nell'interfaccia web. L'import AEF non importava gli eventi. I form non erano allineati a Ruby.

**Soluzione:**

#### A. Form allineati a Ruby (EventForm + EventFormSet)
- **2 radio button**: `data puntuale` (Y) e `data secolare` (C) — come Ruby
- **Combo specifica inizio**: `=`, `ante`, `circa` (come Ruby)
- **Combo specifica fine**: `ante`, `=`, `circa` (come Ruby)
- **Combo validità**: `certa`, `incerta`, `attribuita`, `incerta e attribuita`
- **Data puntuale**: anno, mese, giorno
- **Data secolare**: secolo (I-XXI), intervallo (inizio, fine, metà, prima metà, ecc.)
- **Equal bounds**: checkbox "Uguale all'estremo iniziale"
- **Luoghi**: luogo inizio/fine (visibile per Creator tipo Persona)
- Campi ChoiceField espliciti (non CharField) per far funzionare RadioSelect

#### B. Import AEF eventi
- Aggiunti handler per `unit_event` e `fond_event` in `import_utils.py`
- Metodi `import_unit_event()` e `import_fond_event()` con GenericForeignKey
- Mappa `unit_id`/`fond_id` → `content_type` + `object_id`

#### C. Detail view
- **Unit**: tab dedicato "Estremi cronologici" (appare solo se ci sono eventi)
- **Fond**: card dedicata dopo "Storia archivistica"
- **Creator**: card dedicata dopo info principali

#### D. JavaScript Archidate
- Toggle formato: Y mostra campi anno/mese/giorno, C mostra secolo/intervallo
- Equal bounds: nasconde estremo finale quando selezionato

#### E. File modificati/creati
- `forms/event.py` — Nuovo, EventForm + EventFormSet
- `views/unit.py`, `views/fond.py`, `views/creator.py` — Aggiunti event_formset a create/update/detail
- `import_utils.py` — Aggiunto import eventi
- `templates/.../unit_form.html`, `fond_form.html`, `creator_form.html` — Sezione estremi cronologici
- `templates/.../unit_detail.html`, `fond_detail.html`, `creator_detail.html` — Visualizzazione eventi
- `templates/.../units/partials/_detail_dates.html` — Partial per tab dates

**Priorità:** ALTA - Completato ✅

---

### v0.49.0 — Bug fix scoperti dalla test suite completa (✅ COMPLETATO - 2026-04-07)

**6 bug corretti** (tutti scoperti eseguendo la test suite estesa da 67 a 167 test):

| # | Bug | File | Tipo |
|---|-----|------|------|
| 1 | `HeadingForm.save()` → `AttributeError: 'Heading' object has no attribute 'heading_type_term'` | `forms/heading.py` | **Bug modello/form** |
| 2 | `AnagraphicCreateView.form_valid()` — formset validato prima del save dell'oggetto | `views/entities.py` | **Bug vista** |
| 3 | `DocumentFormDeleteView` — `NoReverseMatch` per `context_object_name` mancante | `views/document_forms.py` | **Bug vista** |
| 4 | `QualityCheckFondView` — 4 related name errati (`relcreatorfond` → `rel_creator_fonds`, ecc.) | `views/quality_checks.py` | **Bug query** |
| 5 | `Creator.sources` — `NameError: name 'Source' is not defined` (import mancante) | `models/core.py` | **Bug import** |
| 6 | Test suite — DB `:memory:` causava problemi di sessione | `test_complete.py` | **Bug test** |

**Risultato:** 102/102 test passati (prima 67/67, riorganizzati in `tests/` directory modulare).

---

### v0.50.0 — Suite test completa, 242 test (+140 nuovi) (✅ COMPLETATO - 2026-04-07)

**140 nuovi test aggiunti** in 7 nuovi moduli, portando il totale da 102 a **242 test passati**.

#### Nuovi moduli di test

| Modulo | Test | Copertura |
|--------|------|-----------|
| `test_digital_objects.py` | 20 | CRUD completo (upload file, validazione tipo/dimensione, nested per entity, model methods is_image/is_video/is_pdf) |
| `test_service_entities_complete.py` | 22 | CRUD update/delete per Source, Project, Institution, Heading, Anagraphic, Editor, Classification (detail, update, delete, tree, units, circular ref), DocumentForm create |
| `test_model_properties.py` | 22 | Fond (subtree, root, descendants, subtree_ids, active_descendant_units_count, preferred_event), Unit (is_movable_up/down, full_path, display_sequence_numbers_of/from_hash), Creator (preferred_name, sources, institutions, fonds), Custodian (preferred_name, sources, fonds), Event (date formatting edge cases), Classification (is_root, descendants) |
| `test_form_validation.py` | 18 | Validazione Fond, Unit, Creator, Custodian, DigitalObject, Source, Project, Heading, Anagraphic, Classification, Institution (dati minimi validi + Select2 widgets) |
| `test_search.py` | 8 | Ricerca globale con dati reali, ricerca avanzata con filtri (entity_type, fond_id, published), paginazione |
| `test_quality_checks.py` | 12 | QC fondo (incompleto, completo, con unità, con relazioni, con sottoalbero), QC creatore (incompleto, completo, con corporate type), QC conservatore (incompleto, completo con sedi), QC index |
| `test_import_export_auth.py` | 15 | Import AEF con file ZIP reale (NDJSON formato corretto), export PDF/RTF/AEF/CSV content validation, auth (password change flow, must_change_password), middleware exclusion paths, Unit move view, Tree view, Unit list |
| `test_seed_scripts.py` | 8 | Seed vocabularies, seed source_types, seed admin_user, modelli Vocabulary/Term, Group default |

#### Bug Python scoperti e corretti

| # | Bug | Fix |
|---|-----|-----|
| 1 | `Fond.subtree` property mancante | Aggiunta `@property subtree` in `models/core.py` |
| 2 | `Fond.root` property mancante | Aggiunta `@property root` con prevenzione loop circolari |
| 3 | `Unit.full_path()` metodo mancante | Aggiunto metodo `full_path()` in `models/core.py` |
| 4 | `Classification.is_root` property mancante | Aggiunta `@property is_root` in `models/core.py` |

**Risultato:** **242/242 test passati** (prima 102/102).
