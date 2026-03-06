import uuid

from django.test import TestCase

from rule.factories import RulesetFactory
from rule.models import Ruleset
from user.factories import ClientFactory


class TestRulesetModel(TestCase):
    def test_create_with_defaults(self):
        ruleset = RulesetFactory()

        self.assertIsInstance(ruleset.id, uuid.UUID)
        self.assertIsNotNone(ruleset.name)
        self.assertIsNotNone(ruleset.created_at)
        self.assertIsNotNone(ruleset.updated_at)
        self.assertFalse(ruleset.is_public)

    def test_uuid_is_primary_key(self):
        ruleset = RulesetFactory()

        fetched = Ruleset.objects.get(pk=ruleset.id)
        self.assertEqual(fetched.id, ruleset.id)

    def test_client_can_be_null(self):
        ruleset = RulesetFactory(client=None)

        ruleset.refresh_from_db()
        self.assertIsNone(ruleset.client)

    def test_client_set_null_on_client_delete(self):
        client = ClientFactory()
        ruleset = RulesetFactory(client=client)
        ruleset_id = ruleset.id

        client.delete()

        fetched = Ruleset.objects.get(pk=ruleset_id)
        self.assertIsNone(fetched.client)

    def test_is_public_defaults_to_false(self):
        ruleset = RulesetFactory()

        self.assertFalse(ruleset.is_public)

    def test_reverse_relation_on_client(self):
        client = ClientFactory()
        ruleset = RulesetFactory(client=client)

        self.assertIn(ruleset, client.rulesets.all())
