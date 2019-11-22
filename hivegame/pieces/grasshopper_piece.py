from hivegame.pieces.piece import HivePiece
from engine.hive_utils import Direction, HiveException

from typing import TYPE_CHECKING, Optional
from hivegame.utils import hexutil
if TYPE_CHECKING:
    from engine.hive import Hive

class GrassHopperPiece(HivePiece):
    directions = [
        Direction.HX_W,
        Direction.HX_NW,
        Direction.HX_NE,
        Direction.HX_E,
        Direction.HX_SE,
        Direction.HX_SW
    ]

    def __new__(cls, color, number):
        return super().__new__(cls, color, "G", number)

    def validate_move(self, hive: 'Hive', endcell: hexutil.Hex, pos: hexutil.Hex):
        return endcell in self.available_moves(hive, pos)
    
    def available_moves(self, hive: 'Hive', pos: hexutil.Hex):
        super().available_moves(hive, pos)
        if self.check_blocked(hive, pos):
            return []
        result = []
        for direction in self.directions:
            target_cell = self._get_tile_in_direction(hive, pos, direction)
            if not target_cell:
                continue
            result.append(target_cell)
        return result

    def _get_tile_in_direction(self, hive: 'Hive', pos: hexutil.Hex, direction: Direction) -> Optional[hexutil.Hex]:
        next_cell = hive.level.goto_direction(pos, direction)
        if not hive.level.get_tile_content(next_cell):
            # no neighbor, can't jump that way
            return None
        while hive.level.get_tile_content(next_cell):
            next_cell = hive.level.goto_direction(next_cell, direction)
        return next_cell

    def available_moves_vector(self, hive: 'Hive', pos: hexutil.Hex):
        if self.check_blocked(hive, pos):
            return [0] * 6
        result = []
        for direction in self.directions:
            next_cell = hive.level.goto_direction(pos, direction)
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

    def index_to_target_cell(self, hive: 'Hive', number: int, pos: hexutil.Hex) -> hexutil.Hex:
        d = self.directions[number]
        res = self._get_tile_in_direction(hive, pos, d)
        if not res:
            raise HiveException("Invalid grasshopper action index", 10011)
        return res
    