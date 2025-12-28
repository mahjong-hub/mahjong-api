import uuid

from django.db import models

from core.models import TimeStampedModel
from hand.models.hand import Hand
from hand.models.hand_detection import HandDetection


class HandCorrection(TimeStampedModel):
    """
    Represents a user-verified snapshot of tiles in a hand.

    After detection results are shown, users can validate and correct
    the detected tiles. Each correction creates an immutable snapshot
    of the tiles the user confirms are in the hand.

    The Hand.active_hand_correction points to the latest verified snapshot.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    hand = models.ForeignKey(
        Hand,
        on_delete=models.CASCADE,
        related_name='corrections',
    )

    detection = models.ForeignKey(
        HandDetection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='corrections',
    )

    class Meta:
        indexes = [
            models.Index(fields=['hand', 'created_at']),
            models.Index(fields=['detection']),
        ]
        ordering = ['-created_at']
