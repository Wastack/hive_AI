from hivegame.pieces.piece import HivePiece

from typing import TYPE_CHECKING
from hivegame.utils import hexutil
if TYPE_CHECKING:
    from hivegame.hive import Hive


class BeetlePiece(HivePiece):
    def __new__(cls, color, number):
        return super().__new__(cls, color, "B", number)

    def validate_move(self, hive: 'Hive', endcell: hexutil.Hex, pos: hexutil.Hex):
        return endcell in self.available_moves(hive, pos)

    def available_moves(self, hive: 'Hive', pos: hexutil.Hex):
        super().available_moves(hive, pos)
        if self.check_blocked(hive, pos):
            return []
        res = []
        # are we on top of the hive?
        # TODO this practically does the trick, but not precise
        if len(hive.level.get_tile_content(pos)) > 1:
            res += pos.neighbours()
        else:
            # remove piece temporary
            del hive.level.tiles[pos]
            res += (hive.bee_moves(pos) +
                   hive.level.occupied_surroundings(pos)
                   )
            hive.level.tiles[pos] = [self]

        return res

    def available_moves_vector(self, hive: 'Hive', pos: hexutil.Hex):
        if self.check_blocked(hive, pos):
            return [0] * self.move_vector_size

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
        return "B"

    @property
    def move_vector_size(self):
        """
        :return: Size of the fixed-size move vector. Beetle can step to a maximum of 6 directions.
        """
        return 6
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "B", self.number)

    def index_to_target_cell(self, hive: 'Hive', number: int, pos: hexutil.Hex):
        aval_indexes = (i for i, v in enumerate(self.available_moves_vector(hive, pos)) if v > 0)
        assert number in aval_indexes
        return pos.neighbours()[number]