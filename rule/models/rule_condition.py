import uuid

from django.db import models

from rule.constants import (
    ConditionContext,
    ConditionType,
    CountTarget,
    HandStructureTarget,
    Operator,
)


class RuleCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_logic = models.ForeignKey(
        'rule.RuleLogic',
        related_name='conditions',
        on_delete=models.CASCADE,
    )
    operator = models.CharField(max_length=32, null=True, blank=True)
    value = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=32)
    target = models.CharField(max_length=64, null=True, blank=True)
    context = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(operator__isnull=True)
                    | models.Q(operator__in=[e.value for e in Operator])
                ),
                name='rule_rulecondition_operator_valid',
            ),
            models.CheckConstraint(
                condition=models.Q(type__in=[e.value for e in ConditionType]),
                name='rule_rulecondition_type_valid',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        operator__isnull=False,
                        value__isnull=False,
                        type__in=[
                            ConditionType.CHOW_COUNT.value,
                            ConditionType.PUNG_COUNT.value,
                            ConditionType.KONG_COUNT.value,
                            ConditionType.PAIR_COUNT.value,
                            ConditionType.TILE_COUNT.value,
                        ],
                        target__in=[e.value for e in CountTarget],
                        context__isnull=True,
                    )
                    | models.Q(
                        operator__isnull=False,
                        value__isnull=False,
                        type__in=[
                            ConditionType.CHOW_COUNT.value,
                            ConditionType.PUNG_COUNT.value,
                            ConditionType.KONG_COUNT.value,
                            ConditionType.PAIR_COUNT.value,
                        ],
                        target__isnull=True,  # counts melds of any tile type
                        context__isnull=True,
                    )
                    | models.Q(
                        operator__isnull=False,
                        value__isnull=False,
                        type__in=[
                            ConditionType.CHOW_COUNT.value,
                            ConditionType.PUNG_COUNT.value,
                            ConditionType.KONG_COUNT.value,
                            ConditionType.PAIR_COUNT.value,
                        ],
                        target__in=[e.value for e in CountTarget],
                        context__in=[e.value for e in ConditionContext],
                    )
                    | models.Q(
                        operator__isnull=False,
                        value__isnull=False,
                        type__in=[
                            ConditionType.CHOW_COUNT.value,
                            ConditionType.PUNG_COUNT.value,
                            ConditionType.KONG_COUNT.value,
                            ConditionType.PAIR_COUNT.value,
                        ],
                        target__isnull=True,
                        context__in=[e.value for e in ConditionContext],
                    )
                    | models.Q(
                        operator__isnull=True,
                        value__isnull=True,
                        type=ConditionType.HAND_STRUCTURE.value,
                        target__in=[e.value for e in HandStructureTarget],
                        context__isnull=True,
                    )
                    | models.Q(
                        operator__isnull=False,
                        type=ConditionType.SUIT_COUNT.value,
                        target__isnull=True,
                        value__isnull=False,
                        context__isnull=True,
                    )
                    | models.Q(
                        operator__isnull=True,
                        value__isnull=True,
                        type=ConditionType.WIN_CONDITION.value,
                        target__isnull=True,
                        context__in=[e.value for e in ConditionContext],
                    )
                ),
                name='rule_rulecondition_target_valid',
            ),
        ]
