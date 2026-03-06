import uuid

from django.db import models

from rule.constants import ScoringUnit


class RulesetScoringConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ruleset_version = models.OneToOneField(
        'rule.RulesetVersion',
        related_name='scoring_config',
        on_delete=models.CASCADE,
    )
    scoring_unit = models.CharField(max_length=16)
    min_scoring_unit = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    scoring_unit__in=[e.value for e in ScoringUnit],
                ),
                name='rule_rulesetscoringconfig_scoring_unit_valid',
            ),
        ]
