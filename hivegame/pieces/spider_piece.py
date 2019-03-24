from hivegame.pieces.piece import HivePiece

class SpiderPiece(HivePiece):
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

    @property       
    def kind(self):
        return "S"

    def __repr__(self):
        return "%s%s%s" % (self.color, "S", self.number)