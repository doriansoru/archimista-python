# Confronto Maschere Ruby vs Python — Analisi Completa

**Data:** 2026-04-09
**Versione Python:** 0.54.0 — ✅ COMPLETATO: Select2 ibrido, Export XML (SAN/EAD/METS), Refactor AEF modulare, 4 opzioni export come Ruby

---

## 1. FOND (Fondo / Complesso archivistico)

### Tab: 1. Descrizione

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `fond_type` | ✅ terms_select | ✅ fond_type_term | OK |
| `published` | ✅ checkbox | ✅ checkbox | OK |
| `name` | ✅ text_field | ✅ Textarea | OK |
| **other_names** (formset) | ✅ name, note, qualifier, patronymic, nickname, preferred, _destroy | ✅ name, note, qualifier, patronymic, nickname, preferred, DELETE | OK |
| **events** (archidate) | ✅ | ✅ | OK — formato puntuale/secolare, combo specifiche, secolo, validità, luogo, equal_bounds |
| `length` | ✅ text_field | ✅ NumberInput | OK |
| `extent` | ✅ text_area | ✅ Textarea | OK |
| `abstract` | ✅ text_area (solo se is_root) | ✅ Textarea | ⚠️ Python non controlla `is_root` |
| `description` | ✅ text_area | ✅ Textarea | OK |
| `history` | ✅ text_area | ✅ Textarea | OK |
| `arrangement_note` | ✅ text_area | ✅ IMPLEMENTATO v0.26.0 |

### Tab: 2. Altre informazioni

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| **fond_langs** (formset) | ✅ code (collection_select da @langs), _destroy | ✅ code (TextInput), DELETE | ⚠️ Ruby usa dropdown da lingue DB, Python usa text |
| **fond_owners** (formset) | ✅ owner, _destroy | ✅ owner, DELETE | OK |
| `related_materials` | ✅ text_area | ✅ Textarea | OK |
| `note` | ✅ text_area | ✅ Textarea | OK |
| **fond_urls** (formset) | ✅ url, note, _destroy | ✅ url, note, position, DELETE | ✅ Python ha anche `position` |
| **fond_identifiers** (formset) | ✅ identifier, identifier_source, note, _destroy | ✅ identifier, identifier_source, note, DELETE | OK |

### Tab: 3. Accesso

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `access_condition` | ✅ terms_select | ✅ access_condition_term | OK |
| `access_condition_note` | ✅ text_area | ✅ access_condition (Textarea) | OK |
| `use_condition` | ✅ terms_select | ✅ use_condition_term | OK |
| `use_condition_note` | ✅ text_area | ✅ use_condition (TextInput) | OK |
| `preservation` | ✅ terms_select | ✅ preservation_term | OK |
| `preservation_note` | ✅ text_area | ✅ preservation (Textarea) | OK |
| `description_type` | ❌ **NON PRESENTE IN RUBY** | ✅ description_type_term | ✅ Extra Python |

### Tab: 4. Relazioni

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `creators` (autocomplete) | ✅ rel_creator_fonds | ✅ RelCreatorFond formset | ✅ IMPLEMENTATO v0.26.0 — formset esistente, label corretta |
| `custodians` (autocomplete, solo is_root) | ✅ rel_custodian_fonds | ✅ RelCustodianFond formset | ✅ IMPLEMENTATO v0.26.0 — formset esistente |
| `projects` (autocomplete, solo is_root) | ✅ rel_project_fonds | ✅ RelProjectFond formset | ✅ IMPLEMENTATO v0.26.0 — formset esistente |
| `document_forms` (autocomplete) | ✅ rel_fond_document_forms | ✅ RelFondDocumentForm formset | OK (Python usa dropdown, Ruby autocomplete) |
| Voci di indice | ✅ RelFondHeading | ✅ RelFondHeading | OK |

### Tab: 5. Fonti

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `sources` (livesearch) | ✅ rel_fond_sources | ✅ RelFondSource formset (dropdown) | ⚠️ Ruby usa livesearch, Python usa dropdown |

### Tab: 6. Compilatori

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| **fond_editors** (formset) | ✅ name (autocomplete), qualifier, editing_type (terms_select), edited_at (datepicker), _destroy | ✅ name, qualifier, editing_type (TextInput), edited_at, DELETE | ⚠️ Ruby: editing_type=terms_select, Python=TextInput; Ruby: name=autocomplete, Python=text |

---

## 2. UNIT (Unità archivistica)

