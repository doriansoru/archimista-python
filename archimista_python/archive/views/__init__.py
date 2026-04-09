# Archive Views - Archimista Python/Django
# Questo modulo espone tutte le viste per mantenere la compatibilitÃ 
# con gli import esistenti: from archive.views import X

from archimista_python.archive.views.fond import (
    FondListView, FondDetailView, FondCreateView, FondUpdateView, FondDeleteView,
)

from archimista_python.archive.views.unit import (
    UnitCreateView, UnitUpdateView, UnitDetailView, UnitDeleteView,
    units_classify, unit_move, unit_move_up, unit_move_down,
)

from archimista_python.archive.views.unit_list import UnitListView

from archimista_python.archive.views.creator import (
    CreatorListView, CreatorDetailView, CreatorCreateView,
    CreatorUpdateView, CreatorDeleteView,
)

from archimista_python.archive.views.custodian import (
    CustodianListView, CustodianDetailView, CustodianCreateView,
    CustodianUpdateView, CustodianDeleteView,
)

from archimista_python.archive.views.tree import (
    tree_data, tree_children, tree_children_fonds_only, archive_tree_view,
    tree_create_node, tree_rename_node, tree_move_node,
    tree_move_to_trash, tree_restore_subtree,
    tree_trash_view, tree_trashed_children,
)

from archimista_python.archive.views.search import GlobalSearchView

from archimista_python.archive.views.export import ExportFondPDFView, ExportFondRTFView

from archimista_python.archive.views.import_view import ImportAEFView

from archimista_python.archive.views.projects import (
    ProjectListView, ProjectDetailView, ProjectCreateView,
    ProjectUpdateView, ProjectDeleteView,
)

from archimista_python.archive.views.source import (
    SourceListView, SourceDetailView,
    SourceCreateView, SourceUpdateView, SourceDeleteView,
)

from archimista_python.archive.views.institutions import (
    InstitutionListView, InstitutionDetailView,
    InstitutionCreateView, InstitutionUpdateView, InstitutionDeleteView,
)

from archimista_python.archive.views.editors import (
    EditorListView, EditorDetailView,
    EditorCreateView, EditorUpdateView, EditorDeleteView,
)

from archimista_python.archive.views.digital_objects import (
    DigitalObjectListView, DigitalObjectDetailView,
    DigitalObjectCreateView, DigitalObjectUpdateView, DigitalObjectDeleteView,
)

from archimista_python.archive.views.entities import (
    HeadingListView, HeadingDetailView,
    HeadingCreateView, HeadingUpdateView, HeadingDeleteView,
    AnagraphicListView, AnagraphicDetailView,
    AnagraphicCreateView, AnagraphicUpdateView, AnagraphicDeleteView,
)

from archimista_python.archive.views.document_forms import (
    DocumentFormListView, DocumentFormDetailView,
    DocumentFormCreateView, DocumentFormUpdateView, DocumentFormDeleteView,
)

from archimista_python.archive.views.classifications import (
    ClassificationListView, ClassificationDetailView,
    ClassificationCreateView, ClassificationUpdateView, ClassificationDeleteView,
    ClassificationTreeDataView, ClassificationUnitsView,
)

from archimista_python.archive.views.quality_checks import (
    QualityCheckIndexView, QualityCheckFondView,
    QualityCheckCreatorView, QualityCheckCustodianView,
)

from archimista_python.archive.views.export_aef import (
    ExportAEFView, ExportFondAEFView, ExportUnitsAEFView,
)

from archimista_python.archive.views.export_csv import (
    ExportUnitsCSVView,
)

from archimista_python.archive.views.reports import (
    ReportIndexView, InventoryReportView, ProjectReportView, CustodianReportView,
)

from archimista_python.archive.views.advanced_search import (
    AdvancedSearchView,
)

from archimista_python.archive.views.auth import (
    ArchimistaLoginView,
    archimista_logout,
    password_change_view,
)
