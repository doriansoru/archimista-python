from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Group(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'groups'

    def __str__(self):
        return self.name


class Fond(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    ancestry = models.CharField(max_length=255, null=True, blank=True)
    ancestry_depth = models.IntegerField(null=True, blank=True)
    position = models.IntegerField(default=0)
    sequence_number = models.IntegerField(null=True, blank=True)
    trashed = models.BooleanField(default=False)
    trashed_ancestor_id = models.IntegerField(null=True, blank=True)
    units_count = models.IntegerField(default=0)

    name = models.TextField(null=True, blank=True)
    # Campi a scelta con vocabolari controllati (foreign key verso Term)
    fond_type_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='fonds_by_fond_type', db_column='fond_type_term_id')
    access_condition_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='fonds_by_access_condition', db_column='access_condition_term_id')
    use_condition_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='fonds_by_use_condition', db_column='use_condition_term_id')
    preservation_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='fonds_by_preservation', db_column='preservation_term_id')
    description_type_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='fonds_by_description_type', db_column='description_type_term_id')
    # Campi testo originali (mantenuti per retrocompatibilità e fallback)
    fond_type = models.CharField(max_length=255, null=True, blank=True)
    length = models.FloatField(null=True, blank=True)
    extent = models.TextField(null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    history = models.TextField(null=True, blank=True)
    arrangement_note = models.TextField(null=True, blank=True)
    related_materials = models.TextField(null=True, blank=True)

    access_condition = models.TextField(null=True, blank=True)
    access_condition_note = models.TextField(null=True, blank=True)
    use_condition = models.CharField(max_length=255, null=True, blank=True)
    use_condition_note = models.TextField(null=True, blank=True)
    type_materials = models.CharField(max_length=255, null=True, blank=True)
    preservation = models.CharField(max_length=255, null=True, blank=True)
    preservation_note = models.TextField(null=True, blank=True)
    description_type = models.CharField(max_length=255, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    created_by = models.IntegerField(default=1)
    updated_by = models.IntegerField(default=1)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, db_column='group_id')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)
    legacy_parent_id = models.CharField(max_length=255, null=True, blank=True)

    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relazioni per modelli aggiuntivi
    fond_names = GenericRelation('FondName', related_query_name='fond') if False else None  # Usiamo ForeignKey diretta
    events = GenericRelation('Event', related_query_name='fond')
    biog_hists = GenericRelation('BiogHist', related_query_name='fond')
    digital_objects = GenericRelation('DigitalObject', related_query_name='fond')

    @property
    def preferred_event(self):
        """Restituisce l'evento preferito (datazione principale) del fondo."""
        return self.events.filter(preferred=True).first()

    @property
    def active_descendant_units_count(self):
        """Conta le unità attive nel sottoalbero di questo fondo."""
        from archimista_python.archive.models.core import Unit
        ids = self.subtree_ids
        return Unit.objects.filter(fond_id__in=ids).count()

    # Convenience properties per relazioni through tabelle di join
    @property
    def creators(self):
        from archimista_python.archive.models.relations import RelCreatorFond
        return Creator.objects.filter(
            pk__in=RelCreatorFond.objects.filter(fond=self).values_list('creator_id', flat=True)
        )

    @property
    def custodians(self):
        from archimista_python.archive.models.relations import RelCustodianFond
        return Custodian.objects.filter(
            pk__in=RelCustodianFond.objects.filter(fond=self).values_list('custodian_id', flat=True)
        )

    @property
    def projects(self):
        from archimista_python.archive.models.relations import RelProjectFond
        from archimista_python.archive.models.system import Project
        return Project.objects.filter(
            pk__in=RelProjectFond.objects.filter(fond=self).values_list('project_id', flat=True)
        )

    @property
    def sources(self):
        from archimista_python.archive.models.relations import RelFondSource
        from archimista_python.archive.models.system import Source
        return Source.objects.filter(
            pk__in=RelFondSource.objects.filter(fond=self).values_list('source_id', flat=True)
        )

    @property
    def document_forms(self):
        from archimista_python.archive.models.relations import RelFondDocumentForm
        from archimista_python.archive.models.system import DocumentForm
        return DocumentForm.objects.filter(
            pk__in=RelFondDocumentForm.objects.filter(fond=self).values_list('document_form_id', flat=True)
        )

    @property
    def other_names(self):
        """Alias per fond_names (compatibilità con Ruby other_names)."""
        return self.fond_names.all()

    class Meta:
        db_table = 'fonds'
        indexes = [
            models.Index(fields=['ancestry']),
            models.Index(fields=['db_source', 'legacy_id']),
        ]

    def __str__(self):
        return str(self.name)

    @property
    def root(self):
        """Restituisce il nodo root dell'albero a cui appartiene questo fondo."""
        if self.parent is None:
            return self
        if self.ancestry:
            root_id = self.ancestry.split('/')[0]
            return Fond.objects.get(pk=root_id)
        # Fallback: risale ricorsivamente
        node = self
        while node.parent:
            node = node.parent
        return node

    @property
    def is_root(self):
        """True se questo fondo è un nodo root (non ha genitore)."""
        return self.parent is None

    @property
    def descendants(self):
        """Restituisce tutti i discendenti di questo fondo (ricorsivo)."""
        def _get_descendants(fond, seen=None):
            if seen is None:
                seen = set()
            children = Fond.objects.filter(parent_id=fond.id)
            for child in children:
                if child.id not in seen:
                    seen.add(child.id)
                    _get_descendants(child, seen)
            return Fond.objects.filter(id__in=seen)
        return _get_descendants(self)

    @property
    def subtree_ids(self):
        """Restituisce gli ID di tutti i nodi nel sottoalbero (incluso se stesso)."""
        ids = [self.id]
        ids.extend(self.descendants.values_list('id', flat=True))
        return ids

    @property
    def subtree(self):
        """Restituisce tutti i nodi nel sottoalbero (incluso se stesso) come QuerySet."""
        return Fond.objects.filter(id__in=self.subtree_ids)

    @property
    def root(self):
        """Restituisce il nodo radice di questo fondo."""
        if self.parent is None:
            return self
        visited = set()
        current = self
        while current.parent is not None:
            if current.pk in visited:
                break  # Prevent infinite loop on circular refs
            visited.add(current.pk)
            current = current.parent
        return current


