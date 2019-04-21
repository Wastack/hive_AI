# piece.py
# Classes representing playing pieces

import abc
from hivegame.hive_utils import HiveException
import functools

class HivePiece(metaclass=abc.ABCMeta):
    """Representation of Playing Piece"""

    def __init__(self, color, number):
        self.color = color      # can be 'b' or 'w'
        self.number = number    # can be [1, 2, 3]

        self.position = (None, None)


    def __repr__(self):
        return "%s%s%s" % (self.color, "?", self.number)
    
    def check_blocked(self, hive):
        """
        Check if the piece is blocked by a beetle. Returns True if blocked
        """
        if hive.piecesInCell[self.position][-1] == self:
            return False
        return True

    @abc.abstractproperty
    def kind(self):
        return "?"
    
    @abc.abstractmethod
    def validate_move(self, hive, end_cell):
        return

    @abc.abstractmethod
    def available_moves(self, hive):
        return []

    @abc.abstractmethod
    def available_moves_vector(self, hive):
        return []

    def index_to_target_cell(self, hive, number):
        aval_moves = self.available_moves(hive)
        if len(aval_moves) < number or number >= self.move_vector_size:
            raise HiveException
        return aval_moves[number]

    # TODO this can be static.
    @property
    @abc.abstractmethod
    def move_vector_size(self):
        return None