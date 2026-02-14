from django.test import TestCase, override_settings

from asset.constants import AssetRole, UploadStatus
from asset.factories import AssetFactory, UploadSessionFactory
from asset.models import AssetRef
from hand.constants import DetectionStatus
from hand.factories import HandDetectionFactory, HandFactory
from hand.services.hand_detection import (
    create_detection,
    find_existing_detection,
)
from user.factories import ClientFactory


@override_settings(MODEL_VERSION='v0')
class TestFindExistingDetection(TestCase):
    def test_returns_none_when_no_asset_ref(self):
        session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
        asset = AssetFactory(upload_session=session, is_active=True)

        result = find_existing_detection(asset)

        self.assertIsNone(result)

    def test_returns_none_when_no_detection(self):
        client = ClientFactory()
        session = UploadSessionFactory(
            client=client,
            status=UploadStatus.COMPLETED.value,
        )
        asset = AssetFactory(upload_session=session, is_active=True)
        hand = HandFactory(client=client)
        AssetRef.attach(
            asset=asset,
            owner=hand,
            role=AssetRole.HAND_PHOTO.value,
        )

        result = find_existing_detection(asset)

        self.assertIsNone(result)

    def test_returns_existing_pending_detection(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.PENDING.value,
            model_version='v0',
        )
        asset = detection.asset_ref.asset

        result = find_existing_detection(asset)

        self.assertEqual(result.id, detection.id)

    def test_returns_existing_succeeded_detection(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.SUCCEEDED.value,
            model_version='v0',
        )
        asset = detection.asset_ref.asset

        result = find_existing_detection(asset)

        self.assertEqual(result.id, detection.id)

    def test_returns_none_when_detection_failed(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.FAILED.value,
            model_version='v0',
        )
        asset = detection.asset_ref.asset

        result = find_existing_detection(asset)

        self.assertIsNone(result)

    def test_returns_none_when_different_model_version(self):
        detection = HandDetectionFactory(
            status=DetectionStatus.SUCCEEDED.value,
            model_version='v1',
        )
        asset = detection.asset_ref.asset

        result = find_existing_detection(asset)

        self.assertIsNone(result)


@override_settings(MODEL_VERSION='v0')
class TestCreateDetection(TestCase):
    def test_creates_hand_asset_ref_detection(self):
        client = ClientFactory()
        session = UploadSessionFactory(
            client=client,
            status=UploadStatus.COMPLETED.value,
        )
        asset = AssetFactory(upload_session=session, is_active=True)

        detection = create_detection(
            asset=asset,
            client=client,
            source='camera',
        )

        self.assertIsNotNone(detection.id)
        self.assertEqual(detection.status, DetectionStatus.PENDING.value)

        # Verify Hand was created
        hand = detection.hand
        self.assertEqual(hand.client, client)
        self.assertEqual(hand.source, 'camera')

        # Verify AssetRef was created
        asset_ref = detection.asset_ref
        self.assertEqual(asset_ref.asset, asset)
        self.assertEqual(asset_ref.owner_id, hand.id)
        self.assertEqual(asset_ref.role, AssetRole.HAND_PHOTO.value)

        # Verify HandDetection fields
        self.assertEqual(detection.model_name, 'tile_detector')
        self.assertEqual(detection.model_version, 'v0')
