import factory

from rule.constants import CombineOp, ConditionType, Operator, RuleKind
from rule.models import RuleCondition, RuleDefinition, RuleExclusion, RuleLogic


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
    combine_op = CombineOp.AND.value


class RuleConditionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleCondition

    rule_logic = factory.SubFactory(RuleLogicFactory)
    type = ConditionType.PUNG.value
    operator = Operator.AT_LEAST.value
    value = 1
    target = None
    context = None


class RuleExclusionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleExclusion

    rule = factory.SubFactory(RuleDefinitionFactory)
    excludes = factory.SubFactory(RuleDefinitionFactory)
