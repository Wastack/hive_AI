from hivegame.pieces.piece import HivePiece

from typing import TYPE_CHECKING
from hivegame.utils import hexutil
if TYPE_CHECKING:
    from hivegame.hive import Hive

class BeePiece(HivePiece):
    def validate_move(self, hive: 'Hive', endcell: hexutil.Hex):
        if self.check_blocked(hive):
            return False
        res = True
        # remove piece temporary
        del hive.level.tiles[self.position]
        possible_end_cells = hive.bee_moves(self.position)
        if not endcell in possible_end_cells:
            res = False
        hive.level.tiles[self.position] = [self]
        return res

    def available_moves(self, hive: 'Hive'):
        if self.check_blocked(hive):
            return []
        return hive.bee_moves(self.position)

    def available_moves_vector(self, hive: 'Hive'):
        super().available_moves(hive)
        if self.check_blocked(hive):
            return [0] * 6
        result = []
        aval_moves = self.available_moves(hive)
        for nb in self.position.neighbours():
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

    def index_to_target_cell(self, hive: 'Hive', number: int):
        aval_moves = self.available_moves(hive)
        num_in_list = sum(self.available_moves_vector(hive)[:number])
        return aval_moves[num_in_list]
