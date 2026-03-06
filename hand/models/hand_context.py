from django.db import models

from core.models import TimeStampedModel
from hand.constants import Wind, WinMethod
from hand.models.hand import Hand


class HandContext(TimeStampedModel):
    """
    Stores scoring context for a hand (1:1 with Hand).

    Captures the game state at the time the hand is scored:
    the player's seat wind, the current round wind, and how the
    hand was won.
    """

    hand = models.OneToOneField(
        Hand,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='context',
    )

    seat_wind = models.CharField(max_length=2)
    round_wind = models.CharField(max_length=2)
    win_method = models.CharField(max_length=16, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(seat_wind__in=[e.value for e in Wind]),
                name='hand_handcontext_seat_wind_valid',
            ),
            models.CheckConstraint(
                condition=models.Q(round_wind__in=[e.value for e in Wind]),
                name='hand_handcontext_round_wind_valid',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(win_method__isnull=True)
                    | models.Q(win_method__in=[e.value for e in WinMethod])
                ),
                name='hand_handcontext_win_method_valid',
            ),
        ]
