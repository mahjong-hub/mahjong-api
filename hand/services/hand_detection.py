from django.conf import settings
from django.db import transaction

from asset.constants import AssetRole
from asset.models import Asset, AssetRef
from hand.constants import DetectionStatus
from hand.models import Hand, HandDetection
from user.models import Client


def find_existing_detection(asset: Asset) -> HandDetection | None:
    """
    Find existing non-failed detection for the asset with current model version.

    Returns the detection if found and not failed, otherwise None.
    """
    model_version = settings.TILE_DETECTOR_MODEL_VERSION

    existing_ref = (
        AssetRef.objects.filter(
            asset=asset,
            role=AssetRole.HAND_PHOTO.value,
        )
        .select_related('owner_content_type')
        .first()
    )

    if not existing_ref:
        return None

    existing_detection = (
        HandDetection.objects.filter(
            hand_id=existing_ref.owner_id,
            model_version=model_version,
        )
        .order_by('-created_at')
        .first()
    )

    if (
        existing_detection
        and existing_detection.status != DetectionStatus.FAILED.value
    ):
        return (
            HandDetection.objects.select_related('asset_ref')
            .prefetch_related('tiles')
            .get(id=existing_detection.id)
        )

    return None


def create_detection(
    asset: Asset,
    client: Client,
    source: str,
) -> HandDetection:
    """
    Create Hand, AssetRef, and HandDetection for the asset.

    All records are created atomically in a single transaction.
    """
    with transaction.atomic():
        hand = Hand.objects.create(client=client, source=source)

        asset_ref = AssetRef.attach(
            asset=asset,
            owner=hand,
            role=AssetRole.HAND_PHOTO.value,
        )

        detection = HandDetection.objects.create(
            hand=hand,
            asset_ref=asset_ref,
            status=DetectionStatus.PENDING.value,
            model_name=settings.TILE_DETECTOR_MODEL_NAME,
            model_version=settings.TILE_DETECTOR_MODEL_VERSION,
        )

    return (
        HandDetection.objects.select_related('asset_ref')
        .prefetch_related('tiles')
        .get(id=detection.id)
    )
