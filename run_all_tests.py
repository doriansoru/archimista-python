#!/usr/bin/env python
"""
Runner unificato per tutti i test di Archimista Python.

Lancia in sequenza:
  1. Test server-side (323 test, harness custom in tests/__init__.py)
  2. Test regressione Python vs Ruby (confronto AEF/PDF/RTF) — se i file esistono
  3. Test E2E (35 test, Playwright con pytest)

Se i test server-side falliscono, gli step successivi non partono.

Utilizzo:
  python run_all_tests.py                          # tutto (server + regressione + E2E)
  python run_all_tests.py --no-comparison          # senza regressione Python vs Ruby
  python run_all_tests.py --e2e-only               # solo E2E
  python run_all_tests.py --e2e-only --headed      # solo E2E, browser visibile
  python test_server.py                            # solo server-side (esistente, invariato)
  python tests/regression/test_ruby_comparison.py  # solo regressione Python vs Ruby
  venv/bin/python -m pytest tests_e2e/             # solo E2E (pytest diretto)

NOTA: Usa il Python del venv del progetto per avere Django disponibile.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Cambia directory alla root del progetto
PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)

# Usa il Python del venv se disponibile
VENV_PYTHON = PROJECT_ROOT / 'venv' / 'bin' / 'python'
if VENV_PYTHON.exists():
    PYTHON = str(VENV_PYTHON)
else:
    PYTHON = sys.executable

# Colori ANSI
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Separatori
W = 60


def print_header(title):
    print(f"\n{'=' * W}")
    print(f"  {BOLD}{title}{RESET}")
    print(f"{'=' * W}")


def print_section(title):
    print(f"\n{'─' * W}")
    print(f"  {CYAN}{title}{RESET}")
    print(f"{'─' * W}")


def parse_server_output(output):
    """Parsa l'output del test server-side per estrarre conteggi."""
    passed = failed = skipped = 0
    for line in output.splitlines():
        line = line.strip()
        if line.startswith('✅ Passati:'):
            try:
                passed = int(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith('❌ Falliti:'):
            try:
                failed = int(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith('⏭️  Saltati:'):
            try:
                skipped = int(line.split(':')[1].strip())
            except (ValueError, IndexError):
                pass
    return passed, failed, skipped


def parse_pytest_output(output):
    """Parsa l'output di pytest per estrarre conteggi."""
    passed = failed = 0
    for line in output.splitlines():
        # pytest summary: "35 passed, 2 failed in 10.5s"
        if 'passed' in line and 'failed' in line:
            try:
                parts = line.split(',')
                for part in parts:
                    part = part.strip()
                    if 'passed' in part:
                        passed = int(part.split()[0])
                    elif 'failed' in part:
                        failed = int(part.split()[0])
            except (ValueError, IndexError):
                pass
    return passed, failed


def run_server_tests():
    """Esegue i test server-side (harness custom)."""
    print_header(f"[1/2] Test server-side ({BOLD}test_server.py{RESET})")
    print(f"  Command: python test_server.py\n")

    start = time.time()
    result = subprocess.run(
        [PYTHON, 'test_server.py'],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=300,
    )
    elapsed = time.time() - start

    # Stampa output (sempre, per visibilità)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    passed, failed, skipped = parse_server_output(result.stdout + result.stderr)

    return {
        'success': result.returncode == 0,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'total': passed + failed + skipped,
        'elapsed': elapsed,
        'stdout': result.stdout,
        'stderr': result.stderr,
    }


def run_regression_comparison():
    """Esegue il test di regressione Python vs Ruby (confronto AEF/PDF/RTF)."""
    comparison_script = PROJECT_ROOT / 'tests' / 'regression' / 'test_ruby_comparison.py'

    # Check if the script and required files exist
    if not comparison_script.exists():
        print(f"\n  {YELLOW}⏭️  Test regressione Python vs Ruby: script non trovato.{RESET}")
        return None

    ruby_aef = PROJECT_ROOT / 'tests' / 'regression' / 'ruby_output' / 'ruby_export.aef'
    if not ruby_aef.exists():
        print(f"\n  {YELLOW}⏭️  Test regressione Python vs Ruby: file Ruby mancanti.{RESET}")
        print(f"    Richiesto: {ruby_aef}")
        print(f"    Vedi: tests/regression/README.md")
        return None

    print_header(f"[2/3] Test regressione Python vs Ruby ({BOLD}test_ruby_comparison.py{RESET})")
    print(f"  Command: python tests/regression/test_ruby_comparison.py\n")

    start = time.time()
    result = subprocess.run(
        [PYTHON, str(comparison_script)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=300,
    )
    elapsed = time.time() - start

    # Stampa output
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # Parse result (the script prints its own summary)
    success = result.returncode == 0
    return {
        'success': success,
        'elapsed': elapsed,
        'stdout': result.stdout,
        'stderr': result.stderr,
    }


def run_e2e_tests(headed=False):
    """Esegue i test E2E con Playwright."""
    cmd = [PYTHON, '-m', 'pytest', 'tests_e2e/', '-v', '--tb=short']
    if headed:
        cmd.append('--headed')

    print_header(f"[3/3] Test E2E ({BOLD}tests_e2e/ — Playwright{RESET})")
    print(f"  Command: {' '.join(cmd)}\n")

    start = time.time()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=600,
    )
    elapsed = time.time() - start

    # Stampa output
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    passed, failed = parse_pytest_output(result.stdout + result.stderr)

    return {
        'success': result.returncode == 0,
        'passed': passed,
        'failed': failed,
        'skipped': 0,
        'total': passed + failed,
        'elapsed': elapsed,
        'stdout': result.stdout,
        'stderr': result.stderr,
    }


def print_summary(server_result, comparison_result, e2e_result):
    """Stampa il riepilogo finale unificato."""
    print_header('RIEPILOGO FINALE')

    total_passed = server_result['passed'] + e2e_result['passed']
    total_failed = server_result['failed'] + e2e_result['failed']
    total_skipped = server_result['skipped'] + e2e_result['skipped']
    total_all = total_passed + total_failed + total_skipped
    total_time = server_result['elapsed'] + e2e_result['elapsed']
    if comparison_result:
        total_time += comparison_result['elapsed']

    # Tabella
    print(f"  {'Componente':<35} {'✅ Passati':>10} {'❌ Falliti':>10} {'⏭️ Saltati':>10} {'⏱️ Tempo':>10}")
    print(f"  {'─' * 35} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10}")

    if server_result:
        s = server_result
        status = f"{GREEN}✅{RESET}" if s['success'] else f"{RED}❌{RESET}"
        print(f"  {status} Server-side {'':<23} {s['passed']:>10} {s['failed']:>10} {s['skipped']:>10} {s['elapsed']:.1f}s")

    if comparison_result:
        c = comparison_result
        status = f"{GREEN}✅{RESET}" if c['success'] else f"{RED}❌{RESET}"
        label = 'Regressione Python vs Ruby'
        print(f"  {status} {label:<34} {'—':>10} {'—':>10} {'—':>10} {c['elapsed']:.1f}s")

    if e2e_result:
        e = e2e_result
        status = f"{GREEN}✅{RESET}" if e['success'] else f"{RED}❌{RESET}"
        label = 'E2E (Playwright)'
        print(f"  {status} {label:<34} {e['passed']:>10} {e['failed']:>10} {e['skipped']:>10} {e['elapsed']:.1f}s")

    print(f"  {'─' * 35} {'─' * 10} {'─' * 10} {'─' * 10} {'─' * 10}")
    print(f"  {BOLD}{'TOTALE':<35} {total_passed:>10} {total_failed:>10} {total_skipped:>10} {total_time:>9.1f}s{RESET}")
    print(f"  {'=' * W}")

    if total_failed == 0:
        print(f"\n  {GREEN}{BOLD}🎉 Tutti i test sono passati!{RESET}")
    else:
        print(f"\n  {RED}{BOLD}⚠️  {total_failed} test falliti.{RESET}")

    return total_failed == 0


def main():
    args = sys.argv[1:]
    e2e_only = '--e2e-only' in args
    no_comparison = '--no-comparison' in args
    headed = '--headed' in args

    all_success = True

    # Fase 1: Server-side tests
    server_result = None
    if not e2e_only:
        server_result = run_server_tests()
        if not server_result['success']:
            print(f"\n{RED}{BOLD}⚠️  I test server-side sono falliti. Gli E2E non partiranno.{RESET}")
            print_summary(server_result, None, None)
            sys.exit(1)
    else:
        print(f"\n{YELLOW}Modalità --e2e-only: salto i test server-side.{RESET}")

    # Fase 2: Regression comparison (Python vs Ruby)
    comparison_result = None
    if not e2e_only and not no_comparison:
        comparison_result = run_regression_comparison()
        if comparison_result and not comparison_result['success']:
            all_success = False
    elif no_comparison:
        print(f"\n{YELLOW}Modalità --no-comparison: salto il test di regressione Python vs Ruby.{RESET}")

    # Fase 3: E2E tests
    e2e_result = run_e2e_tests(headed=headed)
    if not e2e_result['success']:
        all_success = False

    # Riepilogo
    print_summary(server_result, comparison_result, e2e_result)
    sys.exit(0 if all_success else 1)


if __name__ == '__main__':
    main()
