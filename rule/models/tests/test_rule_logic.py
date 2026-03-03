import uuid

from django.db import IntegrityError
from django.test import TestCase

from rule.constants import CombineOp
from rule.factories import RuleDefinitionFactory, RuleLogicFactory
from rule.models import RuleLogic


class TestRuleLogicModel(TestCase):
    def test_create_with_defaults(self):
        logic = RuleLogicFactory()

        self.assertIsInstance(logic.id, uuid.UUID)
        self.assertEqual(logic.combine_op, CombineOp.AND.value)

    def test_uuid_is_primary_key(self):
        logic = RuleLogicFactory()

        fetched = RuleLogic.objects.get(pk=logic.id)
        self.assertEqual(fetched.id, logic.id)

    def test_one_to_one_with_rule_definition(self):
        definition = RuleDefinitionFactory()
        logic = RuleLogicFactory(rule_definition=definition)

        self.assertEqual(logic.rule_definition, definition)
        self.assertEqual(definition.logic, logic)

    def test_cascade_delete_with_rule_definition(self):
        logic = RuleLogicFactory()
        logic_id = logic.id

        logic.rule_definition.delete()

        self.assertFalse(RuleLogic.objects.filter(pk=logic_id).exists())

    def test_combine_op_can_be_blank(self):
        logic = RuleLogicFactory(combine_op='')

        logic.refresh_from_db()
        self.assertEqual(logic.combine_op, '')

    def test_combine_op_rejects_invalid_value(self):
        definition = RuleDefinitionFactory()

        with self.assertRaises(IntegrityError):
            RuleLogic.objects.create(
                rule_definition=definition,
                combine_op='xor',
            )
