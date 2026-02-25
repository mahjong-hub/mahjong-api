from django.db import models
from localized_fields.fields import LocalizedCharField


class Tile(models.Model):
    code = models.CharField(primary_key=True, max_length=4, unique=True)
    suit = models.CharField(max_length=20)
    rank = models.IntegerField(null=True, blank=True)
    label = LocalizedCharField(max_length=20)

    class Meta:
        ordering = ['suit', 'rank']
