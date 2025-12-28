import uuid
from dataclasses import dataclass

from celery import current_app
from django.conf import settings
from django.db import transaction

from asset.constants import AssetRole
from asset.models import Asset, AssetRef
from hand.constants import DetectionStatus, HandSource
from hand.models import Hand, HandDetection
from user.models import Client


HAND_DETECTION_TASK_NAME = 'hand.tasks.run_hand_detection'


@dataclass(frozen=True)
class TriggerDetectionResult:
    hand_id: uuid.UUID
    asset_ref_id: uuid.UUID
    hand_detection_id: uuid.UUID
    status: str


def trigger_hand_detection(
    *,
    asset_id: uuid.UUID,
    install_id: str,
    source: str = HandSource.CAMERA.value,
) -> TriggerDetectionResult:
    """
    Trigger a detection for the given asset.

    Creates Hand, AssetRef, and HandDetection, then enqueues the Celery task.

    Note: Assumes asset ownership and is_active have been validated by caller.
    """
    asset = Asset.objects.get(id=asset_id)

    model_version = settings.TILE_DETECTOR_MODEL_VERSION

    # Check for existing detection (idempotency)
    existing_ref = (
        AssetRef.objects.filter(
            asset=asset,
            role=AssetRole.HAND_PHOTO.value,
        )
        .select_related('owner_content_type')
        .first()
    )

    if existing_ref:
        hand_id = existing_ref.owner_id

        # Check for existing detection with same model version
        existing_detection = (
            HandDetection.objects.filter(
                hand_id=hand_id,
                model_version=model_version,
            )
            .order_by('-created_at')
            .first()
        )

        if existing_detection:
            # If not failed, return existing
            if existing_detection.status != DetectionStatus.FAILED.value:
                return TriggerDetectionResult(
                    hand_id=hand_id,
                    asset_ref_id=existing_ref.id,
                    hand_detection_id=existing_detection.id,
                    status=existing_detection.status,
                )

    # Create new detection run
    client = Client.objects.get(install_id=install_id)

    with transaction.atomic():
        hand = Hand.objects.create(
            client=client,
            source=source,
        )

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
            model_version=model_version,
        )

    # Enqueue Celery task via send_task to avoid importing the task module
    # This breaks the import chain that would otherwise load ML dependencies
    current_app.send_task(HAND_DETECTION_TASK_NAME, args=[str(detection.id)])

    return TriggerDetectionResult(
        hand_id=hand.id,
        asset_ref_id=asset_ref.id,
        hand_detection_id=detection.id,
        status=detection.status,
    )
