# Guida ai Vocabolari Controllati - Archimista Python

**Data:** 2026-04-02  
**Versione:** 0.14.0  
**Stato:** ✅ PULITI - Solo termini originali Ruby

---

## Panoramica

Questo documento descrive i vocabolari controllati utilizzati in Archimista Python per standardizzare l'inserimento dei dati. I vocabolari sono stati allineati a quelli di **Archimista Ruby** originale.

**Importante:** I vocabolari contengono **SOLO i termini originali di Ruby**. Sono stati eliminati tutti i termini duplicati o personalizzati non presenti in Ruby.

---

## Fonte dei Vocabolari

I vocabolari originali di Archimista Ruby si trovano in:

```
/home/srbntt/Documenti/ProgrammiInformatici/archimista/db/seeds/
├── vocabularies.json    # Definizione vocabolari (nome)
└── terms.json           # Termini per ogni vocabolario
```

### Struttura dei file Ruby

**vocabularies.json** (ogni riga è un JSON object):
```json
{"name":"unit_damages.code"}
{"name":"units.preservation"}
{"name":"units.unit_type"}
```

**terms.json** (ogni riga è un termine):
```json
{"vocabulary_id":14,"position":18,"term_key":"lacune","term_value":"lacune"}
{"vocabulary_id":14,"position":23,"term_key":"rottura_cuciture","term_value":"rottura delle cuciture"}
{"vocabulary_id":12,"position":1,"term_key":"excellent","term_value":"ottimo"}
```

### Mappatura vocabulary_id → nome vocabolario

L'ordine in `vocabularies.json` determina l'ID:

| ID | Nome Vocabolario | Descrizione |
|----|------------------|-------------|
| 1 | creators.creator_type | Tipo creatore (P, F, C) |
| 2 | creator_names.qualifier | Qualificatore nomi creatore |
| 3 | creator_legal_statuses.legal_status | Stato giuridico creatore |
| 4 | custodian_contacts.contact_type | Tipo contatto custode |
| 5 | projects.project_type | Tipo progetto |
| 6 | projects.status | Stato progetto |
| 7 | project_managers.qualifier | Qualificatore responsabile progetto |
| 8 | project_credits.credit_type | Tipo credito progetto |
| 9 | fonds.fond_type | Tipologia fondo archivistico |
| 10 | fonds.preservation | Stato conservazione fondo |
| 11 | custodians.legal_status | Stato giuridico custode |
| **12** | **units.preservation** | **Stato conservazione unità** |
| **13** | **units.unit_type** | **Tipo unità archivistica** |
| **14** | **unit_damages.code** | **Tipologia danni** |
| 15 | custodian_names.qualifier | Qualificatore nomi custode |
| 16 | custodian_buildings.custodian_building_type | Tipo edificio custode |
| 17 | fonds.access_condition | Condizione accesso fondo |
| 18 | fonds.use_condition | Condizione uso fondo |
| 19 | units.access_condition | Condizione accesso unità |
| 20 | units.use_condition | Condizione uso unità |
| 21 | units.level_type | Tipo livello archivistico |
| **22** | **units.physical_type** | **Tipo fisico unità** |
| **23** | **units.medium** | **Supporto materiale** |
| 24 | headings.heading_type | Tipo voce di indice |
| 25 | editors.editing_type | Tipo compilazione |
| 26 | digital_objects.digital_object_type | Tipo oggetto digitale |
| 27 | project_stakeholders.qualifier | Qualificatore stakeholder |
| 28 | units.file_type | Tipo file (FSC) |
| 29 | anagraphics.anagraphic_type | Tipo anagrafica |
| 30 | fe_operas.status | Stato opera edilizia |

---

## Vocabolari Implementati in Python

### Script di Popolamento

Il file `seed_vocabularies.py` crea tutti i vocabolari nel database Django:

```bash
cd /home/srbntt/Documenti/ProgrammiInformatici/archimista/python_rewrite
source venv/bin/activate
python seed_vocabularies.py
```

### Vocabolario: unit_damages.code

**Descrizione:** Tipologia danni per le unità archivistiche

**Termini (da Ruby - vocabulary_id: 14):**

