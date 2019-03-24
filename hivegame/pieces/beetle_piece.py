from hivegame.pieces.piece import HivePiece

class BeetlePiece(HivePiece):
    def validate_move(self, hive, endcell):
        return endcell in self.available_moves(hive)

    def available_moves(self, hive):
        if self.check_blocked(hive):
            return []
        # temporarily remove beetle
        hive.piecesInCell[self.position].remove(self)

        res = []
        # are we on top of the hive?
        if len(hive.piecesInCell[self.position]) > 0:
            res = hive.board.get_surrounding(self.position)
        else:
            res = (hive.bee_moves(self.position) +
                hive.occupied_surroundings(self.position)
            )

        # restore beetle to it's original position
        hive.piecesInCell[self.position].append(self)

        return res
    
    @property
    def kind(self):
        return "B"
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "B", self.number)