import uuid

from django.test import TestCase

from rule.constants import ContextField, ContextOperator
from rule.factories import ContextConditionFactory, RuleLogicFactory
from rule.models import ContextCondition


class TestContextConditionModel(TestCase):
    def test_create_with_defaults(self):
        condition = ContextConditionFactory()

        self.assertIsInstance(condition.id, uuid.UUID)
        self.assertEqual(
            condition.context_field,
            ContextField.WIN_SOURCE.value,
        )
        self.assertEqual(condition.operator, ContextOperator.EQUALS.value)
        self.assertEqual(condition.value, 'self_draw')

    def test_uuid_is_primary_key(self):
        condition = ContextConditionFactory()

        fetched = ContextCondition.objects.get(pk=condition.id)
        self.assertEqual(fetched.id, condition.id)

    def test_cascade_delete_with_rule_logic(self):
        condition = ContextConditionFactory()
        condition_id = condition.id

        condition.rule_logic.delete()

        self.assertFalse(
            ContextCondition.objects.filter(pk=condition_id).exists(),
        )

    def test_reverse_relation_on_rule_logic(self):
        logic = RuleLogicFactory()
        ContextConditionFactory(rule_logic=logic)
        ContextConditionFactory(rule_logic=logic)

        self.assertEqual(logic.context_conditions.count(), 2)

    def test_context_field_stores_value(self):
        for cf in ContextField:
            condition = ContextConditionFactory(context_field=cf.value)
            condition.refresh_from_db()
            self.assertEqual(condition.context_field, cf.value)

    def test_operator_stores_value(self):
        for op in ContextOperator:
            condition = ContextConditionFactory(operator=op.value)
            condition.refresh_from_db()
            self.assertEqual(condition.operator, op.value)
