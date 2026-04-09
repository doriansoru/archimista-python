from django.db import models


class IccdAuthor(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, null=True, blank=True)
    biography = models.TextField(null=True, blank=True, verbose_name="Dati anagrafici/biografia")

    class Meta:
        db_table = 'iccd_authors'

    def __str__(self):
        return self.name


class IccdDescription(models.Model):
    unit = models.OneToOneField('Unit', on_delete=models.CASCADE, related_name='iccd_card')
    denomination = models.CharField(max_length=255, null=True, blank=True)
    object_type = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    age_century = models.CharField(max_length=255, null=True, blank=True)
    authors = models.ManyToManyField(IccdAuthor, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'iccd_descriptions'
        verbose_name = 'Cultural Heritage Card (Iccd)'

    def __str__(self):
        return f'ICCD per {self.unit}'


class IccdSubject(models.Model):
    iccd_description = models.ForeignKey(IccdDescription, on_delete=models.CASCADE, related_name='iccd_subjects')
    subject = models.TextField()
    subject_type = models.CharField(max_length=50, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'iccd_subjects'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.subject


class IccdDamage(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='iccd_damages')
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'iccd_damages'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.code


class IccdTechSpec(models.Model):
    unit = models.OneToOneField('Unit', on_delete=models.CASCADE, related_name='iccd_tech_spec')
    mtcm = models.CharField(max_length=255, blank=True, null=True)
    mtct = models.CharField(max_length=255, blank=True, null=True)
    misa = models.CharField(max_length=50, blank=True, null=True)
    misl = models.CharField(max_length=50, blank=True, null=True)
    misp = models.CharField(max_length=50, blank=True, null=True)
    misu = models.CharField(max_length=20, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'iccd_tech_specs'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return f'Specifiche tecniche per {self.unit}'
