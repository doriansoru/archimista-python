"""
Test settings — imports main settings and overrides DB for testing.
Usato da test_complete.py. Il file viene eliminato automaticamente.
"""
import os
from archimista_python.settings import *  # noqa: F401,F403

# Sovrascrivi database con file di test
TEST_DB_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'test_db.sqlite3'
)
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': TEST_DB_FILE,
}
