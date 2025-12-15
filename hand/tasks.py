from celery import shared_task

from mahjong_api import env
from ml.inference.model import get_model


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def run_hand_detection(self, hand_id: str):
    model = get_model(
        name=env.TILE_DETECTOR_MODEL_NAME,
        version=env.TILE_DETECTOR_MODEL_VERSION,
    )
