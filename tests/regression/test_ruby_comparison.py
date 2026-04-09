#!/usr/bin/env python
"""
Confronto output Python vs Ruby — Test di regressione su dati reali.

Workflow:
1. Genera AEF di riferimento: python generate_reference_aef.py
2. Importa l'AEF su Archimista Ruby (VirtualBox)
3. Da Ruby, esporta:
   - AEF → tests/regression/ruby_output/ruby_export.aef
   - PDF → tests/regression/ruby_output/ruby_report.pdf
   - RTF → tests/regression/ruby_output/ruby_report.rtf
   - SAN XML → tests/regression/ruby_output/ruby_export_san.zip
   - EAD XML → tests/regression/ruby_output/ruby_export_ead.zip
   - METS XML → tests/regression/ruby_output/ruby_export_mets.zip
4. Esegui questo script: python tests/regression/test_ruby_comparison.py

Nota: I file Ruby AEF devono esistere in tests/regression/ruby_output/.
      I file XML Ruby sono opzionali (confronto saltato se non presenti).
"""
import os
import sys
import io
import json
import zipfile
import re
import subprocess

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_DIR = os.path.join(BASE_DIR, 'tests', 'regression', 'reference')
RUBY_DIR = os.path.join(BASE_DIR, 'tests', 'regression', 'ruby_output')

REF_AEF = os.path.join(REF_DIR, 'reference_aef.zip')
RUBY_AEF = os.path.join(RUBY_DIR, 'ruby_export.aef')
RUBY_PDF = os.path.join(RUBY_DIR, 'ruby_report.pdf')
RUBY_RTF = os.path.join(RUBY_DIR, 'ruby_report.rtf')


def parse_aef(aef_path):
    """Parse an AEF file and return (model_counts, records, model_fields, metadata).

    Supports both NDJSON (one JSON object per line) and JSON array formats.
    Handles both CRLF and LF line endings.
    """
    with open(aef_path, 'rb') as f:
        zf = zipfile.ZipFile(f)
        data_raw = zf.read('data.json')
        metadata = json.loads(zf.read('metadata.json').decode('utf-8'))

    # Detect format: starts with '[' -> JSON array, otherwise NDJSON
    if data_raw.startswith(b'['):
        records_list = json.loads(data_raw.decode('utf-8').strip())
    else:
        # NDJSON format — split on \n but handle \r\n
        lines = [l.decode('utf-8') for l in data_raw.split(b'\n') if l.strip()]
        records_list = [json.loads(line) for line in lines]

    records = []
    model_counts = {}
    model_fields = {}
    for record in records_list:
        for model_name, fields in record.items():
            model_counts[model_name] = model_counts.get(model_name, 0) + 1
            records.append((model_name, fields))
            if model_name not in model_fields:
                model_fields[model_name] = set()
            if isinstance(fields, dict):
                model_fields[model_name].update(fields.keys())

    return model_counts, records, model_fields, metadata


