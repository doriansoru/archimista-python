# Test di Regressione Python vs Ruby — Istruzioni

**Data:** 2026-04-08
**Versione:** 0.53.0 (in sviluppo)

---

## Obiettivo

Confrontare l'output del porting Python con quello di Archimista Ruby (in VirtualBox) per verificare che:

1. **AEF (data.json)** — Gli stessi dati esportati da Python e Ruby abbiano la stessa struttura
2. **PDF** — I report generati contengano le stesse informazioni
3. **RTF** — I report RTF abbiano contenuto comparabile

Questo approccio risolve il problema della non-installabilità di Ruby su sistemi moderni, usando VirtualBox come ambiente di riferimento.

---

## Architettura

```
┌──────────────────────────────────────────────────────┐
│  Python (host)                                       │
│                                                      │
│  1. generate_reference_aef.py                        │
│     → Crea dati completi in DB                       │
│     → Esporta AEF → reference_aef.zip               │
│                                                      │
│  2. [TU su VirtualBox]                               │
│     → Importa reference_aef.zip in Ruby             │
│     → Esporta AEF → ruby_export.aef                 │
│     → Esporta PDF → ruby_report.pdf                 │
│     → Esporta RTF → ruby_report.rtf                 │
│                                                      │
│  3. test_ruby_comparison.py / test_regression_ruby   │
│     → Confronta AEF vs AEF (data.json diff)          │
│     → Confronta PDF vs PDF (text extraction)         │
│     → Confronta RTF vs RTF (text extraction)         │
└──────────────────────────────────────────────────────┘
```

---

## Passaggio 1 — Genera l'AEF di riferimento

```bash
cd /home/srbntt/Documenti/ProgrammiInformatici/Python/archimista/python_rewrite
source venv/bin/activate
python generate_reference_aef.py
```

**Cosa fa:**
- Pulisce il database
- Crea dati completi (vedi dettaglio sotto)
- Genera **DUE** file:
  - `reference_aef.zip` — formato NDJSON (per Python)
  - `reference_aef_ruby.aef` — formato JSON array (per Ruby)

**Output atteso:** ~85 record in 74 modelli

---

## Passaggio 2 — Importa ed esporta da Ruby (VirtualBox)

### 2a. Copia l'AEF sulla VM

```bash
# Dalla macchina host, copia il file Ruby-format sulla VM
scp tests/regression/reference/reference_aef.aef utente@vm:/percorso/condiviso/
```

**IMPORTANTE:** Usa `reference_aef.aef` (formato NDJSON, estensione .aef).

### 2b. Importa su Archimista Ruby

1. Avvia la VM VirtualBox con Archimista Ruby
2. Apri il browser e vai su Archimista Ruby
3. Vai su **Strumenti → Importa AEF**
4. Seleziona `reference_aef.zip`
5. Attendi il completamento dell'importazione

### 2c. Esporta da Ruby

Dalla scheda del fondo appena importato:

1. **AEF:** Clicca "Esporta AEF" → salva come `ruby_export.aef`
2. **PDF:** Vai su **Strumenti → Report → Inventario completo** → seleziona il fondo → clicca "Scarica PDF" → salva come `ruby_report.pdf`
3. **RTF:** Dalla stessa pagina → clicca "Scarica RTF" → salva come `ruby_report.rtf`

### 2d. Copia i file Ruby sulla macchina host

```bash
# Dalla VM, copia i file nella directory di confronto
scp ruby_export.aef host:/path/to/python_rewrite/tests/regression/ruby_output/
scp ruby_report.pdf host:/path/to/python_rewrite/tests/regression/ruby_output/
scp ruby_report.rtf host:/path/to/python_rewrite/tests/regression/ruby_output/
```

**Posizione finale attesa:**
```
python_rewrite/tests/regression/ruby_output/
├── ruby_export.aef
├── ruby_report.pdf
└── ruby_report.rtf
```

---

## Passaggio 3 — Esegui il confronto

### Opzione A: Standalone (script completo)

```bash
cd /home/srbntt/Documenti/ProgrammiInformatici/Python/archimista/python_rewrite
source venv/bin/activate
python tests/regression/test_ruby_comparison.py
```

Questo script:
- Genera automaticamente i report Python (PDF + RTF) se non esistono
- Confronta AEF Python vs Ruby
- Confronta PDF Python vs Ruby
- Confronta RTF Python vs Ruby
- Stampa un riepilogo con PASS/FAIL

