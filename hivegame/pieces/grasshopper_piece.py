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
        if self.check_blocked(hive):
            return False
        # is the move in only one direction?
        (sx, sy) = self.position
        (ex, ey) = endcell
        dx = ex - sx
        dy = ey - sy

        # horizontal jump
        if dy == 0:
            # must jump at least over one piece
            if abs(dx) <= 1:
                return False
        # diagonal jump (dy != 0)
        else:
            # must jump at least over one piece
            if abs(dy) <= 1:
                return False

        moveDir = hive.board.get_line_dir(self.position, endcell)
        # must move in a straight line
        if moveDir is None or moveDir == 0:
            return False

        # are all in-between cells occupied?
        c = hive.board.get_dir_cell(self.position, moveDir)
        while c != endcell:
            if hive.is_cell_free(c):
                return False
            c = hive.board.get_dir_cell(c, moveDir)

        # is the endCell free?
        if not hive.is_cell_free(endcell):
            return False

        return True
    
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

    def kind(self):
        return "G"
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "G", self.number)
    