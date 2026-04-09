"""Test: URL resolving."""
from tests import test, section
from django.urls import reverse, resolve


def run():
    section("2. URL resolving")

    url_names = [
        'archive:fond_list',
        'archive:unit_list',
        'archive:creator_list',
        'archive:custodian_list',
        'archive:project_list',
        'archive:source_list',
        'archive:heading_list',
        'archive:anagraphic_list',
        'archive:institution_list',
        'archive:document_form_list',
        'archive:editor_list',
        'archive:classification_list',
        'archive:digital_object_list',
        'archive:tree_data_root',
        'archive:import_aef',
        'archive:export_aef',
        'archive:export_units_csv',
        'archive:advanced_search',
        'archive:report_index',
        'archive:quality_check_index',
        'archive:login',
        'archive:logout',
        'archive:password_change',
    ]

    for url_name in url_names:
        def make_test(name):
            def _():
                resolve(reverse(name))
            return _
        test(f"URL: {url_name}", make_test(url_name))
