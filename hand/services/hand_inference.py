import logging
from decimal import Decimal

from django.conf import settings

from asset.services.s3 import generate_presigned_get_url
from hand.constants import DetectionStatus
from hand.models import DetectionTile, HandDetection
from hand.services.modal_client import submit_detection

logger = logging.getLogger(__name__)


def dispatch_detection(detection: HandDetection) -> None:
    """
    Dispatch a detection job to Modal.

    Generates a presigned GET URL for the image, submits to Modal,
    and updates the detection status to RUNNING with the call_id.
    """
    storage_key = detection.asset_ref.asset.storage_key

    image_url = generate_presigned_get_url(
        bucket_name=settings.STORAGE_BUCKET_IMAGES,
        object_name=storage_key,
    )

    call_id = submit_detection(image_url, detection.model_version)

    detection.status = DetectionStatus.RUNNING.value
    detection.call_id = call_id
    detection.save(update_fields=['status', 'call_id', 'updated_at'])


def process_detection_result(
    detection: HandDetection,
    result: dict,
) -> HandDetection:
    """
    Process detection results from Modal.

    Filters by confidence threshold, creates DetectionTile records,
    computes overall confidence, and marks detection as SUCCEEDED.
    """
    threshold = settings.DETECTION_CONFIDENCE_THRESHOLD
    detections = result.get('detections', [])

    tiles_to_create = []
    confidences = []

    for det in detections:
        conf = float(det['confidence'])
        if conf < threshold:
            continue

        tiles_to_create.append(
            DetectionTile(
                detection=detection,
                tile_code=det['tile_code'],
                x1=int(det['x1']),
                y1=int(det['y1']),
                x2=int(det['x2']),
                y2=int(det['y2']),
                confidence=Decimal(str(round(conf, 4))),
            ),
        )
        confidences.append(conf)

    if tiles_to_create:
        DetectionTile.objects.bulk_create(tiles_to_create)

    if confidences:
        avg_conf = sum(confidences) / len(confidences)
        detection.confidence_overall = Decimal(str(round(avg_conf, 4)))
    else:
        detection.confidence_overall = Decimal('0')

    detection.status = DetectionStatus.SUCCEEDED.value
    detection.save(
        update_fields=['status', 'confidence_overall', 'updated_at'],
    )

    return (
        HandDetection.objects.select_related('asset_ref')
        .prefetch_related('tiles')
        .get(id=detection.id)
    )
