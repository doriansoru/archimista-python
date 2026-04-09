from django.urls import path
from . import views

app_name = 'archive'

urlpatterns = [
    # Auth routes
    path('login/', views.ArchimistaLoginView.as_view(), name='login'),
    path('logout/', views.archimista_logout, name='logout'),
    path('password-change/', views.password_change_view, name='password_change'),

    path('', views.FondListView.as_view(), name='fond_list'),
    path('fonds/new/', views.FondCreateView.as_view(), name='fond_create'),
    path('fonds/<int:pk>/', views.FondDetailView.as_view(), name='fond_detail'),
    path('fonds/<int:pk>/edit/', views.FondUpdateView.as_view(), name='fond_update'),
    path('fonds/<int:pk>/delete/', views.FondDeleteView.as_view(), name='fond_delete'),

    path('units/', views.UnitListView.as_view(), name='unit_list'),
    path('units/new/', views.UnitCreateView.as_view(), name='unit_create'),
    path('units/<int:pk>/', views.UnitDetailView.as_view(), name='unit_detail'),
    path('units/<int:pk>/edit/', views.UnitUpdateView.as_view(), name='unit_update'),
    path('units/<int:pk>/delete/', views.UnitDeleteView.as_view(), name='unit_delete'),
    path('units/<int:pk>/move/', views.unit_move, name='unit_move'),
    path('units/<int:pk>/move_up/', views.unit_move_up, name='unit_move_up'),
    path('units/<int:pk>/move_down/', views.unit_move_down, name='unit_move_down'),
    path('units/classify/', views.units_classify, name='units_classify'),
    
    # Creator URLs
    path('creators/', views.CreatorListView.as_view(), name='creator_list'),
    path('creators/new/', views.CreatorCreateView.as_view(), name='creator_create'),
    path('creators/<int:pk>/', views.CreatorDetailView.as_view(), name='creator_detail'),
    path('creators/<int:pk>/edit/', views.CreatorUpdateView.as_view(), name='creator_update'),
    path('creators/<int:pk>/delete/', views.CreatorDeleteView.as_view(), name='creator_delete'),
    
    # Custodian URLs
    path('custodians/', views.CustodianListView.as_view(), name='custodian_list'),
    path('custodians/new/', views.CustodianCreateView.as_view(), name='custodian_create'),
    path('custodians/<int:pk>/', views.CustodianDetailView.as_view(), name='custodian_detail'),
    path('custodians/<int:pk>/edit/', views.CustodianUpdateView.as_view(), name='custodian_update'),
    path('custodians/<int:pk>/delete/', views.CustodianDeleteView.as_view(), name='custodian_delete'),
    
    # Tree & Search
    path('tree/', views.archive_tree_view, name='archive_tree'),
    path('api/tree/', views.tree_data, name='tree_data_root'),
    path('api/tree/<str:node_id>/', views.tree_children, name='tree_data_children'),
    path('api/tree-fonds/<str:node_id>/', views.tree_children_fonds_only, name='tree_data_children_fonds_only'),
    # Tree manipulation API
    path('api/tree/node/create/', views.tree_create_node, name='tree_create_node'),
    path('api/tree/node/<int:fond_id>/rename/', views.tree_rename_node, name='tree_rename_node'),
    path('api/tree/node/<int:fond_id>/move/', views.tree_move_node, name='tree_move_node'),
    path('api/tree/node/<int:fond_id>/trash/', views.tree_move_to_trash, name='tree_move_to_trash'),
    path('api/tree/node/<int:fond_id>/restore/', views.tree_restore_subtree, name='tree_restore_subtree'),
    path('tree/<int:root_id>/trash/', views.tree_trash_view, name='tree_trash'),
    path('api/tree/<int:root_id>/trashed/', views.tree_trashed_children, name='tree_trashed_children'),
    path('search/', views.GlobalSearchView.as_view(), name='search'),
    
    # Export/Import
    path('fonds/<int:pk>/export/pdf/', views.ExportFondPDFView.as_view(), name='fond_export_pdf'),
    path('fonds/<int:pk>/export/rtf/', views.ExportFondRTFView.as_view(), name='fond_export_rtf'),
    path('fonds/<int:pk>/export/aef/', views.ExportFondAEFView.as_view(), name='fond_export_aef'),
    path('import/aef/', views.ImportAEFView.as_view(), name='import_aef'),

    # Export AEF batch
    path('export/aef/', views.ExportAEFView.as_view(), name='export_aef'),
    path('export/units/aef/', views.ExportUnitsAEFView.as_view(), name='export_units_aef'),

    # Export CSV
    path('export/units/csv/', views.ExportUnitsCSVView.as_view(), name='export_units_csv'),

    # Ricerca avanzata
    path('search/advanced/', views.AdvancedSearchView.as_view(), name='advanced_search'),

    # Report
    path('reports/', views.ReportIndexView.as_view(), name='report_index'),
    path('reports/fond/<int:pk>/', views.InventoryReportView.as_view(), name='report_inventory'),
    path('reports/project/<int:pk>/', views.ProjectReportView.as_view(), name='report_project'),
    path('reports/custodian/<int:pk>/', views.CustodianReportView.as_view(), name='report_custodian'),

    # Entity URLs (Schede di servizio)
    path('sources/', views.SourceListView.as_view(), name='source_list'),
    path('sources/new/', views.SourceCreateView.as_view(), name='source_create'),
    path('sources/<int:pk>/', views.SourceDetailView.as_view(), name='source_detail'),
    path('sources/<int:pk>/edit/', views.SourceUpdateView.as_view(), name='source_edit'),
    path('sources/<int:pk>/delete/', views.SourceDeleteView.as_view(), name='source_delete'),

    path('institutions/', views.InstitutionListView.as_view(), name='institution_list'),
    path('institutions/new/', views.InstitutionCreateView.as_view(), name='institution_create'),
    path('institutions/<int:pk>/', views.InstitutionDetailView.as_view(), name='institution_detail'),
    path('institutions/<int:pk>/edit/', views.InstitutionUpdateView.as_view(), name='institution_edit'),
    path('institutions/<int:pk>/delete/', views.InstitutionDeleteView.as_view(), name='institution_delete'),

    path('document-forms/', views.DocumentFormListView.as_view(), name='document_form_list'),
    path('document-forms/new/', views.DocumentFormCreateView.as_view(), name='document_form_create'),
    path('document-forms/<int:pk>/', views.DocumentFormDetailView.as_view(), name='document_form_detail'),
    path('document-forms/<int:pk>/edit/', views.DocumentFormUpdateView.as_view(), name='document_form_edit'),
    path('document-forms/<int:pk>/delete/', views.DocumentFormDeleteView.as_view(), name='document_form_delete'),

    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),

    path('editors/', views.EditorListView.as_view(), name='editor_list'),
    path('editors/<int:pk>/', views.EditorDetailView.as_view(), name='editor_detail'),

    path('digital-objects/', views.DigitalObjectListView.as_view(), name='digital_object_list'),
    path('digital-objects/<int:pk>/', views.DigitalObjectDetailView.as_view(), name='digital_object_detail'),

    path('headings/', views.HeadingListView.as_view(), name='heading_list'),
    path('headings/new/', views.HeadingCreateView.as_view(), name='heading_create'),
    path('headings/<int:pk>/', views.HeadingDetailView.as_view(), name='heading_detail'),
    path('headings/<int:pk>/edit/', views.HeadingUpdateView.as_view(), name='heading_edit'),
    path('headings/<int:pk>/delete/', views.HeadingDeleteView.as_view(), name='heading_delete'),

    path('anagraphics/', views.AnagraphicListView.as_view(), name='anagraphic_list'),
    path('anagraphics/new/', views.AnagraphicCreateView.as_view(), name='anagraphic_create'),
    path('anagraphics/<int:pk>/', views.AnagraphicDetailView.as_view(), name='anagraphic_detail'),
    path('anagraphics/<int:pk>/edit/', views.AnagraphicUpdateView.as_view(), name='anagraphic_edit'),
    path('anagraphics/<int:pk>/delete/', views.AnagraphicDeleteView.as_view(), name='anagraphic_delete'),

    # Compilatori (Editor)
    path('editors/', views.EditorListView.as_view(), name='editor_list'),
    path('editors/new/', views.EditorCreateView.as_view(), name='editor_create'),
    path('editors/<int:pk>/', views.EditorDetailView.as_view(), name='editor_detail'),
    path('editors/<int:pk>/edit/', views.EditorUpdateView.as_view(), name='editor_edit'),
    path('editors/<int:pk>/delete/', views.EditorDeleteView.as_view(), name='editor_delete'),

    # Oggetti digitali (lista globale)
    path('digital-objects/', views.DigitalObjectListView.as_view(), name='digital_object_list'),
    path('digital-objects/new/', views.DigitalObjectCreateView.as_view(), name='digital_object_create'),
    path('digital-objects/<int:pk>/', views.DigitalObjectDetailView.as_view(), name='digital_object_detail'),
    path('digital-objects/<int:pk>/edit/', views.DigitalObjectUpdateView.as_view(), name='digital_object_edit'),
    path('digital-objects/<int:pk>/delete/', views.DigitalObjectDeleteView.as_view(), name='digital_object_delete'),

    # Oggetti digitali nested (per entità)
    path('fonds/<int:fond_id>/digital-objects/', views.DigitalObjectListView.as_view(), name='fond_digital_object_list'),
    path('fonds/<int:fond_id>/digital-objects/new/', views.DigitalObjectCreateView.as_view(), name='fond_digital_object_create'),
    path('fonds/<int:fond_id>/digital-objects/<int:pk>/edit/', views.DigitalObjectUpdateView.as_view(), name='fond_digital_object_edit'),
    path('fonds/<int:fond_id>/digital-objects/<int:pk>/delete/', views.DigitalObjectDeleteView.as_view(), name='fond_digital_object_delete'),

    path('units/<int:unit_id>/digital-objects/', views.DigitalObjectListView.as_view(), name='unit_digital_object_list'),
    path('units/<int:unit_id>/digital-objects/new/', views.DigitalObjectCreateView.as_view(), name='unit_digital_object_create'),
    path('units/<int:unit_id>/digital-objects/<int:pk>/edit/', views.DigitalObjectUpdateView.as_view(), name='unit_digital_object_edit'),
    path('units/<int:unit_id>/digital-objects/<int:pk>/delete/', views.DigitalObjectDeleteView.as_view(), name='unit_digital_object_delete'),

    path('creators/<int:creator_id>/digital-objects/', views.DigitalObjectListView.as_view(), name='creator_digital_object_list'),
    path('creators/<int:creator_id>/digital-objects/new/', views.DigitalObjectCreateView.as_view(), name='creator_digital_object_create'),
    path('creators/<int:creator_id>/digital-objects/<int:pk>/edit/', views.DigitalObjectUpdateView.as_view(), name='creator_digital_object_edit'),
    path('creators/<int:creator_id>/digital-objects/<int:pk>/delete/', views.DigitalObjectDeleteView.as_view(), name='creator_digital_object_delete'),

    path('custodians/<int:custodian_id>/digital-objects/', views.DigitalObjectListView.as_view(), name='custodian_digital_object_list'),
    path('custodians/<int:custodian_id>/digital-objects/new/', views.DigitalObjectCreateView.as_view(), name='custodian_digital_object_create'),
    path('custodians/<int:custodian_id>/digital-objects/<int:pk>/edit/', views.DigitalObjectUpdateView.as_view(), name='custodian_digital_object_edit'),
    path('custodians/<int:custodian_id>/digital-objects/<int:pk>/delete/', views.DigitalObjectDeleteView.as_view(), name='custodian_digital_object_delete'),

    path('sources/<int:source_id>/digital-objects/', views.DigitalObjectListView.as_view(), name='source_digital_object_list'),
    path('sources/<int:source_id>/digital-objects/new/', views.DigitalObjectCreateView.as_view(), name='source_digital_object_create'),
    path('sources/<int:source_id>/digital-objects/<int:pk>/edit/', views.DigitalObjectUpdateView.as_view(), name='source_digital_object_edit'),
    path('sources/<int:source_id>/digital-objects/<int:pk>/delete/', views.DigitalObjectDeleteView.as_view(), name='source_digital_object_delete'),

    # Titolario di classificazione
    path('classifications/', views.ClassificationListView.as_view(), name='classification_list'),
    path('classifications/new/', views.ClassificationCreateView.as_view(), name='classification_create'),
    path('classifications/<int:pk>/', views.ClassificationDetailView.as_view(), name='classification_detail'),
    path('classifications/<int:pk>/edit/', views.ClassificationUpdateView.as_view(), name='classification_update'),
    path('classifications/<int:pk>/delete/', views.ClassificationDeleteView.as_view(), name='classification_delete'),
    path('classifications/<int:pk>/units/', views.ClassificationUnitsView.as_view(), name='classification_units'),
    path('api/classification/<int:pk>/tree/', views.ClassificationTreeDataView.as_view(), name='classification_tree_data'),

    # Controllo qualità
    path('quality-checks/', views.QualityCheckIndexView.as_view(), name='quality_check_index'),
    path('quality-checks/fond/<int:pk>/', views.QualityCheckFondView.as_view(), name='quality_check_fond'),
    path('quality-checks/creator/<int:pk>/', views.QualityCheckCreatorView.as_view(), name='quality_check_creator'),
    path('quality-checks/custodian/<int:pk>/', views.QualityCheckCustodianView.as_view(), name='quality_check_custodian'),
]
