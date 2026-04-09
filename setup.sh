#!/usr/bin/env bash
# =============================================================================
# setup.sh — Script di inizializzazione rapida per Archimista Python/Django
# =============================================================================
#
# Crea il database, applica le migrazioni, popola vocabolari e source_types,
# inserisce dati di esempio e crea l'utente admin.
#
# Uso:
#   bash setup.sh            # Con dati di esempio
#   bash setup.sh --no-seed  # Senza dati di esempio (database vuoto)
#
# Requisiti:
#   - Virtual environment attivato (source venv/bin/activate)
#   - Dipendenze installate (pip install -r requirements.txt)
# =============================================================================

set -e  # Esci immediatamente in caso di errore

echo "============================================================"
echo "  Archimista Python/Django — Setup iniziale"
echo "============================================================"
echo ""

# Controlla che Django sia disponibile
if ! python -c "import django" 2>/dev/null; then
    echo "ERRORE: Django non è installato."
    echo "Assicurati che il virtual environment sia attivo:"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Controlla che manage.py esista
if [ ! -f "manage.py" ]; then
    echo "ERRORE: manage.py non trovato."
    echo "Esegui questo script dalla directory python_rewrite/"
    exit 1
fi

# -------------------------------------------------------
# Passo 1: Migrazioni
# -------------------------------------------------------
echo ""
echo "── Passo 1/5: Applicazione migrazioni database ──"
python manage.py migrate --no-input
echo "  ✓ Migrazioni applicate."

# -------------------------------------------------------
# Passo 2: Vocabolari controllati
# -------------------------------------------------------
echo ""
echo "── Passo 2/5: Popolamento vocabolari controllati ──"
python seed_vocabularies.py
echo ""

# -------------------------------------------------------
# Passo 3: Tipologie di fonte
# -------------------------------------------------------
echo ""
echo "── Passo 3/5: Popolamento tipologie di fonte ──"
python seed_source_types.py
echo ""

# -------------------------------------------------------
# Passo 4: Dati di esempio (opzionale)
# -------------------------------------------------------
NO_SEED=false
for arg in "$@"; do
    if [ "$arg" = "--no-seed" ]; then
        NO_SEED=true
        break
    fi
done

if [ "$NO_SEED" = false ]; then
    echo ""
    echo "── Passo 4/5: Inserimento dati di esempio ──"
    python seed.py
    echo ""
else
    echo ""
    echo "── Passo 4/5: Dati di esempio saltati (--no-seed) ──"
fi

# -------------------------------------------------------
# Passo 5: Utente admin
# -------------------------------------------------------
echo ""
echo "── Passo 5/5: Creazione utente admin ──"
python seed_admin_user.py
echo ""

# -------------------------------------------------------
# Riepilogo
# -------------------------------------------------------
echo "============================================================"
echo "  Setup completato!"
echo "============================================================"
echo ""
echo "Per avviare il server di sviluppo:"
echo "  python manage.py runserver"
echo ""
echo "Poi apri il browser su: http://127.0.0.1:8000/"
echo ""
echo "Note:"
echo "  - Al primo accesso ti verrà chiesto di cambiare la password"
echo "  - I vocabolari controllati sono pronti per l'uso"
echo "  - Il formato import/export AEF è compatibile con Archimista Ruby"
echo ""
if [ "$NO_SEED" = false ]; then
    echo "  Dati di esempio inseriti: 1 fondo, 1 unità, 1 creatore,"
    echo "  1 conservatore, 2 voci di indice, 2 classificazioni."
fi
echo "============================================================"
