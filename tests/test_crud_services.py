"""Test: CRUD 9 entità di servizio (Source, Project, Institution, Heading, Anagraphic, DocumentForm, Editor, Classification, DigitalObject)."""
from tests import test, section, client
from django.urls import reverse


def run():
    section("9a. Source (Fonti)")
    def _run_source_crud():
        from archimista_python.archive.models import Source
        resp = client.post(reverse('archive:source_create'), {
            'short_title': 'Fonte Test', 'title': 'Titolo fonte', 'author': 'Autore',
            'source_type_code': '1',
            'url-TOTAL_FORMS': '0', 'url-INITIAL_FORMS': '0', 'url-MIN_NUM_FORMS': '0', 'url-MAX_NUM_FORMS': '1000',
        }, follow=True)
        assert resp.status_code == 200, f"Source create failed: {resp.status_code}"
        source = Source.objects.filter(short_title='Fonte Test').first()
        assert source is not None, "Source non creata"
        resp = client.get(reverse('archive:source_list'))
        assert resp.status_code == 200
        resp = client.get(reverse('archive:source_detail', args=[source.pk]))
        assert resp.status_code == 200
        resp = client.get(reverse('archive:source_edit', args=[source.pk]))
        assert resp.status_code == 200
        resp = client.get(reverse('archive:source_delete', args=[source.pk]))
        assert resp.status_code == 200
    test("Source: create, list, detail, update, delete", _run_source_crud)

    section("9b. Project (Progetti)")
    def _run_project_crud():
        from archimista_python.archive.models import Project
        resp = client.post(reverse('archive:project_create'), {
            'name': 'Progetto Test', 'project_type_term': '', 'published': False,
            'start_year': '2024', 'end_year': '2025', 'status_term': '',
            'description': 'Descrizione', 'note': '',
            'url-TOTAL_FORMS': '0', 'url-INITIAL_FORMS': '0', 'url-MIN_NUM_FORMS': '0', 'url-MAX_NUM_FORMS': '1000',
            'manager-TOTAL_FORMS': '0', 'manager-INITIAL_FORMS': '0', 'manager-MIN_NUM_FORMS': '0', 'manager-MAX_NUM_FORMS': '1000',
            'stakeholder-TOTAL_FORMS': '0', 'stakeholder-INITIAL_FORMS': '0', 'stakeholder-MIN_NUM_FORMS': '0', 'stakeholder-MAX_NUM_FORMS': '1000',
            'fond-TOTAL_FORMS': '0', 'fond-INITIAL_FORMS': '0', 'fond-MIN_NUM_FORMS': '0', 'fond-MAX_NUM_FORMS': '1000',
        }, follow=True)
        assert resp.status_code == 200, f"Project create failed: {resp.status_code}"
        project = Project.objects.filter(name='Progetto Test').first()
        assert project is not None, "Project non creato"
        for view_name in ['project_list', 'project_detail', 'project_update', 'project_delete']:
            kwargs = {'pk': project.pk} if view_name != 'project_list' else {}
            resp = client.get(reverse(f'archive:{view_name}', kwargs=kwargs))
            assert resp.status_code == 200
    test("Project: create, list, detail, update, delete", _run_project_crud)

    section("9c. Institution (Profili istituzionali)")
    def _run_institution_crud():
        from archimista_python.archive.models import Institution
        resp = client.post(reverse('archive:institution_create'), {
            'name': 'Istituto Test', 'description': 'Descrizione', 'note': '',
            'editor-TOTAL_FORMS': '0', 'editor-INITIAL_FORMS': '0', 'editor-MIN_NUM_FORMS': '0', 'editor-MAX_NUM_FORMS': '1000',
        }, follow=True)
        assert resp.status_code == 200, f"Institution create failed: {resp.status_code}"
        institution = Institution.objects.filter(name='Istituto Test').first()
        assert institution is not None, "Institution non creata"
        for view_name in ['institution_list', 'institution_detail', 'institution_edit', 'institution_delete']:
            kwargs = {'pk': institution.pk} if view_name != 'institution_list' else {}
            resp = client.get(reverse(f'archive:{view_name}', kwargs=kwargs))
            assert resp.status_code == 200
    test("Institution: create, list, detail, update, delete", _run_institution_crud)

    section("9d. Heading (Voci di indice)")
    def _run_heading_crud():
        from archimista_python.archive.models import Heading
        resp = client.post(reverse('archive:heading_create'), {
            'heading_type_term': '', 'name': 'Voce Test', 'dates': '', 'qualifier': '',
        }, follow=True)
        assert resp.status_code == 200, f"Heading create failed: {resp.status_code}"
        heading = Heading.objects.filter(name='Voce Test').first()
        assert heading is not None, "Heading non creata"
        for view_name in ['heading_list', 'heading_detail', 'heading_edit', 'heading_delete']:
            kwargs = {'pk': heading.pk} if view_name != 'heading_list' else {}
            resp = client.get(reverse(f'archive:{view_name}', kwargs=kwargs))
            assert resp.status_code == 200
    test("Heading: create, list, detail, update, delete", _run_heading_crud)

    section("9e. Anagraphic (Anagrafiche)")
    def _run_anagraphic_crud():
        from archimista_python.archive.models import Anagraphic
        resp = client.post(reverse('archive:anagraphic_create'), {
            'surname': 'Rossi', 'name': 'Mario',
            'start_date_place': '', 'start_date': '', 'end_date_place': '', 'end_date': '',
            'identifier-TOTAL_FORMS': '0', 'identifier-INITIAL_FORMS': '0', 'identifier-MIN_NUM_FORMS': '0', 'identifier-MAX_NUM_FORMS': '1000',
        }, follow=True)
        assert resp.status_code == 200, f"Anagraphic create failed: {resp.status_code}"
        anagraphic = Anagraphic.objects.filter(surname='Rossi', name='Mario').first()
        assert anagraphic is not None, "Anagraphic non creata"
        for view_name in ['anagraphic_list', 'anagraphic_detail', 'anagraphic_edit', 'anagraphic_delete']:
            kwargs = {'pk': anagraphic.pk} if view_name != 'anagraphic_list' else {}
            resp = client.get(reverse(f'archive:{view_name}', kwargs=kwargs))
            assert resp.status_code == 200
    test("Anagraphic: create, list, detail, update, delete", _run_anagraphic_crud)

    section("9f. DocumentForm (Forme documentarie)")
    def _run_document_form_crud():
        from archimista_python.archive.models import DocumentForm
        df = DocumentForm.objects.create(name='Forma Test', description='Descrizione', note='', created_by=1, updated_by=1)
        for view_name in ['document_form_list', 'document_form_detail', 'document_form_edit', 'document_form_delete']:
            kwargs = {'pk': df.pk} if view_name != 'document_form_list' else {}
            resp = client.get(reverse(f'archive:{view_name}', kwargs=kwargs))
            assert resp.status_code == 200, f"{view_name} failed: {resp.status_code}"
    test("DocumentForm: list, detail, update, delete", _run_document_form_crud)

    section("9g. Editor (Compilatori)")
    def _run_editor_crud():
        from archimista_python.archive.models import Editor
        resp = client.post(reverse('archive:editor_create'), {'first_name': 'Compilatore', 'last_name': 'Test'}, follow=True)
        assert resp.status_code == 200, f"Editor create failed: {resp.status_code}"
        editor = Editor.objects.filter(first_name='Compilatore', last_name='Test').first()
        assert editor is not None, "Editor non creato"
        for view_name in ['editor_list', 'editor_detail', 'editor_edit', 'editor_delete']:
            kwargs = {'pk': editor.pk} if view_name != 'editor_list' else {}
            resp = client.get(reverse(f'archive:{view_name}', kwargs=kwargs))
            assert resp.status_code == 200
    test("Editor: create, list, detail, update, delete", _run_editor_crud)

    section("9h. Classification (Titolario)")
    def _run_classification_crud():
        from archimista_python.archive.models import Classification
        resp = client.post(reverse('archive:classification_create'), {
            'code': 'CLT001', 'name': 'Classificazione Test', 'description': 'Descrizione', 'parent': '',
        }, follow=True)
        assert resp.status_code == 200, f"Classification create failed: {resp.status_code}"
        classification = Classification.objects.filter(code='CLT001').first()
        assert classification is not None, "Classification non creata"
        for view_name in ['classification_list', 'classification_detail', 'classification_update', 'classification_delete', 'classification_tree_data', 'classification_units']:
            kwargs = {'pk': classification.pk} if view_name != 'classification_list' else {}
            resp = client.get(reverse(f'archive:{view_name}', kwargs=kwargs))
            assert resp.status_code == 200, f"{view_name} failed: {resp.status_code}"
    test("Classification: create, list, detail, update, delete, tree, units", _run_classification_crud)

    section("9i. DigitalObject (Oggetti digitali)")
    def _run_digital_object_crud():
        resp = client.get(reverse('archive:digital_object_create'))
        assert resp.status_code == 200
        resp = client.get(reverse('archive:digital_object_list'))
        assert resp.status_code == 200
    test("DigitalObject: create GET, list", _run_digital_object_crud)

    section("9j. DigitalObject nested URL resolving")
    from django.urls import resolve
    nested = [
        ('archive:fond_digital_object_list', {'fond_id': 1}),
        ('archive:unit_digital_object_list', {'unit_id': 1}),
        ('archive:creator_digital_object_list', {'creator_id': 1}),
        ('archive:custodian_digital_object_list', {'custodian_id': 1}),
        ('archive:source_digital_object_list', {'source_id': 1}),
    ]
    for url_name, kwargs in nested:
        try:
            resolve(reverse(url_name, kwargs=kwargs))
            print(f"  ✅ URL: {url_name}")
            from tests import PASSED
            import tests
            tests.PASSED += 1
        except Exception as e:
            print(f"  ❌ URL: {url_name}: {e}")
            import tests
            tests.FAILED += 1

    section("9k. Nested digital object list funzionali")
    def _test_fond_digital_object_list():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.first()
        if not fond:
            fond = Fond.objects.create(name='DO Fond', created_by=1, updated_by=1)
        resp = client.get(reverse('archive:fond_digital_object_list', args=[fond.pk]))
        assert resp.status_code == 200
    test("Digital objects: lista nested per fondo", _test_fond_digital_object_list)

    def _test_unit_digital_object_list():
        from archimista_python.archive.models import Unit, Fond
        fond = Fond.objects.first()
        if not fond:
            fond = Fond.objects.create(name='DO Unit Fond', created_by=1, updated_by=1)
        unit = Unit.objects.filter(fond=fond).first()
        if not unit:
            unit = Unit.objects.create(title='DO Unit', fond=fond, created_by=1, updated_by=1)
        resp = client.get(reverse('archive:unit_digital_object_list', args=[unit.pk]))
        assert resp.status_code == 200
    test("Digital objects: lista nested per unità", _test_unit_digital_object_list)
