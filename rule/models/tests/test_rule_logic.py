import uuid

from django.test import TestCase

from rule.constants import CombineOp, LogicType
from rule.factories import RuleDefinitionFactory, RuleLogicFactory
from rule.models import RuleLogic


class TestRuleLogicModel(TestCase):
    def test_create_with_defaults(self):
        logic = RuleLogicFactory()

        self.assertIsInstance(logic.id, uuid.UUID)
        self.assertEqual(logic.logic_type, LogicType.STANDARD.value)
        self.assertEqual(logic.combine_op, CombineOp.AND.value)
        self.assertIsNone(logic.min_match)
        self.assertEqual(logic.note, '')

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

    def test_min_match_can_be_null(self):
        logic = RuleLogicFactory(min_match=None)

        logic.refresh_from_db()
        self.assertIsNone(logic.min_match)

    def test_min_match_stores_value(self):
        logic = RuleLogicFactory(min_match=3)

        logic.refresh_from_db()
        self.assertEqual(logic.min_match, 3)

    def test_logic_type_stores_value(self):
        for lt in LogicType:
            definition = RuleDefinitionFactory(code=f'rule_{lt.value}')
            logic = RuleLogicFactory(
                rule_definition=definition,
                logic_type=lt.value,
            )
            logic.refresh_from_db()
            self.assertEqual(logic.logic_type, lt.value)
