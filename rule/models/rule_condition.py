import uuid

from django.db import models

from rule.constants import (
    ConditionContext,
    ConditionTarget,
    ConditionType,
    Operator,
)


class RuleCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_logic = models.ForeignKey(
        'rule.RuleLogic',
        related_name='conditions',
        on_delete=models.CASCADE,
    )
    operator = models.CharField(max_length=32)
    value = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=32)
    target = models.CharField(max_length=64, null=True, blank=True)
    context = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(operator__in=[e.value for e in Operator]),
                name='rule_rulecondition_operator_valid',
            ),
            models.CheckConstraint(
                condition=models.Q(type__in=[e.value for e in ConditionType]),
                name='rule_rulecondition_type_valid',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(target__isnull=True)
                    | models.Q(
                        target__in=[e.value for e in ConditionTarget] + [''],
                    )
                ),
                name='rule_rulecondition_target_valid',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(context__isnull=True)
                    | models.Q(
                        context__in=[e.value for e in ConditionContext] + [''],
                    )
                ),
                name='rule_rulecondition_context_valid',
            ),
        ]
