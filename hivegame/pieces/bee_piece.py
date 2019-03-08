from hivegame.pieces.piece import HivePiece

class BeePiece(HivePiece):
    def validate_move(self, hive, endcell):
        self.check_blocked(hive)
        return endcell in hive.bee_moves(self.position)