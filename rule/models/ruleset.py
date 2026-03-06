import uuid

from django.db import models

from core.models import TimeStampedModel


class Ruleset(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        'user.Client',
        related_name='rulesets',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=128)
    country_code = models.CharField(max_length=8)
    is_public = models.BooleanField(default=False)
