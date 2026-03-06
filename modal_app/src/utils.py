SUPPORTED_MODEL_VERSIONS = ['v0', 'v1', 'v2']


def validate_model_version(version: str) -> str | None:
    """Validate if the provided model version is supported"""
    return version if version in SUPPORTED_MODEL_VERSIONS else None


VALID_TILE_CODES = [
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


def validate_tile_code(label: str) -> str | None:
    """Validate if the provided label corresponds to a known tile code.

    Returns None if the label is not a known tile.
    """
    return label if label in VALID_TILE_CODES else None
