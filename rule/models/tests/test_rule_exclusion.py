import uuid

from django.db import IntegrityError
from django.test import TestCase

from rule.factories import (
    RuleDefinitionFactory,
    RuleExclusionFactory,
    RulesetVersionFactory,
)
from rule.models import RuleExclusion


class TestRuleExclusionModel(TestCase):
    def test_create_with_defaults(self):
        exclusion = RuleExclusionFactory()

        self.assertIsInstance(exclusion.id, uuid.UUID)
        self.assertIsNotNone(exclusion.ruleset_version)
        self.assertIsNotNone(exclusion.rule)
        self.assertIsNotNone(exclusion.excludes)

    def test_uuid_is_primary_key(self):
        exclusion = RuleExclusionFactory()

        fetched = RuleExclusion.objects.get(pk=exclusion.id)
        self.assertEqual(fetched.id, exclusion.id)

    def test_unique_constraint(self):
        rule_a = RuleDefinitionFactory()
        rule_b = RuleDefinitionFactory()
        RuleExclusionFactory(rule=rule_a, excludes=rule_b)

        with self.assertRaises(IntegrityError):
            RuleExclusionFactory(rule=rule_a, excludes=rule_b)

    def test_no_self_exclusion(self):
        rule = RuleDefinitionFactory()

        with self.assertRaises(IntegrityError):
            RuleExclusionFactory(rule=rule, excludes=rule)

    def test_cascade_delete_with_rule_definition(self):
        rule_a = RuleDefinitionFactory()
        rule_b = RuleDefinitionFactory()
        exclusion = RuleExclusionFactory(rule=rule_a, excludes=rule_b)
        exclusion_id = exclusion.id

        rule_a.delete()

        self.assertFalse(
            RuleExclusion.objects.filter(pk=exclusion_id).exists(),
        )

    def test_cascade_delete_with_ruleset_version(self):
        version = RulesetVersionFactory()
        rule_a = RuleDefinitionFactory()
        rule_b = RuleDefinitionFactory()
        exclusion = RuleExclusionFactory(
            ruleset_version=version,
            rule=rule_a,
            excludes=rule_b,
        )
        exclusion_id = exclusion.id

        version.delete()

        self.assertFalse(
            RuleExclusion.objects.filter(pk=exclusion_id).exists(),
        )

    def test_reverse_relations(self):
        rule_a = RuleDefinitionFactory()
        rule_b = RuleDefinitionFactory()
        exclusion = RuleExclusionFactory(rule=rule_a, excludes=rule_b)

        self.assertIn(exclusion, rule_a.exclusions.all())
        self.assertIn(exclusion, rule_b.excluded_by.all())

    def test_reverse_relation_on_ruleset_version(self):
        version = RulesetVersionFactory()
        rule_a = RuleDefinitionFactory()
        rule_b = RuleDefinitionFactory()
        exclusion = RuleExclusionFactory(
            ruleset_version=version,
            rule=rule_a,
            excludes=rule_b,
        )

        self.assertIn(exclusion, version.exclusions.all())
