from hivegame.pieces.piece import HivePiece

class BeetlePiece(HivePiece):
    def validate_move(self, hive, endcell):
        self.check_blocked(hive)
        # temporarily remove beetle
        hive.piecesInCell[self.position].remove(str(self))

        res = False
        # are we on top of the hive?
        if len(hive.piecesInCell[self.position]) > 0:
            res = endcell in hive.board.get_surrounding(self.position)
        else:
            res = endcell in (
                hive.bee_moves(self.position) +
                hive.occupied_surroundings(self.position) # TODO
            )

        # restore beetle to it's original position
        hive.piecesInCell[self.position].append(str(self))

        return res
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "B", self.number)