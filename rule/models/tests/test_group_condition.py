import uuid

from django.db.models import ProtectedError
from django.test import TestCase

from core.factories import TileFactory, TileSetFactory
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

    def test_tile_code_fk(self):
        tile = TileFactory(code='1B', suit='B', rank=1)
        condition = GroupConditionFactory(tile_code=tile)

        condition.refresh_from_db()
        self.assertEqual(condition.tile_code, tile)

    def test_tile_set_code_fk(self):
        tile_set = TileSetFactory(code='DRAGONS')
        condition = GroupConditionFactory(tile_set_code=tile_set)

        condition.refresh_from_db()
        self.assertEqual(condition.tile_set_code, tile_set)

    def test_tile_protected_from_delete(self):
        tile = TileFactory(code='2B', suit='B', rank=2)
        GroupConditionFactory(tile_code=tile)

        with self.assertRaises(ProtectedError):
            tile.delete()

    def test_tile_set_protected_from_delete(self):
        tile_set = TileSetFactory(code='WINDS')
        GroupConditionFactory(tile_set_code=tile_set)

        with self.assertRaises(ProtectedError):
            tile_set.delete()

    def test_group_type_stores_value(self):
        for gt in GroupType:
            condition = GroupConditionFactory(group_type=gt.value)
            condition.refresh_from_db()
            self.assertEqual(condition.group_type, gt.value)
