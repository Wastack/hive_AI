# piece.py
# Classes representing playing pieces

import abc
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
    def validate_move(self, hive, endcell):
        return

    @abc.abstractmethod
    def available_moves(self, hive):
        return []