### Tab: 1. Descrizione

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `parent_id` (hidden) | ✅ | ❌ **MANCANTE** | ⚠️ Python lo ha nel form fields ma non come hidden |
| `fond_id` (hidden) | ✅ | ❌ **MANCANTE** | ⚠️ |
| `tsk` (hidden) | ✅ | ❌ **MANCANTE** | ⚠️ |
| `unit_type` | ✅ terms_select | ✅ unit_type_term | OK |
| `file_type` | ✅ terms_select | ✅ file_type (ChoiceField) | OK |
| `sc2_tsk` | ✅ sc2_terms_select | ✅ sc2_tsk (ChoiceField) | OK |
| `published` | ✅ checkbox | ✅ checkbox | OK |
| `title` | ✅ text_field | ✅ Textarea | OK |
| `given_title` | ✅ checkbox | ✅ checkbox | ✅ IMPLEMENTATO v0.26.0 |
| `fsc_name` | ✅ text_field | ✅ text_field | OK |
| `fsc_surname` | ✅ text_field | ✅ text_field | OK |
| **fe_identifications** (formset) | ✅ code, file_year, category, identification_class | ✅ code, file_year, category, identification_class | OK |
| **events** (archidate) | ✅ | ✅ | OK |
| **fe_contexts** (formset) | ✅ number, sub_number, classification, applicant, request, license_number, license_year, license_date, protocol_number, habitability_number, habitability_year, habitability_date | ✅ number, sub_number, classification, applicant, request, license_number, license_year, license_date, protocol_number, habitability_number, habitability_year, habitability_date, DELETE | ✅ IMPLEMENTATO v0.26.0 — tutti i campi FE aggiunti |
| `content` | ✅ text_area | ✅ Textarea | OK |
| `extent` | ✅ text_area | ✅ IMPLEMENTATO v0.26.0 |
| **sc2_textual_elements** (formset) | ✅ isri, _destroy | ✅ isri, DELETE | OK |
| **sc2_visual_elements** (formset) | ✅ stmd, _destroy | ✅ stmd, DELETE | OK |
| **sc2** (single) | ✅ sgti | ✅ sgti | OK |
| **sc2_authors** (formset) | ✅ autr (openedvoc), autn, auta, _destroy, nested sc2_attribution_reasons (autm) | ✅ autr, autn, auta, DELETE + Sc2AttributionReasonForm | ✅ IMPLEMENTATO v0.26.0 — modello e form aggiunti |
| **sc2_commissions** (formset) | ✅ nested sc2_commission_names (cmmn), cmmc, _destroy | ✅ cmmc, DELETE + Sc2CommissionNameForm | ✅ IMPLEMENTATO v0.26.0 — form aggiunto |
| **sc2** (single, cont.) | ✅ cmmr, lrc, lrd | ✅ cmmr, lrc, lrd | OK |
| **fsc_organizations** (formset) | ✅ organization, _destroy | ✅ organization, DELETE | OK |
| **fsc_nationalities** (formset) | ✅ nationality, _destroy | ✅ nationality, DELETE | OK |
| **fsc_codes** (formset) | ✅ code, _destroy | ✅ code, note, DELETE | ✅ Python ha anche note |
| **fsc_opens** (formset) | ✅ open (datepicker), _destroy | ✅ open, note, DELETE | ✅ Python ha anche note |
| **fsc_closes** (formset) | ✅ close (datepicker), _destroy | ✅ close, note, DELETE | ✅ Python ha anche note |
| `tmp_reference_number` | ✅ number_field | ✅ IMPLEMENTATO v0.26.0 |
| `tmp_reference_string` | ✅ text_field | ✅ IMPLEMENTATO v0.26.0 |
| `folder_number` | ✅ text_field | ✅ IMPLEMENTATO v0.26.0 |
| `file_number` | ✅ text_field | ✅ IMPLEMENTATO v0.26.0 |
| `reference_number` | ✅ text_field (con pulsante "create") | ✅ Textarea | ⚠️ Python manca pulsante "create" |
| `arrangement_note` | ✅ text_area | ✅ IMPLEMENTATO v0.26.0 |

