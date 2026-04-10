# Archimista — Windows Installer Build Guide

This directory contains everything needed to build a standalone Windows installer
for Archimista (the Python/Django port).

---

## Overview

The build process has **two stages**:

| Stage | Tool | Output |
|-------|------|--------|
| **1. PyInstaller** | Bundles Python + Django + all libs | `dist\archimista\` (folder with .exe + DLLs) |
| **2. Inno Setup** | Wraps the bundle in a Windows installer wizard | `output\Archimista-Setup-*.exe` |

```
┌─────────────────────────────────────────────────────────────────┐
│  build_all.bat (one-click)                                      │
│  ┌──────────────────────┐    ┌──────────────────────────────┐  │
│  │  Stage 1: PyInstaller│───▶│  dist\archimista\            │  │
│  │  archimista.spec     │    │  (Archimista.exe + libs)     │  │
│  └──────────────────────┘    └──────────────┬───────────────┘  │
│                                             │                   │
│  ┌──────────────────────┐    ┌──────────────▼───────────────┐  │
│  │  Stage 2: Inno Setup │◀───│  archimista_installer.iss    │  │
│  │  (iscc.exe)          │    │  (installer script)          │  │
│  └──────────┬───────────┘    └──────────────────────────────┘  │
│             │                                                   │
│             ▼                                                   │
│  output\Archimista-Setup-1.0.0.exe ← Final distributable       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites (Build Machine)

### Required
- **Windows 10/11** (x64)
- **Python 3.10+** (64-bit, same arch as target)
- **Git Bash or Command Prompt**

### For Stage 1 (PyInstaller)
```cmd
REM Activate your virtual environment
venv\Scripts\activate

REM Install build dependencies
pip install -r requirements-build.txt

REM Ensure all runtime deps are installed
pip install -r requirements.txt
```

