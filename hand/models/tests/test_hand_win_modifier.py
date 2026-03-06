from django.db import IntegrityError
from django.test import TestCase

from hand.factories import HandContextFactory, HandWinModifierFactory
from hand.models import HandContext, HandWinModifier
from rule.constants import ConditionContext


class TestHandWinModifierModel(TestCase):
    def test_create_with_defaults(self):
        mod = HandWinModifierFactory()
        self.assertIsNotNone(mod.id)
        self.assertEqual(mod.modifier, ConditionContext.LAST_TILE.value)

    def test_modifier_rejects_invalid(self):
        with self.assertRaises(IntegrityError):
            HandWinModifierFactory(modifier='invalid_modifier')

    def test_unique_modifier_per_context(self):
        ctx = HandContextFactory()
        HandWinModifierFactory(
            hand_context=ctx,
            modifier=ConditionContext.LAST_TILE.value,
        )
        with self.assertRaises(IntegrityError):
            HandWinModifierFactory(
                hand_context=ctx,
                modifier=ConditionContext.LAST_TILE.value,
            )

    def test_same_modifier_different_contexts_allowed(self):
        ctx1 = HandContextFactory()
        ctx2 = HandContextFactory()
        mod1 = HandWinModifierFactory(
            hand_context=ctx1,
            modifier=ConditionContext.LAST_TILE.value,
        )
        mod2 = HandWinModifierFactory(
            hand_context=ctx2,
            modifier=ConditionContext.LAST_TILE.value,
        )
        self.assertNotEqual(mod1.id, mod2.id)

    def test_cascade_delete_with_hand_context(self):
        mod = HandWinModifierFactory()
        ctx_id = mod.hand_context_id
        HandContext.objects.filter(pk=ctx_id).delete()
        self.assertFalse(
            HandWinModifier.objects.filter(hand_context_id=ctx_id).exists(),
        )

    def test_reverse_relation_on_hand_context(self):
        ctx = HandContextFactory()
        mod = HandWinModifierFactory(hand_context=ctx)
        self.assertIn(mod, ctx.win_modifiers.all())
