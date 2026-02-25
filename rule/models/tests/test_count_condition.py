import uuid

from django.test import TestCase

from hand.tiles import TileCode, TileSetCode
from rule.constants import Operator, TargetType
from rule.factories import CountConditionFactory, RuleLogicFactory
from rule.models import CountCondition


class TestCountConditionModel(TestCase):
    def test_create_with_defaults(self):
        condition = CountConditionFactory()

        self.assertIsInstance(condition.id, uuid.UUID)
        self.assertEqual(condition.target_type, TargetType.TILE.value)
        self.assertEqual(condition.operator, Operator.AT_LEAST.value)
        self.assertEqual(condition.value_int, 1)
        self.assertIsNone(condition.tile_code)
        self.assertIsNone(condition.tile_set_code)

    def test_uuid_is_primary_key(self):
        condition = CountConditionFactory()

        fetched = CountCondition.objects.get(pk=condition.id)
        self.assertEqual(fetched.id, condition.id)

    def test_cascade_delete_with_rule_logic(self):
        condition = CountConditionFactory()
        condition_id = condition.id

        condition.rule_logic.delete()

        self.assertFalse(
            CountCondition.objects.filter(pk=condition_id).exists(),
        )

    def test_reverse_relation_on_rule_logic(self):
        logic = RuleLogicFactory()
        CountConditionFactory(rule_logic=logic)
        CountConditionFactory(rule_logic=logic)

        self.assertEqual(logic.count_conditions.count(), 2)

    def test_tile_code_accepts_valid_tile_code(self):
        condition = CountConditionFactory(tile_code=TileCode.CHARACTER_1.value)

        condition.refresh_from_db()
        self.assertEqual(condition.tile_code, TileCode.CHARACTER_1.value)

    def test_tile_set_code_accepts_valid_tile_set_code(self):
        condition = CountConditionFactory(
            tile_set_code=TileSetCode.HONORS.value,
        )

        condition.refresh_from_db()
        self.assertEqual(condition.tile_set_code, TileSetCode.HONORS.value)

    def test_tile_code_defaults_to_none(self):
        condition = CountConditionFactory()

        condition.refresh_from_db()
        self.assertIsNone(condition.tile_code)

    def test_tile_set_code_defaults_to_none(self):
        condition = CountConditionFactory()

        condition.refresh_from_db()
        self.assertIsNone(condition.tile_set_code)

    def test_target_type_tile_set(self):
        condition = CountConditionFactory(
            target_type=TargetType.TILE_SET.value,
        )

        condition.refresh_from_db()
        self.assertEqual(condition.target_type, TargetType.TILE_SET.value)