class CreatorCorporateType(models.Model):
    corporate_type = models.CharField(max_length=255)

    class Meta:
        db_table = 'creator_corporate_types'

    def __str__(self):
        return self.corporate_type


class Creator(models.Model):
    creator_type = models.CharField(max_length=1, null=True, blank=True)
    creator_corporate_type = models.ForeignKey(CreatorCorporateType, on_delete=models.SET_NULL, null=True, blank=True)
    residence = models.TextField(null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    history = models.TextField(null=True, blank=True)
    legal_status = models.CharField(max_length=255, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    created_by = models.IntegerField(default=1)
    updated_by = models.IntegerField(default=1)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, db_column='group_id')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relazioni per modelli aggiuntivi
    events = GenericRelation('Event', related_query_name='creator')
    biog_hists = GenericRelation('BiogHist', related_query_name='creator')

    @property
    def preferred_event(self):
        """Restituisce l'evento preferito (datazione principale) del creatore."""
        return self.events.filter(preferred=True).first()

    digital_objects = GenericRelation('DigitalObject', related_query_name='creator')

    @property
    def preferred_name(self):
        """Returns the preferred name record for this creator."""
        return self.creator_names.filter(preferred=True).first()

    @property
    def sources(self):
        from archimista_python.archive.models.relations import RelCreatorSource
        from archimista_python.archive.models.system import Source
        return Source.objects.filter(
            pk__in=RelCreatorSource.objects.filter(creator=self).values_list('source_id', flat=True)
        )

    @property
    def fonds(self):
        from archimista_python.archive.models.relations import RelCreatorFond
        return Fond.objects.filter(
            pk__in=RelCreatorFond.objects.filter(creator=self).values_list('fond_id', flat=True)
        )

    @property
    def institutions(self):
        from archimista_python.archive.models.relations import RelCreatorInstitution
        from archimista_python.archive.models.system import Institution
        return Institution.objects.filter(
            pk__in=RelCreatorInstitution.objects.filter(creator=self).values_list('institution_id', flat=True)
        )

    @property
    def other_names(self):
        """Returns non-preferred name records."""
        return self.creator_names.filter(preferred=False)

    class Meta:
        db_table = 'creators'
        indexes = [
            models.Index(fields=['db_source', 'legacy_id']),
        ]

    def __str__(self):
        return f'Creator {self.legacy_id}'


class CustodianType(models.Model):
    custodian_type = models.CharField(max_length=255)

    class Meta:
        db_table = 'custodian_types'

    def __str__(self):
        return self.custodian_type


class Custodian(models.Model):
    custodian_type = models.ForeignKey(CustodianType, on_delete=models.SET_NULL, null=True, blank=True)
    legal_status = models.CharField(max_length=2, null=True, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    history = models.TextField(null=True, blank=True)
    administrative_structure = models.TextField(null=True, blank=True)
    collecting_policies = models.TextField(null=True, blank=True)
    holdings = models.TextField(null=True, blank=True)
    accessibility = models.TextField(null=True, blank=True)
    services = models.TextField(null=True, blank=True)

    created_by = models.IntegerField(default=1)
    updated_by = models.IntegerField(default=1)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, db_column='group_id')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relazioni per modelli aggiuntivi
    events = GenericRelation('Event', related_query_name='custodian')
    biog_hists = GenericRelation('BiogHist', related_query_name='custodian')
    digital_objects = GenericRelation('DigitalObject', related_query_name='custodian')

    @property
    def preferred_event(self):
        """Restituisce l'evento preferito (datazione principale) del conservatore."""
        return self.events.filter(preferred=True).first()

    # Many-to-many relations through join tables
    @property
    def fonds(self):
        from archimista_python.archive.models.relations import RelCustodianFond
        return Fond.objects.filter(
            pk__in=RelCustodianFond.objects.filter(custodian=self).values_list('fond_id', flat=True)
        ).order_by('name')

    @property
    def sources(self):
        from archimista_python.archive.models.relations import RelCustodianSource
        from archimista_python.archive.models.system import Source
        return Source.objects.filter(
            pk__in=RelCustodianSource.objects.filter(custodian=self).values_list('source_id', flat=True)
        )

    @property
    def preferred_name(self):
        """Returns the preferred name record for this custodian."""
        return self.custodian_names.filter(preferred=True).first()

    @property
    def other_names(self):
        """Returns non-preferred name records."""
        return self.custodian_names.filter(preferred=False)

    @property
    def display_name(self):
        """Returns the preferred name for display."""
        pn = self.preferred_name
        return pn.name if pn else ''

    class Meta:
        db_table = 'custodians'
        indexes = [
            models.Index(fields=['db_source', 'legacy_id']),
        ]

    def __str__(self):
        return f'Custodian {self.legacy_id}'


class Classification(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, db_column='group_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'classifications'
        verbose_name_plural = 'classifications'

    def __str__(self):
        if self.code:
            return f"{self.code} - {self.name}"
        return self.name

    @property
    def is_root(self):
        """True se questa classificazione è un nodo root (non ha genitore)."""
        return self.parent is None


class Unit(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    fond = models.ForeignKey(Fond, on_delete=models.CASCADE, related_name='units', null=True, blank=True)
    root_fond = models.ForeignKey(Fond, on_delete=models.CASCADE, related_name='root_units', null=True, blank=True)
    classification = models.ForeignKey(Classification, on_delete=models.SET_NULL, null=True, blank=True, related_name='units')
    position = models.IntegerField(default=0)
    sequence_number = models.IntegerField(null=True, blank=True)
    ancestry = models.CharField(max_length=255, null=True, blank=True)
    ancestry_depth = models.IntegerField(null=True, blank=True)
    tsk = models.CharField(max_length=5, null=True, blank=True)
    reference_number = models.TextField(null=True, blank=True)
    tmp_reference_number = models.IntegerField(null=True, blank=True)
    tmp_reference_string = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    given_title = models.BooleanField(null=True, blank=True)
    folder_number = models.IntegerField(null=True, blank=True)
    file_number = models.IntegerField(null=True, blank=True)
    sort_letter = models.CharField(max_length=255, null=True, blank=True)
    sort_number = models.IntegerField(null=True, blank=True)
    # Campi a scelta con vocabolari controllati (foreign key verso Term)
    unit_type_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='units_by_unit_type', db_column='unit_type_term_id')
    access_condition_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='units_by_access_condition', db_column='access_condition_term_id')
    use_condition_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='units_by_use_condition', db_column='use_condition_term_id')
    preservation_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='units_by_preservation', db_column='preservation_term_id')
    physical_type_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='units_by_physical_type', db_column='physical_type_term_id')
    medium_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='units_by_medium', db_column='medium_term_id')
    # Campi testo originali (mantenuti per retrocompatibilità e fallback)
    unit_type = models.CharField(max_length=255, null=True, blank=True)
    medium = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    arrangement_note = models.TextField(null=True, blank=True)
    related_materials = models.TextField(null=True, blank=True)
    physical_type = models.CharField(max_length=255, null=True, blank=True)
    physical_description = models.TextField(null=True, blank=True)
    physical_container_type = models.TextField(null=True, blank=True)
    physical_container_title = models.TextField(null=True, blank=True)
    physical_container_number = models.TextField(null=True, blank=True)
    preservation = models.CharField(max_length=255, null=True, blank=True)
    preservation_note = models.TextField(null=True, blank=True)
    restoration = models.TextField(null=True, blank=True)
    access_condition = models.CharField(max_length=255, null=True, blank=True)
    access_condition_note = models.TextField(null=True, blank=True)
    use_condition = models.CharField(max_length=255, null=True, blank=True)
    use_condition_note = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)
    legacy_position = models.IntegerField(null=True, blank=True)
    legacy_sequence_number = models.CharField(max_length=255, null=True, blank=True)
    legacy_parent_unit_id = models.CharField(max_length=255, null=True, blank=True)
    legacy_parent_fond_id = models.CharField(max_length=255, null=True, blank=True)
    legacy_root_fond_id = models.CharField(max_length=255, null=True, blank=True)
    sc2_tsk = models.CharField(max_length=10, null=True, blank=True)
    extent = models.TextField(null=True, blank=True)
    published = models.BooleanField(default=True)
    file_type = models.CharField(max_length=255, null=True, blank=True)
    fsc_name = models.TextField(null=True, blank=True)
    fsc_surname = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def display_sequence_numbers_of(root_fond, index=0):
        """Restituisce un dict {unit_id: display_sequence_number} per tutte le unità del fondo.
        Porting semplificato di Unit.display_sequence_numbers_of da Ruby.
        """
        result = {}
        units = Unit.objects.filter(fond_id=root_fond.pk).order_by('sequence_number')
        for u in units:
            index += 1
            result[u.pk] = index
        return result

    def display_sequence_number_from_hash(self, display_sequence_numbers):
        """Restituisce il numero di sequenza visualizzabile dall'hash."""
        if display_sequence_numbers:
            return display_sequence_numbers.get(self.pk, self.sequence_number or '')
        return self.sequence_number or ''

    class Meta:
        db_table = 'units'

    def __str__(self):
        return str(self.title)

    # =========================================================================
    # Movibilità unità (porting da Ruby unit.rb)
    # Ruby: MAX_LEVEL_OF_NODES = 2 (3 livelli: 0, 1, 2)
    # =========================================================================
    MAX_LEVEL_OF_NODES = 2

    def is_root_unit(self):
        """True se l'unità non ha genitore (livello 0 nel fondo)."""
        return self.parent is None

    def is_leaf_unit(self):
        """True se l'unità è al livello massimo e non può avere figli."""
        return (self.ancestry_depth or 0) >= self.MAX_LEVEL_OF_NODES

    def has_local_siblings(self):
        """True se l'unità ha fratelli nello stesso fondo."""
        return Unit.objects.filter(
            parent_id=self.parent_id,
            fond_id=self.fond_id
        ).exclude(pk=self.pk).exists()

    def is_movable_up(self):
        """Può essere spostata su (promossa al livello del genitore)."""
        return not self.is_root_unit()

    def is_movable_down(self):
        """Può essere spostata giù (demotta sotto un fratello).
        Deve: non essere leaf, avere fratelli, e non avere discendenti al livello max.
        """
        if self.is_leaf_unit():
            return False
        if not self.has_local_siblings():
            return False
        # Controlla se ha discendenti al livello massimo
        descendants_at_max = self._get_descendants().filter(
            ancestry_depth=self.MAX_LEVEL_OF_NODES
        ).exists()
        return not descendants_at_max

    def is_not_movable(self):
        """Non può essere spostata né su né giù."""
        return not self.is_movable_up() and not self.is_movable_down()

    def full_path(self):
        """Restituisce il percorso completo dall'unità root a questa unità (lista di titoli)."""
        path = [self]
        current = self
        visited = set()
        while current.parent is not None:
            if current.pk in visited:
                break
            visited.add(current.pk)
            current = current.parent
            path.append(current)
        path.reverse()
        return path

    def _get_descendants(self):
        """Restituisce tutti i discendenti (ricorsivo)."""
        descendants = []
        children = self.children.all()
        for child in children:
            descendants.append(child)
            descendants.extend(child._get_descendants())
        return Unit.objects.filter(pk__in=[d.pk for d in descendants]) if descendants else Unit.objects.none()


