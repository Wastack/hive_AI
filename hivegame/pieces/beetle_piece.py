from hivegame.pieces.piece import HivePiece

from typing import TYPE_CHECKING
from utils import hexutil
if TYPE_CHECKING:
    from hivegame.hive import Hive


class BeetlePiece(HivePiece):
    def validate_move(self, hive: 'Hive', endcell: hexutil.Hex):
        return endcell in self.available_moves(hive)

    def available_moves(self, hive: 'Hive'):
        super().available_moves(hive)
        if self.check_blocked(hive):
            return []

        res = []
        # are we on top of the hive?
        # TODO this practically does the trick, but not precise
        if len(hive.level.get_tile_content(self.position)) > 1:
            res = self.position.neighbours()
        else:
            res = (hive.bee_moves(self.position) +
                hive.level.occupied_surroundings(self.position)
            )

        return res

    def available_moves_vector(self, hive: 'Hive'):
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
        return "B"

    @property
    def move_vector_size(self):
        """
        :return: Size of the fixed-size move vector. Beetle can step to a maximum of 6 directions.
        """
        return 6
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "B", self.number)

    def index_to_target_cell(self, hive: 'Hive', number: int):
        aval_moves = self.available_moves(hive)
        num_in_list = sum(self.available_moves_vector(hive)[:number])
        assert len(aval_moves)  > num_in_list
        return aval_moves[num_in_list]