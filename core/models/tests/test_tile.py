from django.db import IntegrityError
from django.test import TestCase

from core.factories import TileFactory
from core.models import Tile


class TestTileModel(TestCase):
    def test_create_suited_tile(self):
        tile = TileFactory(
            code='1B',
            suit='B',
            rank=1,
            label={'en': '1 Bamboo', 'zh-hk': '一索', 'zh-cn': '一索'},
        )

        self.assertEqual(tile.code, '1B')
        self.assertEqual(tile.suit, 'B')
        self.assertEqual(tile.rank, 1)

    def test_create_honor_tile_with_null_rank(self):
        tile = TileFactory(code='EW', suit='HONOR', rank=None)

        self.assertIsNone(tile.rank)

    def test_code_is_primary_key(self):
        TileFactory(code='RD', suit='HONOR')

        tile = TileFactory(code='RD', suit='HONOR')  # get_or_create
        self.assertEqual(Tile.objects.filter(code='RD').count(), 1)
        self.assertEqual(tile.code, 'RD')

    def test_code_is_unique(self):
        TileFactory(code='1C', suit='C', rank=1)

        with self.assertRaises(IntegrityError):
            Tile.objects.create(
                code='1C',
                suit='C',
                rank=1,
                label={'en': '1 Character'},
            )

    def test_label_localised(self):
        tile = TileFactory(
            code='GD',
            suit='HONOR',
            label={'en': 'Green Dragon', 'zh-hk': '青龍', 'zh-cn': '青龙'},
        )

        tile.refresh_from_db()
        self.assertEqual(tile.label.en, 'Green Dragon')
        self.assertEqual(tile.label['zh-hk'], '青龍')
        self.assertEqual(tile.label['zh-cn'], '青龙')

    def test_default_ordering_by_suit_then_rank(self):
        TileFactory(code='2B', suit='B', rank=2)
        TileFactory(code='1B', suit='B', rank=1)
        TileFactory(code='EW', suit='HONOR', rank=None)

        tiles = list(Tile.objects.all())
        self.assertEqual(tiles[0].code, '1B')
        self.assertEqual(tiles[1].code, '2B')
        self.assertEqual(tiles[2].code, 'EW')
