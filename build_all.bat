@echo off
REM =============================================================================
REM build_all.bat - One-click build of Archimista Windows installer
REM =============================================================================
REM
REM This script automates the entire build process:
REM   1. Runs build_installer.bat (PyInstaller bundle)
REM   2. Runs Inno Setup compiler (creates .exe installer)
REM
REM Requirements:
REM   - Python 3.10+ installed and in PATH
REM   - Virtual environment with all requirements installed
REM   - Inno Setup 6.x installed (https://jrsoftware.org/isdl.php)
REM     and iscc.exe in PATH or at default install location
REM
REM Output:
REM   output\Archimista-Setup-1.0.0.exe
REM =============================================================================

setlocal enabledelayedexpansion

echo ============================================================
echo   Archimista -- Build Completo Installer Windows
echo ============================================================
echo.

REM ============================================================
REM Step 1: PyInstaller bundle
REM ============================================================
echo ============================================================
echo   FASE 1/2: Build PyInstaller bundle
echo ============================================================
echo.

call build_installer.bat
if errorlevel 1 (
    echo.
    echo ERRORE: Build PyInstaller fallita^!
    echo Correggi gli errori e riprova.
    exit /b 1
)

REM Verify the bundle exists
if not exist "dist\archimista\Archimista.exe" (
    echo.
    echo ERRORE: Bundle non trovato in dist\archimista\Archimista.exe
    exit /b 1
)
echo   [OK] Bundle verificato: dist\archimista\Archimista.exe
echo.

REM ============================================================
REM Step 2: Inno Setup compilation
REM ============================================================
echo ============================================================
echo   FASE 2/2: Compilazione installer Windows (Inno Setup)
echo ============================================================
echo.

REM Find iscc.exe (Inno Setup Compiler)
set ISCC_PATH=
where iscc >nul 2>&1
if not errorlevel 1 (
    set ISCC_PATH=iscc
)

if "!ISCC_PATH!"=="" (
    REM Try default installation paths
    if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    ) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
        set ISCC_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
    ) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
        set ISCC_PATH="C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    ) else if exist "C:\Program Files\Inno Setup 5\ISCC.exe" (
        set ISCC_PATH="C:\Program Files\Inno Setup 5\ISCC.exe"
    )
)

if "!ISCC_PATH!"=="" (
    echo ATTENZIONE: Inno Setup (iscc.exe) non trovato.
    echo.
    echo   Il bundle PyInstaller e stato creato con successo:
    echo     dist\archimista\
    echo.
    echo   Per creare l'installer .exe:
    echo     1. Scarica e installa Inno Setup 6:
    echo        https://jrsoftware.org/isdl.php
    echo     2. Apri archimista_installer.iss in Inno Setup
    echo     3. Clicca Compile (Build)
    echo.
    echo   L'installer sara creato in: output\Archimista-Setup-*.exe
    echo.
    goto :bundle_ok
)

echo   Compiler trovato: !ISCC_PATH!
echo.

"!ISCC_PATH!" "archimista_installer.iss"
if errorlevel 1 (
    echo.
    echo ERRORE: Compilazione Inno Setup fallita^!
    echo Controlla i messaggi sopra per dettagli.
    exit /b 1
)

echo.
echo   [OK] Installer compilato con successo.

REM Find the output file
for %%f in (output\Archimista-Setup-*.exe) do (
    echo.
    echo ============================================================
    echo   INSTALLER CREATO: %%f
    echo ============================================================
    echo.
    echo   Distribuisci questo file agli utenti finali.
    echo   E un installer Windows completo che include:
    echo     - Tutte le dipendenze Python
    echo     - Django e librerie terze parti
    echo     - File del progetto Archimista
    echo.
    echo   Gli utenti dovranno solo:
    echo     1. Eseguire l'installer (doppio click)
    echo     2. Seguire la procedura guidata
    echo     3. Avviare Archimista dal menu Start
    echo     4. Al primo avvio, configurare il database
    echo.
    goto :end
)

echo ERRORE: File di output non trovato in output\
exit /b 1

:bundle_ok
echo ============================================================
echo   BUILD PARZIALE COMPLETATO
echo ============================================================
echo.
echo   Il bundle PyInstaller e pronto in:
echo     dist\archimista\
echo.
echo   Per creare l'installer .exe finale, installa Inno Setup 6:
echo     https://jrsoftware.org/isdl.php
echo.
echo   Poi riesegui questo script.
echo ============================================================
exit /b 0

:end

endlocal