| Position | Term Key | Term Value (Italiano) |
|----------|----------|----------------------|
| 1 | humidity | danni da umidità |
| 2 | flood | danni da alluvione |
| 3 | rodents | danni da roditori |
| 4 | insects | danni da insetti |
| 5 | fire | danni da incendio |
| 6 | laceration | lacerazione |
| 7 | stain | macchia |
| 8 | mutilation | mutilazione |
| 9 | perforation | perforazione |
| 10 | folds | piegature |
| 11 | discoloration | scoloritura |
| 12 | crease | sgualcitura |
| 13 | fragile | fragilità del supporto |
| 14 | funghi_e_batteri | funghi e batteri |
| 15 | strappi | strappi |
| 16 | fogli_staccati | fogli staccati |
| 17 | ingiallimento | ingiallimento della carta |
| **18** | **lacune** | **lacune** |
| 19 | sbiadimento | sbiadimento |
| 20 | dispersione | dispersione |
| 21 | acidita | acidità |
| 22 | usura | usura |
| **23** | **rottura_cuciture** | **rottura delle cuciture** |

**Utilizzo nel form:**
```python
# archive/forms/unit.py
class UnitDamageForm(forms.ModelForm):
    class Meta:
        model = UnitDamage
        fields = ['code', 'note']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'list': 'damage_code_list',  # Datalist per suggerimenti
                'placeholder': 'Seleziona o inserisci tipo danno'
            }),
        }
```

**Template con datalist:**
```html
<!-- archimista_python/archive/templates/archive/unit_form.html -->
<datalist id="damage_code_list">
    {% for term in terms.unit_damages_code %}
    <option value="{{ term.term_value }}">{{ term.term_value }}</option>
    {% endfor %}
</datalist>
```

### Vocabolario: units.preservation

**Descrizione:** Stato di conservazione dell'unità

**Termini (da Ruby - vocabulary_id: 12):**

| Position | Term Key | Term Value |
|----------|----------|------------|
| 1 | excellent | ottimo |
| 2 | good | buono |
| 3 | discreet | discreto |
| 4 | mediocre | mediocre |
| 5 | bad | cattivo |
| 6 | very_bad | pessimo |

**Utilizzo nel form:**
```python
# archive/forms/unit.py - UnitForm
preservation_term = forms.ModelChoiceField(
    queryset=Term.objects.filter(vocabulary__name='units.preservation'),
    required=False,
    widget=forms.Select(attrs={'class': 'form-select'}),
    empty_label="-- Seleziona --"
)
```

### Vocabolario: units.unit_type

**Descrizione:** Tipo di unità archivistica

**Termini (da Ruby - vocabulary_id: 13):**

| Position | Term Key | Term Value |
|----------|----------|------------|
| 1 | list | registro o altra unità rilegata |
| 2 | file | fascicolo o altra unità complessa |
| 3 | item | unità documentaria |

### Vocabolario: units.physical_type

**Descrizione:** Tipo fisico dell'unità (contenitore)

**Termini (da Ruby - vocabulary_id: 22):**

| Position | Term Key | Term Value |
|----------|----------|------------|
| 1 | album | album |
| 2 | busta | busta |
| 3 | cartella | cartella |
| 4 | faldone | faldone |
| 5 | fascicolo | fascicolo |
| 6 | filza | filza |
| 7 | foglio | foglio |
| 8 | manifesto | manifesto |
| 9 | mappa | mappa |
| 10 | mazzo | mazzo |
| 11 | opuscolo | opuscolo |
| 12 | pacco | pacco |
| 13 | plico | plico |
| 14 | quaderno | quaderno |
| 15 | registro | registro |
| 16 | rivista | rivista |
| 17 | rotolo | rotolo |
| 18 | scatola | scatola |
| 19 | scheda | scheda |
| 20 | taccuino | taccuino |
| 21 | volume | volume |

### Vocabolario: units.medium

**Descrizione:** Supporto materiale dell'unità

**Termini (da Ruby - vocabulary_id: 23):**

| Position | Term Key | Term Value |
|----------|----------|------------|
| 1 | paper | carta |
| 2 | parchment | pergamena |
| 3 | linen_paper | carta telata |
| 4 | cardboard | cartoncino |
| 5 | film | pellicola |
| 6 | other | altro |

---

## Differenze tra Ruby e Python

### Ruby (Originale)
- Usa `terms_select` helper nei form
- I termini sono caricati dal database in base al nome del vocabolario
- Campo dropdown standard

