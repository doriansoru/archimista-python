from django.db import models


class Vocabulary(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vocabularies'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.name


class Term(models.Model):
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE, related_name='terms', null=True, blank=True, db_column='vocabulary_id')
    identifier = models.CharField(max_length=255, blank=True, null=True)
    term_key = models.CharField(max_length=255, blank=True, null=True)  # Chiave univoca per traduzione
    term = models.CharField(max_length=255)
    term_value = models.CharField(max_length=255, blank=True, null=True)  # Valore del termine
    term_type = models.CharField(max_length=50, blank=True, null=True)
    scope_note = models.TextField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)  # Ordinamento nel vocabolario
    parent_id = models.IntegerField(blank=True, null=True)
    native = models.CharField(max_length=1, blank=True, null=True)
    grouping = models.CharField(max_length=1, blank=True, null=True)

    db_source = models.CharField(max_length=255, blank=True, null=True)
    legacy_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'terms'
        indexes = [models.Index(fields=['db_source', 'legacy_id'])]

    def __str__(self):
        return self.term_value or self.term or self.term_key or str(self.pk)
