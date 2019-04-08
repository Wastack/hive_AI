from hivegame.pieces.piece import HivePiece

class AntPiece(HivePiece):
    MAX_STEP_COUNT = 50
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
        """
        :return: available moves. The order of the list depends on the distance of the target cell.
        Cells in a shorter distance come first.
        """
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

    def available_moves_vector(self, hive):
        """
        It assumes that the ant can step onto a maximum of pre-specified number of cells
        """
        available_moves_count = len(self.available_moves(hive))
        assert available_moves_count < AntPiece.MAX_STEP_COUNT
        result = [1] * available_moves_count + [0] * (AntPiece.MAX_STEP_COUNT - available_moves_count)
        assert len(result) == AntPiece.MAX_STEP_COUNT
        return result

    @property
    def kind(self):
        return "A"

    @property
    def move_vector_size(self):
        return AntPiece.MAX_STEP_COUNT
    
    def __repr__(self):
        return "%s%s%s" % (self.color, "A", self.number)