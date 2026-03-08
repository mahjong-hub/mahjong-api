from collections import Counter
from enum import Enum

# Standard tiles have 4 copies in a mahjong set
MAX_STANDARD_TILE_COUNT = 4
MAX_UNIQUE_TILE_COUNT = 1


class TileCode(Enum):
    """
    Canonical tile codes for all mahjong tiles.

    Format:
    - Suited tiles: <rank><suit> (e.g., 1B = 1 Bamboo)
    - Winds: <direction>W (e.g., EW = East Wind)
    - Dragons: <color>D (e.g., RD = Red Dragon)
    - Flowers/Seasons: <num><type> (e.g., 1F = Flower 1)
    """

    # Bamboo (条/Tiao)
    BAMBOO_1 = '1B'
    BAMBOO_2 = '2B'
    BAMBOO_3 = '3B'
    BAMBOO_4 = '4B'
    BAMBOO_5 = '5B'
    BAMBOO_6 = '6B'
    BAMBOO_7 = '7B'
    BAMBOO_8 = '8B'
    BAMBOO_9 = '9B'

    # Character (万/Wan)
    CHARACTER_1 = '1C'
    CHARACTER_2 = '2C'
    CHARACTER_3 = '3C'
    CHARACTER_4 = '4C'
    CHARACTER_5 = '5C'
    CHARACTER_6 = '6C'
    CHARACTER_7 = '7C'
    CHARACTER_8 = '8C'
    CHARACTER_9 = '9C'

    # Dot (饼/Bing)
    DOT_1 = '1D'
    DOT_2 = '2D'
    DOT_3 = '3D'
    DOT_4 = '4D'
    DOT_5 = '5D'
    DOT_6 = '6D'
    DOT_7 = '7D'
    DOT_8 = '8D'
    DOT_9 = '9D'

    # Winds
    EAST_WIND = 'EW'
    SOUTH_WIND = 'SW'
    WEST_WIND = 'WW'
    NORTH_WIND = 'NW'

    # Dragons
    RED_DRAGON = 'RD'
    GREEN_DRAGON = 'GD'
    WHITE_DRAGON = 'WD'

    # Flowers
    FLOWER_1 = '1F'
    FLOWER_2 = '2F'
    FLOWER_3 = '3F'
    FLOWER_4 = '4F'

    # Seasons
    SEASON_1 = '1S'
    SEASON_2 = '2S'
    SEASON_3 = '3S'
    SEASON_4 = '4S'

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(tile.value, tile.name) for tile in cls]


class TileSetCode(Enum):
    BAMBOO = 'bamboo'
    CHARACTER = 'character'
    DOT = 'dot'
    WINDS = 'winds'
    DRAGONS = 'dragons'
    HONORS = 'honors'
    TERMINALS = 'terminals'
    SIMPLES = 'simples'
    FLOWERS = 'flowers'
    SEASONS = 'seasons'
    BONUS = 'bonus'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


# Tiles that are unique in a standard mahjong set (max 1 of each)
UNIQUE_TILES: frozenset[str] = frozenset(
    {
        TileCode.FLOWER_1.value,
        TileCode.FLOWER_2.value,
        TileCode.FLOWER_3.value,
        TileCode.FLOWER_4.value,
        TileCode.SEASON_1.value,
        TileCode.SEASON_2.value,
        TileCode.SEASON_3.value,
        TileCode.SEASON_4.value,
    },
)


def is_valid_tile_code(code: str) -> bool:
    """
    Check if a tile code string is valid.

    Args:
        code: The tile code to validate.

    Returns:
        True if the code is a valid TileCode value, False otherwise.
    """
    return code in {t.value for t in TileCode}


def validate_tile_counts(tile_codes: list[str]) -> list[str]:
    """
    Validate that tile counts don't exceed mahjong set limits.

    Rules:
    - Flowers and Seasons: max 1 of each (unique in set)
    - All other tiles: max 4 of each

    Args:
        tile_codes: List of tile code strings to validate.

    Returns:
        List of error messages. Empty list means validation passed.
    """
    errors = []
    counts = Counter(tile_codes)

    for tile_code, count in counts.items():
        if not is_valid_tile_code(tile_code):
            errors.append(f'Invalid tile code: {tile_code}')
            continue

        if tile_code in UNIQUE_TILES:
            if count > MAX_UNIQUE_TILE_COUNT:
                errors.append(
                    f'Tile {tile_code} appears {count} times, '
                    f'but max is {MAX_UNIQUE_TILE_COUNT} (unique tile)',
                )
        else:
            if count > MAX_STANDARD_TILE_COUNT:
                errors.append(
                    f'Tile {tile_code} appears {count} times, '
                    f'but max is {MAX_STANDARD_TILE_COUNT}',
                )

    return errors


def sort_tiles(tile_codes: list[str]) -> list[str]:
    """
    Sort tile codes in a standard order for display and processing.

    Order:
    1. Bamboo (1B-9B)
    2. Character (1C-9C)
    3. Dot (1D-9D)
    4. Winds (EW, SW, WW, NW)
    5. Dragons (RD, GD, WD)
    6. Flowers (1F-4F)
    7. Seasons (1S-4S)

    Args:
        tile_codes: List of tile code strings to sort.

    Returns:
        New list of tile codes sorted in the defined order.
    """
    tile_order = {tile.value: index for index, tile in enumerate(TileCode)}
    return sorted(
        tile_codes,
        key=lambda code: tile_order.get(code, float('inf')),
    )
