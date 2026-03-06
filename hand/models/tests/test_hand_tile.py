from django.db import IntegrityError
from django.test import TestCase

from hand.factories import HandFactory
from hand.models import HandCorrection, HandTile


class TestHandTileModel(TestCase):
    def test_tile_code_rejects_invalid_value(self):
        correction = HandCorrection.objects.create(hand=HandFactory())

        with self.assertRaises(IntegrityError):
            HandTile.objects.create(
                hand_correction=correction,
                tile_code='XX',
            )
