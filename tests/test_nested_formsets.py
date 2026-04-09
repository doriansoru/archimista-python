"""Test: formset annidati complessi — SC2 author + attribution reason, commission + commission name.

COPRE:
  - Salvataggio corretto di Sc2Author con Sc2AttributionReason annidato
  - Salvataggio corretto di Sc2Commission con Sc2CommissionName annidato
  - Cancellazione (DELETE) nei formset
  - Validazione formset con dati incompleti
  - Model-level relationships
"""
from tests import test, section, client, admin_user
from django.test import Client
from django.urls import reverse


# Re-login
_test_client = Client()
_test_client.force_login(admin_user)


def run():
    section("18a. SC2 nested formsets — model-level direct creation")

    def _test_sc2_author_with_nested_attribution_reason_model():
        """Crea direttamente via ORM: Sc2Author + Sc2AttributionReason annidato."""
        from archimista_python.archive.models import (
            Fond, Unit, Sc2, Sc2Author, Sc2AttributionReason,
        )
        fond = Fond.objects.create(name='SC2 Direct Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita SC2 Direct', fond=fond, created_by=1, updated_by=1)
        sc2 = Sc2.objects.create(unit=unit, card_type='SC2', sgti='Soggetto diretto')

        author = Sc2Author.objects.create(
            unit=unit,
            autr='Scultore',
            autn='Michelangelo Buonarroti',
            auta='1501-1504',
        )
        reason = Sc2AttributionReason.objects.create(
            sc2_author=author,
            autm="Documento d'archivio",
        )

        # Verifica relazione inversa
        author.refresh_from_db()
        reasons = list(author.sc2_attribution_reasons.all())
        assert len(reasons) == 1, f"Expected 1 attribution reason, got {len(reasons)}"
        assert reasons[0].autm == "Documento d'archivio", f"Reason mismatch: {reasons[0].autm}"
    test("SC2: Author + AttributionReason via ORM", _test_sc2_author_with_nested_attribution_reason_model)

    def _test_sc2_commission_with_nested_commission_name_model():
        """Crea direttamente via ORM: Sc2Commission + Sc2CommissionName annidato."""
        from archimista_python.archive.models import (
            Fond, Unit, Sc2, Sc2Commission, Sc2CommissionName,
        )
        fond = Fond.objects.create(name='SC2 Commission Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita SC2 Commission', fond=fond, created_by=1, updated_by=1)
        Sc2.objects.create(unit=unit, card_type='SC2')

        commission = Sc2Commission.objects.create(
            unit=unit,
            cmmc='Ordine dei Domenicani',
        )
        comm_name = Sc2CommissionName.objects.create(
            sc2_commission=commission,
            cmmn='Frate Bartolomeo',
        )

        # Verifica relazione inversa
        commission.refresh_from_db()
        names = list(commission.sc2_commission_names.all())
        assert len(names) == 1, f"Expected 1 commission name, got {len(names)}"
        assert names[0].cmmn == 'Frate Bartolomeo', f"Commission name mismatch: {names[0].cmmn}"
    test("SC2: Commission + CommissionName via ORM", _test_sc2_commission_with_nested_commission_name_model)

    def _test_multiple_authors_with_multiple_reasons():
        """Piu autori, ciascuno con piu motivi di attribuzione."""
        from archimista_python.archive.models import (
            Fond, Unit, Sc2, Sc2Author, Sc2AttributionReason,
        )
        fond = Fond.objects.create(name='SC2 Multi Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita SC2 Multi', fond=fond, created_by=1, updated_by=1)
        Sc2.objects.create(unit=unit, card_type='SC2')

        a1 = Sc2Author.objects.create(unit=unit, autr='Pittore', autn='Autore 1')
        a2 = Sc2Author.objects.create(unit=unit, autr='Aiutante', autn='Autore 2')

        Sc2AttributionReason.objects.create(sc2_author=a1, autm='Stile')
        Sc2AttributionReason.objects.create(sc2_author=a1, autm='Documentazione')
        Sc2AttributionReason.objects.create(sc2_author=a2, autm='Tradizione')

        a1.refresh_from_db()
        a2.refresh_from_db()
        assert a1.sc2_attribution_reasons.count() == 2, f"a1 should have 2 reasons, got {a1.sc2_attribution_reasons.count()}"
        assert a2.sc2_attribution_reasons.count() == 1, f"a2 should have 1 reason, got {a2.sc2_attribution_reasons.count()}"

        # Verifica che i motivi siano corretti per ogni autore
        a1_reasons = set(a1.sc2_attribution_reasons.values_list('autm', flat=True))
        assert a1_reasons == {'Stile', 'Documentazione'}, f"a1 reasons mismatch: {a1_reasons}"
    test("SC2: piu autori con piu ragioni ciascuno", _test_multiple_authors_with_multiple_reasons)

    section("18b. Formset SC2 — creazione tramite formset inline")

    def _test_sc2_author_formset_save():
        """Salvataggio tramite Sc2AuthorFormSet inline su Unit."""
        from archimista_python.archive.models import Fond, Unit, Sc2, Sc2Author
        from archimista_python.archive.forms import Sc2AuthorFormSet

        fond = Fond.objects.create(name='SC2 FS Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita SC2 FS', fond=fond, created_by=1, updated_by=1)
        Sc2.objects.create(unit=unit, card_type='SC2')

        before_count = Sc2Author.objects.filter(unit=unit).count()

        post_data = {
            'sc2_authors-TOTAL_FORMS': '2',
            'sc2_authors-INITIAL_FORMS': '0',
            'sc2_authors-MIN_NUM_FORMS': '0',
            'sc2_authors-MAX_NUM_FORMS': '1000',
            'sc2_authors-0-autr': 'Pittore',
            'sc2_authors-0-autn': 'Leonardo',
            'sc2_authors-0-auta': '1503',
            'sc2_authors-0-DELETE': '',
            'sc2_authors-1-autr': 'Aiutante',
            'sc2_authors-1-autn': 'Allievo',
            'sc2_authors-1-auta': '1505',
            'sc2_authors-1-DELETE': '',
        }
        formset = Sc2AuthorFormSet(post_data, instance=unit)
        assert formset.is_valid(), f"Formset invalid: {formset.errors} non_form: {formset.non_form_errors()}"

        # Salva tutti i form
        instances = formset.save(commit=False)
        for inst in instances:
            if not inst.pk:
                inst.unit = unit
                inst.save()

        after_count = Sc2Author.objects.filter(unit=unit).count()
        assert after_count == before_count + 2, f"Expected {before_count + 2} authors, got {after_count}"

        # Verifica i dati
        authors = list(Sc2Author.objects.filter(unit=unit).order_by('autn'))
        assert authors[0].autn == 'Allievo', f"First author name mismatch: {authors[0].autn}"
        assert authors[1].autn == 'Leonardo', f"Second author name mismatch: {authors[1].autn}"
    test("SC2 AuthorFormSet: salvataggio corretto", _test_sc2_author_formset_save)

    def _test_sc2_commission_formset_save():
        """Salvataggio tramite Sc2CommissionFormSet inline su Unit."""
        from archimista_python.archive.models import Fond, Unit, Sc2, Sc2Commission
        from archimista_python.archive.forms import Sc2CommissionFormSet

        fond = Fond.objects.create(name='SC2 Comm FS Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita SC2 Comm FS', fond=fond, created_by=1, updated_by=1)
        Sc2.objects.create(unit=unit, card_type='SC2')

        post_data = {
            'sc2_commissions-TOTAL_FORMS': '1',
            'sc2_commissions-INITIAL_FORMS': '0',
            'sc2_commissions-MIN_NUM_FORMS': '0',
            'sc2_commissions-MAX_NUM_FORMS': '1000',
            'sc2_commissions-0-cmmc': 'Committenza Medicea',
            'sc2_commissions-0-DELETE': '',
        }
        formset = Sc2CommissionFormSet(post_data, instance=unit)
        assert formset.is_valid(), f"Formset invalid: {formset.errors} non_form: {formset.non_form_errors()}"

        instances = formset.save(commit=False)
        for inst in instances:
            if not inst.pk:
                inst.unit = unit
                inst.save()

        assert Sc2Commission.objects.filter(unit=unit).count() == 1
        comm = Sc2Commission.objects.filter(unit=unit).first()
        assert comm.cmmc == 'Committenza Medicea', f"Commission mismatch: {comm.cmmc}"
    test("SC2 CommissionFormSet: salvataggio corretto", _test_sc2_commission_formset_save)

    section("18c. Formset SC2 — cancellazione con DELETE")

    def _test_sc2_author_delete_via_formset():
        """Elimina autore SC2 tramite formset con DELETE."""
        from archimista_python.archive.models import (
            Fond, Unit, Sc2, Sc2Author, Sc2AttributionReason,
        )
        from archimista_python.archive.forms import Sc2AuthorFormSet

        fond = Fond.objects.create(name='SC2 Delete Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita SC2 Delete', fond=fond, created_by=1, updated_by=1)
        Sc2.objects.create(unit=unit, card_type='SC2')
        author = Sc2Author.objects.create(unit=unit, autr='Da eliminare', autn='Autore X')
        Sc2AttributionReason.objects.create(sc2_author=author, autm='Motivo X')

        author_pk = author.pk
        assert Sc2Author.objects.filter(pk=author_pk).exists(), "Author should exist before deletion"

        post_data = {
            'sc2_authors-TOTAL_FORMS': '1',
            'sc2_authors-INITIAL_FORMS': '1',
            'sc2_authors-MIN_NUM_FORMS': '0',
            'sc2_authors-MAX_NUM_FORMS': '1000',
            f'sc2_authors-0-id': str(author_pk),
            'sc2_authors-0-autr': 'Da eliminare',
            'sc2_authors-0-autn': 'Autore X',
            'sc2_authors-0-DELETE': 'on',
        }
        formset = Sc2AuthorFormSet(post_data, instance=unit)
        assert formset.is_valid(), f"Formset invalid: {formset.errors} non_form: {formset.non_form_errors()}"

        # Pattern di salvataggio come nelle view: elimina se DELETE=True
        formset.save(commit=False)
        for form in formset.forms:
            if form.cleaned_data and form.cleaned_data.get('DELETE', False) and form.instance.pk:
                form.instance.delete()

        assert not Sc2Author.objects.filter(pk=author_pk).exists(), "Author should be deleted"
        # CASCADE: i reasons devono essere eliminati
        assert Sc2AttributionReason.objects.filter(sc2_author_id=author_pk).count() == 0, \
            "Attribution reasons should be cascade deleted"
    test("SC2: cancellazione autore con formset DELETE", _test_sc2_author_delete_via_formset)

    section("18d. Formset SC2 — validazione edge cases")

    def _test_sc2_author_formset_with_empty_form():
        """Formset SC2 author con form vuoto non deve creare record."""
        from archimista_python.archive.models import Fond, Unit, Sc2, Sc2Author
        from archimista_python.archive.forms import Sc2AuthorFormSet

        fond = Fond.objects.create(name='SC2 Empty Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita SC2 Empty', fond=fond, created_by=1, updated_by=1)
        Sc2.objects.create(unit=unit, card_type='SC2')

        before_count = Sc2Author.objects.filter(unit=unit).count()

        post_data = {
            'sc2_authors-TOTAL_FORMS': '1',
            'sc2_authors-INITIAL_FORMS': '0',
            'sc2_authors-MIN_NUM_FORMS': '0',
            'sc2_authors-MAX_NUM_FORMS': '1000',
            'sc2_authors-0-autr': '',
            'sc2_authors-0-autn': '',
            'sc2_authors-0-auta': '',
            'sc2_authors-0-DELETE': '',
        }
        formset = Sc2AuthorFormSet(post_data, instance=unit)
        assert formset.is_valid(), f"Formset invalid: {formset.non_form_errors()}"

        # Salva ma il form e vuoto — Django salva record vuoti se can_delete=False
        # ma i campi sono blank=True quindi non c'e validazione error
        instances = formset.save(commit=False)
        for inst in instances:
            if not inst.pk:
                # Controlla se c'e almeno un campo compilato (pattern view)
                if any([inst.autr, inst.autn, inst.auta]):
                    inst.unit = unit
                    inst.save()

        after_count = Sc2Author.objects.filter(unit=unit).count()
        assert after_count == before_count, f"Empty formset should not create records: before={before_count}, after={after_count}"
    test("SC2: formset vuoto non crea record", _test_sc2_author_formset_with_empty_form)

    def _test_sc2_technique_and_scale_creation():
        """Verifica creazione di tecniche e scale SC2."""
        from archimista_python.archive.models import (
            Fond, Unit, Sc2, Sc2Technique, Sc2Scale,
        )
        fond = Fond.objects.create(name='SC2 Tech Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita SC2 Tech', fond=fond, created_by=1, updated_by=1)
        Sc2.objects.create(unit=unit, card_type='SC2')

        Sc2Technique.objects.create(unit=unit, mtct='olio su tela')
        Sc2Technique.objects.create(unit=unit, mtct='acquerello')
        Sc2Scale.objects.create(unit=unit, sca='1:50')

        assert unit.sc2_techniques.count() == 2
        assert unit.sc2_scales.count() == 1
    test("SC2: tecniche e scale multiple", _test_sc2_technique_and_scale_creation)

    def _test_sc2_textual_and_visual_elements():
        """Verifica creazione di elementi testuali e visivi SC2."""
        from archimista_python.archive.models import (
            Fond, Unit, Sc2, Sc2TextualElement, Sc2VisualElement,
        )
        fond = Fond.objects.create(name='SC2 Elements Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unita SC2 Elements', fond=fond, created_by=1, updated_by=1)
        Sc2.objects.create(unit=unit, card_type='SC2')

        Sc2TextualElement.objects.create(unit=unit, isri='Iscrizione sul retro')
        Sc2VisualElement.objects.create(unit=unit, stmd='Stato di conservazione buono')

        assert unit.sc2_textual_elements.count() == 1
        assert unit.sc2_visual_elements.count() == 1
    test("SC2: elementi testuali e visivi", _test_sc2_textual_and_visual_elements)
