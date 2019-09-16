# piece.py
# Classes representing playing pieces

import abc
from typing import Optional

from hivegame.hive_utils import HiveException
import logging

from hivegame.utils import hexutil

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from hivegame.hive import Hive

class HivePiece(metaclass=abc.ABCMeta):
    """Representation of Playing Piece"""

    def __init__(self, color, number):
        self.color = color      # can be 'b' or 'w'
        self.number = number    # can be [1, 2, 3]

        self.position: Optional[hexutil.Hex] = None


    def __repr__(self):
        return "%s%s%s" % (self.color, "?", self.number)
    
    def check_blocked(self, hive: 'Hive'):
        """
        Check if the piece is blocked by a beetle. Returns True if blocked
        """
        if not self.position:
            logging.warning("Check_blocked called without having a position.")
            return False
        assert hive.level.get_tile_content(self.position)
        if hive.level.get_tile_content(self.position)[-1] == self:
            return False
        return True

    @abc.abstractproperty
    def kind(self):
        return "?"
    
    @abc.abstractmethod
    def validate_move(self, hive: 'Hive', end_cell: hexutil.Hex):
        return

    @abc.abstractmethod
    def available_moves(self, hive: 'Hive'):
        if not self.position:
            raise HiveException("Bug not yet placed.", 9997)
        return []

    @abc.abstractmethod
    def available_moves_vector(self, hive: 'Hive'):
        return []

    def index_to_target_cell(self, hive: 'Hive', number: int):
        aval_moves = self.available_moves(hive)
        if len(aval_moves) < number or number >= self.move_vector_size:
            raise HiveException("moving piece with action number is out of bounds", 10001)
        return aval_moves[number]

    @property
    @abc.abstractmethod
    def move_vector_size(self) -> int:
        return 0

    def __eq__(self, obj):
        return isinstance(obj, HivePiece) and str(obj) == str(self)

    def __hash__(self):
        return hash((self.color, self.kind, self.number))
