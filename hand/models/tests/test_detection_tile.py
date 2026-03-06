from django.db import IntegrityError
from django.test import TestCase

from hand.factories import HandDetectionFactory
from hand.models import DetectionTile


class TestDetectionTileModel(TestCase):
    def test_tile_code_rejects_invalid_value(self):
        detection = HandDetectionFactory()

        with self.assertRaises(IntegrityError):
            DetectionTile.objects.create(
                detection=detection,
                tile_code='INVALID',
                x1=0,
                y1=0,
                x2=100,
                y2=100,
                confidence='0.9500',
            )
