from hivegame.pieces.piece import HivePiece

class BeePiece(HivePiece):
    def validate_move(self, hive, endcell):
        if self.check_blocked(hive):
            return False
        return endcell in hive.bee_moves(self.position)

    def available_moves(self, hive):
        if self.check_blocked(hive):
            return []
        return hive.bee_moves(self.position)
    
    @property
    def kind(self):
        return "Q"
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "Q", self.number)