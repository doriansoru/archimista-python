# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Archimista.

Usage:
    pyinstaller archimista.spec

This produces a one-dir build in dist/archimista/.
"""

import os
from pathlib import Path

SPECDIR = Path(SPECDIR) if 'SPECDIR' in dir() else Path('.').resolve()
PROJECT = SPECDIR

# ---------------------------------------------------------------------------
# Hidden imports — everything PyInstaller can't auto-detect
# ---------------------------------------------------------------------------
hiddenimports = [
    # Django core
    'django',
    'django.apps',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.core.management',
    'django.core.management.commands.migrate',
    'django.core.management.commands.runserver',
    'django.core.management.commands.collectstatic',
    'django.core.management.commands.check',
    'django.template.backends.django',
    'django.db.backends.sqlite3',
    'django.db.models',
    'django.forms',
    'django.utils',
    'django.utils.timezone',
    'django.utils.translation',
    'django.contrib.auth.hashers',
    'django.contrib.auth.password_validation',
    'django.contrib.sessions.backends.db',
    'django.contrib.sessions.middleware',
    'django.contrib.messages.middleware',
    # Django extensions
    'django_extensions',
    'django_select2',
    # lxml
    'lxml',
    'lxml.etree',
    'lxml.html',
    'lxml.builder',
    # Pillow
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'PIL.ImageFile',
    # ReportLab
    'reportlab',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.lib.styles',
    'reportlab.lib.units',
    'reportlab.platypus',
    'reportlab.platypus.tables',
    'reportlab.platypus.paragraph',
    'reportlab.pdfbase',
    'reportlab.pdfbase.ttfonts',
    'reportlab.pdfbase.pdfmetrics',
    # WeasyPrint
    'weasyprint',
    'weasyprint.text',
    'weasyprint.formatting_structure',
    'weasyprint.layout',
    'weasyprint.draw',
    # python-docx
    'docx',
    'docx.opc',
    'docx.oxml',
    'docx.text',
    # requests
    'requests',
    'requests.adapters',
    'urllib3',
    'urllib3.util',
    'charset_normalizer',
    'certifi',
    # Our app
    'archimista_python',
    'archimista_python.settings',
    'archimista_python.urls',
    'archimista_python.wsgi',
    'archimista_python.archive',
    'archimista_python.archive.apps',
    'archimista_python.archive.admin',
    'archimista_python.archive.middleware',
    'archimista_python.archive.widgets',
    'archimista_python.archive.urls',
    'archimista_python.archive.export_utils',
    'archimista_python.archive.import_utils',
    'archimista_python.archive.report_support',
    'archimista_python.archive.rtf_builder',
    'archimista_python.archive.rtf_writer',
    'archimista_python.archive.aef_exporter',
    'archimista_python.archive.aef_exporter.constants',
    'archimista_python.archive.aef_exporter.serializers',
    'archimista_python.archive.aef_exporter.fond_units',
    'archimista_python.archive.aef_exporter.extensions',
    'archimista_python.archive.aef_exporter.relations',
    'archimista_python.archive.aef_exporter.digital_objects',
    'archimista_python.archive.aef_exporter.single_entity',
    'archimista_python.archive.aef_exporter.metadata',
    'archimista_python.archive.aef_exporter.xml_export',
    'archimista_python.archive.models',
    'archimista_python.archive.models.core',
    'archimista_python.archive.models.relations',
    'archimista_python.archive.models.extensions',
    'archimista_python.archive.models.sc2',
    'archimista_python.archive.models.iccd',
    'archimista_python.archive.models.fsc',
    'archimista_python.archive.models.fe',
    'archimista_python.archive.models.vocabulary',
    'archimista_python.archive.models.system',
    'archimista_python.archive.forms',
    'archimista_python.archive.forms.fond',
    'archimista_python.archive.forms.unit',
    'archimista_python.archive.forms.creator',
    'archimista_python.archive.forms.custodian',
    'archimista_python.archive.forms.source',
    'archimista_python.archive.forms.institution',
    'archimista_python.archive.forms.project',
    'archimista_python.archive.forms.editor',
    'archimista_python.archive.forms.heading',
    'archimista_python.archive.forms.classification',
    'archimista_python.archive.forms.digital_object',
    'archimista_python.archive.forms.anagraphic',
    'archimista_python.archive.forms.document_form',
    'archimista_python.archive.forms.event',
    'archimista_python.archive.forms.fsc',
    'archimista_python.archive.forms.fe',
    'archimista_python.archive.forms.iccd',
    'archimista_python.archive.forms.sc2',
    'archimista_python.archive.views',
    'archimista_python.archive.views.fond',
    'archimista_python.archive.views.unit',
    'archimista_python.archive.views.creator',
    'archimista_python.archive.views.custodian',
    'archimista_python.archive.views.source',
    'archimista_python.archive.views.institutions',
    'archimista_python.archive.views.projects',
    'archimista_python.archive.views.editors',
    'archimista_python.archive.views.search',
    'archimista_python.archive.views.tree',
    'archimista_python.archive.views.export',
    'archimista_python.archive.views.export_aef',
    'archimista_python.archive.views.export_csv',
    'archimista_python.archive.views.import_view',
    'archimista_python.archive.views.reports',
    'archimista_python.archive.views.auth',
    'archimista_python.archive.views.entities',
    'archimista_python.archive.views.classifications',
    'archimista_python.archive.views.digital_objects',
    'archimista_python.archive.views.advanced_search',
    'archimista_python.archive.views.quality_checks',
    'archimista_python.archive.views.unit_list',
    'archimista_python.archive.views.unit_formsets',
    'archimista_python.archive.views.document_forms',
    'archimista_python.archive.management',
    'archimista_python.archive.management.commands',
    'archimista_python.archive.management.commands.seed_db',
    'archimista_python.archive.templatetags',
    # Seed scripts (imported by launcher)
    'seed_vocabularies',
    'seed_source_types',
    'seed',
    'seed_admin_user',
]

# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------
datas = []

# HTML templates
templates_dir = PROJECT / 'archimista_python' / 'archive' / 'templates'
if templates_dir.exists():
    datas.append((str(templates_dir), 'archimista_python/archive/templates'))

# Static files
static_dir = PROJECT / 'archimista_python' / 'static'
if static_dir.exists():
    datas.append((str(static_dir), 'archimista_python/static'))

# Migrations
migrations_dir = PROJECT / 'archimista_python' / 'archive' / 'migrations'
if migrations_dir.exists():
    datas.append((str(migrations_dir), 'archimista_python/archive/migrations'))

# manage.py
manage_py = PROJECT / 'manage.py'
if manage_py.exists():
    datas.append((str(manage_py), '.'))

# Seed scripts (also as data files so they're importable)
for seed_file in ['seed.py', 'seed_vocabularies.py', 'seed_source_types.py',
                  'seed_admin_user.py']:
    sf = PROJECT / seed_file
    if sf.exists():
        datas.append((str(sf), '.'))

# requirements.txt
req = PROJECT / 'requirements.txt'
if req.exists():
    datas.append((str(req), '.'))

# Launcher
launcher = PROJECT / 'archimista_launcher.py'
if launcher.exists():
    datas.append((str(launcher), '.'))

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
a = Analysis(
    ['archimista_launcher.py'],
    pathex=[str(PROJECT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'playwright',
        'pytest',
        'pytest_playwright',
        'tests',
        'tests_e2e',
        'test_server',
        'run_all_tests',
        'generate_reference_aef',
        'clean_vocabularies',
        'fix_sc2_card_types',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Archimista',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='archimista',
)
