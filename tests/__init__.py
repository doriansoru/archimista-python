"""
Test runner condiviso per Archimista Python/Django.
Modulo __init__.py — esporta globals condivise + main().
"""

import os
import sys
import traceback

# =============================================================================
# Database setup — DEVE avvenire PRIMA di django.setup()
# =============================================================================
TEST_DB_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'test_db.sqlite3'
)

# Elimina vecchio file se esiste
if os.path.exists(TEST_DB_FILE):
    os.remove(TEST_DB_FILE)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.test_settings')

import django.conf
django.conf.settings.DATABASES['default']['NAME'] = TEST_DB_FILE

import django
django.setup()

from django.core.management import call_command
call_command('migrate', verbosity=0)

# Seed minimi
from archimista_python.archive.models import Group
Group.objects.get_or_create(id=1, defaults={'name': 'Default'})

# Admin user
from django.contrib.auth import get_user_model
User = get_user_model()
admin_user, _ = User.objects.get_or_create(
    username='testadmin',
    defaults={'email': 'test@test.com', 'is_staff': True, 'is_superuser': True}
)
admin_user.set_password('testpass123')
admin_user.save()
from archimista_python.archive.models import UserProfile
profile, _ = UserProfile.objects.get_or_create(user=admin_user)
profile.must_change_password = False
profile.save()

from django.test import Client
client = Client()
client.force_login(admin_user)

# =============================================================================
# Counter globali
# =============================================================================
PASSED = 0
FAILED = 0
SKIPPED = 0
ERRORS = []


def test(name, fn):
    global PASSED, FAILED, SKIPPED, ERRORS
    try:
        fn()
        PASSED += 1
        print(f"  ✅ {name}")
    except AssertionError as e:
        FAILED += 1
        ERRORS.append((name, str(e)))
        print(f"  ❌ {name}: {e}")
    except Exception as e:
        FAILED += 1
        ERRORS.append((name, traceback.format_exc()))
        print(f"  💥 {name}: {type(e).__name__}: {e}")


def skip(name, reason):
    global SKIPPED
    SKIPPED += 1
    print(f"  ⏭️  {name}: {reason}")


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# =============================================================================
# Main runner
# =============================================================================
def run_all():
    """Importa ed esegue tutti i moduli test_*.py in ordine."""
    import importlib
    from pathlib import Path

    test_dir = Path(__file__).parent
    test_modules = sorted(
        f.stem for f in test_dir.glob('test_*.py')
        if f.stem != '__init__' and f.stem != 'test_regression_ruby'
    )

    for mod_name in test_modules:
        mod = importlib.import_module(f'tests.{mod_name}')
        if hasattr(mod, 'run'):
            mod.run()

    # Riepilogo
    total = PASSED + FAILED + SKIPPED
    print(f"\n{'='*60}")
    print(f"  RIEPILOGO")
    print(f"{'='*60}")
    print(f"  ✅ Passati:   {PASSED}")
    print(f"  ❌ Falliti:   {FAILED}")
    print(f"  ⏭️  Saltati:   {SKIPPED}")
    print(f"  📊 Totale:    {total}")
    print(f"  {'='*60}")

    if ERRORS:
        print(f"\n  ERRORI DETTAGLIATI:")
        for name, err in ERRORS:
            print(f"\n  ❌ {name}:")
            print(f"     {err[:200]}")

    # Cleanup
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
        print(f"\n  🗑️  Database di test eliminato: {TEST_DB_FILE}")

    sys.exit(0 if FAILED == 0 else 1)
