import factory

from rule.constants import (
    CombineOp,
    ConditionType,
    Operator,
    RuleKind,
    RulesetVersionStatus,
    ScoringUnit,
)
from rule.models import (
    RuleCondition,
    RuleDefinition,
    RuleExclusion,
    RuleLogic,
    Ruleset,
    RulesetItem,
    RulesetScoringConfig,
    RulesetVersion,
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


class RulesetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ruleset

    client = None
    name = factory.Sequence(lambda n: f'Ruleset {n}')
    country_code = 'HKG'
    is_public = False


class RulesetVersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RulesetVersion

    ruleset = factory.SubFactory(RulesetFactory)
    version_int = factory.Sequence(lambda n: n + 1)
    status = RulesetVersionStatus.DRAFT.value


class RuleExclusionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleExclusion

    ruleset_version = factory.SubFactory(RulesetVersionFactory)
    rule = factory.SubFactory(RuleDefinitionFactory)
    excludes = factory.SubFactory(RuleDefinitionFactory)


class RulesetScoringConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RulesetScoringConfig

    ruleset_version = factory.SubFactory(RulesetVersionFactory)
    scoring_unit = ScoringUnit.FAAN.value
    min_scoring_unit = None


class RulesetItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RulesetItem

    ruleset_version = factory.SubFactory(RulesetVersionFactory)
    rule_definition = factory.SubFactory(RuleDefinitionFactory)
    value_int = 1
    enabled = True
