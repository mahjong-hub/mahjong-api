import uuid

from django.db import models

from hand.tiles import TileCode, TileSetCode
from rule.constants import Operator, TargetType


class CountCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_logic = models.ForeignKey(
        'rule.RuleLogic',
        related_name='count_conditions',
        on_delete=models.CASCADE,
    )
    target_type = models.CharField(
        max_length=16,
        choices=TargetType.count_choices(),
    )
    tile_code = models.CharField(
        max_length=4,
        choices=TileCode.choices(),
        null=True,
        blank=True,
    )
    tile_set_code = models.CharField(
        max_length=20,
        choices=TileSetCode.choices(),
        null=True,
        blank=True,
    )
    operator = models.CharField(max_length=16, choices=Operator.choices())
    value_int = models.IntegerField()
