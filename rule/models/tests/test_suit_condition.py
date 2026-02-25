import uuid

from django.test import TestCase

from rule.constants import SuitConstraint
from rule.factories import RuleLogicFactory, SuitConditionFactory
from rule.models import SuitCondition


class TestSuitConditionModel(TestCase):
    def test_create_with_defaults(self):
        condition = SuitConditionFactory()

        self.assertIsInstance(condition.id, uuid.UUID)
        self.assertEqual(
            condition.suit_constraint,
            SuitConstraint.SINGLE_SUIT.value,
        )

    def test_uuid_is_primary_key(self):
        condition = SuitConditionFactory()

        fetched = SuitCondition.objects.get(pk=condition.id)
        self.assertEqual(fetched.id, condition.id)

    def test_cascade_delete_with_rule_logic(self):
        condition = SuitConditionFactory()
        condition_id = condition.id

        condition.rule_logic.delete()

        self.assertFalse(
            SuitCondition.objects.filter(pk=condition_id).exists(),
        )

    def test_reverse_relation_on_rule_logic(self):
        logic = RuleLogicFactory()
        SuitConditionFactory(rule_logic=logic)
        SuitConditionFactory(rule_logic=logic)

        self.assertEqual(logic.suit_conditions.count(), 2)

    def test_suit_constraint_stores_value(self):
        for sc in SuitConstraint:
            condition = SuitConditionFactory(suit_constraint=sc.value)
            condition.refresh_from_db()
            self.assertEqual(condition.suit_constraint, sc.value)
