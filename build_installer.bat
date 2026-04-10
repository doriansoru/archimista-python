@echo off
REM =============================================================================
REM build_installer.bat - Build PyInstaller bundle for Archimista
REM =============================================================================
REM
REM This script:
REM   1. Installs PyInstaller (if not already present)
REM   2. Runs collectstatic
REM   3. Builds the PyInstaller bundle using archimista.spec
REM
REM Requirements:
REM   - Python 3.10+ installed
REM   - Virtual environment activated (venv\Scripts\activate)
REM   - All requirements installed (pip install -r requirements.txt)
REM
REM Output:
REM   dist\archimista\  (one-dir bundle)
REM =============================================================================

setlocal enabledelayedexpansion

echo ============================================================
echo   Archimista -- PyInstaller Build
echo ============================================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato. Installalo e assicurati che sia nel PATH.
    exit /b 1
)

echo [1/4] Verifica ambiente Python...
python -c "import django" 2>nul
if errorlevel 1 (
    echo.
    echo ERRORE: Django non e installato.
    echo Attiva il virtual environment e installa le dipendenze:
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)
echo   [OK] Django disponibile.
echo.

REM --- Install PyInstaller ---
echo [2/4] Installazione PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERRORE: Installazione PyInstaller fallita^!
    exit /b 1
)
echo   [OK] PyInstaller installato.
echo.

REM --- Collect static files ---
echo [3/4] Raccolta file statici (collectstatic)...
python manage.py collectstatic --no-input --clear
if errorlevel 1 (
    echo ATTENZIONE: collectstatic ha riportato errori (non critico^).
)
echo   [OK] File statici raccolti.
echo.

REM --- Build with PyInstaller ---
echo [4/4] Build PyInstaller bundle...
echo   (puo richiedere alcuni minuti...)
echo.

pyinstaller --clean archimista.spec
if errorlevel 1 (
    echo.
    echo ERRORE: Build PyInstaller fallita^!
    echo Controlla i messaggi sopra per dettagli.
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD COMPLETATO^!
echo ============================================================
echo.
echo   Bundle creato in: dist\archimista\
echo.
echo   Per testare il bundle:
echo     cd dist\archimista
echo     Archimista.exe
echo.
echo   Il bundle contiene tutto il necessario per funzionare.
echo   Al primo avvio partira la configurazione guidata.
echo.
echo ============================================================

endlocal
