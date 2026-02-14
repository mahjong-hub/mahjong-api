import uuid
from decimal import Decimal
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from asset.constants import UploadStatus
from asset.factories import AssetFactory, UploadSessionFactory
from hand.constants import DetectionStatus
from hand.factories import HandDetectionFactory
from hand.models import HandDetection
from user.factories import ClientFactory


class TestDetectionViewSetRetrieve(APITestCase):
    def test_success_pending(self):
        detection = HandDetectionFactory()
        client_obj = detection.hand.client

        response = self.client.get(
            f'/hand/detection/{detection.id}/',
            HTTP_X_INSTALL_ID=client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(detection.id))
        self.assertEqual(
            response.data['status'],
            DetectionStatus.PENDING.value,
        )
        self.assertEqual(response.data['tiles'], [])

    def test_missing_install_id_header(self):
        response = self.client.get(f'/hand/detection/{uuid.uuid4()}/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_found(self):
        client_obj = ClientFactory()

        response = self.client.get(
            f'/hand/detection/{uuid.uuid4()}/',
            HTTP_X_INSTALL_ID=client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ownership_returns_not_found(self):
        """Non-owned detections return 404 (queryset excludes them)."""
        detection = HandDetectionFactory()
        other_client = ClientFactory()

        response = self.client.get(
            f'/hand/detection/{detection.id}/',
            HTTP_X_INSTALL_ID=other_client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestDetectionViewSetCreate(APITestCase):
    @patch('hand.views.hand_detection_view.dispatch_detection')
    def test_create_dispatches_detection(self, mock_dispatch):
        client_obj = ClientFactory()
        session = UploadSessionFactory(
            client=client_obj,
            status=UploadStatus.COMPLETED.value,
        )
        asset = AssetFactory(upload_session=session, is_active=True)

        response = self.client.post(
            '/hand/detection/',
            data={'asset_id': str(asset.id)},
            format='json',
            HTTP_X_INSTALL_ID=client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['status'],
            DetectionStatus.PENDING.value,
        )
        mock_dispatch.assert_called_once()
        detection = mock_dispatch.call_args[0][0]
        self.assertIsInstance(detection, HandDetection)

    @patch('hand.views.hand_detection_view.dispatch_detection')
    def test_create_returns_existing_detection(self, mock_dispatch):
        """If a non-failed detection already exists, return it."""
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
        )
        client_obj = detection.hand.client
        asset = detection.asset_ref.asset

        response = self.client.post(
            '/hand/detection/',
            data={'asset_id': str(asset.id)},
            format='json',
            HTTP_X_INSTALL_ID=client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(detection.id))
        mock_dispatch.assert_not_called()


class TestDetectionViewSetPoll(APITestCase):
    @patch('hand.views.hand_detection_view.poll_detection_result')
    def test_poll_returns_succeeded_without_calling_modal(
        self,
        mock_poll,
    ):
        detection = HandDetectionFactory(
            status=DetectionStatus.SUCCEEDED.value,
            confidence_overall=Decimal('0.9500'),
        )
        client_obj = detection.hand.client

        response = self.client.get(
            f'/hand/detection/{detection.id}/poll/',
            HTTP_X_INSTALL_ID=client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'succeeded')
        mock_poll.assert_not_called()

    @patch('hand.views.hand_detection_view.poll_detection_result')
    def test_poll_returns_failed_without_calling_modal(self, mock_poll):
        detection = HandDetectionFactory(
            status=DetectionStatus.FAILED.value,
        )
        client_obj = detection.hand.client

        response = self.client.get(
            f'/hand/detection/{detection.id}/poll/',
            HTTP_X_INSTALL_ID=client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'failed')
        mock_poll.assert_not_called()

    @patch('hand.views.hand_detection_view.poll_detection_result')
    def test_poll_still_running(self, mock_poll):
        """Modal returns None (202) — detection stays RUNNING."""
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
            call_id='fc-123',
        )
        client_obj = detection.hand.client
        mock_poll.return_value = None

        response = self.client.get(
            f'/hand/detection/{detection.id}/poll/',
            HTTP_X_INSTALL_ID=client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'running')
        mock_poll.assert_called_once_with('fc-123')

    @patch(
        'hand.views.hand_detection_view.process_detection_result',
    )
    @patch('hand.views.hand_detection_view.poll_detection_result')
    def test_poll_processes_result(self, mock_poll, mock_process):
        """Modal returns a result — view calls process_detection_result."""
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
            call_id='fc-456',
        )
        client_obj = detection.hand.client
        modal_result = {
            'detections': [
                {
                    'tile_code': '1B',
                    'x1': 10,
                    'y1': 20,
                    'x2': 110,
                    'y2': 120,
                    'confidence': 0.95,
                },
            ],
        }
        mock_poll.return_value = modal_result

        # Make process return the same detection with updated status
        detection.status = DetectionStatus.SUCCEEDED.value
        mock_process.return_value = detection

        response = self.client.get(
            f'/hand/detection/{detection.id}/poll/',
            HTTP_X_INSTALL_ID=client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_poll.assert_called_once_with('fc-456')
        mock_process.assert_called_once()

    def test_poll_not_found(self):
        client_obj = ClientFactory()

        response = self.client.get(
            f'/hand/detection/{uuid.uuid4()}/poll/',
            HTTP_X_INSTALL_ID=client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('hand.views.hand_detection_view.poll_detection_result')
    def test_poll_ownership_returns_not_found(self, mock_poll):
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
            call_id='fc-789',
        )
        other_client = ClientFactory()

        response = self.client.get(
            f'/hand/detection/{detection.id}/poll/',
            HTTP_X_INSTALL_ID=other_client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_poll.assert_not_called()
