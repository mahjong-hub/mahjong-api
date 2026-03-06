import uuid

from django.db import models

from core.models import TimeStampedModel
from rule.constants import RulesetVersionStatus


class RulesetVersion(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ruleset = models.ForeignKey(
        'rule.Ruleset',
        related_name='versions',
        on_delete=models.CASCADE,
    )
    version_int = models.PositiveIntegerField()
    status = models.CharField(max_length=16)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[e.value for e in RulesetVersionStatus],
                ),
                name='rule_rulesetversion_status_valid',
            ),
            models.UniqueConstraint(
                fields=['ruleset', 'version_int'],
                name='rule_rulesetversion_unique_version_int',
            ),
        ]
