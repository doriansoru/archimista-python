"""
Fixture E2E per Archimista Python — Playwright.

Setup:
  1. Crea DB di test separato
  2. Applica migrazioni
  3. Inserisce dati seed (admin, group, vocabolari minimi, fond+unit di test)
  4. Avvia Django dev server come subprocess
  5. Fornisce base_url e page già autenticata

Utilizzo:
  pytest tests_e2e/                    # headless
  pytest tests_e2e/ --headed           # browser visibile
  pytest tests_e2e/ --slowmo=500       # rallentato per debug
"""

import os
import sys
import time
import signal
import subprocess
import socket
import shutil
from pathlib import Path

import pytest
import requests

# =============================================================================
# Percorsi
# =============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

# Aggiungi il progetto al path Python PRIMA di importare Django
# Questo assicura che 'archimista_python' sia risolvibile
ARCHIMISTA_PYTHON = PROJECT_ROOT / 'archimista_python'
if str(ARCHIMISTA_PYTHON) not in sys.path:
    sys.path.insert(0, str(ARCHIMISTA_PYTHON))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TEST_DB_FILE = PROJECT_ROOT / 'test_e2e_db.sqlite3'
SERVER_PORT = 8888
BASE_URL = f'http://127.0.0.1:{SERVER_PORT}'

ADMIN_USERNAME = 'e2eadmin'
ADMIN_PASSWORD = 'e2epass123'

# File di settings temporaneo per il server E2E
E2E_SETTINGS_FILE = PROJECT_ROOT / 'archimista_python' / 'e2e_settings.py'

# =============================================================================
# Session-scoped: setup DB + server
# =============================================================================

