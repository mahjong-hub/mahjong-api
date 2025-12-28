from django.test import TestCase

from hand.tiles import (
    TileCode,
    is_valid_tile_code,
    label_to_tile,
    validate_tile_counts,
)


class TestLabelToTile(TestCase):
    def test_valid_labels_return_correct_tile_code(self):
        test_cases = [
            ('1B', TileCode.BAMBOO_1),
            ('9B', TileCode.BAMBOO_9),
            ('1C', TileCode.CHARACTER_1),
            ('5D', TileCode.DOT_5),
            ('EW', TileCode.EAST_WIND),
            ('SW', TileCode.SOUTH_WIND),
            ('WW', TileCode.WEST_WIND),
            ('NW', TileCode.NORTH_WIND),
            ('RD', TileCode.RED_DRAGON),
            ('GD', TileCode.GREEN_DRAGON),
            ('WD', TileCode.WHITE_DRAGON),
            ('1F', TileCode.FLOWER_1),
            ('4F', TileCode.FLOWER_4),
            ('1S', TileCode.SEASON_1),
            ('4S', TileCode.SEASON_4),
        ]

        for label, expected_tile in test_cases:
            result = label_to_tile(label)
            self.assertEqual(
                result,
                expected_tile,
                f"label_to_tile('{label}') should return {expected_tile}",
            )

    def test_invalid_labels_return_none(self):
        invalid_labels = [
            'INVALID',
            '0B',
            '10B',
            'XX',
            '',
            'bamboo_1',
            '1b',
        ]

        for label in invalid_labels:
            result = label_to_tile(label)
            self.assertIsNone(
                result,
                f"label_to_tile('{label}') should return None",
            )


class TestIsValidTileCode(TestCase):
    def test_valid_codes_return_true(self):
        valid_codes = [
            '1B',
            '2B',
            '3B',
            '4B',
            '5B',
            '6B',
            '7B',
            '8B',
            '9B',
            '1C',
            '2C',
            '3C',
            '4C',
            '5C',
            '6C',
            '7C',
            '8C',
            '9C',
            '1D',
            '2D',
            '3D',
            '4D',
            '5D',
            '6D',
            '7D',
            '8D',
            '9D',
            'EW',
            'SW',
            'WW',
            'NW',
            'RD',
            'GD',
            'WD',
            '1F',
            '2F',
            '3F',
            '4F',
            '1S',
            '2S',
            '3S',
            '4S',
        ]

        for code in valid_codes:
            self.assertTrue(
                is_valid_tile_code(code),
                f"is_valid_tile_code('{code}') should return True",
            )

    def test_invalid_codes_return_false(self):
        invalid_codes = [
            'INVALID',
            '0B',
            '10B',
            'XX',
            '',
            'bamboo_1',
            '1b',
            '1X',
            'AB',
        ]

        for code in invalid_codes:
            self.assertFalse(
                is_valid_tile_code(code),
                f"is_valid_tile_code('{code}') should return False",
            )


class TestValidateTileCounts(TestCase):
    def test_empty_list_passes(self):
        errors = validate_tile_counts([])
        self.assertEqual(errors, [])

    def test_valid_counts_pass(self):
        tile_codes = ['1B', '2B', '3B', '4B', '5B']
        errors = validate_tile_counts(tile_codes)
        self.assertEqual(errors, [])

    def test_four_of_same_standard_tile_passes(self):
        tile_codes = ['1B', '1B', '1B', '1B']
        errors = validate_tile_counts(tile_codes)
        self.assertEqual(errors, [])

    def test_invalid_tile_code_returns_error(self):
        tile_codes = ['INVALID']
        errors = validate_tile_counts(tile_codes)

        self.assertEqual(len(errors), 1)
        self.assertIn('Invalid tile code', errors[0])
        self.assertIn('INVALID', errors[0])

    def test_standard_tile_more_than_four_returns_error(self):
        tile_codes = ['1B', '1B', '1B', '1B', '1B']
        errors = validate_tile_counts(tile_codes)

        self.assertEqual(len(errors), 1)
        self.assertIn('1B', errors[0])
        self.assertIn('5 times', errors[0])
        self.assertIn('max is 4', errors[0])

    def test_unique_tile_more_than_one_returns_error(self):
        tile_codes = ['1F', '1F']
        errors = validate_tile_counts(tile_codes)

        self.assertEqual(len(errors), 1)
        self.assertIn('1F', errors[0])
        self.assertIn('2 times', errors[0])
        self.assertIn('unique tile', errors[0])

    def test_season_is_unique_tile(self):
        tile_codes = ['1S', '1S']
        errors = validate_tile_counts(tile_codes)

        self.assertEqual(len(errors), 1)
        self.assertIn('1S', errors[0])
        self.assertIn('unique tile', errors[0])

    def test_multiple_errors_returned_together(self):
        tile_codes = ['1B', '1B', '1B', '1B', '1B', '1F', '1F', 'INVALID']
        errors = validate_tile_counts(tile_codes)

        self.assertEqual(len(errors), 3)

        error_text = ' '.join(errors)
        self.assertIn('1B', error_text)
        self.assertIn('1F', error_text)
        self.assertIn('INVALID', error_text)

    def test_different_flowers_allowed(self):
        tile_codes = ['1F', '2F', '3F', '4F']
        errors = validate_tile_counts(tile_codes)
        self.assertEqual(errors, [])

    def test_different_seasons_allowed(self):
        tile_codes = ['1S', '2S', '3S', '4S']
        errors = validate_tile_counts(tile_codes)
        self.assertEqual(errors, [])

    def test_mixed_valid_tiles(self):
        tile_codes = [
            '1B',
            '1B',
            '1B',
            '1B',
            '2C',
            '2C',
            '2C',
            'EW',
            'EW',
            'RD',
            '1F',
            '1S',
        ]
        errors = validate_tile_counts(tile_codes)
        self.assertEqual(errors, [])
