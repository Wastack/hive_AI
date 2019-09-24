from hivegame.pieces.piece import HivePiece
from hivegame.hive_utils import Direction

from typing import TYPE_CHECKING
from hivegame.utils import hexutil
if TYPE_CHECKING:
    from hivegame.hive import Hive

class GrassHopperPiece(HivePiece):
    directions = [
        Direction.HX_W,
        Direction.HX_NW,
        Direction.HX_NE,
        Direction.HX_E,
        Direction.HX_SE,
        Direction.HX_SW
    ]

    def validate_move(self, hive: 'Hive', endcell: hexutil.Hex):
        return endcell in self.available_moves(hive)
    
    def available_moves(self, hive: 'Hive'):
        super().available_moves(hive)
        if self.check_blocked(hive):
            return []
        result = []
        for direction in self.directions:
            next_cell = hive.level.goto_direction(self.position, direction)
            if not hive.level.get_tile_content(next_cell):
                # no neighbor, can't jump that way
                continue
            while hive.level.get_tile_content(next_cell):
                next_cell = hive.level.goto_direction(next_cell, direction)
            result.append(next_cell)
        return result

    def available_moves_vector(self, hive: 'Hive'):
        if self.check_blocked(hive):
            return [0] * 6
        result = []
        for direction in self.directions:
            next_cell = hive.level.goto_direction(self.position, direction)
            # cannot jump if there is no adjacent tile that way
            result.append(1 if hive.level.get_tile_content(next_cell) else 0)
        assert len(result) == 6
        return result

    @property
    def kind(self):
        return "G"

    @property
    def move_vector_size(self):
        """
        :return: Size of the fixed-size move vector. Grasshopper can step to a maximum of 6 directions.
        """
        return 6
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "G", self.number)

    def index_to_target_cell(self, hive: 'Hive', number: int):
        aval_moves = self.available_moves(hive)
        # index of available moves, starting from 0
        num_in_list = sum(self.available_moves_vector(hive)[:number]) - 1
        assert len(aval_moves) > num_in_list
        return aval_moves[num_in_list]
    