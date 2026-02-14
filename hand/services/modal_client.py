import logging

import httpx
from django.conf import settings

from hand.exceptions import ModalServiceError

logger = logging.getLogger(__name__)


def _get_client() -> httpx.Client:
    return httpx.Client(
        base_url=settings.MODAL_CV_ENDPOINT,
        headers={'Authorization': f'Bearer {settings.MODAL_AUTH_TOKEN}'},
        timeout=30.0,
    )


def submit_detection(image_url: str, model_version: str) -> str:
    """
    Submit a detection job to Modal.

    Returns the call_id for polling results.
    """
    with _get_client() as client:
        try:
            response = client.post(
                '/detect',
                json={
                    'image_url': image_url,
                    'version': model_version,
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error('Modal submit_detection failed: %s', e)
            raise ModalServiceError(
                message=f'Failed to submit detection to Modal: {e}',
            ) from e

    return response.json()['call_id']


def poll_detection_result(call_id: str) -> dict | None:
    """
    Poll Modal for detection results.

    Returns the result dict if complete, or None if still processing (202).
    """
    with _get_client() as client:
        try:
            response = client.get(f'/results/{call_id}')
        except httpx.HTTPError as e:
            logger.error('Modal poll_detection_result failed: %s', e)
            raise ModalServiceError(
                message=f'Failed to poll Modal for results: {e}',
            ) from e

    if response.status_code == 202:
        return None

    if response.status_code != 200:
        logger.error(
            'Modal poll returned status %s: %s',
            response.status_code,
            response.text,
        )
        raise ModalServiceError(
            message=f'Modal returned status {response.status_code}',
        )

    return response.json()
