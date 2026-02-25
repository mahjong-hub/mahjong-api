import uuid

from django.test import TestCase

from hand.tiles import TileCode, TileSetCode
from rule.constants import GroupType, Operator, TargetType
from rule.factories import GroupConditionFactory, RuleLogicFactory
from rule.models import GroupCondition


class TestGroupConditionModel(TestCase):
    def test_create_with_defaults(self):
        condition = GroupConditionFactory()

        self.assertIsInstance(condition.id, uuid.UUID)
        self.assertEqual(condition.group_type, GroupType.PUNG.value)
        self.assertEqual(condition.operator, Operator.AT_LEAST.value)
        self.assertEqual(condition.target_type, TargetType.TILE.value)
        self.assertTrue(condition.allow_open)
        self.assertTrue(condition.allow_closed)
        self.assertIsNone(condition.tile_code)
        self.assertIsNone(condition.tile_set_code)

    def test_uuid_is_primary_key(self):
        condition = GroupConditionFactory()

        fetched = GroupCondition.objects.get(pk=condition.id)
        self.assertEqual(fetched.id, condition.id)

    def test_cascade_delete_with_rule_logic(self):
        condition = GroupConditionFactory()
        condition_id = condition.id

        condition.rule_logic.delete()

        self.assertFalse(
            GroupCondition.objects.filter(pk=condition_id).exists(),
        )

    def test_reverse_relation_on_rule_logic(self):
        logic = RuleLogicFactory()
        GroupConditionFactory(rule_logic=logic)
        GroupConditionFactory(rule_logic=logic)

        self.assertEqual(logic.group_conditions.count(), 2)

    def test_value_int_can_be_null(self):
        condition = GroupConditionFactory(value_int=None)

        condition.refresh_from_db()
        self.assertIsNone(condition.value_int)

    def test_tile_code_accepts_valid_tile_code(self):
        condition = GroupConditionFactory(tile_code=TileCode.BAMBOO_1.value)

        condition.refresh_from_db()
        self.assertEqual(condition.tile_code, TileCode.BAMBOO_1.value)

    def test_tile_set_code_accepts_valid_tile_set_code(self):
        condition = GroupConditionFactory(
            tile_set_code=TileSetCode.DRAGONS.value,
        )

        condition.refresh_from_db()
        self.assertEqual(condition.tile_set_code, TileSetCode.DRAGONS.value)

    def test_tile_code_defaults_to_none(self):
        condition = GroupConditionFactory()

        condition.refresh_from_db()
        self.assertIsNone(condition.tile_code)

    def test_tile_set_code_defaults_to_none(self):
        condition = GroupConditionFactory()

        condition.refresh_from_db()
        self.assertIsNone(condition.tile_set_code)

    def test_group_type_stores_value(self):
        for gt in GroupType:
            condition = GroupConditionFactory(group_type=gt.value)
            condition.refresh_from_db()
            self.assertEqual(condition.group_type, gt.value)