### Tab: 2. Descrizione fisica

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| **fe_operas** (formset) | ✅ is_present, status (terms_select), building_name, building_type, place_name, place_type, house_number, district | ✅ is_present, status, building_name, building_type, place_name, place_type, house_number, district | OK |
| **fe_designers** (formset) | ✅ designer_name, designer_role, _destroy | ✅ designer_name, designer_role, DELETE | OK |
| **fe_cadastrals** (formset) | ✅ way_code, cadastral_municipality, municipality_code, paper_code | ✅ way_code, cadastral_municipality, municipality_code, paper_code, DELETE | OK |
| **fe_land_parcels** (formset) | ✅ land_parcel_number, _destroy | ✅ land_parcel_number, DELETE | OK |
| **fe_fract_land_parcels** (formset) | ✅ fract_land_parcel_number, edil_parcel_number, _destroy | ✅ IMPLEMENTATO v0.26.0 |
| **fe_fract_edil_parcels** (formset) | ✅ fract_edil_parcel_number, material_portion, _destroy | ✅ IMPLEMENTATO v0.26.0 |
| `physical_type` | ✅ terms_select | ✅ physical_type_term | OK |
| `medium` | ✅ text_field (openedvoc) | ✅ TextInput + datalist | OK (approccio diverso ma equivalente) |
| **sc2_techniques** (formset) | ✅ mtct (openedvoc), _destroy | ✅ mtct, DELETE | OK |
| **sc2** (single) | ✅ mtce, sdtt, sdts, dpgf, misa, misl, ort | ✅ mtce, sdtt, sdts, dpgf, misa, misl, ort | OK |
| **sc2_scales** (formset) | ✅ sca (openedvoc), _destroy | ✅ sca, DELETE | OK |
| `related_materials` | ✅ text_area | ✅ IMPLEMENTATO v0.26.0 |
| `physical_description` | ✅ text_area | ✅ Textarea | OK |
| `preservation` | ✅ terms_select | ✅ preservation_term | OK |
| `preservation_note` | ✅ text_area | ✅ IMPLEMENTATO v0.26.0 |
| **unit_damages** (formset) | ✅ code (terms_select), _destroy | ✅ code (TextInput+datalist), note, DELETE | ✅ Python ha anche note |
| `restoration` | ✅ text_area | ✅ IMPLEMENTATO v0.26.0 |
| `note` | ✅ text_area | ✅ IMPLEMENTATO v0.26.0 |
| `physical_container_type` | ✅ text_field | ✅ IMPLEMENTATO v0.26.0 |
| `physical_container_title` | ✅ text_field | ✅ IMPLEMENTATO v0.26.0 |
| `physical_container_number` | ✅ text_field | ✅ IMPLEMENTATO v0.26.0 |
| **unit_other_reference_numbers** (formset) | ✅ other_reference_number, qualifier, note, _destroy | ✅ other_reference_number, qualifier, note, DELETE | ✅ IMPLEMENTATO v0.26.0 — aggiunti qualifier e note al modello |
| **unit_langs** (formset) | ✅ code (collection_select da @langs), _destroy | ✅ code (TextInput), DELETE | ⚠️ Ruby usa dropdown da lingue DB |
| **unit_urls** (formset) | ✅ url, note, _destroy | ✅ IMPLEMENTATO v0.26.0 |
| **unit_identifiers** (formset) | ✅ identifier, identifier_source, note, _destroy | ✅ IMPLEMENTATO v0.26.0 |

### Tab: 3. Accesso

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| **unit_langs** (formset) | ✅ code (collection_select), _destroy | ❌ Nel tab Accesso di Python | ⚠️ In Python è nel tab Descrizione |
| `access_condition` | ✅ terms_select | ✅ access_condition_term | OK |
| `access_condition_note` | ✅ text_area | ✅ access_condition (Textarea) | OK |
| `use_condition` | ✅ terms_select | ✅ use_condition_term | OK |
| `use_condition_note` | ✅ text_area | ✅ use_condition (TextInput) | OK |
| **unit_urls** (formset) | ✅ url, note, _destroy | ❌ **MANCANTE** | 🔴 (già segnalato sopra) |
| **unit_identifiers** (formset) | ✅ identifier, identifier_source, note, _destroy | ❌ **MANCANTE** | 🔴 (già segnalato sopra) |

### Tab 4. Fonti

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `sources` (livesearch) | ✅ rel_unit_sources | ✅ RelUnitSource formset (dropdown) | ⚠️ Ruby usa livesearch, Python usa dropdown |

### Tab 5. Compilatori

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| **unit_editors** (formset) | ✅ name (autocomplete), qualifier, editing_type (terms_select), edited_at (datepicker), _destroy | ✅ name, qualifier, editing_type (ChoiceField), edited_at, DELETE, id | ⚠️ Ruby: name=autocomplete, editing_type=terms_select; Python: name=text, editing_type=ChoiceField |

---

## 3. CREATOR (Soggetto produttore)

### Tab: 1. Identificazione

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `creator_type` | ✅ terms_select | ✅ Select (P/F/E) | OK |
| `creator_corporate_type_id` | ✅ select da CustodianType | ✅ Select | OK |
| `published` | ✅ checkbox | ✅ checkbox | OK |
| **preferred_name** (single) | ✅ cf: name, note_cf / p: first_name, last_name, note_p | ✅ name, first_name, last_name, note | OK |
| **other_names** (formset) | ✅ name, qualifier (terms_select), note, _destroy | ✅ name, qualifier (TextInput), note, DELETE | ⚠️ Ruby: qualifier=terms_select, Python=TextInput |
| **events** (archidate) | ✅ | ✅ | OK |
| **creator_legal_statuses** (formset, hidden) | ✅ legal_status (terms_select), note, _destroy | ✅ legal_status, note, DELETE | ✅ IMPLEMENTATO v0.26.0 — formset aggiunto al form e template |
| `residence` | ✅ text_field (autocomplete da places) | ✅ Textarea | ⚠️ Ruby: autocomplete, Python: textarea |
| **creator_urls** (formset) | ✅ url, note, _destroy | ✅ url, note, DELETE | OK |
| **creator_identifiers** (formset) | ✅ identifier, identifier_source, note, _destroy | ✅ identifier, identifier_source, note, DELETE | OK |

