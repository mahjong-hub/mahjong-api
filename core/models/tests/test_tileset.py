from django.db import IntegrityError
from django.test import TestCase

from core.factories import TileSetFactory
from core.models import TileSet


class TestTileSetModel(TestCase):
    def test_create_tileset(self):
        tileset = TileSetFactory(
            code='DRAGONS',
            description={
                'en': 'All dragon tiles',
                'zh-hk': '所有箭牌',
                'zh-cn': '所有箭牌',
            },
        )

        self.assertEqual(tileset.code, 'DRAGONS')

    def test_code_is_primary_key(self):
        TileSetFactory(code='TERMINALS')

        tileset = TileSet.objects.get(pk='TERMINALS')
        self.assertEqual(tileset.code, 'TERMINALS')

    def test_code_is_unique(self):
        TileSetFactory(code='SIMPLES')

        with self.assertRaises(IntegrityError):
            TileSet.objects.create(code='SIMPLES')

    def test_str_returns_code(self):
        tileset = TileSetFactory(code='HONORS')

        self.assertEqual(str(tileset), 'HONORS')

    def test_description_localised(self):
        tileset = TileSetFactory(
            code='WINDS',
            description={
                'en': 'All wind tiles',
                'zh-hk': '所有風牌',
                'zh-cn': '所有风牌',
            },
        )

        tileset.refresh_from_db()
        self.assertEqual(tileset.description.en, 'All wind tiles')
        self.assertEqual(tileset.description['zh-hk'], '所有風牌')
        self.assertEqual(tileset.description['zh-cn'], '所有风牌')

    def test_description_can_be_blank(self):
        tileset = TileSetFactory(code='EMPTY_DESC', description={})

        tileset.refresh_from_db()
        self.assertIsNotNone(tileset.description)
