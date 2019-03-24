from hivegame.pieces.piece import HivePiece
from hivegame.board import HexBoard

class GrassHopperPiece(HivePiece):
    directions = [
        HexBoard.HX_W,
        HexBoard.HX_NW,
        HexBoard.HX_NE,
        HexBoard.HX_E,
        HexBoard.HX_SE,
        HexBoard.HX_SW
    ]

    def validate_move(self, hive, endcell):
        return endcell in self.available_moves(hive)
    
    def available_moves(self, hive):
        if self.check_blocked(hive):
            return []
        result = []
        for direction in self.directions:
            next_cell = hive.board.get_dir_cell(self.position, direction)
            if hive.is_cell_free(next_cell):
                # no neighbor, can't jump that way
                continue
            while not hive.is_cell_free(next_cell):
                next_cell = hive.board.get_dir_cell(next_cell, direction)
            result.append(next_cell)
        return result

    @property
    def kind(self):
        return "G"
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "G", self.number)
    