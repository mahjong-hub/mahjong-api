import uuid

from django.db import IntegrityError
from django.test import TestCase

from rule.constants import RulesetVersionStatus
from rule.factories import RulesetFactory, RulesetVersionFactory
from rule.models import RulesetVersion


class TestRulesetVersionModel(TestCase):
    def test_create_with_defaults(self):
        version = RulesetVersionFactory()

        self.assertIsInstance(version.id, uuid.UUID)
        self.assertIsNotNone(version.ruleset)
        self.assertEqual(version.status, RulesetVersionStatus.DRAFT.value)
        self.assertIsNotNone(version.created_at)
        self.assertIsNotNone(version.updated_at)

    def test_uuid_is_primary_key(self):
        version = RulesetVersionFactory()

        fetched = RulesetVersion.objects.get(pk=version.id)
        self.assertEqual(fetched.id, version.id)

    def test_unique_version_int_per_ruleset(self):
        ruleset = RulesetFactory()
        RulesetVersionFactory(ruleset=ruleset, version_int=1)

        with self.assertRaises(IntegrityError):
            RulesetVersion.objects.create(
                ruleset=ruleset,
                version_int=1,
                status=RulesetVersionStatus.DRAFT.value,
            )

    def test_same_version_int_different_rulesets_allowed(self):
        ruleset_a = RulesetFactory()
        ruleset_b = RulesetFactory()
        RulesetVersionFactory(ruleset=ruleset_a, version_int=1)
        version_b = RulesetVersionFactory(ruleset=ruleset_b, version_int=1)

        self.assertIsNotNone(version_b.id)

    def test_status_rejects_invalid_value(self):
        ruleset = RulesetFactory()

        with self.assertRaises(IntegrityError):
            RulesetVersion.objects.create(
                ruleset=ruleset,
                version_int=1,
                status='invalid_status',
            )

    def test_cascade_delete_with_ruleset(self):
        ruleset = RulesetFactory()
        version = RulesetVersionFactory(ruleset=ruleset)
        version_id = version.id

        ruleset.delete()

        self.assertFalse(RulesetVersion.objects.filter(pk=version_id).exists())

    def test_reverse_relation_on_ruleset(self):
        ruleset = RulesetFactory()
        version = RulesetVersionFactory(ruleset=ruleset)

        self.assertIn(version, ruleset.versions.all())
