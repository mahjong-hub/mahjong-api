import uuid

from django.db import models

from hand.tiles import TileCode, TileSetCode
from rule.constants import GroupType, Operator, TargetType


class GroupCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_logic = models.ForeignKey(
        'rule.RuleLogic',
        related_name='group_conditions',
        on_delete=models.CASCADE,
    )
    group_type = models.CharField(max_length=16, choices=GroupType.choices())
    operator = models.CharField(max_length=16, choices=Operator.choices())
    value_int = models.IntegerField(null=True, blank=True)
    target_type = models.CharField(max_length=32, choices=TargetType.choices())
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
    allow_open = models.BooleanField(default=True)
    allow_closed = models.BooleanField(default=True)
