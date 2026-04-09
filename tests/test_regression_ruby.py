"""Test regressione Python vs Ruby — confronto su output reali.

Questi test confrontano l'output del porting Python con quello di Ruby
(importando lo stesso AEF di riferimento su entrambi e confrontando i risultati).

REQUISITI:
  - tests/regression/ruby_output/ruby_export.aef  (AEF esportato da Ruby)
  - tests/regression/ruby_output/ruby_report.pdf  (PDF esportato da Ruby)
  - tests/regression/ruby_output/ruby_report.rtf  (RTF esportato da Ruby)

Se i file Ruby non esistono, i test vengono saltati (skip).
"""
import os
import io
import json
import zipfile
import re

from tests import test, section, skip

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF_AEF = os.path.join(BASE_DIR, 'tests', 'regression', 'reference', 'reference_aef.zip')
RUBY_AEF = os.path.join(BASE_DIR, 'tests', 'regression', 'ruby_output', 'ruby_export.aef')
RUBY_PDF = os.path.join(BASE_DIR, 'tests', 'regression', 'ruby_output', 'ruby_report.pdf')
RUBY_RTF = os.path.join(BASE_DIR, 'tests', 'regression', 'ruby_output', 'ruby_report.rtf')
PY_PDF = os.path.join(BASE_DIR, 'tests', 'regression', 'reference', 'python_report.pdf')
PY_RTF = os.path.join(BASE_DIR, 'tests', 'regression', 'reference', 'python_report.rtf')


def _aef_exists(path):
    return os.path.exists(path)


def _parse_aef(aef_path):
    """Parse AEF file and return (model_counts, records, model_fields, metadata).

    Supports both NDJSON (one JSON object per line) and JSON array formats.
    Handles both CRLF and LF line endings.
    """
    with open(aef_path, 'rb') as f:
        zf = zipfile.ZipFile(f)
        data_raw = zf.read('data.json')
        # Handle CRLF vs LF
        if data_raw.startswith(b'['):
            # JSON array format
            data_str = data_raw.decode('utf-8').strip()
            records_list = json.loads(data_str)
        else:
            # NDJSON format — split on \n but handle \r\n
            lines = [l.decode('utf-8') for l in data_raw.split(b'\n') if l.strip()]
            records_list = [json.loads(line) for line in lines]
        metadata = json.loads(zf.read('metadata.json').decode('utf-8'))

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


