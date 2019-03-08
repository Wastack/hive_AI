from hivegame.pieces.piece import HivePiece

class AntPiece(HivePiece):
    def validate_move(self, hive, endcell):
        self.check_blocked(hive)
         # temporarily remove ant
        hive.piecesInCell[self.position].remove(str(self))

        toExplore = set([self.position])
        visited = set([self.position])
        res = False

        while len(toExplore) > 0:
            found = set()
            for c in toExplore:
                found.update(hive.bee_moves(c))
            found.difference_update(visited)
            # have we found the endCell?
            if endcell in found:
                res = True
                break

            visited.update(found)
            toExplore = found

        # restore ant to it's original position
        hive.piecesInCell[self.position].append(str(self))

        return res
    
    def __repr__(self):
        return "%s%s%s" % (self.color, "A", self.number)