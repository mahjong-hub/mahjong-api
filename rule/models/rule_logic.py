import uuid

from django.db import models

from rule.constants import CombineOp, LogicType


class RuleLogic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_definition = models.OneToOneField(
        'rule.RuleDefinition',
        related_name='logic',
        on_delete=models.CASCADE,
    )
    logic_type = models.CharField(max_length=32, choices=LogicType.choices())
    combine_op = models.CharField(
        max_length=8,
        choices=CombineOp.choices(),
        blank=True,
        default='',
    )
    min_match = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True, default='')
