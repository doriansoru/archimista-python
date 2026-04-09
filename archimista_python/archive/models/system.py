from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Institution(models.Model):
    identifier = models.CharField(max_length=255, null=True, blank=True)
    identifier_source = models.CharField(max_length=255, null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    created_by = models.IntegerField(default=1)
    updated_by = models.IntegerField(default=1)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, db_column='group_id')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'institutions'

    def __str__(self):
        return str(self.name)


class InstitutionEditor(models.Model):
    """Compilatore per istituzione (da Ruby institution_editors)."""
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE, related_name='institution_editors')
    name = models.CharField(max_length=255, null=True, blank=True)
    qualifier = models.CharField(max_length=255, null=True, blank=True)
    editing_type = models.CharField(max_length=255, null=True, blank=True)
    edited_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'institution_editors'
        ordering = ['edited_at']

    def __str__(self):
        return f"{self.name} - {self.institution.name}" if self.name else str(self.institution)


class SourceType(models.Model):
    """Tipologia di fonte (da Ruby source_types).
    Gerarchica: parent_code=None = root, altrimenti sottotipo."""
    code = models.IntegerField(primary_key=True)
    source_type = models.CharField(max_length=255)
    parent_code = models.IntegerField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'source_types'
        ordering = ['position']

    def __str__(self):
        return self.source_type


class Source(models.Model):
    use_legacy = models.BooleanField(default=False)
    source_type_code = models.IntegerField(null=True, blank=True)
    source_subtype_code = models.IntegerField(null=True, blank=True)

    short_title = models.TextField(null=True, blank=True)
    author = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    editor = models.TextField(null=True, blank=True)
    publisher = models.TextField(null=True, blank=True)
    place = models.TextField(null=True, blank=True)
    year = models.IntegerField(default=0)

    # Campi aggiuntivi da Ruby (mancanti nel port Python)
    date_string = models.TextField(null=True, blank=True, verbose_name="Data")
    finding_aid_valid = models.BooleanField(null=True, blank=True, verbose_name="Strumento di corredo valido")
    finding_aid_published = models.BooleanField(null=True, blank=True, verbose_name="Strumento di corredo pubblicato")
    related_item = models.TextField(null=True, blank=True, verbose_name="Titolo libro correlato/rivista")
    related_item_specs = models.TextField(null=True, blank=True, verbose_name="Specifiche elemento correlato")
    abstract = models.TextField(null=True, blank=True, verbose_name="Abstract")

    # Campi legacy (da Ruby, commentati ma presenti nel DB)
    institution = models.TextField(null=True, blank=True)
    volume = models.TextField(null=True, blank=True)
    pages = models.TextField(null=True, blank=True)
    book_title = models.TextField(null=True, blank=True)
    legacy_description = models.TextField(null=True, blank=True)

    created_by = models.IntegerField(default=1)
    updated_by = models.IntegerField(default=1)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, db_column='group_id')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sources'

    def __str__(self):
        return str(self.short_title or self.title)

    def formatted_source(self):
        """Formatta la fonte come: Autore, _Titolo_, Luogo, Editore, Data"""
        parts = []
        if self.author:
            parts.append(self.author)
        if self.title:
            parts.append(f"<em>{self.title}</em>")
        if self.place:
            parts.append(self.place)
        if self.publisher:
            parts.append(self.publisher)
        if self.date_string:
            parts.append(self.date_string)
        return ", ".join(parts) if parts else str(self.title or "Fonte")


class SourceUrl(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='source_urls')
    url = models.CharField(max_length=500)
    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'source_urls'
        ordering = ['id']

    def __str__(self):
        return self.url


class BiogHist(models.Model):
    # Relazione polimorfica (GenericForeignKey)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    body = models.TextField(null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'biog_hists'
        verbose_name = 'Biographical/Administrative History'
        verbose_name_plural = 'Biographical/Administrative Histories'

    def __str__(self):
        return self.body[:50] if self.body else 'BiogHist'


