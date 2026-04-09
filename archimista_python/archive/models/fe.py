from django.db import models


class FeIdentification(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fe_identifications')
    code = models.TextField(blank=True, null=True)
    file_year = models.IntegerField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    identification_class = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fe_identifications'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.code or 'Identificazione FE'


class FeContext(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fe_contexts')
    number = models.IntegerField(blank=True, null=True)
    sub_number = models.IntegerField(blank=True, null=True)
    classification = models.TextField(blank=True, null=True)
    applicant = models.TextField(blank=True, null=True)
    request = models.TextField(blank=True, null=True)
    license_number = models.IntegerField(blank=True, null=True)
    license_year = models.IntegerField(blank=True, null=True)
    protocol_number = models.IntegerField(blank=True, null=True)
    license_date = models.DateField(blank=True, null=True)
    habitability_number = models.IntegerField(blank=True, null=True)
    habitability_year = models.IntegerField(blank=True, null=True)
    habitability_date = models.DateField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fe_contexts'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return f'Contesto FE {self.number}'


class FeOpera(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fe_operas')
    is_present = models.BooleanField(default=False)
    status = models.CharField(max_length=10, blank=True, null=True)
    building_name = models.TextField(blank=True, null=True)
    building_type = models.TextField(blank=True, null=True)
    place_name = models.TextField(blank=True, null=True)
    place_type = models.TextField(blank=True, null=True)
    house_number = models.CharField(max_length=255, blank=True, null=True)
    district = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fe_operas'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.building_name or 'Opera FE'


class FeDesigner(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fe_designers')
    designer_name = models.TextField(blank=True, null=True)
    designer_role = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fe_designers'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.designer_name or 'Progettista FE'


class FeCadastral(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fe_cadastrals')
    way_code = models.IntegerField(blank=True, null=True)
    cadastral_municipality = models.TextField(blank=True, null=True)
    municipality_code = models.IntegerField(blank=True, null=True)
    paper_code = models.IntegerField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fe_cadastrals'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return f'Catastale {self.cadastral_municipality}'


class FeLandParcel(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fe_land_parcels')
    land_parcel_number = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fe_land_parcels'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.land_parcel_number or 'Particella fondiaria'


class FeFractLandParcel(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fe_fract_land_parcels')
    fract_land_parcel_number = models.IntegerField(blank=True, null=True)
    edil_parcel_number = models.IntegerField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fe_fract_land_parcels'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return f'Fraz. {self.fract_land_parcel_number}'


class FeFractEdilParcel(models.Model):
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE, related_name='fe_fract_edil_parcels')
    fract_edil_parcel_number = models.IntegerField(blank=True, null=True)
    material_portion = models.IntegerField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fe_fract_edil_parcels'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return f'Fraz. edilizia {self.fract_edil_parcel_number}'
