import uuid

from django.test import TestCase

from rule.constants import SpecialShapeType
from rule.factories import RuleLogicFactory, SpecialShapeConditionFactory
from rule.models import SpecialShapeCondition


class TestSpecialShapeConditionModel(TestCase):
    def test_create_with_defaults(self):
        condition = SpecialShapeConditionFactory()

        self.assertIsInstance(condition.id, uuid.UUID)
        self.assertEqual(
            condition.special_shape,
            SpecialShapeType.SEVEN_PAIRS.value,
        )

    def test_uuid_is_primary_key(self):
        condition = SpecialShapeConditionFactory()

        fetched = SpecialShapeCondition.objects.get(pk=condition.id)
        self.assertEqual(fetched.id, condition.id)

    def test_cascade_delete_with_rule_logic(self):
        condition = SpecialShapeConditionFactory()
        condition_id = condition.id

        condition.rule_logic.delete()

        self.assertFalse(
            SpecialShapeCondition.objects.filter(pk=condition_id).exists(),
        )

    def test_reverse_relation_on_rule_logic(self):
        logic = RuleLogicFactory()
        SpecialShapeConditionFactory(rule_logic=logic)
        SpecialShapeConditionFactory(rule_logic=logic)

        self.assertEqual(logic.shape_conditions.count(), 2)

    def test_special_shape_stores_value(self):
        for shape in SpecialShapeType:
            condition = SpecialShapeConditionFactory(special_shape=shape.value)
            condition.refresh_from_db()
            self.assertEqual(condition.special_shape, shape.value)