class Heading(models.Model):
    heading_type = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    dates = models.CharField(max_length=255, null=True, blank=True)
    qualifier = models.TextField(null=True, blank=True)

    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, default=1, db_column='group_id')
    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'headings'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['db_source', 'legacy_id']),
        ]

    def __str__(self):
        return self.name


class DigitalObject(models.Model):
    # Generic Foreign Key per collegarsi a qualsiasi modello
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    attachable = GenericForeignKey('content_type', 'object_id')

    # Per compatibilità con schema esistente
    attachable_type = models.CharField(max_length=255, null=True, blank=True)
    attachable_id = models.IntegerField(null=True, blank=True)

    position = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)

    # File upload (allineato a Ruby Paperclip)
    asset = models.FileField(upload_to='digital_objects/%Y/%m/%d/', null=True, blank=True)

    # Paperclip fields (popolati automaticamente dall'upload)
    asset_file_name = models.CharField(max_length=255, null=True, blank=True)
    asset_content_type = models.CharField(max_length=255, null=True, blank=True)
    asset_file_size = models.IntegerField(null=True, blank=True)
    asset_updated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.IntegerField(null=True, blank=True)
    updated_by = models.IntegerField(null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, db_column='group_id')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)
    published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'digital_objects'

    def __str__(self):
        return self.title or f'Digital Object {self.id}'

    def save(self, *args, **kwargs):
        """Popola i metadati del file e genera access_token se necessario."""
        if self.asset and not self.asset_file_name:
            self.asset_file_name = self.asset.name.split('/')[-1]
            self.asset_content_type = self.asset.file.content_type if hasattr(self.asset.file, 'content_type') else ''
            self.asset_file_size = self.asset.size
            self.asset_updated_at = self.updated_at or self.created_at

        if not self.access_token:
            import hashlib
            import time
            name = self.asset_file_name or str(self.pk or '')
            self.access_token = hashlib.sha1(f"{name}{time.time()}".encode()).hexdigest()[:16]

        super().save(*args, **kwargs)

    def is_image(self):
        """Verifica se il file è un'immagine JPEG (come Ruby)."""
        if not self.asset_content_type:
            return False
        return self.asset_content_type in [
            'image/jpeg', 'image/jpg', 'image/pjpeg', 'image/png', 'image/webp', 'image/gif'
        ]

    def is_video(self):
        """Verifica se il file è un video MP4 (come Ruby)."""
        if not self.asset_content_type:
            return False
        return self.asset_content_type in [
            'video/mp4', 'application/mp4', 'video/mpeg4', 'video/webm'
        ]

    def is_pdf(self):
        """Verifica se il file è un PDF."""
        if not self.asset_content_type:
            return False
        return self.asset_content_type == 'application/pdf'

    def get_thumbnail_url(self):
        """Restituisce URL della thumbnail (generata on-demand per immagini)."""
        if not self.asset:
            return None
        if self.is_image():
            return f'/media/thumbnails/{self.access_token}_thumb.jpg'
        elif self.is_pdf():
            return '/static/images/pdf-medium.png'
        elif self.is_video():
            return '/static/images/mp4-medium.png'
        return None

    def get_medium_url(self):
        """Restituisce URL dell'immagine medium."""
        if not self.asset:
            return None
        if self.is_image():
            return f'/media/thumbnails/{self.access_token}_medium.jpg'
        elif self.is_pdf():
            return '/static/images/pdf-medium.png'
        elif self.is_video():
            return '/static/images/mp4-medium.png'
        return None

    def get_large_url(self):
        """Restituisce URL dell'immagine large."""
        if not self.asset:
            return None
        if self.is_image():
            return f'/media/thumbnails/{self.access_token}_large.jpg'
        return self.asset.url

    def generate_thumbnails(self):
        """Genera thumbnail per immagini usando Pillow (come Paperclip)."""
        if not self.asset or not self.is_image():
            return
        try:
            from PIL import Image
            from django.conf import settings
            import os

            img = Image.open(self.asset.path)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            thumb_dir = settings.MEDIA_ROOT / 'thumbnails'
            os.makedirs(thumb_dir, exist_ok=True)

            # Stili allineati a Ruby Paperclip
            sizes = {
                'thumb': (130, 130),
                'medium': (210, 210),
                'large': (1280, 1280),
            }
            for style, (max_w, max_h) in sizes.items():
                thumb = img.copy()
                thumb.thumbnail((max_w, max_h), Image.LANCZOS)
                thumb_path = thumb_dir / f'{self.access_token}_{style}.jpg'
                thumb.save(thumb_path, 'JPEG', quality=85)
        except Exception:
            pass  # Silenzioso come Ruby's rescue