```erb
<!-- Ruby: app/views/units/_unit_damage.html.erb -->
<%= terms_select(f, "unit_damages.code", {:include_blank => true}) %>
```

### Python (Django)
- Usa `ModelChoiceField` con queryset filtrato
- **Approccio ibrido:** campo testo con datalist per suggerimenti
- Permette sia selezione da vocabolario che inserimento libero

```python
# Python: archive/forms/unit.py
widgets = {
    'code': forms.TextInput(attrs={'list': 'damage_code_list'})
}
```

**Motivazione:** L'import AEF salva valori testuali liberi (es. "lacune"). Mantenere il campo testo permette di:
1. Visualizzare i valori importati
2. Avere suggerimenti dal vocabolario
3. Inserire nuovi valori personalizzati

---

## Come Aggiungere Nuovi Vocabolari

### 1. Aggiungere a seed_vocabularies.py

```python
vocab_new = create_vocabulary("entities.new_field", "Descrizione")
new_terms = [
    ("entities.new_field.value1", "Valore 1"),
    ("entities.new_field.value2", "Valore 2"),
]
for i, (key, value) in enumerate(new_terms, 1):
    create_term(vocab_new, key, value, i)
```

### 2. Aggiungere il campo al modello

```python
# archive/models/core.py
class Entity(models.Model):
    new_field_term = models.ForeignKey(
        'Term', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='new_field_term_id'
    )
    new_field = models.CharField(max_length=255, null=True, blank=True)
```

### 3. Creare migrazione

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Aggiungere al form

```python
# archive/forms/unit.py
class EntityForm(forms.ModelForm):
    new_field_term = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleziona --"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_field_term'].queryset = Term.objects.filter(
            vocabulary__name='entities.new_field'
        ).order_by('position')
```

### 5. Passare i termini alla vista

```python
# archive/views/unit.py
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['terms'] = {
        'entities_new_field': Term.objects.filter(
            vocabulary__name='entities.new_field'
        ).order_by('position'),
    }
    return context
```

---

## Verifica Vocabolari Esistenti

```bash
cd /home/srbntt/Documenti/ProgrammiInformatici/archimista/python_rewrite
source venv/bin/activate
python manage.py shell
```

```python
from archive.models import Vocabulary, Term

# Lista vocabolari
for vocab in Vocabulary.objects.all():
    print(f"{vocab.name}: {vocab.terms.count()} termini")

# Termini di un vocabolario specifico
terms = Term.objects.filter(vocabulary__name='unit_damages.code').order_by('position')
for term in terms:
    print(f"{term.term_key}: {term.term_value}")
```

---

## Note Importanti

1. **Import AEF:** I valori importati sono salvati come testo libero, non come FK a Term
2. **Retrocompatibilità:** I campi testo originali sono mantenuti per fallback
3. **Termini Ruby originali:** I vocabolari contengono SOLO i termini originali di Ruby (puliti il 2026-04-02)
4. **Aggiornamenti:** Se si aggiungono termini, eseguire `python seed_vocabularies.py` (usa `get_or_create`, non duplica)
5. **Pulizia duplicati:** Usare `python clean_vocabularies.py` per eliminare termini non-Ruby

### Pulizia eseguita il 2026-04-02

**Script utilizzato:** `clean_vocabularies.py`

**Termini eliminati:**
- 53 termini non-Ruby (es. "Acido", "Fragile", "Libro", "Busta", ecc.)
- 8 duplicati con chiavi diverse (es. "Ottimo" vs "ottimo")

**Risultato:**
- `unit_damages.code`: 23 termini (solo Ruby)
- `units.preservation`: 6 termini (solo Ruby)
- `units.unit_type`: 3 termini (solo Ruby)
- `units.physical_type`: 21 termini (solo Ruby)
- `units.medium`: 6 termini (solo Ruby)

---

## Riferimenti

- File Ruby originali: `/home/srbntt/Documenti/ProgrammiInformatici/archimista/db/seeds/`
- Script Python:
  - `seed_vocabularies.py` - Popola vocabolari
  - `clean_vocabularies.py` - Pulisce duplicati
- Modelli: `/home/srbntt/Documenti/ProgrammiInformatici/archimista/python_rewrite/archimista_python/archive/models/vocabulary.py`
- Form: `/home/srbntt/Documenti/ProgrammiInformatici/archimista/python_rewrite/archimista_python/archive/forms/`