### Tab: 2. Descrizione

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `abstract` | ✅ text_area | ✅ Textarea | OK |
| `history` | ✅ text_area | ✅ Textarea | OK |
| `note` | ✅ text_area | ✅ Textarea | OK |
| **creator_activities** (formset) | ✅ activity, note, _destroy | ✅ activity, note, DELETE | OK |

### Tab: 3. Relazioni

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `fonds` (autocomplete) | ✅ rel_creator_fonds | ✅ RelCreatorFond formset (dropdown) | ⚠️ Ruby: autocomplete, Python: dropdown |
| `institutions` (autocomplete) | ✅ rel_creator_institutions | ✅ RelCreatorInstitution formset (dropdown) | ⚠️ Ruby: autocomplete, Python: dropdown |
| `related_creators` (autocomplete) | ✅ rel_creator_creators, con association_type | ✅ RelCreatorCreator formset (dropdown + association_type) | ⚠️ Ruby: autocomplete, Python: dropdown |

### Tab: 4. Fonti

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `sources` (livesearch) | ✅ rel_creator_sources | ✅ RelCreatorSource formset (dropdown) | ⚠️ Ruby: livesearch, Python: dropdown |

### Tab: 5. Compilatori

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| **creator_editors** (formset) | ✅ name (autocomplete), qualifier, editing_type (terms_select), edited_at (datepicker), _destroy | ✅ name, qualifier, editing_type (ChoiceField), edited_at, DELETE, id | ⚠️ Ruby: name=autocomplete, editing_type=terms_select; Python: name=text, editing_type=ChoiceField |

---

## 4. CUSTODIAN (Soggetto conservatore)

### Tab: 1. Identificazione

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `legal_status` | ✅ terms_select | ✅ Select (P/R) | OK |
| `custodian_type_id` (macro) | ✅ select da CustodianType | ✅ Select | OK |
| `published` | ✅ checkbox | ✅ checkbox | OK |
| **preferred_name** (single) | ✅ name, note, preferred (hidden) | ✅ name, note | ⚠️ Python manca campo hidden `preferred` |
| **other_names** (formset) | ✅ qualifier (terms_select), name, note, _destroy | ✅ qualifier, name, note, DELETE | ⚠️ Ruby: qualifier=terms_select, Python=TextInput |
| `history` | ✅ text_area | ✅ Textarea | OK |
| **custodian_contacts** (formset) | ✅ contact_type (terms_select), contact, contact_note, _destroy | ✅ contact_type (TextInput), contact, contact_note, DELETE | ⚠️ Ruby: contact_type=terms_select, Python=TextInput |
| `contact_person` | ✅ text_field | ✅ TextInput | OK |
| **custodian_owners** (formset) | ✅ owner, _destroy | ✅ owner, DELETE | OK |
| **custodian_urls** (formset) | ✅ url, note, _destroy | ✅ url, note, position, DELETE | ✅ Python ha anche position |
| **custodian_identifiers** (formset) | ✅ identifier, identifier_source, note, _destroy | ✅ identifier, identifier_source, note, DELETE | OK |

### Tab: 2. Descrizione

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `holdings` | ✅ text_area | ✅ Textarea | OK |
| `collecting_policies` | ✅ text_area | ✅ Textarea | OK |
| `administrative_structure` | ✅ text_area | ✅ Textarea | OK |

### Tab: 3. Accesso

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `accessibility` | ✅ text_area | ✅ Textarea | OK |
| `services` | ✅ text_area | ✅ Textarea | OK |

### Tab: 4. Sedi

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| **custodian_buildings** (formset) | ✅ name, custodian_building_type (terms_select), address, city (autocomplete), postcode, country (autocomplete), description, _destroy | ✅ name, custodian_building_type (TextInput), address, city (TextInput), postcode, country (TextInput), description, DELETE | ⚠️ Ruby: building_type=terms_select, city/country=autocomplete; Python: tutti TextInput |

### Tab: 5. Relazioni

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `fonds` (autocomplete) | ✅ rel_custodian_fonds | ✅ RelCustodianFond formset (dropdown) | ⚠️ Ruby: autocomplete, Python: dropdown |

### Tab: 6. Fonti

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `sources` (livesearch) | ✅ rel_custodian_sources | ✅ RelCustodianSource formset (dropdown) | ⚠️ Ruby: livesearch, Python: dropdown |

### Tab: 7. Compilatori

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| **custodian_editors** (formset) | ✅ name (autocomplete), qualifier, editing_type (terms_select), edited_at (datepicker), _destroy | ✅ name, qualifier, editing_type (ChoiceField da vocabolario), edited_at, DELETE | ✅ IMPLEMENTATO v0.26.0 — editing_type da vocabolario 7 termini |

---

## 5. PROJECT (Progetto)

