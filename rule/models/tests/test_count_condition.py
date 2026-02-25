import uuid

from django.db.models import ProtectedError
from django.test import TestCase

from core.factories import TileFactory, TileSetFactory
from rule.constants import Operator
from rule.factories import CountConditionFactory, RuleLogicFactory
from rule.models import CountCondition


class TestCountConditionModel(TestCase):
    def test_create_with_defaults(self):
        condition = CountConditionFactory()

        self.assertIsInstance(condition.id, uuid.UUID)
        self.assertEqual(condition.target_type, 'tile')
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

    def test_tile_code_fk(self):
        tile = TileFactory(code='1C', suit='C', rank=1)
        condition = CountConditionFactory(tile_code=tile)

        condition.refresh_from_db()
        self.assertEqual(condition.tile_code, tile)

    def test_tile_set_code_fk(self):
        tile_set = TileSetFactory(code='HONORS')
        condition = CountConditionFactory(tile_set_code=tile_set)

        condition.refresh_from_db()
        self.assertEqual(condition.tile_set_code, tile_set)

    def test_tile_protected_from_delete(self):
        tile = TileFactory(code='2C', suit='C', rank=2)
        CountConditionFactory(tile_code=tile)

        with self.assertRaises(ProtectedError):
            tile.delete()

    def test_tile_set_protected_from_delete(self):
        tile_set = TileSetFactory(code='TERMINALS')
        CountConditionFactory(tile_set_code=tile_set)

        with self.assertRaises(ProtectedError):
            tile_set.delete()

    def test_target_type_tile_set(self):
        condition = CountConditionFactory(target_type='tile_set')

        condition.refresh_from_db()
        self.assertEqual(condition.target_type, 'tile_set')
