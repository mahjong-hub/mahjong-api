import uuid

from django.db import models

from core.models import TimeStampedModel
from hand.models.hand_correction import HandCorrection
from hand.tiles import TileCode


class HandTile(TimeStampedModel):
    """
    Represents a single tile in a hand correction.

    Each row represents one tile instance. Duplicates (e.g., three 1B tiles)
    are represented as multiple rows with the same tile_code.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    hand_correction = models.ForeignKey(
        HandCorrection,
        on_delete=models.CASCADE,
        related_name='tiles',
    )

    tile_code = models.CharField(
        max_length=4,
        choices=TileCode.choices(),
    )

    # Stable ordering for UI display (left-to-right)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['hand_correction', 'sort_order']),
        ]
        ordering = ['sort_order']
