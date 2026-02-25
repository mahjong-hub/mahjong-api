import uuid

from django.db import models

from rule.constants import SpecialShapeType


class SpecialShapeCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_logic = models.ForeignKey(
        'rule.RuleLogic',
        related_name='shape_conditions',
        on_delete=models.CASCADE,
    )
    special_shape = models.CharField(
        max_length=32,
        choices=SpecialShapeType.choices(),
    )
