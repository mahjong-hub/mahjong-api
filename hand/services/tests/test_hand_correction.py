from django.test import TestCase

from asset.constants import AssetRole
from asset.factories import AssetFactory, ClientFactory, UploadSessionFactory
from asset.models import AssetRef
from hand.constants import DetectionStatus
from hand.exceptions import DetectionHandMismatchError, InvalidTileDataError
from hand.models import Hand, HandDetection, HandTile
from hand.services.hand_correction import TileInput, create_hand_correction


class TestCreateHandCorrection(TestCase):
    def setUp(self):
        self.client = ClientFactory()
        self.hand = Hand.objects.create(client=self.client, source='camera')
        session = UploadSessionFactory(client=self.client)
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

    def test_creates_correction_with_tiles(self):
        tiles = [
            TileInput(tile_code='1B', sort_order=0),
            TileInput(tile_code='2B', sort_order=1),
            TileInput(tile_code='3B', sort_order=2),
        ]

        correction = create_hand_correction(
            hand=self.hand,
            tiles=tiles,
        )

        self.assertIsNotNone(correction.id)
        self.assertEqual(correction.hand_id, self.hand.id)
        self.assertIsNone(correction.detection)

        hand_tiles = HandTile.objects.filter(hand_correction=correction)
        self.assertEqual(hand_tiles.count(), 3)

        tile_codes = [t.tile_code for t in hand_tiles.order_by('sort_order')]
        self.assertEqual(tile_codes, ['1B', '2B', '3B'])

    def test_creates_correction_with_detection(self):
        tiles = [TileInput(tile_code='1B', sort_order=0)]

        correction = create_hand_correction(
            hand=self.hand,
            tiles=tiles,
            detection=self.detection,
        )

        self.assertEqual(correction.detection_id, self.detection.id)

    def test_updates_active_hand_correction(self):
        tiles = [TileInput(tile_code='1B', sort_order=0)]

        correction = create_hand_correction(
            hand=self.hand,
            tiles=tiles,
        )

        self.hand.refresh_from_db()
        self.assertEqual(self.hand.active_hand_correction_id, correction.id)

    def test_raises_mismatch_for_detection_from_other_hand(self):
        other_hand = Hand.objects.create(client=self.client, source='camera')
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

        tiles = [TileInput(tile_code='1B', sort_order=0)]

        with self.assertRaises(DetectionHandMismatchError):
            create_hand_correction(
                hand=self.hand,
                tiles=tiles,
                detection=other_detection,
            )

    def test_raises_invalid_tile_for_too_many_standard_tiles(self):
        # 5 of the same tile exceeds the max of 4
        tiles = [TileInput(tile_code='1B', sort_order=i) for i in range(5)]

        with self.assertRaises(InvalidTileDataError) as ctx:
            create_hand_correction(
                hand=self.hand,
                tiles=tiles,
            )

        self.assertIn('1B', ctx.exception.message)
        self.assertIn('5 times', ctx.exception.message)

    def test_raises_invalid_tile_for_duplicate_flower(self):
        # Flowers are unique, max 1 of each
        tiles = [
            TileInput(tile_code='1F', sort_order=0),
            TileInput(tile_code='1F', sort_order=1),
        ]

        with self.assertRaises(InvalidTileDataError) as ctx:
            create_hand_correction(
                hand=self.hand,
                tiles=tiles,
            )

        self.assertIn('1F', ctx.exception.message)
        self.assertIn('unique tile', ctx.exception.message)

    def test_raises_invalid_tile_for_invalid_tile_code(self):
        tiles = [TileInput(tile_code='INVALID', sort_order=0)]

        with self.assertRaises(InvalidTileDataError) as ctx:
            create_hand_correction(
                hand=self.hand,
                tiles=tiles,
            )

        self.assertIn('Invalid tile code', ctx.exception.message)

    def test_allows_max_standard_tiles(self):
        # 4 of the same tile is allowed
        tiles = [TileInput(tile_code='1B', sort_order=i) for i in range(4)]

        correction = create_hand_correction(
            hand=self.hand,
            tiles=tiles,
        )

        self.assertIsNotNone(correction.id)

    def test_allows_unique_flowers_and_seasons(self):
        tiles = [
            TileInput(tile_code='1F', sort_order=0),
            TileInput(tile_code='2F', sort_order=1),
            TileInput(tile_code='1S', sort_order=2),
            TileInput(tile_code='2S', sort_order=3),
        ]

        correction = create_hand_correction(
            hand=self.hand,
            tiles=tiles,
        )

        self.assertIsNotNone(correction.id)

    def test_returns_correction_with_prefetched_tiles(self):
        tiles = [
            TileInput(tile_code='1B', sort_order=0),
            TileInput(tile_code='2B', sort_order=1),
        ]

        correction = create_hand_correction(
            hand=self.hand,
            tiles=tiles,
        )

        # Should have tiles prefetched
        self.assertEqual(correction.tiles.count(), 2)
