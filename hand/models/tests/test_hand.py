import uuid

from django.test import TestCase

from hand.constants import HandSource
from hand.factories import HandFactory
from hand.models import Hand
from user.factories import ClientFactory


class TestHandModel(TestCase):
    def setUp(self):
        self.client_obj = ClientFactory()

    def test_create_hand_with_defaults(self):
        hand = HandFactory(client=self.client_obj)

        self.assertIsInstance(hand.id, uuid.UUID)
        self.assertEqual(hand.client, self.client_obj)
        self.assertEqual(hand.source, HandSource.CAMERA.value)
        self.assertIsNotNone(hand.created_at)
        self.assertIsNotNone(hand.updated_at)

    def test_create_hand_with_manual_source(self):
        hand = HandFactory(
            client=self.client_obj,
            source=HandSource.MANUAL.value,
        )

        self.assertEqual(hand.source, HandSource.MANUAL.value)

    def test_create_hand_with_import_source(self):
        hand = HandFactory(
            client=self.client_obj,
            source=HandSource.IMPORT.value,
        )

        self.assertEqual(hand.source, HandSource.IMPORT.value)

    def test_hand_client_relationship(self):
        HandFactory(client=self.client_obj)
        HandFactory(client=self.client_obj)

        self.assertEqual(self.client_obj.hands.count(), 2)

    def test_hand_cascade_delete_with_client(self):
        HandFactory(client=self.client_obj)
        HandFactory(client=self.client_obj)

        self.assertEqual(Hand.objects.count(), 2)

        self.client_obj.delete()

        self.assertEqual(Hand.objects.count(), 0)

    def test_uuid_is_primary_key(self):
        hand = HandFactory(client=self.client_obj)

        fetched = Hand.objects.get(pk=hand.id)
        self.assertEqual(fetched.id, hand.id)