### Tab: 1. Identificazione

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `name` | ✅ text_field | ✅ TextInput | OK |
| `project_type` | ✅ terms_select | ✅ project_type_term | OK |
| `published` | ✅ checkbox | ✅ checkbox | OK |
| `start_year` | ✅ select (1970..current) | ✅ ChoiceField (1970..current+5) | OK |
| `end_year` | ✅ select (1970..current+5) | ✅ ChoiceField (1970..current+5) | OK |
| `status` | ✅ terms_select | ✅ status_term | OK |
| `description` | ✅ text_area | ✅ Textarea | OK |
| `note` | ✅ text_area | ✅ Textarea | OK |
| **project_urls** (formset) | ✅ url, note, _destroy | ✅ url, note, position, DELETE | ✅ Python ha anche position |

### Tab: 2. Responsabilità

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| **project_managers** (formset) | ✅ name, qualifier (terms_select), _destroy | ✅ name, qualifier_term (terms_select), qualifier (hidden), DELETE | OK |
| **project_stakeholders** (formset) | ✅ name, qualifier (terms_select), _destroy | ✅ name, qualifier_term (terms_select), qualifier (hidden), DELETE | OK |

### Tab: 3. Relazioni

| Campo | Ruby | Python | Note |
|-------|------|--------|------|
| `fonds` (autocomplete) | ✅ rel_project_fonds | ✅ RelProjectFond formset (dropdown) | ⚠️ Ruby: autocomplete, Python: dropdown |

---

## RIEPILOGO CAMPI MANCANTI IN PYTHON

### ✅ TUTTI IMPLEMENTATI (v0.26.0)

Tutti i 26+ campi mancanti sono stati aggiunti. Vedi sotto per il dettaglio storico.

### Storico campi precedentemente mancanti (ora implementati)

#### FOND
1. ✅ `arrangement_note` — Nota sull'ordinamento (textarea) — **IMPLEMENTATO v0.26.0**

#### UNIT
2. ✅ `given_title` — Checkbox "titolo assegnato" — **IMPLEMENTATO v0.26.0**
3. ✅ `extent` — Entità dell'unità (textarea) — **IMPLEMENTATO v0.26.0**
4. ✅ `arrangement_note` — Nota sull'ordinamento (textarea) — **IMPLEMENTATO v0.26.0**
5. ✅ `tmp_reference_number` — Numero riferimento temporaneo — **IMPLEMENTATO v0.26.0**
6. ✅ `tmp_reference_string` — Stringa riferimento temporanea — **IMPLEMENTATO v0.26.0**
7. ✅ `folder_number` — Numero fascicolo — **IMPLEMENTATO v0.26.0**
8. ✅ `file_number` — Numero file — **IMPLEMENTATO v0.26.0**
9. ✅ `related_materials` — Materiali correlati (textarea, tab Descrizione fisica) — **IMPLEMENTATO v0.26.0**
10. ✅ `preservation_note` — Nota conservazione (textarea) — **IMPLEMENTATO v0.26.0**
11. ✅ `restoration` — Restauro (textarea) — **IMPLEMENTATO v0.26.0**
12. ✅ `note` — Nota unità (textarea) — **IMPLEMENTATO v0.26.0**
13. ✅ `physical_container_type` — Tipo contenitore fisico — **IMPLEMENTATO v0.26.0**
14. ✅ `physical_container_title` — Titolo contenitore fisico — **IMPLEMENTATO v0.26.0**
15. ✅ `physical_container_number` — Numero contenitore fisico — **IMPLEMENTATO v0.26.0**
16. ✅ **fe_fract_land_parcels** (formset) — Frazionamenti particelle fondiarie — **IMPLEMENTATO v0.26.0**
17. ✅ **fe_fract_edil_parcels** (formset) — Frazionamenti particelle edilizie — **IMPLEMENTATO v0.26.0**
18. ✅ **unit_urls** (formset) — URL dell'unità — **IMPLEMENTATO v0.26.0**
19. ✅ **unit_identifiers** (formset) — Identificativi dell'unità — **IMPLEMENTATO v0.26.0**
20. ✅ **sc2_attribution_reasons** (nested formset dentro sc2_authors) — autm — **IMPLEMENTATO v0.26.0**
21. ✅ **sc2_commission_names** (nested formset dentro sc2_commissions) — cmmn — **IMPLEMENTATO v0.26.0**
22. ✅ **fe_context** campi mancanti: sub_number, request, license_number, license_date, protocol_number, habitability_number, habitability_year, habitability_date — **IMPLEMENTATO v0.26.0**
23. ✅ **unit_other_reference_numbers** campi mancanti: qualifier, note — **IMPLEMENTATO v0.26.0** (modello aggiornato)

#### CREATOR
24. ✅ **creator_legal_statuses** (formset) — Stati giuridici — **IMPLEMENTATO v0.26.0**

