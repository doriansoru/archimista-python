from django.db import models


# =============================================================================
# FOND EXTENSIONS
# =============================================================================

class FondName(models.Model):
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='fond_names')
    preferred = models.BooleanField(default=False)
    name = models.TextField()
    qualifier = models.CharField(max_length=10)
    note = models.TextField(blank=True, null=True)
    patronymic = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fond_names'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


class FondIdentifier(models.Model):
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='fond_identifiers')
    identifier = models.TextField()
    identifier_source = models.TextField()
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fond_identifiers'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.identifier


class FondLang(models.Model):
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='fond_langs')
    code = models.CharField(max_length=10)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fond_langs'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.code


class FondOwner(models.Model):
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='fond_owners')
    owner = models.CharField(max_length=255)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fond_owners'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.owner


class FondUrl(models.Model):
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='fond_urls')
    url = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)
    position = models.IntegerField(default=0)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fond_urls'
        ordering = ['position']
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.url


class FondEditor(models.Model):
    fond = models.ForeignKey('Fond', on_delete=models.CASCADE, related_name='fond_editors')
    name = models.TextField()
    qualifier = models.TextField(blank=True, null=True)
    editing_type = models.CharField(max_length=255, blank=True, null=True)
    edited_at = models.DateField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fond_editors'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


# =============================================================================
# UNIT EXTENSIONS
# =============================================================================

class UnitIdentifier(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='unit_identifiers')
    identifier = models.TextField()
    identifier_source = models.TextField()
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unit_identifiers'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.identifier


class UnitOtherReferenceNumber(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='unit_other_reference_numbers')
    other_reference_number = models.TextField()
    qualifier = models.CharField(max_length=255, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unit_other_reference_numbers'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.other_reference_number


class UnitLang(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='unit_langs')
    code = models.CharField(max_length=10)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unit_langs'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.code


class UnitDamage(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='unit_damages')
    code = models.CharField(max_length=50)
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unit_damages'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.code


class UnitUrl(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='unit_urls')
    url = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)
    position = models.IntegerField(default=0)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unit_urls'
        ordering = ['position']
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.url


class UnitEditor(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='unit_editors')
    name = models.TextField()
    qualifier = models.TextField(blank=True, null=True)
    editing_type = models.CharField(max_length=255, blank=True, null=True)
    edited_at = models.DateField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unit_editors'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


# =============================================================================
# CREATOR EXTENSIONS
# =============================================================================

class CreatorName(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='creator_names')
    preferred = models.BooleanField(default=False)
    name = models.TextField()
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    qualifier = models.CharField(max_length=10, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    note_p = models.TextField(blank=True, null=True)
    note_cf = models.TextField(blank=True, null=True)
    patronymic = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    creator_type = models.CharField(max_length=1, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creator_names'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


class CreatorLegalStatus(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='creator_legal_statuses')
    legal_status = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creator_legal_statuses'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.legal_status


class CreatorUrl(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='creator_urls')
    url = models.TextField()
    note = models.TextField(blank=True, null=True)
    position = models.IntegerField(default=0)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creator_urls'
        ordering = ['position']
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.url


class CreatorIdentifier(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='creator_identifiers')
    identifier = models.TextField()
    identifier_source = models.TextField()
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creator_identifiers'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.identifier


class CreatorActivity(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='creator_activities')
    activity = models.TextField()
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creator_activities'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.activity[:50] if self.activity else ''


class CreatorEditor(models.Model):
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, related_name='creator_editors')
    name = models.TextField()
    qualifier = models.TextField(blank=True, null=True)
    editing_type = models.CharField(max_length=255, blank=True, null=True)
    edited_at = models.DateField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'creator_editors'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


# =============================================================================
# CUSTODIAN EXTENSIONS
# =============================================================================

class CustodianName(models.Model):
    custodian = models.ForeignKey('Custodian', on_delete=models.CASCADE, related_name='custodian_names')
    preferred = models.BooleanField(default=False)
    name = models.TextField()
    qualifier = models.CharField(max_length=10, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custodian_names'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


class CustodianIdentifier(models.Model):
    custodian = models.ForeignKey('Custodian', on_delete=models.CASCADE, related_name='custodian_identifiers')
    identifier = models.CharField(max_length=255)
    identifier_source = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custodian_identifiers'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.identifier


class CustodianContact(models.Model):
    custodian = models.ForeignKey('Custodian', on_delete=models.CASCADE, related_name='custodian_contacts')
    contact = models.CharField(max_length=255)
    contact_type = models.CharField(max_length=255)
    contact_note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custodian_contacts'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.contact


class CustodianBuilding(models.Model):
    custodian = models.ForeignKey('Custodian', on_delete=models.CASCADE, related_name='custodian_buildings')
    custodian_building_type = models.CharField(max_length=255, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custodian_buildings'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name or f'{self.address}, {self.city}'


class CustodianOwner(models.Model):
    custodian = models.ForeignKey('Custodian', on_delete=models.CASCADE, related_name='custodian_owners')
    owner = models.CharField(max_length=255)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custodian_owners'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.owner


class CustodianUrl(models.Model):
    custodian = models.ForeignKey('Custodian', on_delete=models.CASCADE, related_name='custodian_urls')
    url = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)
    position = models.IntegerField(default=0)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custodian_urls'
        ordering = ['position']
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.url


class CustodianEditor(models.Model):
    custodian = models.ForeignKey('Custodian', on_delete=models.CASCADE, related_name='custodian_editors')
    name = models.CharField(max_length=255)
    qualifier = models.CharField(max_length=255, blank=True, null=True)
    editing_type = models.CharField(max_length=255, blank=True, null=True)
    edited_at = models.DateField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custodian_editors'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name
