from enum import IntEnum


class dotdict(dict):
    def __getattr__(self, name):
        return self[name]


class HiveException(Exception):
    """Base class for exceptions."""
    pass

class Direction(IntEnum):
    HX_O = 0  # origin/on-top
    HX_W = 1  # west
    HX_NW = 2  # north-west
    HX_NE = 3  # north-east
    HX_E = 4  # east
    HX_SE = 5  # south-east
    HX_SW = 6  # south-west
    HX_LOW = 7  # lower
    HX_UP = 8  # upper