#### FOND (relazioni)
25. ✅ Relazione con **Creatori** nel form Fond — **GIÀ ESISTENTE** (RelCreatorFond formset)
26. ✅ Relazione con **Custodi** nel form Fond — **GIÀ ESISTENTE** (RelCustodianFond formset)
27. ✅ Relazione con **Progetti** nel form Fond — **GIÀ ESISTENTE** (RelProjectFond formset)

#### CUSTODIAN
28. ✅ **custodian_editors editing_type** — da hardcoded a vocabolario — **FIXATO v0.26.0**

### ⚠️ DIFFERENZE DI WIDGET (funzionali ma diverse)

| Entità | Campo | Ruby | Python | Impatto | Stato |
|--------|-------|------|--------|---------|-------|
| Fond | `abstract` | Solo se is_root | Sempre visibile | Basso | Da fare |
| Fond | fond_langs | Dropdown da DB | LangSelect2Widget | ✅ Fixato | ✅ FIXATO v0.47.0 |
| Fond | sources | Livesearch | Dropdown Select2 | Medio | Da fare |
| Fond | fond_editors editing_type | terms_select | TextInput | Medio | Da fare |
| Fond | parent | Select | FondSelect2Widget | ✅ Fixato | ✅ FIXATO v0.47.0 |
| Unit | sources | Livesearch | Dropdown Select2 | Medio | Da fare |
| Unit | fond | Select | FondSelect2Widget | ✅ Fixato | ✅ FIXATO v0.47.0 |
| Unit | parent | Select | UnitSelect2Widget | ✅ Fixato | ✅ FIXATO v0.47.0 |
| Unit | classification | Select | ClassificationSelect2Widget | ✅ Fixato | ✅ FIXATO v0.47.0 |
| Unit | unit_langs | Dropdown da DB | LangSelect2Widget | ✅ Fixato | ✅ FIXATO v0.47.0 |
| Unit | unit_editors name | Autocomplete | TextInput | Medio | Da fare |
| Unit | unit_editors editing_type | terms_select | ChoiceField | Basso | Da fare |
| Unit | unit_other_reference_numbers | qualifier+note | Solo other_reference_number | Medio | Da fare |
| Creator | other_names qualifier | terms_select | TextInput | Medio | Da fare |
| Creator | residence | Autocomplete | Textarea | Medio | Da fare |
| Creator | sources | Livesearch | Dropdown Select2 | Medio | Da fare |
| Creator | relations | Autocomplete | Dropdown Select2 | Medio | Da fare |
| Custodian | other_names qualifier | terms_select | TextInput | Medio | Da fare |
| Custodian | contact_type | terms_select | TextInput | Medio | Da fare |
| Custodian | building_type | terms_select | TextInput | Medio | Da fare |
| Custodian | city/country | Autocomplete | TextInput | Medio | Da fare |
| Custodian | sources | Livesearch | Dropdown Select2 | Medio | Da fare |
| Custodian | relations | Autocomplete | Dropdown Select2 | Medio | Da fare |
| Custodian | custodian_editors editing_type | terms_select (7 termini) | ChoiceField da vocabolario (7 termini) | ✅ FIXATO v0.26.0 |
| Project | relations | Autocomplete | Dropdown Select2 | Medio | Da fare |
| Classification | parent | Select | ClassificationSelect2Widget | ✅ Fixato | ✅ FIXATO v0.47.0 |

---

## 6. DETAIL VIEWS (Viste di Lettura)

**Stato:** A partire da v0.27.0, tutte le detail view sono allineate ai rispettivi form, mostrando esattamente gli stessi campi che l'utente può inserire in scrittura.

### Fond Detail

| Sezione | Campi | Note |
|---------|-------|------|
| 1. Descrizione | padre, tipologia, pubblicato, lunghezza, entità, nomi alternativi, identificativi, lingue, abstract, descrizione, storia, nota archivista | ✅ Allineato v0.27.0 |
| 2. Altre informazioni | materiali correlati, tipo materiali, note, possessori, URL | ✅ Allineato v0.27.0 |
| 3. Accesso | condizioni accesso/uso, note, conservazione, tipo descrizione | ✅ Allineato v0.27.0 |
| 4. Relazioni | voci indice, forme documentarie | ✅ Allineato v0.27.0 |
| 5. Fonti | fonti collegate | ✅ Allineato v0.27.0 |
| 6. Compilatori | tabella compilatori | ✅ Allineato v0.27.0 |
| 7. Estremi cronologici | eventi | ✅ Allineato v0.27.0 |

### Creator Detail

| Sezione | Campi | Note |
|---------|-------|------|
| 1. Identificazione | tipo, tipo ente, pubblicato, sede, denominazione principale, denominazioni alternative, identificativi, URL, condizione giuridica | ✅ Allineato v0.27.0 |
| 2. Descrizione | abstract, storia, note, attività | ✅ Allineato v0.27.0 |
| 3. Relazioni | fondi, istituzioni, altri soggetti | ✅ Allineato v0.27.0 |
| 4. Fonti | fonti collegate | ✅ Allineato v0.27.0 |
| 5. Compilatori | tabella compilatori | ✅ Allineato v0.27.0 |
| Estremi cronologici | eventi | ✅ Allineato v0.27.0 |

