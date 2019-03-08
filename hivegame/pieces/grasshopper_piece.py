from hivegame.pieces.piece import HivePiece

class GrassHopperPiece(HivePiece):
    def validate_move(self, hive, endcell):
        self.check_blocked(hive)
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