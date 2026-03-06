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
    IS = 'is'
    NONE = 'none'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class ConditionType(Enum):
    HAND = 'hand'  # whole-hand structure check
    CHOW = 'chow'  # chow meld count
    PUNG = 'pung'  # pung meld count
    KONG = 'kong'  # kong meld count
    PAIR = 'pair'  # pair count
    TILE = 'tile'  # individual tile count
    SUIT = 'suit'  # distinct suit count
    WIN = 'win'  # win condition check

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class ConditionTarget(Enum):
    HONOR = 'honor'
    DRAGON = 'dragon'
    WIND = 'wind'
    RED = 'red'
    GREEN = 'green'
    WHITE = 'white'
    TERMINAL = 'terminal'
    SIMPLE = 'simple'
    FLOWER = 'flower'
    BAMBOO = 'bamboo'
    DOT = 'dot'
    CHARACTER = 'character'
    STANDARD = 'standard'
    SEVEN_PAIRS = 'seven_pairs'
    THIRTEEN_ORPHANS = 'thirteen_orphans'
    NINE_GATES = 'nine_gates'
    ALL_GREEN = 'all_green'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class ConditionContext(Enum):
    CONCEALED = 'concealed'
    SEAT_WIND = 'seat_wind'
    ROUND_WIND = 'round_wind'
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

    @classmethod
    def win_modifier_values(cls):
        return [
            cls.CONCEALED.value,
            cls.ROB_KONG.value,
            cls.REPLACEMENT.value,
            cls.DOUBLE_REPLACEMENT.value,
            cls.LAST_TILE.value,
            cls.LAST_DISCARD.value,
            cls.HEAVENLY.value,
            cls.EARTHLY.value,
        ]