class Event(models.Model):
    # Relazione polimorfica (GenericForeignKey)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    preferred = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=True)
    event_type = models.CharField(max_length=255, null=True, blank=True)

    # Start Date
    start_date_place = models.TextField(null=True, blank=True)
    start_date_spec = models.CharField(max_length=255, null=True, blank=True)
    start_date_from = models.DateField(null=True, blank=True)
    start_date_to = models.DateField(null=True, blank=True)
    start_date_valid = models.CharField(max_length=255, null=True, blank=True)
    start_date_format = models.CharField(max_length=255, null=True, blank=True)
    start_date_display = models.CharField(max_length=255, null=True, blank=True)

    # End Date
    end_date_place = models.TextField(null=True, blank=True)
    end_date_spec = models.CharField(max_length=255, null=True, blank=True)
    end_date_from = models.DateField(null=True, blank=True)
    end_date_to = models.DateField(null=True, blank=True)
    end_date_valid = models.CharField(max_length=255, null=True, blank=True)
    end_date_format = models.CharField(max_length=255, null=True, blank=True)
    end_date_display = models.CharField(max_length=255, null=True, blank=True)

    legacy_display_date = models.CharField(max_length=255, null=True, blank=True)
    order_date = models.CharField(max_length=255, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'

    def __str__(self):
        return self.start_date_display or "Event"

    @property
    def full_display_date(self):
        """Restituisce la datazione completa come stringa leggibile."""
        if self.start_date_display:
            return self.start_date_display
        parts = []
        if self.start_date_from:
            parts.append(self.start_date_from.strftime('%Y'))
        if self.start_date_to and self.start_date_to != self.start_date_from:
            parts.append(self.start_date_to.strftime('%Y'))
        if self.end_date_display:
            parts.append(self.end_date_display)
        return ' - '.join(parts) if parts else ''

    @property
    def full_display_date_with_place(self):
        """Restituisce la datazione completa con il luogo."""
        result = self.full_display_date
        place = self.start_date_place or ''
        if place:
            result = f"{result} ({place})" if result else place
        return result


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    # Campi allineati a Ruby
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)
    
    # Vocabolari controllati (approccio ibrido term + text)
    status = models.IntegerField(default=0, null=True, blank=True)
    status_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='project_statuses', db_column='status_term_id')
    
    project_type = models.CharField(max_length=255, null=True, blank=True)
    project_type_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='project_types', db_column='project_type_term_id')
    
    note = models.TextField(blank=True, null=True)

    created_by = models.IntegerField(default=1)
    updated_by = models.IntegerField(default=1)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, db_column='group_id')

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