### Unit Detail

| Sezione | Campi | Note |
|---------|-------|------|
| Descrizione | contesto, identificazione, titolo, attribuito, contenuti, estremi cronologici, identificativi, altre segnature, lingue | ✅ Completato v0.27.0 |
| Descrizione fisica | tipo fisico, supporto, conservazione, descrizione fisica, danni, materiali correlati, restauri, note, contenitore fisico | ✅ Completato v0.27.0 |
| Accesso | condizioni accesso/uso con note | ✅ Completato v0.27.0 |
| Fonti | fonti, voci di indice, anagrafiche | ✅ Esistente |
| Compilatori | tabella compilatori | ✅ Esistente |
| SC2/SC3, ICCD, FSC, FE | schede specialistiche | ✅ Esistenti |

### Custodian Detail

| Sezione | Campi | Note |
|---------|-------|------|
| Identificazione | condizione giuridica, macrotipologia, pubblicato, denominazione principale, altre denominazioni, contatti, referente, enti titolari, URL, identificativi | ✅ Allineato v0.27.0 (aggiunto "Pubblicato") |
| Descrizione | patrimonio, politiche di gestione, struttura amministrativa | ✅ Esistente |
| Accesso | orari, servizi | ✅ Esistente |
| Sedi | edifici | ✅ Esistente |
| Relazioni | fondi collegati | ✅ Esistente |
| Fonti | fonti collegate | ✅ Esistente |
| Compilatori | tabella compilatori | ✅ Esistente |

### Project Detail

| Sezione | Campi | Note |
|---------|-------|------|
| Identificazione | nome, tipologia, pubblicato, anno inizio/fine, status, descrizione, annotazioni, URL | ✅ Già completo |
| Responsabilità | responsabili, soggetti coinvolti | ✅ Già completo |
| Relazioni | fondi collegati | ✅ Già completo |

---

## AZIONI RICHIESTE

### ✅ Completate (v0.27.0 - v0.37.0)

- ✅ Fix JavaScript formset buttons (v0.27.0)
- ✅ Allineamento completo detail views (v0.27.0)
- ✅ Autocomplete Select2 per tutte le relazioni principali (v0.33.0)
- ✅ Refactoring Unit Views: God Object → handler (v0.37.0)
- ✅ Fix Sc2Form card_type (v0.37.0)

### ⚠️ Parzialmente completate (widget da migliorare — non bloccanti)

1. ~~Convertire dropdown → autocomplete/livesearch~~ — ✅ Select2 implementato per relazioni principali (v0.33.0). **Rimangono:** alcuni formset relazione usano ancora dropdown semplici (RelCreatorCreator, RelCreatorInstitution, ecc.)
2. Convertire qualifier TextInput → terms_select dove Ruby usa terms_select — **ANCORA DA FARE** per: Creator other_names, Custodian other_names, Custodian contact_type, Custodian building_type
3. Convertire residence Textarea → autocomplete — **ANCORA DA FARE**
4. Convertire city/country TextInput → autocomplete — **ANCORA DA FARE**
5. ~~Fond abstract: mostrare solo se is_root~~ — **✅ FATTO** (v0.38.0)

### ⚠️ Discrepanze note

| Campo | Ruby | Python | Impatto | Stato |
|-------|------|--------|---------|-------|
| ~~Unit: `parent_id`, `fond_id`, `tsk`~~ | ~~Hidden fields~~ | ~~Nel form ma non come hidden~~ | ~~Basso~~ | ~~Basso~~ | ✅ **FIXATO v0.38.0** |
| ~~Custodian: preferred_name `preferred`~~ | ~~Hidden = true~~ | ~~Mancante~~ | ~~Basso~~ | ~~Basso~~ | ✅ **FIXATO v0.38.0** |
| ~~Fond: `abstract`~~ | ~~Solo se is_root~~ | ~~Sempre visibile~~ | ~~Basso~~ | ~~Basso~~ | ✅ **FIXATO v0.38.0** |
| Relazioni formset | Autocomplete/livesearch | Dropdown Select2 | Basso | ✅ Select2 implementato v0.33.0 |
| Qualifier (varie entità) | terms_select | TextInput | Medio | ✅ **FIXATO v0.38.0** (CustodianName, CreatorName → dropdown da vocabolario) |

### ✅ Completate (v0.38.0)
- ✅ Unit hidden fields: `parent_id`, `fond_id`, `tsk` ora sono `<input type="hidden">`
- ✅ Custodian preferred_name: aggiunto campo hidden `preferred=True`
- ✅ Fond abstract: visibile solo se `is_root`
- ✅ Qualifier dropdown: `CustodianNameForm` e `CreatorOtherNameForm` usano dropdown da vocabolario (`custodian_names.qualifier`, `creator_names.qualifier`)

