import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from asset.constants import AssetRole
from asset.factories import AssetFactory, ClientFactory, UploadSessionFactory
from asset.models import AssetRef
from hand.constants import DetectionStatus
from hand.models import Hand, HandCorrection, HandDetection, HandTile


class TestHandCorrectionViewSetCreate(APITestCase):
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

    def test_success_with_valid_tiles(self):
        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(self.hand.id),
                'tiles': [
                    {'tile_code': '1B', 'sort_order': 0},
                    {'tile_code': '2B', 'sort_order': 1},
                    {'tile_code': '3B', 'sort_order': 2},
                ],
            },
            format='json',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(len(response.data['tiles']), 3)
        self.assertTrue(response.data['is_active'])

    def test_success_with_detection_id(self):
        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(self.hand.id),
                'detection_id': str(self.detection.id),
                'tiles': [{'tile_code': '1B', 'sort_order': 0}],
            },
            format='json',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        correction = HandCorrection.objects.get(
            id=response.data['id'],
        )
        self.assertEqual(correction.detection_id, self.detection.id)

    def test_missing_install_id_header(self):
        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(self.hand.id),
                'tiles': [{'tile_code': '1B', 'sort_order': 0}],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_hand_id(self):
        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(uuid.uuid4()),
                'tiles': [{'tile_code': '1B', 'sort_order': 0}],
            },
            format='json',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_hand_not_owned_by_client(self):
        other_client = ClientFactory()
        other_hand = Hand.objects.create(client=other_client, source='camera')

        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(other_hand.id),
                'tiles': [{'tile_code': '1B', 'sort_order': 0}],
            },
            format='json',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_tile_code(self):
        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(self.hand.id),
                'tiles': [{'tile_code': 'INVALID', 'sort_order': 0}],
            },
            format='json',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_too_many_duplicate_tiles(self):
        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(self.hand.id),
                'tiles': [
                    {'tile_code': '1B', 'sort_order': i} for i in range(5)
                ],
            },
            format='json',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_flower_tiles(self):
        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(self.hand.id),
                'tiles': [
                    {'tile_code': '1F', 'sort_order': 0},
                    {'tile_code': '1F', 'sort_order': 1},
                ],
            },
            format='json',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detection_not_found(self):
        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(self.hand.id),
                'detection_id': str(uuid.uuid4()),
                'tiles': [{'tile_code': '1B', 'sort_order': 0}],
            },
            format='json',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detection_from_other_hand(self):
        other_hand = Hand.objects.create(
            client=self.client_obj,
            source='camera',
        )
        other_asset_ref = AssetRef.attach(
            asset=self.asset,
            owner=other_hand,
            role=AssetRole.HAND_PHOTO.value,
        )
        other_detection = HandDetection.objects.create(
            hand=other_hand,
            asset_ref=other_asset_ref,
            status=DetectionStatus.SUCCEEDED.value,
            model_name='tile_detector',
            model_version='v0.1.0',
        )

        response = self.client.post(
            '/hand/correction/',
            {
                'hand_id': str(self.hand.id),
                'detection_id': str(other_detection.id),
                'tiles': [{'tile_code': '1B', 'sort_order': 0}],
            },
            format='json',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestHandCorrectionViewSetList(APITestCase):
    def setUp(self):
        self.client_obj = ClientFactory()
        self.hand = Hand.objects.create(
            client=self.client_obj,
            source='camera',
        )

    def test_success_returns_list(self):
        correction = HandCorrection.objects.create(hand=self.hand)
        HandTile.objects.create(
            hand_correction=correction,
            tile_code='1B',
            sort_order=0,
        )

        response = self.client.get(
            '/hand/correction/',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['id'],
            str(correction.id),
        )

    def test_filter_by_hand_id(self):
        correction1 = HandCorrection.objects.create(hand=self.hand)
        HandTile.objects.create(
            hand_correction=correction1,
            tile_code='1B',
            sort_order=0,
        )

        other_hand = Hand.objects.create(
            client=self.client_obj,
            source='camera',
        )
        correction2 = HandCorrection.objects.create(hand=other_hand)
        HandTile.objects.create(
            hand_correction=correction2,
            tile_code='2B',
            sort_order=0,
        )

        response = self.client.get(
            f'/hand/correction/?hand_id={self.hand.id}',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['id'],
            str(correction1.id),
        )

    def test_missing_install_id(self):
        response = self.client.get('/hand/correction/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_list_when_no_corrections(self):
        response = self.client.get(
            '/hand/correction/',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_only_returns_own_corrections(self):
        correction = HandCorrection.objects.create(hand=self.hand)
        HandTile.objects.create(
            hand_correction=correction,
            tile_code='1B',
            sort_order=0,
        )

        other_client = ClientFactory()

        response = self.client.get(
            '/hand/correction/',
            HTTP_X_INSTALL_ID=other_client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TestHandCorrectionViewSetRetrieve(APITestCase):
    def setUp(self):
        self.client_obj = ClientFactory()
        self.hand = Hand.objects.create(
            client=self.client_obj,
            source='camera',
        )
        self.correction = HandCorrection.objects.create(hand=self.hand)
        HandTile.objects.create(
            hand_correction=self.correction,
            tile_code='1B',
            sort_order=0,
        )
        HandTile.objects.create(
            hand_correction=self.correction,
            tile_code='2B',
            sort_order=1,
        )

    def test_success_with_tiles(self):
        response = self.client.get(
            f'/hand/correction/{self.correction.id}/',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['id'],
            str(self.correction.id),
        )
        self.assertEqual(len(response.data['tiles']), 2)

    def test_not_found(self):
        response = self.client.get(
            f'/hand/correction/{uuid.uuid4()}/',
            HTTP_X_INSTALL_ID=self.client_obj.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_owned_by_client(self):
        other_client = ClientFactory()

        response = self.client.get(
            f'/hand/correction/{self.correction.id}/',
            HTTP_X_INSTALL_ID=other_client.install_id,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_install_id(self):
        response = self.client.get(f'/hand/correction/{self.correction.id}/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
