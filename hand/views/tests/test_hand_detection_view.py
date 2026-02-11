import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from asset.constants import AssetRole, UploadStatus
from asset.factories import AssetFactory, ClientFactory, UploadSessionFactory
from asset.models import AssetRef
from hand.constants import DetectionStatus
from hand.models import Hand, HandDetection


class TestDetectionViewSetRetrieve(APITestCase):
    def test_success_pending(self):
        client = ClientFactory()
        hand = Hand.objects.create(client=client, source='camera')
        session = UploadSessionFactory(client=client)
        asset = AssetFactory(upload_session=session, is_active=True)
        asset_ref = AssetRef.attach(
            asset=asset,
            owner=hand,
            role=AssetRole.HAND_PHOTO.value,
        )
        detection = HandDetection.objects.create(
            hand=hand,
            asset_ref=asset_ref,
            status=DetectionStatus.PENDING.value,
            model_name='tile_detector',
            model_version='v0.1.0',
        )

        response = self.client.get(
            f'/hand/detection/{detection.id}/',
            HTTP_X_INSTALL_ID=client.install_id,
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
        client = ClientFactory()

        response = self.client.get(
            f'/hand/detection/{uuid.uuid4()}/',
            HTTP_X_INSTALL_ID=client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_ownership_returns_not_found(self):
        """Non-owned detections return 404 (queryset excludes them)."""
        client = ClientFactory()
        other_client = ClientFactory()
        hand = Hand.objects.create(client=client, source='camera')
        session = UploadSessionFactory(client=client)
        asset = AssetFactory(upload_session=session, is_active=True)
        asset_ref = AssetRef.attach(
            asset=asset,
            owner=hand,
            role=AssetRole.HAND_PHOTO.value,
        )
        detection = HandDetection.objects.create(
            hand=hand,
            asset_ref=asset_ref,
            status=DetectionStatus.PENDING.value,
        )

        response = self.client.get(
            f'/hand/detection/{detection.id}/',
            HTTP_X_INSTALL_ID=other_client.install_id,
        )

        # Queryset filtering returns 404, not 403 (doesn't reveal existence)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
