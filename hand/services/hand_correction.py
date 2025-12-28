from dataclasses import dataclass

from django.db import transaction

from hand.exceptions import DetectionHandMismatchError, InvalidTileDataError
from hand.models import Hand, HandCorrection, HandDetection, HandTile
from hand.tiles import validate_tile_counts


@dataclass(frozen=True)
class TileInput:
    """Input data for a single tile."""

    tile_code: str
    sort_order: int


def create_hand_correction(
    *,
    hand: Hand,
    tiles: list[TileInput],
    detection: HandDetection | None = None,
) -> HandCorrection:
    """
    Create a new hand correction with the given tiles.

    Business logic:
    - Validates detection belongs to hand (if provided)
    - Validates tile counts
    - Creates correction and tiles atomically
    - Updates Hand.active_hand_correction

    Args:
        hand: The hand to create a correction for.
        tiles: List of tiles to include in the correction.
        detection: Optional detection this correction is based on.

    Returns:
        The created HandCorrection with tiles.

    Raises:
        InvalidTileDataError: If tile validation fails.
        DetectionHandMismatchError: If detection doesn't belong to the hand.
    """
    # Validate detection belongs to hand
    if detection and detection.hand_id != hand.id:
        raise DetectionHandMismatchError(
            message='Detection does not belong to this hand.',
        )

    # Validate tile counts
    tile_codes = [t.tile_code for t in tiles]
    validation_errors = validate_tile_counts(tile_codes)
    if validation_errors:
        raise InvalidTileDataError(
            message='; '.join(validation_errors),
        )

    # Create correction and tiles atomically
    with transaction.atomic():
        correction = HandCorrection.objects.create(
            hand=hand,
            detection=detection,
        )

        # Bulk create tiles
        hand_tiles = [
            HandTile(
                hand_correction=correction,
                tile_code=tile.tile_code,
                sort_order=tile.sort_order,
            )
            for tile in tiles
        ]
        HandTile.objects.bulk_create(hand_tiles)

        # Update active correction on hand
        hand.active_hand_correction = correction
        hand.save(update_fields=['active_hand_correction', 'updated_at'])

    # Reload with tiles for response
    correction.refresh_from_db()
    return HandCorrection.objects.prefetch_related('tiles').get(
        id=correction.id,
    )