### For Stage 2 (Inno Setup)
- Download and install [Inno Setup 6.x](https://jrsoftware.org/isdl.php)
- The installer auto-detects it; if not, add `iscc.exe` to your PATH

---

## Quick Build (One-Click)

```cmd
build_all.bat
```

If successful, the final installer appears in:
```
output\Archimista-Setup-1.0.0.exe
```

---

## Step-by-Step Build

### Stage 1: PyInstaller Bundle

```cmd
build_installer.bat
```

**What it does:**
1. Verifies Django is available
2. Installs PyInstaller via pip
3. Runs `collectstatic` to gather CSS/JS/images
4. Runs `pyinstaller --clean archimista.spec`

**Output:**
```
dist\archimista\
├── Archimista.exe          ← Main executable (launcher)
├── python312.dll           ← Embedded Python runtime
├── _internal\              ← All bundled packages (Django, etc.)
├── archimista_python\      ← Django app code + templates + migrations
├── manage.py
├── seed.py
├── seed_vocabularies.py
├── seed_source_types.py
├── seed_admin_user.py
├── requirements.txt
└── archimista_launcher.py
```

**Test the bundle:**
```cmd
cd dist\archimista
Archimista.exe
```

At first run, the launcher will:
1. Run Django migrations
2. Seed controlled vocabularies
3. Seed source types
4. **Ask** if you want demo data
5. Create the admin user and display the temporary password
6. Start the web server and open your browser

---

### Stage 2: Inno Setup Installer

```cmd
REM Make sure Stage 1 completed successfully first
iscc.exe archimista_installer.iss
```

Or open `archimista_installer.iss` in the Inno Setup IDE and click **Build → Compile**.

**What it does:**
- Packages the `dist\archimista\` folder into a professional Windows installer
- Creates Start Menu shortcuts
- Creates optional Desktop shortcut
- Shows an Italian/English installation wizard

**Output:**
```
output\Archimista-Setup-1.0.0.exe
```

**File size:** ~150-300 MB (includes Python + all dependencies)

---

## File Reference

| File | Purpose |
|------|---------|
| `archimista_launcher.py` | Smart launcher — handles first-run setup, asks about demo data, creates admin, starts server |
| `archimista.spec` | PyInstaller specification — defines what to bundle |
| `build_installer.bat` | Stage 1 build script (PyInstaller) |
| `archimista_installer.iss` | Inno Setup script — defines the installer wizard |
| `build_all.bat` | One-click orchestrator (runs both stages) |
| `requirements-build.txt` | Build-time dependencies (PyInstaller only) |
| `INSTALLER_BUILD.md` | This file |

---

## How the Launcher Works

`archimista_launcher.py` is the entry point of the bundled application.

### First Run
```
┌────────────────────────────────────────────┐
│  Archimista — Prima esecuzione             │
│                                            │
│  1. Applica migrazioni database            │
│  2. Popola vocabolari controllati          │
│  3. Popola tipologie di fonte              │
│  4. Vuoi dati di esempio? [S/n]: _        │
│  5. Crea utente admin → mostra password    │
│  6. Salva credenziali in admin_credentials │
│  7. Avvia server + apre browser            │
└────────────────────────────────────────────┘
```

A marker file `first_run.done` is created after the first run.

### Subsequent Runs
```
┌────────────────────────────────────────────┐
│  Archimista — Avvio                        │
│                                            │
│  1. Verifica database esistente            │
│  2. Avvia server su :8000                  │
│  3. Apre browser automaticamente           │
└────────────────────────────────────────────┘
```

### Reset First-Run State
Delete `first_run.done` (and optionally `db.sqlite3`) to re-run setup.

---

## Customization

### Change the Version Number

Edit `archimista_installer.iss`:
```pascal
#define MyAppVersion "1.0.0"   ← change this
```

And recompile.

### Add an Application Icon

1. Create/buy a `.ico` file (256x256 recommended)
2. Place it in `python_rewrite\archimista_icon.ico`
3. Edit `archimista.spec`:
   ```python
   exe = EXE(
       ...
       icon='archimista_icon.ico',
   )
   ```
4. Edit `archimista_installer.iss`:
   ```pascal
   SetupIconFile=archimista_icon.ico
   ```
5. Rebuild both stages.

### Change the Default Port

Edit `archimista_launcher.py`, line with `port = 8000`.

### Disable Auto-Open Browser

Comment out the browser launch in `archimista_launcher.py`:
```python
# t = threading.Thread(target=_open_browser, daemon=True)
# t.start()
```

### Code-Sign the Installer

To avoid Windows SmartScreen warnings:
```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com output\Archimista-Setup-*.exe
```

---

## Troubleshooting

### PyInstaller fails with "module not found"
- Ensure `pip install -r requirements.txt` completed successfully
- Check `hiddenimports` in `archimista.spec` — add missing modules
- Run with `--debug imports` to see import trace:
  ```cmd
  pyinstaller --debug imports archimista.spec
  ```

### collectstatic fails
- `STATIC_ROOT` is defined in `settings.py` as `BASE_DIR / 'staticfiles'`
- Make sure the directory is writable
- Non-critical — the app still works without collected statics

### WeasyPrint / GTK issues on Windows
WeasyPrint requires GTK3 DLLs. PyInstaller usually bundles them automatically.
If not:
1. Install GTK3 from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
2. Or manually copy the GTK3 `bin` folder into the bundle

### Inno Setup "file not found" errors
- Make sure `dist\archimista\` exists (run Stage 1 first)
- Check the `Source:` lines in `archimista_installer.iss` match your output path

### App doesn't start
- Run from Command Prompt to see error output:
  ```cmd
  cd dist\archimista
  Archimista.exe
  ```
- Check that `db.sqlite3` can be created (write permissions)
- Check that `manage.py` and seed scripts are in the same directory as the .exe

### Antivirus flags the .exe as malware
False positives are common with PyInstaller. Solutions:
1. Code-sign the executable (see above)
2. Submit to antivirus vendors for whitelisting
3. Use `--onefile` mode (larger but sometimes fewer false positives)

---

## Distribution

The final `Archimista-Setup-*.exe` file is **all the user needs**. They:

1. Double-click the installer
2. Follow the wizard (next, next, install)
3. Launch Archimista from the Start Menu
4. At first run, configure the database (guided)
5. Log in with the admin credentials shown during setup

No Python installation, no pip, no manual configuration needed.
