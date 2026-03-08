from enum import Enum


class RulesetVersionStatus(Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    DEPRECATED = 'deprecated'


class ScoringUnit(Enum):
    FAAN = 'faan'
    HAN = 'han'
    TAI = 'tai'
    POINTS = 'points'


class RuleKind(Enum):
    PATTERN = 'pattern'
    BONUS = 'bonus'
    LIMIT = 'limit'
    SPECIAL = 'special'
    DORA_LIKE = 'dora_like'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class CombineOp(Enum):
    AND = 'and'
    OR = 'or'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class Operator(Enum):
    AT_LEAST = 'at_least'
    AT_MOST = 'at_most'
    EXACTLY = 'exactly'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class ConditionType(Enum):
    """
    Defines the type of condition to check for a rule. This can be used to determine
    how to evaluate the condition.
    """

    HAND_STRUCTURE = 'hand_structure'  # whole-hand structure check
    CHOW_COUNT = 'chow_count'  # chow meld count
    PUNG_COUNT = 'pung_count'  # pung meld count
    KONG_COUNT = 'kong_count'  # kong meld count
    PAIR_COUNT = 'pair_count'  # pair count
    TILE_COUNT = 'tile_count'  # individual tile count
    SUIT_COUNT = 'suit_count'  # distinct suit count
    WIN_CONDITION = 'win_condition'  # win condition check

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class HandStructureTarget(Enum):
    """
    Targets for hand structure conditions, specifying the
    overall hand pattern to check for.
    """

    STANDARD = 'standard'
    SEVEN_PAIRS = 'seven_pairs'
    THIRTEEN_ORPHANS = 'thirteen_orphans'
    NINE_GATES = 'nine_gates'
    ALL_GREEN = 'all_green'
    ALL_CONCEALED = 'all_concealed'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class CountTarget(Enum):
    """
    Targets for chow/pung/kong/pair/tile count conditions.
    These specify what type of meld or tile the count condition applies to.
    """

    SIMPLE = 'simple'  # 2-8 of any suit
    TERMINAL = 'terminal'  # 1 or 9 of any suit
    HONOR = 'honor'  # any wind or dragon tile
    DRAGON = 'dragon'  # any of the three dragon tiles
    WIND = 'wind'  # any of the four wind tiles
    RED = 'red'  # red dragon tile
    GREEN = 'green'  # green dragon tile
    WHITE = 'white'  # white dragon tile
    BAMBOO = 'bamboo'  # 1-9 of bamboo suit
    DOT = 'dot'  # 1-9 of dot suit
    CHARACTER = 'character'  # 1-9 of character suit
    FLOWER = 'flower'  # any flower/season tile
    CONCEALED = 'concealed'  # only count concealed melds/tiles

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class WinContext(Enum):
    """
    Context for win condition checks, specifying the circumstances of the win.
    """

    SELF_DRAW = 'self_draw'
    ROB_KONG = 'rob_kong'
    REPLACEMENT = 'replacement'
    DOUBLE_REPLACEMENT = 'double_replacement'
    LAST_TILE = 'last_tile'
    LAST_DISCARD = 'last_discard'
    HEAVENLY = 'heavenly'
    EARTHLY = 'earthly'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class CountContext(Enum):
    """
    Context for count conditions, specifying when the count applies.
    """

    SEAT_WIND = 'seat_wind'
    ROUND_WIND = 'round_wind'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