### Priorità BASSA (nice to have)
6. Pulsante "create reference number" per Unit
7. Textile editor sui textarea
8. Word counter sui textarea
9. Convertire city/country TextInput → autocomplete

---

## ✅ COMPLETAMENTO FUNZIONALE (v0.44.0 - 2026-04-07)

Tutte le funzionalità mancanti sono state implementate:

### Nuove funzionalità
- ✅ **Export AEF** — Round-trip completo con import (AEFExporter modulare + ExportFondAEFView + ExportAEFView)
- ✅ **Export XML** — 4 opzioni come Ruby: AEF, CAT-SAN, EAD/ICAR-IMPORT, METS (v0.54.0)
- ✅ **Export CSV unità** — Con filtri per fondo e ricerca
- ✅ **Report** — Report progetto + conservatore
- ✅ **Ricerca avanzata** — Filtri multipli per tipo entità, fondo, tipo unità, tipo produttore, pubblicati
- ✅ **Storico modifiche** — Modello EditorLog per tracciamento cambiamenti
- ✅ **Fix import/export round-trip** — 15+ handler import aggiunti, fix FK field names, mapping snake_case modelli
- ✅ **Export PDF/RTF completo** — Report inventario (fond), progetto, conservatore identici a Ruby (v0.46.0)
- ✅ **Select2 ibrido** — minimum-input-length=0 per dataset piccoli, nessun campo vuoto (v0.54.0)

### Export — Confronto Ruby vs Python (v0.54.0)
| Opzione export | Ruby | Python | Formato output |
|----------------|------|--------|----------------|
| Oggetti digitali | ✅ checkbox | ✅ checkbox | `.aef` (ZIP) |
| Entità correlate | ✅ checkbox | ✅ checkbox | `.aef` (mode full/not-full) |
| CAT-SAN / METS-SAN | ✅ checkbox | ✅ checkbox (v0.54.0) | `.zip` (XML multipli) |
| ICAR-IMPORT (EAD) | ✅ checkbox | ✅ checkbox (v0.54.0) | `.zip` (XML multipli) |
| Entità esportabili | Fond, Custodian, Creator, Source, Project | Fond, Custodian, Creator, Source, Project | ✅ Identico |
| Mutual exclusion JS | ✅ (SAN↔EAD, project→solo AEF) | ✅ (identica a Ruby) | ✅ Identico |

### Formattazione XML (v0.54.0)
| Formato | Namespace | Root element | File prodotti |
|---------|-----------|--------------|---------------|
| CAT-SAN | `http://san.mibac.it/cat-import/` | `catListRecords` | `complessi_*.xml`, `soggetto_produttore_*.xml`, `soggetto_conservatore_*.xml`, `fonte_*.xml` |
| EAD3 (Fond) | `http://ead3.archivists.org/schema/` | `ead` | `ead_fond_*.xml` |
| EAC-CPF (Creator) | `urn:isbn:1-931666-33-4` | `eac-cpf` | `ead_creator_*.xml` |
| SCONS2 (Custodian) | `http://www.san.beniculturali.it/scons2` | `scons` | `ead_custodian_*.xml` |
| EAD (Source) | `http://ead3.archivists.org/schema/` | `ead` | `ead_source_*.xml` |
| METS | `http://san.beniculturali.it/envelope-san/` + `http://www.loc.gov/mets/` | `envelope` | `digital_objects_mets.xml` |

### Export PDF/RTF (v0.46.0)
| Aspetto | Ruby | Python | Note |
|---------|------|--------|------|
| PDF | HTML ERB → wkhtmltopdf | HTML template → WeasyPrint | ✅ Identico |
| RTF | RtfBuilder + RtfWriter | RtfBuilder + RtfWriter | ✅ Identico |
| Campi Fond | 29 | 29 | ✅ Identico |
| Campi Unit | 49 | 49 | ✅ Identico |
| Campi Creator | 18 | 18 | ✅ Identico |
| Campi Custodian | 32 | 32 | ✅ Identico |
| Campi Project | 10 | 10 | ✅ Identico |
| Schede speciali | SC2, ICCD, FSC, FE | SC2, ICCD, FSC, FE | ✅ Identico |
| Callback complessi | 30+ | 30+ | ✅ Identico |
| Struttura report | Titolo→Progetti→Custodian→Creatori→Fondo→Unità | Identica | ✅ Identico |

### Differenze widget (funzionali ma non bloccanti)
| Differenza | Impatto | Note |
|-----------|---------|------|
| Relazioni: autocomplete vs Select2 | Basso | Select2 con AJAX implementato (v0.33.0) + ibrido per dataset piccoli (v0.54.0) |
| Qualifier: terms_select vs dropdown da vocabolario | Basso | Fixato v0.38.0 |
| Lingue: collection_select da DB vs LangSelect2Widget | Basso | Fixato v0.47.0 + ibrido per dataset piccoli (v0.54.0) |
| Città/Paese: autocomplete vs TextInput | Basso | Nice to have |
