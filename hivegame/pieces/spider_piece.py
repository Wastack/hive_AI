from hivegame.pieces.piece import HivePiece

class SpiderPiece(HivePiece):
    MAX_STEP_COUNT = 15
    def validate_move(self, hive, endcell):
        return endcell in self.available_moves(hive)
    
    def available_moves(self, hive):
        if self.check_blocked(hive):
            return []
        # temporarily remove spider
        hive.piecesInCell[self.position].remove(self)

        visited = set()
        firstStep = set()
        secondStep = set()
        thirdStep = set()

        visited.add(self.position)

        firstStep.update(set(hive.bee_moves(self.position)))
        visited.update(firstStep)

        for c in firstStep:
            secondStep.update(set(hive.bee_moves(c)))
        secondStep.difference_update(visited)
        visited.update(secondStep)

        for c in secondStep:
            thirdStep.update(set(hive.bee_moves(c)))
        thirdStep.difference_update(visited)

        # restore spider to it's original position
        hive.piecesInCell[self.position].append(self)

        return thirdStep

    def available_moves_vector(self, hive):
        """
        It assumes that the ant can step onto a maximum of pre-specified number of cells
        """
        available_moves_count = len(self.available_moves(hive))
        assert available_moves_count < SpiderPiece.MAX_STEP_COUNT
        result = [1] * available_moves_count + [0] * (SpiderPiece.MAX_STEP_COUNT - available_moves_count)
        assert len(result) == SpiderPiece.MAX_STEP_COUNT
        return result

    @property
    def kind(self):
        return "S"

    @property
    def move_vector_size(self):
        """
        :return: Size of the fixed-size move vector.
        """
        return SpiderPiece.MAX_STEP_COUNT

    def __repr__(self):
        return "%s%s%s" % (self.color, "S", self.number)