from django.db import models


class FscCode(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fsc_codes')
    code = models.CharField(max_length=50)
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fsc_codes'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.code


class FscOrganization(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fsc_organizations')
    organization = models.CharField(max_length=255)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fsc_organizations'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.organization


class FscNationality(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fsc_nationalities')
    nationality = models.CharField(max_length=255)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fsc_nationalities'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.nationality


class FscOpen(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fsc_opens')
    open = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fsc_opens'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.open


class FscClose(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fsc_closes')
    close = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fsc_closes'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.close
