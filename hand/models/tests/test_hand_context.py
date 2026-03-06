from django.db import IntegrityError
from django.test import TestCase

from hand.constants import Wind, WinMethod
from hand.factories import HandContextFactory, HandFactory
from hand.models import Hand, HandContext


class TestHandContextModel(TestCase):
    def test_create_with_defaults(self):
        ctx = HandContextFactory()
        self.assertIsNotNone(ctx.hand)
        self.assertEqual(ctx.seat_wind, Wind.EAST.value)
        self.assertEqual(ctx.round_wind, Wind.EAST.value)
        self.assertIsNone(ctx.win_method)

    def test_hand_is_primary_key(self):
        ctx = HandContextFactory()
        self.assertEqual(ctx.pk, ctx.hand_id)

    def test_seat_wind_rejects_invalid(self):
        with self.assertRaises(IntegrityError):
            HandContextFactory(seat_wind='X')

    def test_round_wind_rejects_invalid(self):
        with self.assertRaises(IntegrityError):
            HandContextFactory(round_wind='X')

    def test_win_method_rejects_invalid(self):
        with self.assertRaises(IntegrityError):
            HandContextFactory(win_method='teleport')

    def test_win_method_can_be_null(self):
        ctx = HandContextFactory(win_method=None)
        ctx.refresh_from_db()
        self.assertIsNone(ctx.win_method)

    def test_win_method_accepts_valid_values(self):
        for method in WinMethod:
            hand = HandFactory()
            ctx = HandContextFactory(hand=hand, win_method=method.value)
            ctx.refresh_from_db()
            self.assertEqual(ctx.win_method, method.value)

    def test_cascade_delete_with_hand(self):
        ctx = HandContextFactory()
        hand_id = ctx.hand_id
        Hand.objects.filter(pk=hand_id).delete()
        self.assertFalse(HandContext.objects.filter(hand_id=hand_id).exists())

    def test_reverse_relation_on_hand(self):
        ctx = HandContextFactory()
        hand = Hand.objects.get(pk=ctx.hand_id)
        self.assertEqual(hand.context, ctx)
