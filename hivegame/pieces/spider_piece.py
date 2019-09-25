from hivegame.pieces.piece import HivePiece

from typing import TYPE_CHECKING
from hivegame.utils import hexutil
if TYPE_CHECKING:
    from hivegame.hive import Hive

class SpiderPiece(HivePiece):
    MAX_STEP_COUNT = 15

    def __new__(cls, color, number):
        return super().__new__(cls, color, "S", number)

    def validate_move(self, hive: 'Hive', endcell: hexutil.Hex, pos:hexutil.Hex):
        return endcell in self.available_moves(hive, pos)
    
    def available_moves(self, hive: 'Hive', pos:hexutil.Hex):
        super().available_moves(hive, pos)
        if self.check_blocked(hive, pos):
            return []

        # remove piece temporary
        del hive.level.tiles[pos]

        visited = set()
        firstStep = set()
        secondStep = set()
        thirdStep = set()

        visited.add(pos)

        firstStep.update(set(hive.bee_moves(pos)))
        visited.update(firstStep)

        for c in firstStep:
            secondStep.update(set(hive.bee_moves(c)))
        secondStep.difference_update(visited)
        visited.update(secondStep)

        for c in secondStep:
            thirdStep.update(set(hive.bee_moves(c)))
        thirdStep.difference_update(visited)

        hive.level.tiles[pos] = [self]
        return sorted(thirdStep)

    def available_moves_vector(self, hive: 'Hive', pos:hexutil.Hex):
        """
        It assumes that the ant can step onto a maximum of pre-specified number of cells
        """
        available_moves_count = len(self.available_moves(hive, pos))
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