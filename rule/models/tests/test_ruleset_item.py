import uuid

from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase

from rule.factories import (
    RuleDefinitionFactory,
    RulesetItemFactory,
    RulesetVersionFactory,
)
from rule.models import RulesetItem


class TestRulesetItemModel(TestCase):
    def test_create_with_defaults(self):
        item = RulesetItemFactory()

        self.assertIsInstance(item.id, uuid.UUID)
        self.assertIsNotNone(item.ruleset_version)
        self.assertIsNotNone(item.rule_definition)
        self.assertEqual(item.value_int, 1)
        self.assertTrue(item.enabled)

    def test_uuid_is_primary_key(self):
        item = RulesetItemFactory()

        fetched = RulesetItem.objects.get(pk=item.id)
        self.assertEqual(fetched.id, item.id)

    def test_unique_rule_definition_per_version(self):
        version = RulesetVersionFactory()
        rule = RuleDefinitionFactory()
        RulesetItemFactory(ruleset_version=version, rule_definition=rule)

        with self.assertRaises(IntegrityError):
            RulesetItem.objects.create(
                ruleset_version=version,
                rule_definition=rule,
                value_int=2,
            )

    def test_same_rule_definition_different_versions_allowed(self):
        version_a = RulesetVersionFactory()
        version_b = RulesetVersionFactory()
        rule = RuleDefinitionFactory()
        RulesetItemFactory(ruleset_version=version_a, rule_definition=rule)
        item_b = RulesetItemFactory(
            ruleset_version=version_b,
            rule_definition=rule,
        )

        self.assertIsNotNone(item_b.id)

    def test_enabled_defaults_to_true(self):
        item = RulesetItemFactory()

        self.assertTrue(item.enabled)

    def test_enabled_can_be_false(self):
        item = RulesetItemFactory(enabled=False)

        item.refresh_from_db()
        self.assertFalse(item.enabled)

    def test_cascade_delete_with_ruleset_version(self):
        version = RulesetVersionFactory()
        item = RulesetItemFactory(ruleset_version=version)
        item_id = item.id

        version.delete()

        self.assertFalse(RulesetItem.objects.filter(pk=item_id).exists())

    def test_protect_prevents_rule_definition_delete(self):
        rule = RuleDefinitionFactory()
        RulesetItemFactory(rule_definition=rule)

        with self.assertRaises(ProtectedError):
            rule.delete()

    def test_reverse_relation_on_ruleset_version(self):
        version = RulesetVersionFactory()
        item = RulesetItemFactory(ruleset_version=version)

        self.assertIn(item, version.items.all())

    def test_reverse_relation_on_rule_definition(self):
        rule = RuleDefinitionFactory()
        item = RulesetItemFactory(rule_definition=rule)

        self.assertIn(item, rule.ruleset_items.all())