### Opzione B: Integrato nella suite test

```bash
python test_complete.py
```

Il modulo `test_regression_ruby.py` viene eseguito automaticamente insieme agli altri 359 test. Se i file Ruby non esistono, i test vengono **saltati** (non falliscono).

---

## Cosa viene confrontato

### AEF (data.json)

| Check | Descrizione |
|-------|-------------|
| **Modelli presenti** | Stessi modelli in entrambi (nessuno solo in Python o solo in Ruby) |
| **Conteggio record** | Ogni modello ha lo stesso numero di record |
| **Campi per modello** | Fond, Unit, SC2, ICCD hanno gli stessi campi |
| **Valori chiave** | name, description, abstract, history del Fond sono identici |
| **Completezza SC2** | Campi essenziali: sgti, mtce, sdtt, sdts, dpgf, misa, misl, card_type |
| **Completezza ICCD** | Campi essenziali: denomination, object_type, category, age_century |

### PDF

| Check | Descrizione |
|-------|-------------|
| **Contenuto Python** | Parole chiave presenti (fondo, comune, registro, fascicolo, fotografia, pianta, torino, sc2) |
| **Overlap Python vs Ruby** | Almeno 50% delle parole in comune |

### RTF

| Check | Descrizione |
|-------|-------------|
| **Contenuto Python** | Parole chiave presenti (fondo, comune, registro, fascicolo, torino) |
| **Overlap Python vs Ruby** | Almeno 50% delle parole in comune |

---

## Risoluzione problemi

### "Ruby AEF non trovato"

I test vengono saltati. Significa che non hai ancora copiato i file Ruby. Segui il Passaggio 2.

### "Impossibile estrarre testo dai PDF"

Installa una libreria per l'estrazione testo:

```bash
pip install pymupdf    # Opzione migliore
# oppure
pip install pypdf      # Alternativa
# oppure
sudo apt install poppler-utils  # Per pdftotext CLI
```

### Differenze nei conteggi record

Possibili cause:
- Ruby crea record aggiuntivi automaticamente (es. editor di sistema)
- Ruby non esporta alcuni modelli che Python esporta
- L'importazione Ruby ha creato record duplicati

**Cosa fare:** Controlla il dettaglio dell'errore per identificare quali modelli differiscono.

### Differenze nei campi

Possibili cause:
- Ruby usa nomi campo diversi (es. `parent_id` vs `legacy_parent_id`)
- Python ha campi extra non presenti in Ruby
- Ruby ha campi legacy non portati in Python

**Cosa fare:** Verifica nel file `data.json` estratto da entrambi gli AEF:

```bash
# Estrai data.json dagli AEF
cd tests/regression
unzip reference/reference_aef.zip -d py_aef/
unzip ruby_output/ruby_export.aef -d rb_aef/

# Confronta visivamente
cat py_aef/data.json | python -m json.tool | head -100
cat rb_aef/data.json | python -m json.tool | head -100
```

### Overlap PDF/RTF troppo basso

Possibili cause:
- Formattazione diversa (date, numeri, intestazioni)
- Ordine delle sezioni diverso
- Lingua diversa (alcune etichette potrebbero essere in inglese in Ruby)

**Cosa fare:** Estrai il testo e confronta manualmente:

```bash
python -c "
from tests.regression.test_ruby_comparison import extract_pdf_text, normalize
py = normalize(extract_pdf_text('tests/regression/reference/python_report.pdf'))
rb = normalize(extract_pdf_text('tests/regression/ruby_output/ruby_report.pdf'))
print('Python:', py[:500])
print('---')
print('Ruby:', rb[:500])
"
```

---

## Rigenerare l'AEF di riferimento

Se modifichi i dati di riferimento:

```bash
python generate_reference_aef.py
```

Poi **devi** rieseguire il Passaggio 2 (import/export da Ruby) con il nuovo AEF.

---

## Struttura file

```
tests/regression/
├── reference/
│   ├── reference_aef.zip      # AEF generato da Python
│   ├── python_report.pdf      # Report PDF generato da Python
│   └── python_report.rtf      # Report RTF generato da Python
├── ruby_output/
│   ├── ruby_export.aef        # AEF esportato da Ruby
│   ├── ruby_report.pdf        # PDF esportato da Ruby
│   └── ruby_report.rtf        # RTF esportato da Ruby
└── test_ruby_comparison.py    # Script standalone di confronto

tests/
└── test_regression_ruby.py    # Modulo integrato nella suite test
```