def _extract_text_from_pdf(pdf_path):
    """Extract text from PDF."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = ''.join(page.get_text() for page in doc)
        doc.close()
        return text
    except Exception:
        pass
    return None


def _extract_text_from_rtf(rtf_path):
    """Extract plain text from RTF."""
    with open(rtf_path, 'r', encoding='utf-8', errors='replace') as f:
        rtf_content = f.read()
    text = re.sub(r'\\[a-zA-Z]+[0-9]* ?', ' ', rtf_content)
    text = re.sub(r'[{}]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _normalize(text):
    if text is None:
        return None
    return re.sub(r'\s+', ' ', text.lower()).strip()


def _ruby_aef_missing():
    """Check if Ruby AEF exists, skip all tests if not."""
    return not _aef_exists(RUBY_AEF)


# ─── Sezione 21: Confronto Python vs Ruby ───

def run():
    section("21a. Confronto strutturale AEF Python vs Ruby")

    def _test_aef_models_match():
        """Python e Ruby devono esportare gli stessi modelli."""
        if _ruby_aef_missing():
            skip("AEF: stessi modelli", "Ruby AEF non trovato")
            return

        py_counts, _, py_fields, _ = _parse_aef(REF_AEF)
        rb_counts, _, rb_fields, _ = _parse_aef(RUBY_AEF)

        py_models = set(py_counts.keys())
        rb_models = set(rb_counts.keys())

        only_py = py_models - rb_models
        only_rb = rb_models - py_models

        assert not only_py, f"Modelli solo in Python: {sorted(only_py)}"
        assert not only_rb, f"Modelli solo in Ruby: {sorted(only_rb)}"
    test("AEF: stessi modelli in Python e Ruby", _test_aef_models_match)

    def _test_aef_record_counts_match():
        """Conteggio record per modello deve essere uguale."""
        if _ruby_aef_missing():
            skip("AEF: conteggi record", "Ruby AEF non trovato")
            return

        py_counts, _, _, _ = _parse_aef(REF_AEF)
        rb_counts, _, _, _ = _parse_aef(RUBY_AEF)

        all_models = set(py_counts.keys()) | set(rb_counts.keys())
        for model in sorted(all_models):
            py_c = py_counts.get(model, 0)
            rb_c = rb_counts.get(model, 0)
            assert py_c == rb_c, f"{model}: Python={py_c}, Ruby={rb_c}"
    test("AEF: conteggi record identici", _test_aef_record_counts_match)

    def _test_aef_fond_fields_match():
        """Campi del fond devono essere gli stessi."""
        if _ruby_aef_missing():
            skip("AEF: campi fond", "Ruby AEF non trovato")
            return

        _, _, py_fields, _ = _parse_aef(REF_AEF)
        _, _, rb_fields, _ = _parse_aef(RUBY_AEF)

        if 'fond' not in py_fields or 'fond' not in rb_fields:
            skip("AEF: campi fond", "Nessun fond trovato")
            return

        only_py = py_fields['fond'] - rb_fields['fond']
        only_rb = rb_fields['fond'] - py_fields['fond']

        assert not only_py, f"Campi solo in Python fond: {sorted(only_py)}"
        assert not only_rb, f"Campi solo in Ruby fond: {sorted(only_rb)}"
    test("AEF: stessi campi nel fond", _test_aef_fond_fields_match)

    def _test_aef_unit_fields_match():
        """Campi della unit devono essere gli stessi."""
        if _ruby_aef_missing():
            skip("AEF: campi unit", "Ruby AEF non trovato")
            return

        _, _, py_fields, _ = _parse_aef(REF_AEF)
        _, _, rb_fields, _ = _parse_aef(RUBY_AEF)

        if 'unit' not in py_fields or 'unit' not in rb_fields:
            skip("AEF: campi unit", "Nessuna unit trovata")
            return

        only_py = py_fields['unit'] - rb_fields['unit']
        only_rb = rb_fields['unit'] - py_fields['unit']

        assert not only_py, f"Campi solo in Python unit: {sorted(only_py)}"
        assert not only_rb, f"Campi solo in Ruby unit: {sorted(only_rb)}"
    test("AEF: stessi campi nella unit", _test_aef_unit_fields_match)

    def _test_aef_fond_values_match():
        """Valori chiave del fond devono corrispondere."""
        if _ruby_aef_missing():
            skip("AEF: valori fond", "Ruby AEF non trovato")
            return

        _, py_records, _, _ = _parse_aef(REF_AEF)
        _, rb_records, _, _ = _parse_aef(RUBY_AEF)

        py_fond = [f for m, f in py_records if m == 'fond']
        rb_fond = [f for m, f in rb_records if m == 'fond']

        if not py_fond or not rb_fond:
            skip("AEF: valori fond", "Nessun fond trovato")
            return

        pf = py_fond[0]
        rf = rb_fond[0]

        for key in ['name', 'description', 'abstract', 'history']:
            pv = str(pf.get(key, '')).strip()
            rv = str(rf.get(key, '')).strip()
            assert pv == rv, f"fond.{key}: Python='{pv[:50]}' vs Ruby='{rv[:50]}'"
    test("AEF: valori fond identici", _test_aef_fond_values_match)

    def _test_aef_sc2_complete():
        """SC2 esportata da Python e Ruby deve avere i campi essenziali."""
        if _ruby_aef_missing():
            skip("AEF: SC2 completa", "Ruby AEF non trovato")
            return

        _, _, py_fields, _ = _parse_aef(REF_AEF)
        _, _, rb_fields, _ = _parse_aef(RUBY_AEF)

        if 'sc2' not in py_fields or 'sc2' not in rb_fields:
            skip("AEF: SC2 completa", "Nessuna SC2 trovata")
            return

        essential = {'sgti', 'mtce', 'sdtt', 'sdts', 'dpgf', 'misa', 'misl', 'card_type'}
        py_sc2 = py_fields.get('sc2', set())
        rb_sc2 = rb_fields.get('sc2', set())

        missing_py = essential - py_sc2
        missing_rb = essential - rb_sc2

        assert not missing_py, f"SC2 campi mancanti in Python: {sorted(missing_py)}"
        assert not missing_rb, f"SC2 campi mancanti in Ruby: {sorted(missing_rb)}"
    test("AEF: SC2 completa in entrambi", _test_aef_sc2_complete)

    def _test_aef_iccd_complete():
        """ICCD esportato da Python e Ruby deve avere i campi essenziali."""
        if _ruby_aef_missing():
            skip("AEF: ICCD completo", "Ruby AEF non trovato")
            return

        _, _, py_fields, _ = _parse_aef(REF_AEF)
        _, _, rb_fields, _ = _parse_aef(RUBY_AEF)

        if 'iccd_description' not in py_fields or 'iccd_description' not in rb_fields:
            skip("AEF: ICCD completo", "Nessun ICCD trovato")
            return

        essential = {'denomination', 'object_type', 'category', 'age_century'}
        py_iccd = py_fields.get('iccd_description', set())
        rb_iccd = rb_fields.get('iccd_description', set())

        missing_py = essential - py_iccd
        missing_rb = essential - rb_iccd

        assert not missing_py, f"ICCD campi mancanti in Python: {sorted(missing_py)}"
        assert not missing_rb, f"ICCD campi mancanti in Ruby: {sorted(missing_rb)}"
    test("AEF: ICCD completo in entrambi", _test_aef_iccd_complete)

    # ─── Sezione 21b: PDF content comparison ───
    section("21b. Confronto PDF Python vs Ruby")

    def _test_pdf_python_has_expected_content():
        """PDF Python deve contenere le informazioni chiave."""
        if not os.path.exists(PY_PDF):
            skip("PDF Python: contenuto", f"PDF Python non trovato: {PY_PDF}")
            return

        text = _extract_text_from_pdf(PY_PDF)
        if text is None:
            skip("PDF Python: contenuto", "Impossibile estrarre testo dal PDF")
            return

        text_norm = _normalize(text)

        keywords = ['fondo deliberazioni', 'comune di torino', 'registro',
                    'fascicolo', 'fotografia', 'pianta', 'torino', 'sc2']

        found = [kw for kw in keywords if kw in text_norm]
        assert len(found) >= len(keywords) - 2, \
            f"Solo {len(found)}/{len(keywords)} keyword trovate nel PDF Python"
    test("PDF Python: contiene informazioni chiave", _test_pdf_python_has_expected_content)

    def _test_pdf_python_vs_ruby_comparable():
        """PDF Python e Ruby devono avere contenuto comparabile."""
        if not os.path.exists(RUBY_PDF) or not os.path.exists(PY_PDF):
            skip("PDF: Python vs Ruby", "File PDF necessari non trovati")
            return

        py_text = _extract_text_from_pdf(PY_PDF)
        rb_text = _extract_text_from_pdf(RUBY_PDF)

        if py_text is None or rb_text is None:
            skip("PDF: Python vs Ruby", "Impossibile estrarre testo dai PDF")
            return

        py_norm = _normalize(py_text)
        rb_norm = _normalize(rb_text)

        py_words = set(py_norm.split())
        rb_words = set(rb_norm.split())
        common = py_words & rb_words
        overlap = len(common) / max(len(py_words), len(rb_words))

        assert overlap > 0.5, f"Overlap PDF troppo basso: {overlap:.1%} (soglia 50%)"
    test("PDF: contenuto Python vs Ruby comparabile", _test_pdf_python_vs_ruby_comparable)

    # ─── Sezione 21c: RTF content comparison ───
    section("21c. Confronto RTF Python vs Ruby")

    def _test_rtf_python_has_expected_content():
        """RTF Python deve contenere le informazioni chiave."""
        if not os.path.exists(PY_RTF):
            skip("RTF Python: contenuto", f"RTF Python non trovato: {PY_RTF}")
            return

        text = _extract_text_from_rtf(PY_RTF)
        text_norm = _normalize(text)

        keywords = ['fondo deliberazioni', 'comune di torino', 'registro',
                    'fascicolo', 'torino']

        found = [kw for kw in keywords if kw in text_norm]
        assert len(found) >= len(keywords) - 2, \
            f"Solo {len(found)}/{len(keywords)} keyword trovate nel RTF Python"
    test("RTF Python: contiene informazioni chiave", _test_rtf_python_has_expected_content)

    def _test_rtf_python_vs_ruby_comparable():
        """RTF Python e Ruby devono avere contenuto comparabile."""
        if not os.path.exists(RUBY_RTF) or not os.path.exists(PY_RTF):
            skip("RTF: Python vs Ruby", "File RTF necessari non trovati")
            return

        py_text = _extract_text_from_rtf(PY_RTF)
        rb_text = _extract_text_from_rtf(RUBY_RTF)

        py_norm = _normalize(py_text)
        rb_norm = _normalize(rb_text)

        py_words = set(py_norm.split())
        rb_words = set(rb_norm.split())
        common = py_words & rb_words
        overlap = len(common) / max(len(py_words), len(rb_words))

        assert overlap > 0.5, f"Overlap RTF troppo basso: {overlap:.1%} (soglia 50%)"
    test("RTF: contenuto Python vs Ruby comparabile", _test_rtf_python_vs_ruby_comparable)
