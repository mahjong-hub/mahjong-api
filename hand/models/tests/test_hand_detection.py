from django.db import IntegrityError
from django.test import TestCase

from hand.factories import HandDetectionFactory


class TestHandDetectionModel(TestCase):
    def test_status_rejects_invalid_value(self):
        detection = HandDetectionFactory()
        detection.status = 'not_valid'

        with self.assertRaises(IntegrityError):
            detection.save()
