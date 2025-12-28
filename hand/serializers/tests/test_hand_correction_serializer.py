import uuid

from django.test import TestCase

from asset.constants import AssetRole
from asset.factories import AssetFactory, ClientFactory, UploadSessionFactory
from asset.models import AssetRef
from hand.constants import DetectionStatus
from hand.models import Hand, HandCorrection, HandDetection, HandTile
from hand.serializers.hand_correction_serializer import (
    HandCorrectionSerializer,
    HandTileSerializer,
)


class TestHandTileSerializer(TestCase):
    def test_valid_tile_code_accepted(self):
        data = {'tile_code': '1B', 'sort_order': 0}
        serializer = HandTileSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['tile_code'], '1B')

    def test_invalid_tile_code_rejected(self):
        data = {'tile_code': 'INVALID', 'sort_order': 0}
        serializer = HandTileSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('tile_code', serializer.errors)

    def test_all_valid_tile_codes(self):
        valid_codes = [
            '1B',
            '2B',
            '3B',
            '4B',
            '5B',
            '6B',
            '7B',
            '8B',
            '9B',
            '1C',
            '2C',
            '3C',
            '4C',
            '5C',
            '6C',
            '7C',
            '8C',
            '9C',
            '1D',
            '2D',
            '3D',
            '4D',
            '5D',
            '6D',
            '7D',
            '8D',
            '9D',
            'EW',
            'SW',
            'WW',
            'NW',
            'RD',
            'GD',
            'WD',
            '1F',
            '2F',
            '3F',
            '4F',
            '1S',
            '2S',
            '3S',
            '4S',
        ]

        for code in valid_codes:
            data = {'tile_code': code, 'sort_order': 0}
            serializer = HandTileSerializer(data=data)
            self.assertTrue(
                serializer.is_valid(),
                f'Tile code {code} should be valid',
            )

    def test_serialization_output(self):
        client = ClientFactory()
        hand = Hand.objects.create(client=client, source='camera')
        correction = HandCorrection.objects.create(hand=hand)
        tile = HandTile.objects.create(
            hand_correction=correction,
            tile_code='1B',
            sort_order=0,
        )

        serializer = HandTileSerializer(instance=tile)

        self.assertEqual(serializer.data['tile_code'], '1B')
        self.assertEqual(serializer.data['sort_order'], 0)


class TestHandCorrectionSerializer(TestCase):
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

    def test_serialization_output(self):
        correction = HandCorrection.objects.create(
            hand=self.hand,
            detection=self.detection,
        )
        self.hand.active_hand_correction = correction
        self.hand.save()

        HandTile.objects.create(
            hand_correction=correction,
            tile_code='1B',
            sort_order=0,
        )
        HandTile.objects.create(
            hand_correction=correction,
            tile_code='2B',
            sort_order=1,
        )

        correction = HandCorrection.objects.prefetch_related('tiles').get(
            id=correction.id,
        )
        serializer = HandCorrectionSerializer(instance=correction)

        self.assertEqual(
            serializer.data['hand_correction_id'],
            str(correction.id),
        )
        self.assertEqual(len(serializer.data['tiles']), 2)
        self.assertTrue(serializer.data['is_active'])
        self.assertIn('created_at', serializer.data)

    def test_hand_id_required(self):
        data = {
            'tiles': [{'tile_code': '1B', 'sort_order': 0}],
        }
        serializer = HandCorrectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('hand_id', serializer.errors)

    def test_hand_id_must_exist(self):
        data = {
            'hand_id': str(uuid.uuid4()),
            'tiles': [{'tile_code': '1B', 'sort_order': 0}],
        }
        serializer = HandCorrectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('hand_id', serializer.errors)

    def test_hand_must_belong_to_client(self):
        other_client = ClientFactory()
        other_hand = Hand.objects.create(client=other_client, source='camera')

        data = {
            'hand_id': str(other_hand.id),
            'tiles': [{'tile_code': '1B', 'sort_order': 0}],
        }
        serializer = HandCorrectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('hand_id', serializer.errors)

    def test_detection_id_must_exist_if_provided(self):
        data = {
            'hand_id': str(self.hand.id),
            'detection_id': str(uuid.uuid4()),
            'tiles': [{'tile_code': '1B', 'sort_order': 0}],
        }
        serializer = HandCorrectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('detection_id', serializer.errors)

    def test_detection_id_optional(self):
        data = {
            'hand_id': str(self.hand.id),
            'tiles': [{'tile_code': '1B', 'sort_order': 0}],
        }
        serializer = HandCorrectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertTrue(serializer.is_valid())
        self.assertIsNone(serializer.validated_data.get('detection_id'))

    def test_tiles_required(self):
        data = {
            'hand_id': str(self.hand.id),
        }
        serializer = HandCorrectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('tiles', serializer.errors)

    def test_invalid_tile_code_rejected(self):
        data = {
            'hand_id': str(self.hand.id),
            'tiles': [{'tile_code': 'INVALID', 'sort_order': 0}],
        }
        serializer = HandCorrectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('tiles', serializer.errors)

    def test_is_active_computed_correctly_when_active(self):
        correction = HandCorrection.objects.create(hand=self.hand)
        self.hand.active_hand_correction = correction
        self.hand.save()

        correction = HandCorrection.objects.select_related('hand').get(
            id=correction.id,
        )
        serializer = HandCorrectionSerializer(instance=correction)

        self.assertTrue(serializer.data['is_active'])

    def test_is_active_computed_correctly_when_not_active(self):
        correction1 = HandCorrection.objects.create(hand=self.hand)
        correction2 = HandCorrection.objects.create(hand=self.hand)
        self.hand.active_hand_correction = correction2
        self.hand.save()

        correction1 = HandCorrection.objects.select_related('hand').get(
            id=correction1.id,
        )
        serializer = HandCorrectionSerializer(instance=correction1)

        self.assertFalse(serializer.data['is_active'])

    def test_create_saves_correction_and_tiles(self):
        data = {
            'hand_id': str(self.hand.id),
            'tiles': [
                {'tile_code': '1B', 'sort_order': 0},
                {'tile_code': '2B', 'sort_order': 1},
            ],
        }
        serializer = HandCorrectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )
        serializer.is_valid(raise_exception=True)
        correction = serializer.save()

        self.assertIsNotNone(correction.id)
        self.assertEqual(correction.hand_id, self.hand.id)
        self.assertEqual(correction.tiles.count(), 2)

    def test_create_with_detection(self):
        data = {
            'hand_id': str(self.hand.id),
            'detection_id': str(self.detection.id),
            'tiles': [{'tile_code': '1B', 'sort_order': 0}],
        }
        serializer = HandCorrectionSerializer(
            data=data,
            context={'install_id': self.client_obj.install_id},
        )
        serializer.is_valid(raise_exception=True)
        correction = serializer.save()

        self.assertEqual(correction.detection_id, self.detection.id)
