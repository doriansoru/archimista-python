from django.db import models


class Sc2(models.Model):
    unit = models.OneToOneField('Unit', on_delete=models.CASCADE, related_name='sc2_card')
    card_type = models.CharField(max_length=10, default='SC2')  # SC2 (Disegno) o SC3 (Foto)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Campi originali Archimista / Sc2
    mtce = models.CharField(max_length=255, null=True, blank=True, verbose_name="Esecuzione")
    sdtt = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tipo di rappresentazione")
    sdts = models.CharField(max_length=255, null=True, blank=True, verbose_name="Rappresentazione tematica")
    misa = models.CharField(max_length=50, null=True, blank=True, verbose_name="Altezza")
    misl = models.CharField(max_length=50, null=True, blank=True, verbose_name="Larghezza")
    lrc = models.TextField(null=True, blank=True, verbose_name="Luogo di rappresentazione")
    lrd = models.CharField(max_length=255, null=True, blank=True, verbose_name="Data della ripresa")
    dpgf = models.CharField(max_length=255, null=True, blank=True, verbose_name="Numero tavola")
    sgti = models.TextField(null=True, blank=True, verbose_name="Soggetto iconografico")
    sca = models.CharField(max_length=255, null=True, blank=True, verbose_name="Scala")
    cmmr = models.CharField(max_length=255, null=True, blank=True, verbose_name="Numero di commessa")
    ort = models.CharField(max_length=255, null=True, blank=True, verbose_name="Orientamento")

    class Meta:
        db_table = 'sc2s'
        verbose_name = 'Technical Drawing Card (Sc2)'

    def __str__(self):
        return f'SC2 per {self.unit}'


class Sc2TextualElement(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='sc2_textual_elements')
    isri = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sc2_textual_elements'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.isri or 'Elemento testuale SC2'


class Sc2VisualElement(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='sc2_visual_elements')
    stmd = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sc2_visual_elements'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.stmd or 'Elemento visivo SC2'


class Sc2Author(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='sc2_authors')
    autr = models.CharField(max_length=255, blank=True, null=True)
    autn = models.CharField(max_length=255, blank=True, null=True)
    auta = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sc2_authors'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.autn or self.autr or 'Autore SC2'


class Sc2AttributionReason(models.Model):
    sc2_author = models.ForeignKey(Sc2Author, on_delete=models.CASCADE, related_name='sc2_attribution_reasons')
    autm = models.CharField(max_length=255, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sc2_attribution_reasons'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.autm or 'Motivo attribuzione'


class Sc2Commission(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='sc2_commissions')
    cmmc = models.CharField(max_length=255, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sc2_commissions'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.cmmc or 'Commissione SC2'


class Sc2CommissionName(models.Model):
    sc2_commission = models.ForeignKey(Sc2Commission, on_delete=models.CASCADE, related_name='sc2_commission_names')
    cmmn = models.CharField(max_length=255, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sc2_commission_names'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.cmmn or 'Nome commissione'


class Sc2Technique(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='sc2_techniques')
    mtct = models.CharField(max_length=255, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sc2_techniques'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.mtct or 'Tecnica SC2'


class Sc2Scale(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='sc2_scales')
    sca = models.CharField(max_length=255, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sc2_scales'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.sca or 'Scala SC2'
