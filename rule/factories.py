import factory

from rule.constants import (
    CombineOp,
    ContextField,
    ContextOperator,
    GroupType,
    LogicType,
    Operator,
    RuleKind,
    SpecialShapeType,
    SuitConstraint,
    TargetType,
)
from rule.models import (
    ContextCondition,
    CountCondition,
    GroupCondition,
    RuleDefinition,
    RuleLogic,
    SpecialShapeCondition,
    SuitCondition,
)


class RuleDefinitionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleDefinition
        django_get_or_create = ['code']

    code = factory.Sequence(lambda n: f'rule_{n}')
    label = factory.LazyAttribute(
        lambda o: {'en': o.code, 'zh-hk': o.code, 'zh-cn': o.code},
    )
    kind = RuleKind.PATTERN.value
    description = {}


class RuleLogicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleLogic

    rule_definition = factory.SubFactory(RuleDefinitionFactory)
    logic_type = LogicType.STANDARD.value
    combine_op = CombineOp.AND.value


class GroupConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GroupCondition

    rule_logic = factory.SubFactory(RuleLogicFactory)
    group_type = GroupType.PUNG.value
    operator = Operator.AT_LEAST.value
    value_int = 1
    target_type = TargetType.TILE.value


class SuitConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SuitCondition

    rule_logic = factory.SubFactory(RuleLogicFactory)
    suit_constraint = SuitConstraint.SINGLE_SUIT.value


class CountConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CountCondition

    rule_logic = factory.SubFactory(RuleLogicFactory)
    target_type = 'tile'
    operator = Operator.AT_LEAST.value
    value_int = 1


class ContextConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContextCondition

    rule_logic = factory.SubFactory(RuleLogicFactory)
    context_field = ContextField.WIN_SOURCE.value
    operator = ContextOperator.EQUALS.value
    value = 'self_draw'


class SpecialShapeConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SpecialShapeCondition

    rule_logic = factory.SubFactory(RuleLogicFactory)
    special_shape = SpecialShapeType.SEVEN_PAIRS.value