@pytest.fixture(scope='session')
def django_server():
    """Crea DB, applica migrazioni, seed dati, avvia Django server."""
    # Pulisci DB precedente
    if TEST_DB_FILE.exists():
        TEST_DB_FILE.unlink()

    # Configura Django con il DB di test
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.settings')

    import django
    from django.conf import settings
    settings.DATABASES['default']['NAME'] = str(TEST_DB_FILE)
    django.setup()

    from django.core.management import call_command
    from django.contrib.auth import get_user_model

    # Migrazioni
    call_command('migrate', verbosity=0)

    # Group
    from archimista_python.archive.models import Group
    Group.objects.get_or_create(id=1, defaults={'name': 'Default'})

    # Admin user
    User = get_user_model()
    admin, _ = User.objects.get_or_create(
        username=ADMIN_USERNAME,
        defaults={'email': 'e2e@test.com', 'is_staff': True, 'is_superuser': True}
    )
    admin.set_password(ADMIN_PASSWORD)
    admin.save()

    from archimista_python.archive.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=admin)
    profile.must_change_password = False
    profile.save()

    # Vocabolari minimi necessari per i form
    _seed_vocabularies()

    # Fond di test con unità figlia
    test_data = _seed_test_data()

    # Crea file settings temporaneo che punta al DB di test
    _write_e2e_settings(TEST_DB_FILE)

    # Avvia Django dev server con settings E2E
    server_proc = subprocess.Popen(
        [sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{SERVER_PORT}',
         '--noreload', '--settings=archimista_python.e2e_settings'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(PROJECT_ROOT),
    )

    # Attendi che il server sia pronto
    _wait_for_server(BASE_URL, timeout=15)

    yield {
        'base_url': BASE_URL,
        'fond_pk': test_data['fond_pk'],
        'unit_pk': test_data['unit_pk'],
    }

    # Cleanup
    server_proc.terminate()
    try:
        server_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_proc.kill()
        server_proc.wait()

    # Rimuovi DB e settings temporanei
    if TEST_DB_FILE.exists():
        TEST_DB_FILE.unlink()
    if E2E_SETTINGS_FILE.exists():
        E2E_SETTINGS_FILE.unlink()


def _wait_for_server(base_url, timeout=15):
    """Attendi che il server risponda alle richieste HTTP."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(f'{base_url}/login/', timeout=1)
            if resp.status_code == 200:
                return
        except (requests.ConnectionError, requests.Timeout):
            pass
        time.sleep(0.3)
    raise RuntimeError(f'Server non partito entro {timeout}s su {base_url}')


def _write_e2e_settings(db_file):
    """Crea un file e2e_settings.py che punta al DB di test."""
    db_path = str(db_file).replace('\\', '\\\\')
    content = (
        "# Settings E2E — generato automaticamente da conftest.py\n"
        "# NON modificare manualmente.\n"
        "from archimista_python.settings import *  # noqa: F401,F403\n\n"
        "DATABASES['default'] = {\n"
        "    'ENGINE': 'django.db.backends.sqlite3',\n"
        f"    'NAME': '{db_path}',\n"
        "}\n"
    )
    E2E_SETTINGS_FILE.write_text(content)


def _seed_vocabularies():
    """Crea vocabolari minimi necessari per i form E2E."""
    from archimista_python.archive.models import Vocabulary, Term

    # Unit type vocabulary (per unit_type_term — Select2, django-select2)
    # NOMEvocabolario: 'units.unit_type' (come nel form Python)
    unit_type_vocab, _ = Vocabulary.objects.get_or_create(
        name='units.unit_type',
        defaults={'description': 'Tipologia unità'}
    )
    Term.objects.get_or_create(
        vocabulary=unit_type_vocab, term_key='documentaria',
        defaults={'term_value': 'Unità documentaria', 'term': 'Unità documentaria', 'position': 1}
    )
    Term.objects.get_or_create(
        vocabulary=unit_type_vocab, term_key='fascicolo',
        defaults={'term_value': 'Fascicolo', 'term': 'Fascicolo', 'position': 2}
    )

    # SC2 type choices sono hardcoded nel form (CARS, D, DT, F, S)
    # Non serve vocabolario DB

    # Fascicolo type choices sono hardcoded nel form (personale, edilizia)
    # Non serve vocabolario DB

    # Date format vocabulary (per archidate)
    date_format_vocab, _ = Vocabulary.objects.get_or_create(
        name='date_format',
        defaults={'description': 'Formato data'}
    )
    Term.objects.get_or_create(
        vocabulary=date_format_vocab, term_key='Y',
        defaults={'term_value': 'Y', 'term': 'Y', 'position': 1}
    )
    Term.objects.get_or_create(
        vocabulary=date_format_vocab, term_key='C',
        defaults={'term_value': 'C', 'term': 'C', 'position': 2}
    )


def _seed_test_data():
    """Crea dati di test: un fond con un'unità figlia, un evento e record formset.
    Ritorna dict con PK per uso nei test."""
    from archimista_python.archive.models import (
        Fond, Unit, CustodianType, Event,
        FondName, FondLang,
        UnitIdentifier, UnitLang,
    )
    from django.contrib.auth import get_user_model

    User = get_user_model()
    admin = User.objects.get(username=ADMIN_USERNAME)

    # CustodianType (necessario per il form)
    CustodianType.objects.get_or_create(
        id=1,
        defaults={'custodian_type': 'Generico'}
    )

    # Fond
    fond = Fond.objects.create(
        name='Fondo E2E Test',
        created_by=admin.pk,
        updated_by=admin.pk,
    )

    # Record formset per il fond (almeno 1 per tipo, così il JS può clonare)
    FondName.objects.create(fond=fond, name='Fondo E2E Alternativo')
    FondLang.objects.create(fond=fond, code='it')

    # Evento per il fond (per test archidate)
    Event.objects.create(
        content_object=fond,
        start_date_format='Y',
        end_date_format='Y',
    )

    # Unit figlia
    unit = Unit.objects.create(
        title='Unità E2E Test',
        fond=fond,
        created_by=admin.pk,
        updated_by=admin.pk,
    )

    # Record formset per l'unità
    UnitIdentifier.objects.create(unit=unit, identifier='E2E-001', identifier_source='test')
    UnitLang.objects.create(unit=unit, code='it')

    return {'fond_pk': fond.pk, 'unit_pk': unit.pk}


# =============================================================================
# Fixture: base_url
# =============================================================================

@pytest.fixture(scope='session')
def base_url(django_server):
    """URL base del server Django."""
    return django_server['base_url']


@pytest.fixture(scope='session')
def fond_pk(django_server):
    """PK del fond di test."""
    return django_server['fond_pk']


@pytest.fixture(scope='session')
def unit_pk(django_server):
    """PK dell'unità di test."""
    return django_server['unit_pk']


# =============================================================================
# Fixture: pagina autenticata
# =============================================================================

@pytest.fixture
def logged_in_page(page, base_url):
    """Effettua il login via UI nel browser.

    Usa page.evaluate() per compilare e inviare il form,
    garantendo che il CSRF token sia incluso correttamente.
    """
    page.goto(f'{base_url}/login/', wait_until='domcontentloaded')
    page.wait_for_timeout(500)

    # Verifica che siamo sulla pagina di login
    title = page.title()
    assert 'Accesso' in title or 'Login' in title, f'Non sulla login page: {title} - URL: {page.url}'

    # Compila i campi e submit via JavaScript per assicurare CSRF corretto
    page.evaluate(f'''() => {{
        document.querySelector('input[name="username"]').value = '{ADMIN_USERNAME}';
        document.querySelector('input[name="password"]').value = '{ADMIN_PASSWORD}';
        document.querySelector('form[method="post"]').submit();
    }}''')

    # Attendi redirect
    page.wait_for_load_state('networkidle', timeout=15000)
    page.wait_for_timeout(1000)

    url = page.url
    if '/login/' in url:
        page.screenshot(path='/tmp/e2e_login_fail.png')
        body_text = page.locator('body').inner_text()
        # Controlla se ci sono errori nel form
        form_errors = page.locator('.errorlist, .alert-danger')
        err_text = ''
        if form_errors.count() > 0:
            err_text = form_errors.first.inner_text()
        raise RuntimeError(
            f'Login fallito. URL: {url}\n'
            f'Form errors: {err_text}\n'
            f'Body (primi 500): {body_text[:500]}'
        )
    return page
