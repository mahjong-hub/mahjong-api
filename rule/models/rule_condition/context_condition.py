import uuid

from django.db import models

from rule.constants import ContextField, ContextOperator


class ContextCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_logic = models.ForeignKey(
        'rule.RuleLogic',
        related_name='context_conditions',
        on_delete=models.CASCADE,
    )
    context_field = models.CharField(
        max_length=32,
        choices=ContextField.choices(),
    )
    operator = models.CharField(
        max_length=16,
        choices=ContextOperator.choices(),
    )
    value = models.CharField(max_length=32)
