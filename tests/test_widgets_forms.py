"""Test: Select2 widgets e form instanziazione."""
from tests import test, section


def run():
    section("3. Select2 widgets")

    def _test_fond_select2():
        from archimista_python.archive.widgets import FondSelect2Widget
        w = FondSelect2Widget()
        assert w.model.__name__ == 'Fond'
        assert 'name__icontains' in w.search_fields
    test("FondSelect2Widget", _test_fond_select2)

    def _test_unit_select2():
        from archimista_python.archive.widgets import UnitSelect2Widget
        w = UnitSelect2Widget()
        assert w.model.__name__ == 'Unit'
        assert 'title__icontains' in w.search_fields
        assert 'reference_number__icontains' in w.search_fields
    test("UnitSelect2Widget", _test_unit_select2)

    def _test_classification_select2():
        from archimista_python.archive.widgets import ClassificationSelect2Widget
        w = ClassificationSelect2Widget()
        assert w.model.__name__ == 'Classification'
        assert 'code__icontains' in w.search_fields
    test("ClassificationSelect2Widget", _test_classification_select2)

    def _test_lang_select2():
        from archimista_python.archive.widgets import LangSelect2Widget
        w = LangSelect2Widget()
        assert w.model.__name__ == 'Lang'
        assert 'code__icontains' in w.search_fields
        assert 'name__icontains' in w.search_fields
    test("LangSelect2Widget", _test_lang_select2)

    section("4. Form instanziazione e widget")

    def _test_fond_form_fields():
        from archimista_python.archive.forms import FondForm
        f = FondForm()
        assert 'parent' in f.fields
        assert 'name' in f.fields
        assert 'fond_type_term' in f.fields
        from archimista_python.archive.widgets import FondSelect2Widget
        assert isinstance(f.fields['parent'].widget, FondSelect2Widget)
    test("FondForm: campi e widget Select2 per parent", _test_fond_form_fields)

    def _test_unit_form_fields():
        from archimista_python.archive.forms import UnitForm
        f = UnitForm()
        assert 'fond' in f.fields
        assert 'parent' in f.fields
        assert 'classification' in f.fields
        from archimista_python.archive.widgets import FondSelect2Widget, UnitSelect2Widget, ClassificationSelect2Widget
        assert isinstance(f.fields['fond'].widget, FondSelect2Widget), f"Expected FondSelect2Widget, got {type(f.fields['fond'].widget)}"
        assert isinstance(f.fields['parent'].widget, UnitSelect2Widget), f"Expected UnitSelect2Widget, got {type(f.fields['parent'].widget)}"
        assert isinstance(f.fields['classification'].widget, ClassificationSelect2Widget), f"Expected ClassificationSelect2Widget, got {type(f.fields['classification'].widget)}"
    test("UnitForm: campi e widget Select2 per fond/parent/classification", _test_unit_form_fields)

    def _test_unit_lang_form_widget():
        from archimista_python.archive.forms import UnitLangForm
        f = UnitLangForm()
        from archimista_python.archive.widgets import LangSelect2Widget
        assert isinstance(f.fields['code'].widget, LangSelect2Widget), f"Expected LangSelect2Widget, got {type(f.fields['code'].widget)}"
    test("UnitLangForm: widget LangSelect2Widget", _test_unit_lang_form_widget)

    def _test_fond_lang_form_widget():
        from archimista_python.archive.forms import FondLangForm
        f = FondLangForm()
        from archimista_python.archive.widgets import LangSelect2Widget
        assert isinstance(f.fields['code'].widget, LangSelect2Widget), f"Expected LangSelect2Widget, got {type(f.fields['code'].widget)}"
    test("FondLangForm: widget LangSelect2Widget", _test_fond_lang_form_widget)

    def _test_creator_form_fields():
        from archimista_python.archive.forms import CreatorForm
        f = CreatorForm()
        assert 'creator_type' in f.fields
        assert 'residence' in f.fields
    test("CreatorForm: campi base", _test_creator_form_fields)

    def _test_custodian_form_fields():
        from archimista_python.archive.forms import CustodianForm
        f = CustodianForm()
        assert 'custodian_type' in f.fields
        assert 'contact_person' in f.fields
    test("CustodianForm: campi base", _test_custodian_form_fields)

    def _test_classification_form_widget():
        from archimista_python.archive.forms import ClassificationForm
        f = ClassificationForm()
        from archimista_python.archive.widgets import ClassificationSelect2Widget
        assert isinstance(f.fields['parent'].widget, ClassificationSelect2Widget), f"Expected ClassificationSelect2Widget, got {type(f.fields['parent'].widget)}"
    test("ClassificationForm: widget Select2 per parent", _test_classification_form_widget)
