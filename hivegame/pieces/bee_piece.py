from engine.hive_utils import HiveException
from hivegame.pieces.piece import HivePiece

from typing import TYPE_CHECKING
from hivegame.utils import hexutil
if TYPE_CHECKING:
    from engine.hive import Hive

class BeePiece(HivePiece):

    def __new__(cls, color, number):
        return super().__new__(cls, color, "Q", number)

    def validate_move(self, hive: 'Hive', endcell: hexutil.Hex, pos: hexutil.Hex):
        if self.check_blocked(hive, pos):
            return False
        res = True
        # remove piece temporary
        del hive.level.tiles[pos]
        possible_end_cells = hive.bee_moves(pos)
        if not endcell in possible_end_cells:
            res = False
        hive.level.tiles[pos] = [self]
        return res

    def available_moves(self, hive: 'Hive', pos: hexutil.Hex):
        if self.check_blocked(hive, pos):
            return []
        return hive.bee_moves(pos)

    def available_moves_vector(self, hive: 'Hive', pos: hexutil.Hex):
        super().available_moves(hive, pos)
        if self.check_blocked(hive, pos):
            return [0] * 6
        result = []
        aval_moves = self.available_moves(hive, pos)
        for nb in pos.neighbours():
            if nb in aval_moves:
                result.append(1)
            else:
                result.append(0)
        return result

    @property
    def kind(self):
        return "Q"

    @property
    def move_vector_size(self):
        """
        :return: Size of the fixed-size move vector. Be can step to a maximum of 6 directions.
        """
        return 6
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "Q", self.number)

    def index_to_target_cell(self, hive: 'Hive', number: int, pos: hexutil.Hex):
        nbs = pos.neighbours()
        if nbs[number] not in self.available_moves(hive, pos):
            raise HiveException("Invalid action index of queen", 10000)
        return nbs[number]
