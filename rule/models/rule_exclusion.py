import uuid

from django.db import models


class RuleExclusion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ruleset_version = models.ForeignKey(
        'rule.RulesetVersion',
        related_name='exclusions',
        on_delete=models.CASCADE,
    )
    rule = models.ForeignKey(
        'rule.RuleDefinition',
        related_name='exclusions',
        on_delete=models.CASCADE,
    )
    excludes = models.ForeignKey(
        'rule.RuleDefinition',
        related_name='excluded_by',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['rule', 'excludes'],
                name='unique_rule_exclusion',
            ),
            models.CheckConstraint(
                condition=~models.Q(rule_id=models.F('excludes_id')),
                name='rule_exclusion_no_self_exclusion',
            ),
        ]
