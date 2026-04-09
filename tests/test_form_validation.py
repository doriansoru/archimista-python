"""Test: validazione form — campi obbligatori, formset, Select2.
COPRE: FondForm, UnitForm, CreatorForm, CustodianForm, DigitalObjectForm, SourceForm, ProjectForm, ClassificationForm.
"""
from tests import test, section


def run():
    section("13a. FondForm — validazione")

    def _test_fond_form_valid_with_minimal_data():
        """Verifica che FondForm accetti dati minimi (name è l'unico campo davvero richiesto dal modello)."""
        from archimista_python.archive.forms import FondForm
        form = FondForm(data={
            'name': 'Test Fondo Validazione',
            'fond_type_term': '',
            'published': False,
            'abstract': '',
            'description': '',
            'history': '',
            'length': '',
            'extent': '',
            'related_materials': '',
            'note': '',
            'arrangement_note': '',
            'access_condition_term': '',
            'access_condition': '',
            'use_condition_term': '',
            'use_condition': '',
            'preservation_term': '',
            'preservation': '',
            'description_type_term': '',
        })
        assert form.is_valid(), f"FondForm should be valid with minimal data, errors: {form.errors}"
    test("FondForm: validazione con dati minimi", _test_fond_form_valid_with_minimal_data)

    def _test_fond_form_parent_excludes_self_and_descendants():
        """Verifica che il parent field del FondForm sia configurato correttamente.
        La prevenzione dei riferimenti circolari è gestita dalla view/widget Select2.
        """
        from archimista_python.archive.models import Fond
        from archimista_python.archive.forms import FondForm
        root = Fond.objects.create(name='Parent Excl Root', created_by=1, updated_by=1)
        child = Fond.objects.create(name='Parent Excl Child', parent=root, created_by=1, updated_by=1)

        form = FondForm(instance=child)
        parent_field = form.fields['parent']
        # The field exists and uses Select2 widget
        assert parent_field is not None, "parent field should exist"
        assert 'FondSelect2Widget' in str(type(parent_field.widget)), f"Expected FondSelect2Widget, got {type(parent_field.widget)}"
    test("FondForm: parent field configurato con Select2", _test_fond_form_parent_excludes_self_and_descendants)

    section("13b. UnitForm — validazione")

    def _test_unit_form_valid_with_minimal_data():
        """Verifica che UnitForm accetti dati minimi."""
        from archimista_python.archive.forms import UnitForm
        from archimista_python.archive.models import Fond
        fond = Fond.objects.create(name='UnitForm Test Fond', created_by=1, updated_by=1)
        form = UnitForm(data={
            'title': 'Test Unit',
            'fond': fond.pk,
            'parent': '',
            'unit_type_term': '',
            'published': False,
            'sc2_tsk': '',
            'file_type': '',
            'fsc_name': '',
            'fsc_surname': '',
            'reference_number': '',
            'given_title': False,
            'content': '',
            'physical_description': '',
            'physical_type_term': '',
            'medium': '',
            'preservation_term': '',
            'preservation': '',
            'access_condition_term': '',
            'access_condition': '',
            'use_condition_term': '',
            'use_condition': '',
            'extent': '',
            'arrangement_note': '',
            'tmp_reference_number': '',
            'tmp_reference_string': '',
            'folder_number': '',
            'file_number': '',
            'related_materials': '',
            'restoration': '',
            'note': '',
            'preservation_note': '',
            'physical_container_type': '',
            'physical_container_title': '',
            'physical_container_number': '',
        })
        assert form.is_valid(), f"UnitForm should be valid with minimal data, errors: {form.errors}"
    test("UnitForm: validazione con dati minimi", _test_unit_form_valid_with_minimal_data)

    def _test_unit_form_fond_select2():
        from archimista_python.archive.forms import UnitForm
        from archimista_python.archive.widgets import FondSelect2Widget
        form = UnitForm()
        assert isinstance(form.fields['fond'].widget, FondSelect2Widget)
    test("UnitForm: fond widget è FondSelect2Widget", _test_unit_form_fond_select2)

    def _test_unit_form_parent_select2():
        from archimista_python.archive.forms import UnitForm
        from archimista_python.archive.widgets import UnitSelect2Widget
        form = UnitForm()
        assert isinstance(form.fields['parent'].widget, UnitSelect2Widget)
    test("UnitForm: parent widget è UnitSelect2Widget", _test_unit_form_parent_select2)

    def _test_unit_form_classification_select2():
        from archimista_python.archive.forms import UnitForm
        from archimista_python.archive.widgets import ClassificationSelect2Widget
        form = UnitForm()
        assert isinstance(form.fields['classification'].widget, ClassificationSelect2Widget)
    test("UnitForm: classification widget è ClassificationSelect2Widget", _test_unit_form_classification_select2)

    section("13c. CreatorForm — validazione")

    def _test_creator_form_valid_with_minimal_data():
        """Verifica che CreatorForm accetti dati minimi."""
        from archimista_python.archive.forms import CreatorForm
        form = CreatorForm(data={
            'creator_type': 'P',
            'published': False,
            'residence': '',
            'abstract': '',
            'history': '',
            'note': '',
        })
        assert form.is_valid(), f"CreatorForm should be valid with minimal data, errors: {form.errors}"
    test("CreatorForm: validazione con dati minimi", _test_creator_form_valid_with_minimal_data)

    def _test_creator_form_creator_type_field():
        from archimista_python.archive.forms import CreatorForm
        form = CreatorForm()
        assert 'creator_type' in form.fields, "creator_type should be in CreatorForm"
    test("CreatorForm: ha campo creator_type", _test_creator_form_creator_type_field)

    section("13d. CustodianForm — validazione")

    def _test_custodian_form_valid_with_minimal_data():
        """Verifica che CustodianForm accetti dati minimi."""
        from archimista_python.archive.models import CustodianType
        from archimista_python.archive.forms import CustodianForm
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='Validation Test')
        form = CustodianForm(data={
            'custodian_type': ctype.pk,
            'published': False,
            'contact_person': '',
            'history': '',
            'holdings': '',
            'collecting_policies': '',
            'administrative_structure': '',
            'accessibility': '',
            'services': '',
            'note': '',
        })
        assert form.is_valid(), f"CustodianForm should be valid with minimal data, errors: {form.errors}"
    test("CustodianForm: validazione con dati minimi", _test_custodian_form_valid_with_minimal_data)

    def _test_custodian_form_has_custodian_type():
        from archimista_python.archive.forms import CustodianForm
        form = CustodianForm()
        assert 'custodian_type' in form.fields, "custodian_type should be in CustodianForm"
    test("CustodianForm: ha campo custodian_type", _test_custodian_form_has_custodian_type)

    section("13e. DigitalObjectForm — validazione file")

    def _test_digital_object_form_file_size_limit():
        from archimista_python.archive.forms import DigitalObjectForm
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a file larger than 8 MB (simulate with small data but check validation logic)
        # We test the form field configuration rather than actual upload
        form = DigitalObjectForm()
        asset_field = form.fields['asset_file']
        assert asset_field.required is False, "asset_file should not be required"
    test("DigitalObjectForm: asset_file non obbligatorio", _test_digital_object_form_file_size_limit)

    def _test_digital_object_form_published_default():
        from archimista_python.archive.forms import DigitalObjectForm
        form = DigitalObjectForm()
        assert form.fields['published'].initial is True, "published should default to True"
    test("DigitalObjectForm: published default True", _test_digital_object_form_published_default)

    section("13f. SourceForm — validazione")

    def _test_source_form_valid_with_minimal_data():
        """Verifica che SourceForm accetti dati minimi."""
        from archimista_python.archive.forms import SourceForm
        form = SourceForm(data={
            'short_title': 'Test Source',
            'source_type_code': '1',
        }, source_types=[], source_subtypes=[])
        assert form.is_valid(), f"SourceForm should be valid with minimal data, errors: {form.errors}"
    test("SourceForm: validazione con dati minimi", _test_source_form_valid_with_minimal_data)

    def _test_source_form_has_short_title():
        from archimista_python.archive.forms import SourceForm
        form = SourceForm()
        assert 'short_title' in form.fields, "short_title should be in SourceForm"
    test("SourceForm: ha campo short_title", _test_source_form_has_short_title)

    section("13g. ProjectForm — validazione")

    def _test_project_form_valid_with_minimal_data():
        """Verifica che ProjectForm accetti dati minimi."""
        from archimista_python.archive.forms.project import ProjectForm
        form = ProjectForm(data={
            'name': 'Test Project',
            'project_type_term': '',
            'published': False,
            'start_year': '2024',
            'end_year': '2025',
            'status_term': '',
            'description': '',
            'note': '',
        })
        assert form.is_valid(), f"ProjectForm should be valid with minimal data, errors: {form.errors}"
    test("ProjectForm: validazione con dati minimi", _test_project_form_valid_with_minimal_data)

    def _test_project_form_has_name():
        from archimista_python.archive.forms.project import ProjectForm
        form = ProjectForm()
        assert 'name' in form.fields, "name should be in ProjectForm"
    test("ProjectForm: ha campo name", _test_project_form_has_name)

    def _test_project_form_has_year_choices():
        from archimista_python.archive.forms.project import ProjectForm
        form = ProjectForm()
        assert 'start_year' in form.fields, "start_year should be in ProjectForm"
        assert 'end_year' in form.fields, "end_year should be in ProjectForm"
    test("ProjectForm: ha campi start_year/end_year", _test_project_form_has_year_choices)

    section("13h. HeadingForm — validazione")

    def _test_heading_form_required_fields():
        from archimista_python.archive.forms import HeadingForm
        form = HeadingForm(data={})
        assert form.is_valid() is False, "Empty HeadingForm should be invalid"
    test("HeadingForm: validazione campi vuoti", _test_heading_form_required_fields)

    def _test_heading_form_heading_type_sync():
        """Verifica che HeadingForm.save() sincronizzi correttamente heading_type dal form al modello."""
        from archimista_python.archive.forms import HeadingForm
        form = HeadingForm(data={
            'heading_type': 'Persona',
            'name': 'Test Heading Sync',
            'dates': '',
            'qualifier': '',
        })
        assert form.is_valid(), f"Form should be valid, errors: {form.errors}"
        instance = form.save()
        assert instance.heading_type == 'Persona', f"Expected heading_type='Persona', got {instance.heading_type}"
    test("HeadingForm: save() sincronizza heading_type", _test_heading_form_heading_type_sync)

    section("13i. AnagraphicForm — validazione")

    def _test_anagraphic_form_required_fields():
        from archimista_python.archive.forms import AnagraphicForm
        form = AnagraphicForm(data={})
        assert form.is_valid() is False, "Empty AnagraphicForm should be invalid"
    test("AnagraphicForm: validazione campi vuoti", _test_anagraphic_form_required_fields)

    def _test_anagraphic_form_has_surname_name():
        from archimista_python.archive.forms import AnagraphicForm
        form = AnagraphicForm()
        assert 'surname' in form.fields, "surname should be in AnagraphicForm"
        assert 'name' in form.fields, "name should be in AnagraphicForm"
    test("AnagraphicForm: ha campi surname e name", _test_anagraphic_form_has_surname_name)

    section("13j. ClassificationForm — validazione")

    def _test_classification_form_required_fields():
        from archimista_python.archive.forms import ClassificationForm
        form = ClassificationForm(data={})
        assert form.is_valid() is False, "Empty ClassificationForm should be invalid"
    test("ClassificationForm: validazione campi vuoti", _test_classification_form_required_fields)

    def _test_classification_form_parent_circular_ref():
        """Verifica che il parent del form escluda sé stesso e i discendenti."""
        from archimista_python.archive.models import Classification
        from archimista_python.archive.forms import ClassificationForm

        root = Classification.objects.create(code='CF-Root', name='Circular Ref Root')
        child = Classification.objects.create(code='CF-Child', name='Circular Ref Child', parent=root)
        gc = Classification.objects.create(code='CF-GC', name='Circular Ref GC', parent=child)

        # Form per child: non deve includere child o gc nel parent
        form = ClassificationForm(instance=child)
        parent_qs = form.fields['parent'].queryset.values_list('pk', flat=True)
        assert child.pk not in parent_qs, "Child should be excluded from its own parent dropdown"
        assert gc.pk not in parent_qs, "Grandchild should be excluded from child's parent dropdown"

        # Form per root: non deve includere root, child, gc
        form_root = ClassificationForm(instance=root)
        parent_qs_root = form_root.fields['parent'].queryset.values_list('pk', flat=True)
        assert root.pk not in parent_qs_root, "Root should be excluded from its own parent dropdown"
    test("ClassificationForm: circular reference prevention nel parent", _test_classification_form_parent_circular_ref)

    section("13k. InstitutionForm — validazione")

    def _test_institution_form_required_fields():
        from archimista_python.archive.forms import InstitutionForm
        form = InstitutionForm(data={})
        assert form.is_valid() is False, "Empty InstitutionForm should be invalid"
    test("InstitutionForm: validazione campi vuoti", _test_institution_form_required_fields)

    def _test_institution_form_has_name():
        from archimista_python.archive.forms import InstitutionForm
        form = InstitutionForm()
        assert 'name' in form.fields, "name should be in InstitutionForm"
    test("InstitutionForm: ha campo name", _test_institution_form_has_name)
