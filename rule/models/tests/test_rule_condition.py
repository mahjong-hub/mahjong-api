import uuid

from django.db import IntegrityError
from django.test import TestCase

from rule.constants import ConditionType, Operator
from rule.factories import RuleConditionFactory, RuleLogicFactory
from rule.models import RuleCondition


class TestRuleConditionModel(TestCase):
    def test_create_with_defaults(self):
        condition = RuleConditionFactory()

        self.assertIsInstance(condition.id, uuid.UUID)
        self.assertEqual(condition.type, ConditionType.PUNG.value)
        self.assertEqual(condition.operator, Operator.AT_LEAST.value)
        self.assertEqual(condition.value, 1)
        self.assertIsNone(condition.target)
        self.assertIsNone(condition.context)

    def test_uuid_is_primary_key(self):
        condition = RuleConditionFactory()

        fetched = RuleCondition.objects.get(pk=condition.id)
        self.assertEqual(fetched.id, condition.id)

    def test_cascade_delete_with_rule_logic(self):
        condition = RuleConditionFactory()
        condition_id = condition.id

        condition.rule_logic.delete()

        self.assertFalse(
            RuleCondition.objects.filter(pk=condition_id).exists(),
        )

    def test_reverse_relation_on_rule_logic(self):
        logic = RuleLogicFactory()
        c1 = RuleConditionFactory(rule_logic=logic)
        c2 = RuleConditionFactory(rule_logic=logic)

        self.assertIn(c1, logic.conditions.all())
        self.assertIn(c2, logic.conditions.all())

    def test_value_can_be_null(self):
        condition = RuleConditionFactory(value=None)

        condition.refresh_from_db()
        self.assertIsNone(condition.value)

    def test_target_can_be_null(self):
        condition = RuleConditionFactory(target=None)

        condition.refresh_from_db()
        self.assertIsNone(condition.target)

    def test_context_can_be_null(self):
        condition = RuleConditionFactory(context=None)

        condition.refresh_from_db()
        self.assertIsNone(condition.context)

    def test_operator_rejects_invalid_value(self):
        logic = RuleLogicFactory()

        with self.assertRaises(IntegrityError):
            RuleCondition.objects.create(
                rule_logic=logic,
                operator='not_valid',
                type=ConditionType.PUNG.value,
            )

    def test_type_rejects_invalid_value(self):
        logic = RuleLogicFactory()

        with self.assertRaises(IntegrityError):
            RuleCondition.objects.create(
                rule_logic=logic,
                operator=Operator.AT_LEAST.value,
                type='not_valid',
            )

    def test_target_rejects_invalid_value(self):
        logic = RuleLogicFactory()

        with self.assertRaises(IntegrityError):
            RuleCondition.objects.create(
                rule_logic=logic,
                operator=Operator.AT_LEAST.value,
                type=ConditionType.PUNG.value,
                target='not_valid',
            )

    def test_context_rejects_invalid_value(self):
        logic = RuleLogicFactory()

        with self.assertRaises(IntegrityError):
            RuleCondition.objects.create(
                rule_logic=logic,
                operator=Operator.AT_LEAST.value,
                type=ConditionType.PUNG.value,
                context='not_valid',
            )
