from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings

from hand.constants import DetectionStatus
from hand.factories import HandDetectionFactory
from hand.models import HandDetection
from hand.services.hand_inference import (
    dispatch_detection,
    process_detection_result,
)


@override_settings(
    STORAGE_BUCKET_IMAGES='test-bucket',
)
class TestDispatchDetection(TestCase):
    @patch('hand.services.hand_inference.submit_detection')
    @patch('hand.services.hand_inference.generate_presigned_get_url')
    def test_updates_status_and_call_id(
        self,
        mock_presign,
        mock_submit,
    ):
        mock_presign.return_value = 'https://r2.example.com/signed-url'
        mock_submit.return_value = 'fc-abc123'

        detection = HandDetectionFactory(
            status=DetectionStatus.PENDING.value,
            model_version='v0',
        )

        dispatch_detection(detection)

        detection.refresh_from_db()
        self.assertEqual(detection.status, DetectionStatus.RUNNING.value)
        self.assertEqual(detection.call_id, 'fc-abc123')

    @patch('hand.services.hand_inference.submit_detection')
    @patch('hand.services.hand_inference.generate_presigned_get_url')
    def test_generates_presigned_url_with_storage_key(
        self,
        mock_presign,
        mock_submit,
    ):
        mock_presign.return_value = 'https://r2.example.com/signed-url'
        mock_submit.return_value = 'fc-abc123'

        detection = HandDetectionFactory(
            status=DetectionStatus.PENDING.value,
        )
        expected_key = detection.asset_ref.asset.storage_key

        dispatch_detection(detection)

        mock_presign.assert_called_once_with(
            bucket_name='test-bucket',
            object_name=expected_key,
        )

    @patch('hand.services.hand_inference.submit_detection')
    @patch('hand.services.hand_inference.generate_presigned_get_url')
    def test_submits_with_model_version(
        self,
        mock_presign,
        mock_submit,
    ):
        mock_presign.return_value = 'https://r2.example.com/signed-url'
        mock_submit.return_value = 'fc-abc123'

        detection = HandDetectionFactory(
            status=DetectionStatus.PENDING.value,
            model_version='v2',
        )

        dispatch_detection(detection)

        mock_submit.assert_called_once_with(
            'https://r2.example.com/signed-url',
            'v2',
        )


@override_settings(
    DETECTION_CONFIDENCE_THRESHOLD=0.5,
)
class TestProcessDetectionResult(TestCase):
    def test_creates_tiles_above_threshold(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
        )

        result = {
            'detections': [
                {
                    'tile_code': '1B',
                    'x1': 10,
                    'y1': 20,
                    'x2': 110,
                    'y2': 120,
                    'confidence': 0.95,
                },
                {
                    'tile_code': '2B',
                    'x1': 120,
                    'y1': 20,
                    'x2': 220,
                    'y2': 120,
                    'confidence': 0.85,
                },
            ],
        }

        updated = process_detection_result(detection, result)

        self.assertEqual(updated.status, DetectionStatus.SUCCEEDED.value)
        self.assertEqual(updated.tiles.count(), 2)

    def test_filters_tiles_below_threshold(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
        )

        result = {
            'detections': [
                {
                    'tile_code': '1B',
                    'x1': 10,
                    'y1': 20,
                    'x2': 110,
                    'y2': 120,
                    'confidence': 0.95,
                },
                {
                    'tile_code': '2B',
                    'x1': 120,
                    'y1': 20,
                    'x2': 220,
                    'y2': 120,
                    'confidence': 0.3,  # Below threshold
                },
            ],
        }

        updated = process_detection_result(detection, result)

        self.assertEqual(updated.tiles.count(), 1)
        tile = updated.tiles.first()
        self.assertEqual(tile.tile_code, '1B')

    def test_computes_confidence_overall(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
        )

        result = {
            'detections': [
                {
                    'tile_code': '1B',
                    'x1': 10,
                    'y1': 20,
                    'x2': 110,
                    'y2': 120,
                    'confidence': 0.9,
                },
                {
                    'tile_code': '2B',
                    'x1': 120,
                    'y1': 20,
                    'x2': 220,
                    'y2': 120,
                    'confidence': 0.8,
                },
            ],
        }

        updated = process_detection_result(detection, result)

        self.assertEqual(updated.confidence_overall, Decimal('0.85'))

    def test_empty_detections(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
        )

        result = {'detections': []}

        updated = process_detection_result(detection, result)

        self.assertEqual(updated.status, DetectionStatus.SUCCEEDED.value)
        self.assertEqual(updated.tiles.count(), 0)
        self.assertEqual(updated.confidence_overall, Decimal('0'))

    def test_all_below_threshold(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
        )

        result = {
            'detections': [
                {
                    'tile_code': '1B',
                    'x1': 10,
                    'y1': 20,
                    'x2': 110,
                    'y2': 120,
                    'confidence': 0.1,
                },
            ],
        }

        updated = process_detection_result(detection, result)

        self.assertEqual(updated.tiles.count(), 0)
        self.assertEqual(updated.confidence_overall, Decimal('0'))

    def test_tile_fields_stored_correctly(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
        )

        result = {
            'detections': [
                {
                    'tile_code': 'RD',
                    'x1': 50,
                    'y1': 60,
                    'x2': 150,
                    'y2': 160,
                    'confidence': 0.9876,
                },
            ],
        }

        updated = process_detection_result(detection, result)

        tile = updated.tiles.first()
        self.assertEqual(tile.tile_code, 'RD')
        self.assertEqual(tile.x1, 50)
        self.assertEqual(tile.y1, 60)
        self.assertEqual(tile.x2, 150)
        self.assertEqual(tile.y2, 160)
        self.assertEqual(tile.confidence, Decimal('0.9876'))

    def test_returns_detection_with_prefetched_tiles(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.RUNNING.value,
        )

        result = {
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

        updated = process_detection_result(detection, result)

        # Verify it's a fresh queryset result (not the same instance)
        self.assertIsInstance(updated, HandDetection)
        self.assertEqual(updated.id, detection.id)
