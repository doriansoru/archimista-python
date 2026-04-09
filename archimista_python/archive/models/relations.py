from django.db import models


class RelCreatorFond(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='rel_creator_fonds')
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='rel_creator_fonds_fond')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_creator_id = models.CharField(max_length=255, null=True, blank=True)
    legacy_fond_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_creator_fonds'

    def __str__(self):
        return f'{self.creator} - {self.fond}'


class RelCustodianFond(models.Model):
    custodian = models.ForeignKey('Custodian', on_delete=models.CASCADE, related_name='rel_custodian_fonds')
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='rel_custodian_fonds_fond')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_custodian_id = models.CharField(max_length=255, null=True, blank=True)
    legacy_fond_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_custodian_fonds'

    def __str__(self):
        return f'{self.custodian} - {self.fond}'


class RelFondHeading(models.Model):
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='rel_fond_headings')
    heading = models.ForeignKey('Heading', on_delete=models.CASCADE, related_name='rel_fond_headings')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_fond_id = models.CharField(max_length=255, null=True, blank=True)
    legacy_heading_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_fond_headings'

    def __str__(self):
        return f'{self.fond} - {self.heading}'


class RelUnitHeading(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='rel_unit_headings')
    heading = models.ForeignKey('Heading', on_delete=models.CASCADE, related_name='rel_unit_headings')

    db_source = models.CharField(max_length=255, null=True, blank=True)
    legacy_unit_id = models.CharField(max_length=255, null=True, blank=True)
    legacy_heading_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_unit_headings'

    def __str__(self):
        return f'{self.unit} - {self.heading}'


class RelCreatorCreator(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='rel_creator_creators')
    related_creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='inverse_rel_creator_creators')
    association_type = models.CharField(max_length=255, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_creator_id = models.CharField(max_length=255, blank=True, null=True)
    legacy_related_creator_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_creator_creators'
        indexes = [models.Index(fields=['db_source', 'legacy_creator_id'])]

    def __str__(self):
        return f'{self.creator} - {self.related_creator}'


class RelCreatorInstitution(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='rel_creator_institutions')
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE, related_name='rel_creator_institutions')

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_creator_id = models.CharField(max_length=255, blank=True, null=True)
    legacy_institution_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_creator_institutions'
        indexes = [models.Index(fields=['db_source', 'legacy_creator_id'])]

    def __str__(self):
        return f'{self.creator} - {self.institution}'


class RelCreatorSource(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='rel_creator_sources')
    source = models.ForeignKey('Source', on_delete=models.CASCADE, related_name='rel_creator_sources')

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_creator_id = models.CharField(max_length=255, blank=True, null=True)
    legacy_source_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_creator_sources'
        indexes = [models.Index(fields=['db_source', 'legacy_creator_id'])]

    def __str__(self):
        return f'{self.creator} - {self.source}'


class RelCustodianSource(models.Model):
    custodian = models.ForeignKey('Custodian', on_delete=models.CASCADE, related_name='rel_custodian_sources')
    source = models.ForeignKey('Source', on_delete=models.CASCADE, related_name='rel_custodian_sources')

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_custodian_id = models.CharField(max_length=255, blank=True, null=True)
    legacy_source_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_custodian_sources'
        indexes = [models.Index(fields=['db_source', 'legacy_custodian_id'])]

    def __str__(self):
        return f'{self.custodian} - {self.source}'


class RelFondSource(models.Model):
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='rel_fond_sources')
    source = models.ForeignKey('Source', on_delete=models.CASCADE, related_name='rel_fond_sources')

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_fond_id = models.CharField(max_length=255, blank=True, null=True)
    legacy_source_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_fond_sources'
        indexes = [models.Index(fields=['db_source', 'legacy_fond_id'])]

    def __str__(self):
        return f'{self.fond} - {self.source}'


class RelUnitSource(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='rel_unit_sources')
    source = models.ForeignKey('Source', on_delete=models.CASCADE, related_name='rel_unit_sources')

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_unit_id = models.CharField(max_length=255, blank=True, null=True)
    legacy_source_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_unit_sources'
        indexes = [models.Index(fields=['db_source', 'legacy_unit_id'])]

    def __str__(self):
        return f'{self.unit} - {self.source}'


class RelProjectFond(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='rel_project_fonds')
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='rel_project_fonds')

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_project_id = models.CharField(max_length=255, blank=True, null=True)
    legacy_fond_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_project_fonds'
        indexes = [models.Index(fields=['db_source', 'legacy_project_id'])]

    def __str__(self):
        return f'{self.project} - {self.fond}'


class RelFondDocumentForm(models.Model):
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='rel_fond_document_forms')
    document_form = models.ForeignKey('DocumentForm', on_delete=models.CASCADE, related_name='rel_fond_document_forms')

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_fond_id = models.CharField(max_length=255, blank=True, null=True)
    legacy_document_form_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_fond_document_forms'
        indexes = [models.Index(fields=['db_source', 'legacy_fond_id'])]

    def __str__(self):
        return f'{self.fond} - {self.document_form}'


class RelUnitAnagraphic(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='rel_unit_anagraphics')
    anagraphic = models.ForeignKey('Anagraphic', on_delete=models.CASCADE, related_name='rel_unit_anagraphics')

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_unit_id = models.CharField(max_length=255, blank=True, null=True)
    legacy_anagraphic_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rel_unit_anagraphics'
        indexes = [models.Index(fields=['db_source', 'legacy_unit_id'])]

    def __str__(self):
        return f'{self.unit} - {self.anagraphic}'
