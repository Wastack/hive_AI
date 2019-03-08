from hivegame.pieces.piece import HivePiece

class SpiderPiece(HivePiece):
    def validate_move(self, hive, endcell):
        self.check_blocked(hive)
        # temporarily remove spider
        hive.piecesInCell[self.position].remove(str(self))

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
        hive.piecesInCell[self.position].append(str(self))

        return endcell in thirdStep