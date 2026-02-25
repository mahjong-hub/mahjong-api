import uuid

from django.db import models

from core.models import Tile, TileSet
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
    operator = models.CharField(max_length=16, choices=Operator.choices())
    value_int = models.IntegerField()
