import uuid

from django.db import models
from localized_fields.fields import LocalizedCharField, LocalizedTextField

from core.models import TimeStampedModel
from rule.constants import RuleKind


class RuleDefinition(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, unique=True)
    label = LocalizedCharField()
    kind = models.CharField(max_length=32, choices=RuleKind.choices())
    description = LocalizedTextField(blank=True)

    class Meta:
        ordering = ['code']
