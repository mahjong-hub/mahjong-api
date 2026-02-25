from enum import Enum


class RuleKind(Enum):
    PATTERN = 'pattern'
    BONUS = 'bonus'
    LIMIT = 'limit'
    SPECIAL = 'special'
    DORA_LIKE = 'dora_like'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class LogicType(Enum):
    STANDARD = 'standard'
    SPECIAL_SHAPE = 'special_shape'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class CombineOp(Enum):
    AND = 'and'
    OR = 'or'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class GroupType(Enum):
    CHOW = 'chow'
    PUNG = 'pung'
    KONG = 'kong'
    PAIR = 'pair'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class Operator(Enum):
    AT_LEAST = 'at_least'
    EXACTLY = 'exactly'
    NOT_EXISTS = 'not_exists'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class TargetType(Enum):
    TILE = 'tile'
    TILE_SET = 'tile_set'
    SEAT_WIND = 'seat_wind'
    ROUND_WIND = 'round_wind'
    ANY_HONOR = 'any_honor'
    ANY_TERMINAL = 'any_terminal'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

    @classmethod
    def count_choices(cls):
        return [
            (cls.TILE.value, cls.TILE.name),
            (cls.TILE_SET.value, cls.TILE_SET.name),
        ]


class SuitConstraint(Enum):
    SINGLE_SUIT = 'single_suit'
    SINGLE_SUIT_WITH_HONORS = 'single_suit_with_honors'
    NO_HONORS = 'no_honors'
    ALL_SUITS_REQUIRED = 'all_suits_required'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class ContextField(Enum):
    WIN_SOURCE = 'win_source'
    SEAT_WIND = 'seat_wind'
    ROUND_WIND = 'round_wind'
    IS_OPEN_HAND = 'is_open_hand'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class ContextOperator(Enum):
    EQUALS = 'equals'
    NOT_EQUALS = 'not_equals'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class SpecialShapeType(Enum):
    SEVEN_PAIRS = 'seven_pairs'
    THIRTEEN_ORPHANS = 'thirteen_orphans'
    NINE_GATES = 'nine_gates'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class WinSource(Enum):
    SELF_DRAW = 'self_draw'
    DISCARD = 'discard'
    ROB_KONG = 'rob_kong'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