class ProjectUrl(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_urls')
    url = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_urls'
        ordering = ['position']

    def __str__(self):
        return self.url


class ProjectManager(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_managers')
    name = models.CharField(max_length=255)
    qualifier = models.CharField(max_length=255, blank=True, null=True)
    qualifier_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='project_manager_qualifiers', db_column='qualifier_term_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_managers'

    def __str__(self):
        return self.name


class ProjectStakeholder(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_stakeholders')
    name = models.CharField(max_length=255)
    qualifier = models.CharField(max_length=255, blank=True, null=True)
    qualifier_term = models.ForeignKey('Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='project_stakeholder_qualifiers', db_column='qualifier_term_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_stakeholders'

    def __str__(self):
        return self.name


class DocumentForm(models.Model):
    identifier = models.CharField(max_length=255, blank=True, null=True)
    identifier_source = models.CharField(max_length=255, blank=True, null=True)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(default=0)
    note = models.TextField(blank=True, null=True)

    created_by = models.IntegerField(default=1)
    updated_by = models.IntegerField(default=1)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_forms'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


class Anagraphic(models.Model):
    anagraphic_type = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    start_date_place = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date_place = models.CharField(max_length=255, blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'anagraphics'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return f'{self.surname}, {self.name}' if self.name or self.surname else 'Anagrafica'


class Place(models.Model):
    name = models.CharField(max_length=255)
    place_type = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'places'

    def __str__(self):
        return self.name


class Lang(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'langs'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


class Export(models.Model):
    export_type = models.CharField(max_length=50)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    status = models.CharField(max_length=20, default='pending')
    created_by = models.IntegerField(default=1)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exports'

    def __str__(self):
        return f'{self.export_type} - {self.file_name}'


class Import(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    importable = GenericForeignKey('content_type', 'object_id')

    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    status = models.CharField(max_length=20, default='pending')
    deletable = models.BooleanField(default=True)
    created_by = models.IntegerField(default=1)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'imports'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f'{self.content_type} - {self.file_name}'


class Editor(models.Model):
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    created_by = models.IntegerField(default=1)
    updated_by = models.IntegerField(default=1)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'editors'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return f'{self.last_name}, {self.first_name}' if self.first_name or self.last_name else 'Editor'


class Activity(models.Model):
    identifier = models.CharField(max_length=255, blank=True, null=True)
    identifier_source = models.CharField(max_length=255, blank=True, null=True)
    activity_en = models.CharField(max_length=255, blank=True, null=True)
    activity_it = models.CharField(max_length=255, blank=True, null=True)
    parent_id = models.IntegerField(blank=True, null=True)
    native = models.CharField(max_length=1, blank=True, null=True)
    grouping = models.CharField(max_length=1, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'activities'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.activity_it or self.activity_en or 'Attività'


class CreatorAssociationType(models.Model):
    inverse_type = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='inverse_associations')
    association_type = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creator_association_types'

    def __str__(self):
        return self.association_type


class DocumentFormEditor(models.Model):
    document_form = models.ForeignKey(DocumentForm, on_delete=models.CASCADE, related_name='document_form_editors')
    name = models.CharField(max_length=255)
    qualifier = models.CharField(max_length=255, blank=True, null=True)
    editing_type = models.CharField(max_length=255, blank=True, null=True)
    edited_at = models.DateField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_form_editors'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


class AnagIdentifier(models.Model):
    anagraphic = models.ForeignKey(Anagraphic, on_delete=models.CASCADE, related_name='anag_identifiers')
    identifier = models.CharField(max_length=255)
    qualifier = models.CharField(max_length=255, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'anag_identifiers'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.identifier


class EditorLog(models.Model):
    """
    Registro delle modifiche (change history / log compilatori).
    Traccia chi ha modificato cosa e quando.
    """
    ENTITY_CHOICES = [
        ('fond', 'Fondo'),
        ('unit', 'Unità'),
        ('creator', 'Soggetto produttore'),
        ('custodian', 'Soggetto conservatore'),
        ('source', 'Fonte'),
        ('project', 'Progetto'),
        ('heading', 'Voce di indice'),
        ('anagraphic', 'Anagrafica'),
        ('institution', 'Profilo istituzionale'),
        ('document_form', 'Profilo documentario'),
        ('classification', 'Classificazione'),
    ]

    ACTION_CHOICES = [
        ('create', 'Creazione'),
        ('update', 'Modifica'),
        ('delete', 'Eliminazione'),
    ]

    editor = models.ForeignKey('Editor', on_delete=models.SET_NULL, null=True, blank=True, related_name='editor_logs')
    entity_type = models.CharField(max_length=50, choices=ENTITY_CHOICES)
    entity_id = models.IntegerField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='update')
    description = models.TextField(blank=True, null=True, help_text='Descrizione della modifica')
    field_name = models.CharField(max_length=100, blank=True, null=True, help_text='Campo modificato')
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'editor_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['editor']),
        ]

    def __str__(self):
        editor_name = self.editor.name if self.editor else 'Sconosciuto'
        return f"{editor_name} - {self.get_action_display()} {self.get_entity_type_display()} #{self.entity_id}"


class UserProfile(models.Model):
    """Profile for Django User with forced password-change flag."""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='archive_profile')
    must_change_password = models.BooleanField(default=False, help_text='Forza il cambio password al prossimo accesso')

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"Profilo di {self.user.username}"


# Signals per auto-creare il profilo quando si crea un User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='auth.User')
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender='auth.User')
def save_user_profile(sender, instance, **kwargs):
    instance.archive_profile.save()
