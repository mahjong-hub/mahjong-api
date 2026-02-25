import uuid

from django.db import models

from core.models import Tile, TileSet
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
    tile_code = models.ForeignKey(
        Tile,
        null=True,
        blank=True,
        to_field='code',
        on_delete=models.PROTECT,
    )
    tile_set_code = models.ForeignKey(
        TileSet,
        null=True,
        blank=True,
        to_field='code',
        on_delete=models.PROTECT,
    )
    allow_open = models.BooleanField(default=True)
    allow_closed = models.BooleanField(default=True)
