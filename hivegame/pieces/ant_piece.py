from hivegame.pieces.piece import HivePiece

class AntPiece(HivePiece):
    def validate_move(self, hive, end_cell):
        if self.check_blocked(hive):
            return False
         # temporarily remove ant
        hive.piecesInCell[self.position].remove(self)

        toExplore = {self.position}
        visited = {self.position}
        res = False

        while len(toExplore) > 0:
            found = set()
            for c in toExplore:
                found.update(hive.bee_moves(c))
            found.difference_update(visited)
            # have we found the endCell?
            if end_cell in found:
                res = True
                break

            visited.update(found)
            toExplore = found

        # restore ant to it's original position
        hive.piecesInCell[self.position].append(self)

        return res
    
    def available_moves(self, hive):
        # TODO make this a generator and use it for validation
        if self.check_blocked(hive):
            return []
        hive.piecesInCell[self.position].remove(self)

        toExplore = {self.position}
        visited = {self.position}

        while len(toExplore) > 0:
            found = set()
            for c in toExplore:
                found.update(hive.bee_moves(c))
            found.difference_update(visited)

            visited.update(found)
            toExplore = found

        hive.piecesInCell[self.position].append(self)
        return visited

    @property
    def kind(self):
        return "A"
    
    def __repr__(self):
        return "%s%s%s" % (self.color, "A", self.number)