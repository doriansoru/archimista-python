"""Test: template rendering e partials."""
import os
from django.template import loader
from tests import test, section


def run():
    section("5. Template rendering (partials)")

    def _test_fond_form_template():
        t = loader.get_template('archive/fond_form.html')
        assert t is not None
    test("fond_form.html si carica", _test_fond_form_template)

    def _test_fond_partials_exist():
        partials = [
            '_tab_description.html', '_tab_other_info.html', '_tab_access.html',
            '_tab_relations.html', '_tab_sources.html', '_tab_editors.html',
        ]
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'archimista_python/archive/templates/archive/fonds/partials/')
        for p in partials:
            path = os.path.join(base, p)
            assert os.path.exists(path), f"Partial mancante: {path}"
    test("fond partials esistono (6 file)", _test_fond_partials_exist)

    def _test_creator_form_template():
        t = loader.get_template('archive/creator_form.html')
        assert t is not None
    test("creator_form.html si carica", _test_creator_form_template)

    def _test_creator_partials_exist():
        partials = [
            '_tab_identification.html', '_tab_description.html', '_tab_relations.html',
            '_tab_sources.html', '_tab_credits.html',
        ]
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'archimista_python/archive/templates/archive/creators/partials/')
        for p in partials:
            path = os.path.join(base, p)
            assert os.path.exists(path), f"Partial mancante: {path}"
    test("creator partials esistono (5 file)", _test_creator_partials_exist)

    def _test_custodian_form_template():
        t = loader.get_template('archive/custodian_form.html')
        assert t is not None
    test("custodian_form.html si carica", _test_custodian_form_template)

    def _test_custodian_partials_exist():
        partials = [
            '_tab_identification.html', '_tab_description.html', '_tab_access.html',
            '_tab_buildings.html', '_tab_relations.html', '_tab_sources.html', '_tab_credits.html',
        ]
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'archimista_python/archive/templates/archive/custodians/partials/')
        for p in partials:
            path = os.path.join(base, p)
            assert os.path.exists(path), f"Partial mancante: {path}"
    test("custodian partials esistono (7 file)", _test_custodian_partials_exist)

    def _test_unit_form_template():
        t = loader.get_template('archive/unit_form.html')
        assert t is not None
    test("unit_form.html si carica", _test_unit_form_template)

    def _test_fond_detail_template():
        t = loader.get_template('archive/fond_detail.html')
        assert t is not None
    test("fond_detail.html si carica", _test_fond_detail_template)

    def _test_unit_detail_template():
        t = loader.get_template('archive/unit_detail.html')
        assert t is not None
    test("unit_detail.html si carica", _test_unit_detail_template)

    def _test_creator_detail_template():
        t = loader.get_template('archive/creator_detail.html')
        assert t is not None
    test("creator_detail.html si carica", _test_creator_detail_template)

    def _test_custodian_detail_template():
        t = loader.get_template('archive/custodian_detail.html')
        assert t is not None
    test("custodian_detail.html si carica", _test_custodian_detail_template)

    def _test_base_template():
        t = loader.get_template('archive/base.html')
        assert t is not None
    test("base.html si carica", _test_base_template)