def extract_pdf_text(pdf_path):
    """Extract text from a PDF file using pdftotext or PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ''
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        pass

    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text
    except ImportError:
        pass

    # Fallback: try pdftotext CLI
    try:
        result = subprocess.run(['pdftotext', '-layout', pdf_path, '-'],
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def extract_rtf_text(rtf_path):
    """Extract plain text from an RTF file (strip RTF tags)."""
    with open(rtf_path, 'r', encoding='utf-8', errors='replace') as f:
        rtf_content = f.read()

    # Strip RTF control words and braces
    text = re.sub(r'\\[a-zA-Z]+[0-9]* ?', ' ', rtf_content)
    text = re.sub(r'[{}]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def normalize_text(text):
    """Normalize text for comparison: lowercase, strip extra whitespace."""
    if text is None:
        return None
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def compare_aef_data():
    """Confronta data.json: Python vs Ruby."""
    print("\n" + "=" * 70)
    print("CONFRONTO AEF — Python vs Ruby")
    print("=" * 70)

    if not os.path.exists(RUBY_AEF):
        print(f"\n  ERRORE: File Ruby AEF non trovato: {RUBY_AEF}")
        print("  Importa l'AEF su Ruby, esporta e mettilo nella posizione indicata.")
        return False

    py_counts, py_records, py_fields, py_meta = parse_aef(REF_AEF)
    rb_counts, rb_records, rb_fields, rb_meta = parse_aef(RUBY_AEF)

    all_pass = True

    # 1. Confronto modelli presenti
    print("\n1. Modelli presenti:")
    py_models = set(py_counts.keys())
    rb_models = set(rb_counts.keys())

    common = py_models & rb_models
    only_py = py_models - rb_models
    only_rb = rb_models - py_models

    print(f"   Python: {len(py_models)} modelli")
    print(f"   Ruby:   {len(rb_models)} modelli")
    print(f"   Comuni: {len(common)}")

    if only_py:
        print(f"   SOLO in Python: {sorted(only_py)}")
    if only_rb:
        print(f"   SOLO in Ruby:   {sorted(only_rb)}")

    # Modelli noti che Ruby non esporta (limiti noti di Ruby, non bug Python)
    KNOWN_MISSING = {'digital_object', 'editor', 'sc2_attribution_reason', 'sc2_commission_name'}

    only_py = py_models - rb_models
    only_rb = rb_models - py_models

    # Rimuovi le differenze note
    expected_only_py = only_py - KNOWN_MISSING

    if not expected_only_py and not only_rb:
        print("   [PASS] Stessi modelli in entrambi (4 differenze note accettate)")
    else:
        if expected_only_py:
            print(f"   SOLO in Python (inaspettato): {sorted(expected_only_py)}")
        if only_rb:
            print(f"   SOLO in Ruby:   {sorted(only_rb)}")
        print(f"   [FAIL] Differenze modelli inaspettate!")
        all_pass = False

    # Mostra le differenze note per trasparenza
    actual_only_py = only_py & KNOWN_MISSING
    if actual_only_py:
        print(f"   (Differenze note accettate: {sorted(actual_only_py)})")

    # 2. Confronto conteggi per modello
    print("\n2. Conteggio record per modello:")
    count_match = True
    for model in sorted(common | only_py | only_rb):
        py_c = py_counts.get(model, 0)
        rb_c = rb_counts.get(model, 0)
        status = "OK" if py_c == rb_c else f"DIFF (Python={py_c}, Ruby={rb_c})"
        if py_c != rb_c:
            if model in KNOWN_MISSING:
                count_match = False  # Track but don't fail
            else:
                count_match = False
        print(f"   {model:35s} Python={py_c:3d}  Ruby={rb_c:3d}  [{status}]")

    # Conteggi OK se le uniche differenze sono quelle note
    unexpected_diff = [m for m in sorted(common | only_py | only_rb)
                       if py_counts.get(m, 0) != rb_counts.get(m, 0) and m not in KNOWN_MISSING]
    if not unexpected_diff:
        print("   [PASS] Conteggi identici (4 differenze note accettate)")
    else:
        print(f"   [FAIL] Differenze nei conteggi: {unexpected_diff}")
        all_pass = False

    # 3. Confronto campi per modello principale (fond, unit)
    # Nota: sc2 e iccd hanno campi diversi tra Python e Ruby per differenze di modellazione.
    # Ruby li importa correttamente anche con nomi diversi.
    print("\n3. Campi per modello principale (fond, unit):")
    for model in ['fond', 'unit']:
        if model in py_fields and model in rb_fields:
            py_f = py_fields[model]
            rb_f = rb_fields[model]
            common_f = py_f & rb_f
            only_py_f = py_f - rb_f
            only_rb_f = rb_f - py_f
            overlap = len(common_f) / max(len(py_f), len(rb_f)) * 100
            if only_py_f or only_rb_f:
                print(f"   {model}: {len(common_f)} campi comuni, {len(only_py_f)} solo Python, {len(only_rb_f)} solo Ruby")
                print(f"     Overlap: {overlap:.0f}%")
                if only_py_f:
                    print(f"     SOLO Python: {sorted(only_py_f)}")
                if only_rb_f:
                    print(f"     SOLO Ruby:   {sorted(only_rb_f)}")
            else:
                print(f"   {model:25s} [{len(common_f)} campi]  [PASS] ({overlap:.0f}% overlap)")

    # 4. Confronto valori chiave per fond
    print("\n4. Valori chiave Fond:")
    value_match = True
    py_fond = [fields for model, fields in py_records if model == 'fond']
    rb_fond = [fields for model, fields in rb_records if model == 'fond']

    if py_fond and rb_fond:
        pf = py_fond[0]
        rf = rb_fond[0]

        for key in ['name', 'description', 'abstract', 'history', 'arrangement_note',
                     'related_materials', 'note']:
            pv = str(pf.get(key, '')).strip()
            rv = str(rf.get(key, '')).strip()
            if str(pv).strip() != str(rv).strip():
                value_match = False
                print(f"   DIFF '{key}': Python='{pv[:50]}' vs Ruby='{rv[:50]}'")
            else:
                print(f"   OK   '{key}': '{pv[:50]}'")

    if value_match:
        print("   [PASS] Valori fond identici")
    else:
        print("   [FAIL] Differenze valori fond!")
        all_pass = False

    # 5. Confronto metadata
    print("\n5. Metadata AEF:")
    py_version = py_meta.get('version', py_meta.get('app_version', '?'))
    rb_version = rb_meta.get('version', rb_meta.get('app_version', '?'))
    print(f"   Versione: Python={py_version}, Ruby={rb_version}")
    # Version might differ (Python=300, Ruby might differ)
    print(f"   Producer: Python={py_meta.get('producer', '?')}, Ruby={rb_meta.get('producer', '?')}")
    print("   [INFO] Metadata può differire (versione diverso)")

    print(f"\n{'=' * 70}")
    if all_pass:
        print("RISULTATO AEF: PASS — Tutti i confronti sono positivi")
    else:
        print("RISULTATO AEF: FAIL — Ci sono differenze da investigare")
    print("=" * 70)
    return all_pass


def compare_pdf():
    """Confronta PDF Python vs Ruby (text extraction)."""
    print("\n" + "=" * 70)
    print("CONFRONTO PDF — Python vs Ruby")
    print("=" * 70)

    py_pdf = os.path.join(BASE_DIR, 'tests', 'regression', 'reference', 'python_report.pdf')
    if not os.path.exists(py_pdf):
        print(f"\n  ERRORE: File Python PDF non trovato: {py_pdf}")
        print("  Genera il PDF con: python manage.py shell ...")
        print("  (oppure usa lo script di export PDF dal report del fondo di riferimento)")
        return False

    if not os.path.exists(RUBY_PDF):
        print(f"\n  ERRORE: File Ruby PDF non trovato: {RUBY_PDF}")
        print("  Esporta il report da Ruby e mettilo nella posizione indicata.")
        return False

    py_text = extract_pdf_text(py_pdf)
    rb_text = extract_pdf_text(RUBY_PDF)

    if py_text is None or rb_text is None:
        print("  ERRORE: Impossibile estrarre testo dai PDF.")
        print("  Installa PyMuPDF (pip install pymupdf) o pypdf (pip install pypdf)")
        return False

    py_norm = normalize_text(py_text)
    rb_norm = normalize_text(rb_text)

    print(f"\n  Lunghezza testo Python: {len(py_text)} chars")
    print(f"  Lunghezza testo Ruby:   {len(rb_text)} chars")

    # Check for key content presence
    keywords = [
        'fondo deliberazioni',
        'comune di torino',
        'registro',
        'fascicolo',
        'fotografia',
        'pianta',
        'torino',
    ]

    print("\n  Parole chiave nel PDF Python:")
    py_found = 0
    for kw in keywords:
        found = kw in py_norm
        if found:
            py_found += 1
        print(f"    {'[OK]' if found else '[--]'} '{kw}'")

    print(f"\n  {py_found}/{len(keywords)} parole chiave trovate nel PDF Python")

    print("\n  Parole chiave nel PDF Ruby:")
    rb_found = 0
    for kw in keywords:
        found = kw in rb_norm
        if found:
            rb_found += 1
        print(f"    {'[OK]' if found else '[--]'} '{kw}'")

    print(f"\n  {rb_found}/{len(keywords)} parole chiave trovate nel PDF Ruby")

    # Similarity check
    if py_norm and rb_norm:
        # Simple overlap ratio
        py_words = set(py_norm.split())
        rb_words = set(rb_norm.split())
        common_words = py_words & rb_words
        overlap = len(common_words) / max(len(py_words), len(rb_words)) * 100
        print(f"\n  Overlap parole: {overlap:.1f}%")

    # Check sizes are comparable
    size_ratio = len(rb_text) / max(len(py_text), 1)
    print(f"  Ratio dimensioni testo Ruby/Python: {size_ratio:.2f}x")

    all_pass = (py_found >= len(keywords) - 2) and (rb_found >= len(keywords) - 2)

    print(f"\n{'=' * 70}")
    if all_pass:
        print("RISULTATO PDF: PASS — Contenuto comparabile")
    else:
        print("RISULTATO PDF: ATTENZIONE — Contenuto parzialmente diverso (investigare)")
    print("=" * 70)
    return all_pass


def compare_rtf():
    """Confronta RTF Python vs Ruby (text extraction)."""
    print("\n" + "=" * 70)
    print("CONFRONTO RTF — Python vs Ruby")
    print("=" * 70)

    py_rtf = os.path.join(BASE_DIR, 'tests', 'regression', 'reference', 'python_report.rtf')
    if not os.path.exists(py_rtf):
        print(f"\n  ERRORE: File Python RTF non trovato: {py_rtf}")
        print("  Genera il RTF con: python manage.py shell ...")
        return False

    if not os.path.exists(RUBY_RTF):
        print(f"\n  ERRORE: File Ruby RTF non trovato: {RUBY_RTF}")
        print("  Esporta il report da Ruby e mettilo nella posizione indicata.")
        return False

    py_text = extract_rtf_text(py_rtf)
    rb_text = extract_rtf_text(RUBY_RTF)

    py_norm = normalize_text(py_text)
    rb_norm = normalize_text(rb_text)

    print(f"\n  Lunghezza testo Python: {len(py_text)} chars")
    print(f"  Lunghezza testo Ruby:   {len(rb_text)} chars")

    # Check for key content presence
    keywords = [
        'fondo deliberazioni',
        'comune di torino',
        'registro',
        'fascicolo',
        'fotografia',
        'torino',
    ]

    print("\n  Parole chiave nel RTF Python:")
    py_found = 0
    for kw in keywords:
        found = kw in py_norm
        if found:
            py_found += 1
        print(f"    {'[OK]' if found else '[--]'} '{kw}'")

    print(f"\n  {py_found}/{len(keywords)} parole chiave trovate nel RTF Python")

    print("\n  Parole chiave nel RTF Ruby:")
    rb_found = 0
    for kw in keywords:
        found = kw in rb_norm
        if found:
            rb_found += 1
        print(f"    {'[OK]' if found else '[--]'} '{kw}'")

    print(f"\n  {rb_found}/{len(keywords)} parole chiave trovate nel RTF Ruby")

    # Similarity
    if py_norm and rb_norm:
        py_words = set(py_norm.split())
        rb_words = set(rb_norm.split())
        common_words = py_words & rb_words
        overlap = len(common_words) / max(len(py_words), len(rb_words)) * 100
        print(f"\n  Overlap parole: {overlap:.1f}%")

    size_ratio = len(rb_text) / max(len(py_text), 1)
    print(f"  Ratio dimensioni testo Ruby/Python: {size_ratio:.2f}x")

    all_pass = (py_found >= len(keywords) - 2) and (rb_found >= len(keywords) - 2)

    print(f"\n{'=' * 70}")
    if all_pass:
        print("RISULTATO RTF: PASS — Contenuto comparabile")
    else:
        print("RISULTATO RTF: ATTENZIONE — Contenuto parzialmente diverso (investigare)")
    print("=" * 70)
    return all_pass


from lxml import etree


def parse_xml_zip(zip_path):
    """Parse an XML export ZIP and return {filename: root_element}."""
    if not os.path.exists(zip_path):
        return None
    with open(zip_path, 'rb') as f:
        zf = zipfile.ZipFile(f)
        result = {}
        for name in zf.namelist():
            if name.endswith('.xml'):
                try:
                    tree = etree.fromstring(zf.read(name))
                    result[name] = tree
                except etree.XMLSyntaxError:
                    result[name] = None
        return result


def _tag_name(element):
    """Get tag name without namespace."""
    return etree.QName(element.tag).localname if element is not None else ''


def _count_elements(root, local_name):
    """Count elements with a given local name anywhere in the tree."""
    count = 0
    for el in root.iter():
        if etree.QName(el.tag).localname == local_name:
            count += 1
    return count


def _find_element(root, local_name):
    """Find first element with a given local name."""
    for el in root.iter():
        if etree.QName(el.tag).localname == local_name:
            return el
    return None


def compare_xml_format(py_zip_path, rb_zip_path, format_label):
    """Compare Python vs Ruby XML exports for a given format."""
    print(f"\n{'=' * 70}")
    print(f"CONFRONTO XML {format_label} — Python vs Ruby")
    print('=' * 70)

    if not os.path.exists(py_zip_path):
        print(f"  ERRORE: File Python {format_label} non trovato: {py_zip_path}")
        return False
    if not os.path.exists(rb_zip_path):
        print(f"  ⏭️  File Ruby {format_label} non trovato: {rb_zip_path} — confronto saltato")
        return None  # Skip, not fail

    py_xmls = parse_xml_zip(py_zip_path)
    rb_xmls = parse_xml_zip(rb_zip_path)

    if not py_xmls or not rb_xmls:
        print(f"  ERRORE: Impossibile parse XML {format_label}")
        return False

    all_pass = True

    # 1. File names match
    py_names = set(py_xmls.keys())
    rb_names = set(rb_xmls.keys())
    common_names = py_names & rb_names
    only_py = py_names - rb_names
    only_rb = rb_names - py_names

    print(f"\n  File Python: {len(py_names)}, File Ruby: {len(rb_names)}")
    if only_py:
        print(f"  SOLO Python: {sorted(only_py)}")
    if only_rb:
        print(f"  SOLO Ruby:   {sorted(only_rb)}")

    # 2. Compare each common file
    for name in sorted(common_names):
        py_root = py_xmls[name]
        rb_root = rb_xmls[name]
        if py_root is None or rb_root is None:
            print(f"  [WARN] {name}: parse error in uno dei due")
            all_pass = False
            continue

        py_tag = _tag_name(py_root)
        rb_tag = _tag_name(rb_root)
        tag_match = py_tag == rb_tag

        py_ns = etree.QName(py_root.tag).namespace or '(none)'
        rb_ns = etree.QName(rb_root.tag).namespace or '(none)'

        # Count key elements
        py_total = sum(1 for _ in py_root.iter())
        rb_total = sum(1 for _ in rb_root.iter())

        status = "OK" if tag_match else f"TAG DIFF (py={py_tag}, rb={rb_tag})"
        print(f"\n  {name}:")
        print(f"    Root tag: py={py_tag}, rb={rb_tag}  [{status}]")
        print(f"    Namespace: py={py_ns}, rb={rb_ns}")
        print(f"    Total elements: py={py_total}, rb={rb_total}")

        if not tag_match:
            all_pass = False

    if all_pass:
        print(f"\n  [PASS] {format_label}: struttura comparabile")
    else:
        print(f"\n  [FAIL] {format_label}: differenze strutturali")

    return all_pass


def main():
    print("=" * 70)
    print("TEST REGRESSIONE — Confronto Python vs Ruby")
    print("=" * 70)

    # Check if reference AEF exists
    if not os.path.exists(REF_AEF):
        print(f"\nAEF di riferimento non trovato: {REF_AEF}")
        print("Generazione in corso...")
        gen_script = os.path.join(BASE_DIR, 'generate_reference_aef.py')
        if os.path.exists(gen_script):
            result = subprocess.run([sys.executable, gen_script], cwd=BASE_DIR)
            if result.returncode != 0:
                print("ERRORE: Generazione AEF fallita.")
                sys.exit(1)
        else:
            print(f"ERRORE: Script non trovato: {gen_script}")
            sys.exit(1)

    # Check Ruby outputs — AEF is required, PDF/RTF are optional
    if not os.path.exists(RUBY_AEF):
        print(f"\nFile Ruby AEF mancante:")
        print(f"  - {RUBY_AEF}")
        print("\nIMPORTANTE: Usa python_export.aef per l'import su Ruby.")
        print("1. Importa python_export.aef su Archimista Ruby (VirtualBox)")
        print("2. Dal fondo importato, clicca 'Esporta AEF'")
        print(f"3. Salva come {RUBY_AEF}")
        sys.exit(1)

    # Run comparisons — AEF always, PDF/RTF/XML only if available
    results = {}
    results['aef'] = compare_aef_data()

    py_pdf = os.path.join(REF_DIR, 'python_report.pdf')
    py_rtf = os.path.join(REF_DIR, 'python_report.rtf')

    if os.path.exists(RUBY_PDF) and os.path.exists(py_pdf):
        results['pdf'] = compare_pdf()
    else:
        print("\n⏭️  Confronto PDF saltato (file non disponibili)")

    if os.path.exists(RUBY_RTF) and os.path.exists(py_rtf):
        results['rtf'] = compare_rtf()
    else:
        print("⏭️  Confronto RTF saltato (file non disponibili)")

    # XML comparisons (SAN, EAD, METS)
    for fmt, label in [('san', 'SAN'), ('ead', 'EAD'), ('mets', 'METS')]:
        py_xml = os.path.join(REF_DIR, f'reference_{fmt}.zip')
        rb_xml = os.path.join(RUBY_DIR, f'ruby_export_{fmt}.zip')
        xml_result = compare_xml_format(py_xml, rb_xml, label)
        if xml_result is not None:
            results[f'xml_{fmt}'] = xml_result
        else:
            print(f"⏭️  Confronto XML {label} saltato (file Ruby non disponibili)")

    # Summary
    print("\n" + "=" * 70)
    print("RIEPILOGO")
    print("=" * 70)
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name.upper():10s} [{status}]")

    all_pass = all(results.values())
    print(f"\n  TOTALE: {'PASS' if all_pass else 'FAIL'} ({sum(results.values())}/{len(results)} test)")
    print("=" * 70)

    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    main()
