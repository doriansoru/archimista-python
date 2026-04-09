@echo off
REM =============================================================================
REM setup.bat — Script di inizializzazione rapida per Archimista Python/Django
REM =============================================================================
REM
REM Crea il database, applica le migrazioni, popola vocabolari e source_types,
REM inserisce dati di esempio e crea l'utente admin.
REM
REM Uso:
REM   setup.bat            # Con dati di esempio
REM   setup.bat --no-seed  # Senza dati di esempio (database vuoto)
REM
REM Requisiti:
REM   - Virtual environment attivato (venv\Scripts\activate)
REM   - Dipendenze installate (pip install -r requirements.txt)
REM =============================================================================

setlocal enabledelayedexpansion

echo ============================================================
echo   Archimista Python/Django — Setup iniziale
echo ============================================================
echo.

REM Controlla che Django sia disponibile
python -c "import django" 2>nul
if errorlevel 1 (
    echo ERRORE: Django non e installato.
    echo Assicurati che il virtual environment sia attivo:
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Controlla che manage.py esista
if not exist "manage.py" (
    echo ERRORE: manage.py non trovato.
    echo Esegui questo script dalla directory python_rewrite\
    exit /b 1
)

REM -------------------------------------------------------
REM Passo 1: Migrazioni
REM -------------------------------------------------------
echo.
echo -- Passo 1/5: Applicazione migrazioni database --
python manage.py migrate --no-input
if errorlevel 1 (
    echo ERRORE: Migrazioni fallite!
    exit /b 1
)
echo   [OK] Migrazioni applicate.

REM -------------------------------------------------------
REM Passo 2: Vocabolari controllati
REM -------------------------------------------------------
echo.
echo -- Passo 2/5: Popolamento vocabolari controllati --
python seed_vocabularies.py
if errorlevel 1 (
    echo ERRORE: Seed vocabolari fallito!
    exit /b 1
)
echo.

REM -------------------------------------------------------
REM Passo 3: Tipologie di fonte
REM -------------------------------------------------------
echo.
echo -- Passo 3/5: Popolamento tipologie di fonte --
python seed_source_types.py
if errorlevel 1 (
    echo ERRORE: Seed source_types fallito!
    exit /b 1
)
echo.

REM -------------------------------------------------------
REM Passo 4: Dati di esempio (opzionale)
REM -------------------------------------------------------
set NO_SEED=false
for %%a in (%*) do (
    if "%%a"=="--no-seed" set NO_SEED=true
)

if "%NO_SEED%"=="false" (
    echo.
    echo -- Passo 4/5: Inserimento dati di esempio --
    python seed.py
    if errorlevel 1 (
        echo ERRORE: Seed dati fallito!
        exit /b 1
    )
    echo.
) else (
    echo.
    echo -- Passo 4/5: Dati di esempio saltati (--no-seed) --
)

REM -------------------------------------------------------
REM Passo 5: Utente admin
REM -------------------------------------------------------
echo.
echo -- Passo 5/5: Creazione utente admin --
python seed_admin_user.py
if errorlevel 1 (
    echo ERRORE: Creazione admin fallita!
    exit /b 1
)
echo.

REM -------------------------------------------------------
REM Riepilogo
REM -------------------------------------------------------
echo ============================================================
echo   Setup completato!
echo ============================================================
echo.
echo Per avviare il server di sviluppo:
echo   python manage.py runserver
echo.
echo Poi apri il browser su: http://127.0.0.1:8000/
echo.
echo Note:
echo   - Al primo accesso ti verra chiesto di cambiare la password
echo   - I vocabolari controllati sono pronti per l'uso
echo   - Il formato import/export AEF e compatibile con Archimista Ruby
echo.
if "%NO_SEED%"=="false" (
    echo   Dati di esempio inseriti: 1 fondo, 1 unita, 1 creatore,
    echo   1 conservatore, 2 voci di indice, 2 classificazioni.
)
echo ============================================================

endlocal
