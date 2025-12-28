from decimal import Decimal

from django.test import TestCase

from asset.constants import AssetRole, UploadStatus
from asset.factories import AssetFactory, ClientFactory, UploadSessionFactory
from asset.models import AssetRef
from hand.constants import DetectionStatus
from hand.models import DetectionTile, Hand, HandDetection
from hand.serializers.hand_detection_serializer import (
    DetectionTileSerializer,
    HandDetectionSerializer,
)


class TestDetectionTileSerializer(TestCase):
    def setUp(self):
        self.client_obj = ClientFactory()
        self.hand = Hand.objects.create(
            client=self.client_obj,
            source='camera',
        )
        session = UploadSessionFactory(client=self.client_obj)
        self.asset = AssetFactory(upload_session=session, is_active=True)
        self.asset_ref = AssetRef.attach(
            asset=self.asset,
            owner=self.hand,
            role=AssetRole.HAND_PHOTO.value,
        )
        self.detection = HandDetection.objects.create(
            hand=self.hand,
            asset_ref=self.asset_ref,
            status=DetectionStatus.SUCCEEDED.value,
            model_name='tile_detector',
            model_version='v0.1.0',
        )

    def test_serializes_all_fields(self):
        tile = DetectionTile.objects.create(
            detection=self.detection,
            tile_code='1B',
            x1=10,
            y1=20,
            x2=110,
            y2=120,
            confidence=Decimal('0.9876'),
        )

        serializer = DetectionTileSerializer(instance=tile)

        self.assertEqual(serializer.data['tile_code'], '1B')
        self.assertEqual(serializer.data['x1'], 10)
        self.assertEqual(serializer.data['y1'], 20)
        self.assertEqual(serializer.data['x2'], 110)
        self.assertEqual(serializer.data['y2'], 120)
        self.assertEqual(serializer.data['confidence'], '0.9876')


class TestHandDetectionSerializer(TestCase):
    def setUp(self):
        self.client_obj = ClientFactory()
        self.hand = Hand.objects.create(
            client=self.client_obj,
            source='camera',
        )
        session = UploadSessionFactory(
            client=self.client_obj,
            status=UploadStatus.COMPLETED.value,
        )
        self.asset = AssetFactory(upload_session=session, is_active=True)
        self.asset_ref = AssetRef.attach(
            asset=self.asset,
            owner=self.hand,
            role=AssetRole.HAND_PHOTO.value,
        )

    def test_serializes_all_fields(self):
        detection = HandDetection.objects.create(
            hand=self.hand,
            asset_ref=self.asset_ref,
            status=DetectionStatus.SUCCEEDED.value,
            model_name='tile_detector',
            model_version='v0.1.0',
            confidence_overall=Decimal('0.9500'),
        )
        DetectionTile.objects.create(
            detection=detection,
            tile_code='1B',
            x1=10,
            y1=20,
            x2=110,
            y2=120,
            confidence=Decimal('0.9876'),
        )

        detection = (
            HandDetection.objects.select_related('asset_ref')
            .prefetch_related('tiles')
            .get(id=detection.id)
        )
        serializer = HandDetectionSerializer(instance=detection)

        self.assertEqual(str(serializer.data['id']), str(detection.id))
        self.assertEqual(str(serializer.data['hand_id']), str(self.hand.id))
        self.assertEqual(
            str(serializer.data['asset_ref_id']),
            str(self.asset_ref.id),
        )
        self.assertEqual(serializer.data['status'], 'succeeded')
        self.assertEqual(serializer.data['model_name'], 'tile_detector')
        self.assertEqual(serializer.data['model_version'], 'v0.1.0')
        self.assertEqual(serializer.data['confidence_overall'], '0.9500')
        self.assertEqual(len(serializer.data['tiles']), 1)
        self.assertIn('created_at', serializer.data)

    def test_empty_tiles_list_serialized(self):
        detection = HandDetection.objects.create(
            hand=self.hand,
            asset_ref=self.asset_ref,
            status=DetectionStatus.PENDING.value,
            model_name='tile_detector',
            model_version='v0.1.0',
        )

        detection = (
            HandDetection.objects.select_related('asset_ref')
            .prefetch_related('tiles')
            .get(id=detection.id)
        )
        serializer = HandDetectionSerializer(instance=detection)

        self.assertEqual(serializer.data['tiles'], [])

    def test_error_fields_serialized(self):
        detection = HandDetection.objects.create(
            hand=self.hand,
            asset_ref=self.asset_ref,
            status=DetectionStatus.FAILED.value,
            model_name='tile_detector',
            model_version='v0.1.0',
            error_code='inference_error',
            error_message='Model inference failed',
        )

        detection = (
            HandDetection.objects.select_related('asset_ref')
            .prefetch_related('tiles')
            .get(id=detection.id)
        )
        serializer = HandDetectionSerializer(instance=detection)

        self.assertEqual(serializer.data['error_code'], 'inference_error')
        self.assertEqual(
            serializer.data['error_message'],
            'Model inference failed',
        )

    def test_null_confidence_overall(self):
        detection = HandDetection.objects.create(
            hand=self.hand,
            asset_ref=self.asset_ref,
            status=DetectionStatus.PENDING.value,
            model_name='tile_detector',
            model_version='v0.1.0',
            confidence_overall=None,
        )

        detection = (
            HandDetection.objects.select_related('asset_ref')
            .prefetch_related('tiles')
            .get(id=detection.id)
        )
        serializer = HandDetectionSerializer(instance=detection)

        self.assertIsNone(serializer.data['confidence_overall'])

    def test_asset_id_required(self):
        data = {}
        serializer = HandDetectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('asset_id', serializer.errors)

    def test_asset_id_must_exist(self):
        import uuid

        data = {'asset_id': str(uuid.uuid4())}
        serializer = HandDetectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('asset_id', serializer.errors)

    def test_asset_must_belong_to_client(self):
        other_client = ClientFactory()
        other_session = UploadSessionFactory(
            client=other_client,
            status=UploadStatus.COMPLETED.value,
        )
        other_asset = AssetFactory(
            upload_session=other_session,
            is_active=True,
        )

        data = {'asset_id': str(other_asset.id)}
        serializer = HandDetectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('asset_id', serializer.errors)

    def test_invalid_source_rejected(self):
        data = {
            'asset_id': str(self.asset.id),
            'source': 'invalid_source',
        }
        serializer = HandDetectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('source', serializer.errors)

    def test_source_defaults_to_camera(self):
        data = {'asset_id': str(self.asset.id)}
        serializer = HandDetectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['source'], 'camera')

    def test_asset_must_be_active(self):
        inactive_session = UploadSessionFactory(
            client=self.client_obj,
            status=UploadStatus.PRESIGNED.value,
        )
        inactive_asset = AssetFactory(
            upload_session=inactive_session,
            is_active=False,
        )

        data = {'asset_id': str(inactive_asset.id)}
        serializer = HandDetectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('asset_id', serializer.errors)
