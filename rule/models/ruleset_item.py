import uuid

from django.db import models


class RulesetItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ruleset_version = models.ForeignKey(
        'rule.RulesetVersion',
        related_name='items',
        on_delete=models.CASCADE,
    )
    rule_definition = models.ForeignKey(
        'rule.RuleDefinition',
        related_name='ruleset_items',
        on_delete=models.PROTECT,
    )
    value_int = models.IntegerField()
    enabled = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ruleset_version', 'rule_definition'],
                name='rule_rulesetitem_unique_rule_per_version',
            ),
        ]
