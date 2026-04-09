"""Test: edge case dati — unicode, emoji, HTML, NULL, valori speciali.

COPRE:
  - Unicode: caratteri internazionali, CJK, arabo, cirillico
  - Emoji: emoji in vari campi
  - HTML: tag HTML in descrizioni (sanitizzazione)
  - NULL: campi opzionali lasciati vuoti
  - Valori speciali: stringhe lunghissime, numeri estremi
  - Caratteri di controllo: newline, tab, caratteri speciali
"""
import io
import zipfile
from tests import test, section, client, admin_user
from django.test import Client
from django.urls import reverse


# Re-login
_test_client = Client()
_test_client.force_login(admin_user)


def run():
    section("21a. Unicode — caratteri internazionali")

    def _test_unicode_latin_extended():
        """Caratteri latini estesi (accenti, dieresi, cediglie)."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo Z\u00fcrich M\u00fcnch\u00ebn',
            description='Descrizione con caratteri: \u00e0\u00e8\u00e9\u00ec\u00f2\u00f9 \u00c1\u00c9\u00cd\u00d3\u00da \u00f1 \u00e7 \u0160 \u017d',
            history='Storia con: \u00c5\u00c4\u00d6 \u00d8 \u00de \u00d0',
            created_by=1, updated_by=1,
        )
        assert fond.name == 'Fondo Z\u00fcrich M\u00fcnch\u00ebn'
        assert fond.description is not None
        assert '\u00e0\u00e8\u00e9' in fond.description

        # Verifica nella view
        resp = _test_client.get(reverse('archive:fond_detail', args=[fond.pk]))
        assert resp.status_code == 200
        content = resp.content.decode('utf-8')
        assert 'Z\u00fcrich' in content, f"Unicode name not in detail view"
    test("Unicode: caratteri latini estesi", _test_unicode_latin_extended)

    def _test_unicode_cjk():
        """Caratteri CJK (cinese, giapponese, coreano)."""
        from archimista_python.archive.models import Fond, Creator
        from archimista_python.archive.models import CreatorName

        creator = Creator.objects.create(
            creator_type='P',
            created_by=1, updated_by=1,
        )
        CreatorName.objects.create(creator=creator, name='\u5c71\u7530\u592a\u90ce', preferred=True)

        fond = Fond.objects.create(
            name='Fondo CJK \u65e5\u672c\u8a9e\u30c6\u30b9\u30c8',
            description='Contenuto con: \u4f60\u597d\u4e16\u754c \u3053\u3093\u306b\u3061\u306f \uc548\ub155\ud558\uc138\uc694',
            created_by=1, updated_by=1,
        )
        assert '\u5c71\u7530\u592a\u90ce' in creator.preferred_name.name

        resp = _test_client.get(reverse('archive:fond_detail', args=[fond.pk]))
        assert resp.status_code == 200
    test("Unicode: caratteri CJK", _test_unicode_cjk)

    def _test_unicode_cyrillic():
        """Caratteri cirillici."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='\u0424\u043e\u043d\u0434 \u041a\u0438\u0440\u0438\u043b\u043b\u0438\u0446\u0430',
            description='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u043d\u0430 \u0440\u0443\u0441\u0441\u043a\u043e\u043c \u044f\u0437\u044b\u043a\u0435. \u041f\u0440\u0438\u0432\u0435\u0442 \u043c\u0438\u0440!',
            created_by=1, updated_by=1,
        )
        assert '\u041a\u0438\u0440\u0438\u043b\u043b\u0438\u0446\u0430' in fond.name
    test("Unicode: caratteri cirillici", _test_unicode_cyrillic)

    def _test_unicode_arabic():
        """Caratteri arabi (RTL)."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo \u0627\u0644\u0639\u0631\u0628\u064a\u0629',
            description='\u0648\u0635\u0641 \u0628\u0627\u0644\u0644\u063a\u0629 \u0627\u0644\u0639\u0631\u0628\u064a\u0629. \u0645\u0631\u062d\u0628\u0627 \u0628\u0627\u0644\u0639\u0627\u0644\u0645',
            created_by=1, updated_by=1,
        )
        assert '\u0627\u0644\u0639\u0631\u0628\u064a\u0629' in fond.name
    test("Unicode: caratteri arabi", _test_unicode_arabic)

    def _test_unicode_greek():
        """Caratteri greci."""
        from archimista_python.archive.models import Creator
        from archimista_python.archive.models import CreatorName

        creator = Creator.objects.create(
            creator_type='P',
            created_by=1, updated_by=1,
        )
        CreatorName.objects.create(creator=creator, name='\u0391\u03c1\u03c7\u03b5\u03af\u03bf \u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac', preferred=True)
        assert '\u0395\u03bb\u03bb\u03b7\u03bd\u03b9\u03ba\u03ac' in creator.preferred_name.name
    test("Unicode: caratteri greci", _test_unicode_greek)

    section("21b. Emoji")

    def _test_emoji_in_fond_fields():
        """Emoji in vari campi del fondo."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo \U0001f4dc Archivio \U0001f3db\ufe0f',
            description='Descrizione con emoji: \U0001f4da documenti \U0001f5c2\ufe0f organizzati \u2728',
            history='Storia: \U0001f4c5 dal 1800 \U0001f4cd a Firenze \U0001f1ee\U0001f1f9',
            created_by=1, updated_by=1,
        )
        assert '\U0001f4dc' in fond.name
        assert '\U0001f4da' in fond.description
        assert '\U0001f3db\ufe0f' in fond.name

        # Verifica che la detail view gestisca gli emoji
        resp = _test_client.get(reverse('archive:fond_detail', args=[fond.pk]))
        assert resp.status_code == 200
    test("Emoji: nel fondo", _test_emoji_in_fond_fields)

    def _test_emoji_in_unit_fields():
        """Emoji in vari campi dell'unita."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(name='Emoji Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(
            title='Unita con \U0001f3a8 disegni \U0001f4d0',
            content='Contenuto: \U0001f4dd appunti \U0001f5d2\ufe0f personali',
            fond=fond,
            created_by=1, updated_by=1,
        )
        assert '\U0001f3a8' in unit.title

        resp = _test_client.get(reverse('archive:unit_detail', args=[unit.pk]))
        assert resp.status_code == 200
    test("Emoji: nell'unita", _test_emoji_in_unit_fields)

    def _test_emoji_in_creator():
        """Emoji nel soggetto produttore."""
        from archimista_python.archive.models import Creator
        from archimista_python.archive.models import CreatorName

        creator = Creator.objects.create(creator_type='F', created_by=1, updated_by=1)
        CreatorName.objects.create(creator=creator, name='Famiglia Rossi \U0001f468\u200d\U0001f469\u200d\U0001f467\u200d\U0001f466', preferred=True)
        assert '\U0001f468' in creator.preferred_name.name
    test("Emoji: nel creatore", _test_emoji_in_creator)

    section("21c. HTML in campi di testo")

    def _test_html_in_description():
        """Tag HTML in descrizioni — dovrebbero essere preservati o sanitizzati."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo HTML Test',
            description='<p>Descrizione con <strong>grassetto</strong> e <em>corsivo</em>.</p><ul><item>Lista</item></ul>',
            created_by=1, updated_by=1,
        )
        assert '<strong>' in fond.description or '&lt;strong&gt;' in fond.description
    test("HTML: tag in descrizione", _test_html_in_description)

    def _test_html_script_injection():
        """Script tag in descrizione — test di sicurezza."""
        from archimista_python.archive.models import Fond
        malicious_html = '<script>alert("XSS")</script><p>Testo normale</p>'
        fond = Fond.objects.create(
            name='Fondo XSS Test',
            description=malicious_html,
            created_by=1, updated_by=1,
        )
        # Il dato deve essere salvato cosi com'e (o sanitizzato)
        assert 'XSS' in fond.description or 'alert' in fond.description

        # Nella view, lo script non dovrebbe essere eseguito (Django fa escape di default)
        resp = _test_client.get(reverse('archive:fond_detail', args=[fond.pk]))
        assert resp.status_code == 200
        content = resp.content.decode('utf-8')
        # Django dovrebbe aver escapato il tag script
        assert '<script>' not in content or '&lt;script&gt;' in content, \
            "Script tag should be escaped in template"
    test("HTML: script tag (XSS prevention)", _test_html_script_injection)

    def _test_html_entities():
        """HTML entities nei campi."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo &amp; Test',
            description='Testo con &lt;tag&gt; e &quot;virgolette&quot; e &#39;apostrofo&#39;',
            created_by=1, updated_by=1,
        )
        assert '&amp;' in fond.name
    test("HTML: entities", _test_html_entities)

    section("21d. Campi NULL/empty")

    def _test_fond_with_all_optional_fields_empty():
        """Fondo con tutti i campi opzionali vuoti."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo Minimal',
            created_by=1, updated_by=1,
            # abstract, description, history, note tutti None
        )
        assert fond.abstract is None
        assert fond.description is None
        assert fond.history is None
        assert fond.name == 'Fondo Minimal'

        resp = _test_client.get(reverse('archive:fond_detail', args=[fond.pk]))
        assert resp.status_code == 200
    test("NULL: fondo con campi opzionali vuoti", _test_fond_with_all_optional_fields_empty)

    def _test_unit_with_minimal_fields():
        """Unita con solo il titolo."""
        from archimista_python.archive.models import Fond, Unit
        fond = Fond.objects.create(name='Unit Minimal Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita Minimal', fond=fond, created_by=1, updated_by=1)

        assert unit.reference_number is None
        assert unit.content is None

        resp = _test_client.get(reverse('archive:unit_detail', args=[unit.pk]))
        assert resp.status_code == 200
    test("NULL: unita con campi minimi", _test_unit_with_minimal_fields)

    def _test_creator_with_minimal_fields():
        """Creatore con solo tipo."""
        from archimista_python.archive.models import Creator
        creator = Creator.objects.create(creator_type='E', created_by=1, updated_by=1)
        assert creator.creator_type == 'E'

        resp = _test_client.get(reverse('archive:creator_list'))
        assert resp.status_code == 200
    test("NULL: creatore con campi minimi", _test_creator_with_minimal_fields)

    def _test_custodian_with_minimal_fields():
        """Conservatore con solo tipo."""
        from archimista_python.archive.models import Custodian, CustodianType
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='Minimal CT')
        custodian = Custodian.objects.create(custodian_type=ctype, created_by=1, updated_by=1)
        resp = _test_client.get(reverse('archive:custodian_detail', args=[custodian.pk]))
        assert resp.status_code == 200
    test("NULL: conservatore con campi minimi", _test_custodian_with_minimal_fields)

    section("21e. Stringhe lunghissime")

    def _test_very_long_description():
        """Descrizione con testo molto lungo (10KB+)."""
        from archimista_python.archive.models import Fond
        long_text = 'Questa e una descrizione molto lunga. ' * 500  # ~20KB
        fond = Fond.objects.create(
            name='Fondo Long Text',
            description=long_text,
            created_by=1, updated_by=1,
        )
        assert len(fond.description) > 10000
        assert fond.description == long_text

        # Verifica che la view gestisca testi lunghi
        resp = _test_client.get(reverse('archive:fond_detail', args=[fond.pk]))
        assert resp.status_code == 200
    test("Stringhe lunghe: descrizione 20KB", _test_very_long_description)

    def _test_very_long_name():
        """Nome fondo molto lungo (vicino al limite del campo)."""
        from archimista_python.archive.models import Fond
        long_name = 'Fondo ' + 'Lunghissimo ' * 100
        fond = Fond.objects.create(
            name=long_name,
            created_by=1, updated_by=1,
        )
        assert len(fond.name) > 1000
    test("Stringhe lunghe: nome fondo 1KB+", _test_very_long_name)

    def _test_many_special_chars_in_identifier():
        """Identificativo con molti caratteri speciali."""
        from archimista_python.archive.models import Fond, FondIdentifier
        fond = Fond.objects.create(name='Fondo Special Chars', created_by=1, updated_by=1)
        special_id = 'ID-!@#$%^&*()_+-=[]{}|;'
        FondIdentifier.objects.create(fond=fond, identifier=special_id)
        assert FondIdentifier.objects.filter(fond=fond).exists()
    test("Stringhe speciali: identificativo con caratteri speciali", _test_many_special_chars_in_identifier)

    section("21f. Control characters and whitespace edge cases")

    def _test_newlines_in_description():
        """Descrizione con molti newline."""
        from archimista_python.archive.models import Fond
        text_with_newlines = 'Riga 1\nRiga 2\n\nRiga 4 dopo blank\n\n\nRiga 8 dopo due blank'
        fond = Fond.objects.create(
            name='Fondo Newlines',
            description=text_with_newlines,
            created_by=1, updated_by=1,
        )
        assert '\n' in fond.description
        assert fond.description == text_with_newlines
    test("Caratteri di controllo: newline multipli", _test_newlines_in_description)

    def _test_tabs_in_description():
        """Descrizione con tabulazioni."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo Tabs',
            description='Colonna 1\tColonna 2\tColonna 3',
            created_by=1, updated_by=1,
        )
        assert '\t' in fond.description
    test("Caratteri di controllo: tabulazioni", _test_tabs_in_description)

    def _test_whitespace_only_field():
        """Campo con solo spazi bianchi."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='   ',  # Solo spazi
            description='Desc valida',
            created_by=1, updated_by=1,
        )
        assert fond is not None
    test("Caratteri di controllo: campo con solo spazi", _test_whitespace_only_field)

    section("21g. Ricerca con caratteri speciali")

    def _test_search_with_unicode():
        """Ricerca con termini unicode."""
        from archimista_python.archive.models import Fond
        Fond.objects.create(name='Fondo M\u00fcnchen', created_by=1, updated_by=1)
        Fond.objects.create(name='Fondo Milano', created_by=1, updated_by=1)

        resp = _test_client.get(reverse('archive:search') + '?q=M\u00fcnchen')
        assert resp.status_code == 200
    test("Ricerca: termine unicode", _test_search_with_unicode)

    def _test_search_with_special_chars():
        """Ricerca con caratteri speciali nella query."""
        resp = _test_client.get(reverse('archive:search') + '?q=Test%20%26%20Co')
        assert resp.status_code == 200
    test("Ricerca: caratteri speciali nella query", _test_search_with_special_chars)

    section("21h. Import/Export con dati speciali")

    def _test_export_unicode_fond():
        """Export AEF di fondo con dati unicode."""
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(
            name='Fondo Unicode Export',
            description='Beschreibung: \u00d6sterreich, M\u00fcnchen, Z\u00fcrich',
            created_by=1, updated_by=1,
        )
        resp = _test_client.get(reverse('archive:fond_export_aef', args=[fond.pk]))
        assert resp.status_code == 200

        # Verifica che il JSON sia valido e contenga unicode
        import json
        zf = zipfile.ZipFile(__import__('io').BytesIO(resp.content))
        data = json.loads(zf.read('data.json').decode('utf-8').strip().split('\n')[0])
        assert 'Fondo Unicode Export' in str(data)
    test("Export: dati unicode", _test_export_unicode_fond)
