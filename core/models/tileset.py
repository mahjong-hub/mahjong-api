from django.db import models
from localized_fields.fields import LocalizedTextField


class TileSet(models.Model):
    code = models.CharField(primary_key=True, max_length=20, unique=True)
    description = LocalizedTextField(blank=True)
