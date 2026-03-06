import uuid

from django.db import models

from hand.models.hand_context import HandContext
from rule.constants import ConditionContext


class HandWinModifier(models.Model):
    """
    Records special win condition flags for a hand context.

    Each row represents one active win modifier (e.g. self-draw on last tile).
    At most one row per (hand_context, modifier) pair is allowed.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    hand_context = models.ForeignKey(
        HandContext,
        on_delete=models.CASCADE,
        related_name='win_modifiers',
    )

    modifier = models.CharField(max_length=32)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    modifier__in=ConditionContext.win_modifier_values(),
                ),
                name='hand_handwinmodifier_modifier_valid',
            ),
            models.UniqueConstraint(
                fields=['hand_context', 'modifier'],
                name='hand_handwinmodifier_unique_modifier_per_context',
            ),
        ]
