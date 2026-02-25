import uuid

from django.db import models

from rule.constants import SuitConstraint


class SuitCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_logic = models.ForeignKey(
        'rule.RuleLogic',
        related_name='suit_conditions',
        on_delete=models.CASCADE,
    )
    suit_constraint = models.CharField(
        max_length=32,
        choices=SuitConstraint.choices(),
    )
