import uuid

from django.db import IntegrityError
from django.test import TestCase

from rule.constants import ScoringUnit
from rule.factories import RulesetScoringConfigFactory, RulesetVersionFactory
from rule.models import RulesetScoringConfig


class TestRulesetScoringConfigModel(TestCase):
    def test_create_with_defaults(self):
        config = RulesetScoringConfigFactory()

        self.assertIsInstance(config.id, uuid.UUID)
        self.assertIsNotNone(config.ruleset_version)
        self.assertEqual(config.scoring_unit, ScoringUnit.FAAN.value)
        self.assertIsNone(config.min_scoring_unit)

    def test_uuid_is_primary_key(self):
        config = RulesetScoringConfigFactory()

        fetched = RulesetScoringConfig.objects.get(pk=config.id)
        self.assertEqual(fetched.id, config.id)

    def test_one_to_one_with_ruleset_version(self):
        version = RulesetVersionFactory()
        config = RulesetScoringConfigFactory(ruleset_version=version)

        self.assertEqual(config.ruleset_version, version)
        self.assertEqual(version.scoring_config, config)

    def test_duplicate_config_for_same_version_raises(self):
        version = RulesetVersionFactory()
        RulesetScoringConfigFactory(ruleset_version=version)

        with self.assertRaises(IntegrityError):
            RulesetScoringConfig.objects.create(
                ruleset_version=version,
                scoring_unit=ScoringUnit.HAN.value,
            )

    def test_cascade_delete_with_ruleset_version(self):
        version = RulesetVersionFactory()
        config = RulesetScoringConfigFactory(ruleset_version=version)
        config_id = config.id

        version.delete()

        self.assertFalse(
            RulesetScoringConfig.objects.filter(pk=config_id).exists(),
        )

    def test_min_scoring_unit_can_be_null(self):
        config = RulesetScoringConfigFactory(min_scoring_unit=None)

        config.refresh_from_db()
        self.assertIsNone(config.min_scoring_unit)

    def test_min_scoring_unit_can_be_set(self):
        config = RulesetScoringConfigFactory(min_scoring_unit=3)

        config.refresh_from_db()
        self.assertEqual(config.min_scoring_unit, 3)

    def test_scoring_unit_rejects_invalid_value(self):
        version = RulesetVersionFactory()

        with self.assertRaises(IntegrityError):
            RulesetScoringConfig.objects.create(
                ruleset_version=version,
                scoring_unit='invalid_unit',
            )
