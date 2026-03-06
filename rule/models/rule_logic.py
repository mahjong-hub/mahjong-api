import uuid

from django.db import models

from rule.constants import CombineOp


class RuleLogic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_definition = models.OneToOneField(
        'rule.RuleDefinition',
        related_name='logic',
        on_delete=models.CASCADE,
    )
    combine_op = models.CharField(
        max_length=8,
        blank=True,
        default='',
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    combine_op__in=[e.value for e in CombineOp] + [''],
                ),
                name='rule_rulelogic_combine_op_valid',
            ),
        ]
