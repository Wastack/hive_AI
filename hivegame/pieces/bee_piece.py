from hivegame.pieces.piece import HivePiece

class BeePiece(HivePiece):
    def validate_move(self, hive, endcell):
        self.check_blocked(hive)
        return endcell in hive.bee_moves(self.position)
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "Q", self.number)