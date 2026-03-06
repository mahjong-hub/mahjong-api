from enum import Enum


class Wind(Enum):
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'
    NORTH = 'N'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class WinMethod(Enum):
    """How the winning tile was acquired."""

    SELF_DRAW = 'self_draw'
    DISCARD = 'discard'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class WinModifier(Enum):
    """Special circumstances that apply to a winning hand.

    These modify scoring and are stored as individual rows on HandWinModifier
    so that multiple modifiers can apply to a single hand simultaneously.
    """

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


class HandSource(Enum):
    CAMERA = 'camera'
    MANUAL = 'manual'
    IMPORT = 'import'
    OTHER = 'other'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]


class DetectionStatus(Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'

    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
