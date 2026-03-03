import uuid

from django.db import IntegrityError
from django.test import TestCase

from rule.constants import RuleKind
from rule.factories import RuleDefinitionFactory
from rule.models import RuleDefinition


class TestRuleDefinitionModel(TestCase):
    def test_create_with_defaults(self):
        rule = RuleDefinitionFactory()

        self.assertIsInstance(rule.id, uuid.UUID)
        self.assertIsNotNone(rule.code)
        self.assertEqual(rule.kind, RuleKind.PATTERN.value)
        self.assertIsNotNone(rule.created_at)
        self.assertIsNotNone(rule.updated_at)

    def test_uuid_is_primary_key(self):
        rule = RuleDefinitionFactory()

        fetched = RuleDefinition.objects.get(pk=rule.id)
        self.assertEqual(fetched.id, rule.id)

    def test_code_is_unique(self):
        RuleDefinitionFactory(code='pinfu')

        with self.assertRaises(IntegrityError):
            RuleDefinition.objects.create(
                code='pinfu',
                label={'en': 'Pinfu'},
                kind=RuleKind.PATTERN.value,
            )

    def test_kind_stores_value(self):
        for kind in RuleKind:
            rule = RuleDefinitionFactory(
                code=f'rule_{kind.value}',
                kind=kind.value,
            )
            rule.refresh_from_db()
            self.assertEqual(rule.kind, kind.value)

    def test_label_is_localised(self):
        rule = RuleDefinitionFactory(
            code='tanyao',
            label={'en': 'All Simples', 'zh-hk': '斷么九', 'zh-cn': '断幺九'},
        )

        rule.refresh_from_db()
        self.assertEqual(rule.label.en, 'All Simples')
        self.assertEqual(rule.label['zh-hk'], '斷么九')
        self.assertEqual(rule.label['zh-cn'], '断幺九')

    def test_description_is_localised(self):
        rule = RuleDefinitionFactory(
            code='riichi',
            description={
                'en': 'Declare ready',
                'zh-hk': '立直',
                'zh-cn': '立直',
            },
        )

        rule.refresh_from_db()
        self.assertEqual(rule.description.en, 'Declare ready')
        self.assertEqual(rule.description['zh-hk'], '立直')

    def test_description_can_be_blank(self):
        rule = RuleDefinitionFactory(description={})

        rule.refresh_from_db()
        self.assertIsNotNone(rule.description)

    def test_default_ordering_by_code(self):
        RuleDefinitionFactory(code='tanyao')
        RuleDefinitionFactory(code='pinfu')
        RuleDefinitionFactory(code='riichi')

        codes = list(RuleDefinition.objects.values_list('code', flat=True))
        self.assertEqual(codes, sorted(codes))

    def test_kind_rejects_invalid_value(self):
        with self.assertRaises(IntegrityError):
            RuleDefinition.objects.create(
                code='invalid_kind_rule',
                label={'en': 'Test'},
                kind='not_a_valid_kind',
            )
