from __future__ import annotations
from hivegame.pieces.piece import HivePiece

from typing import TYPE_CHECKING
from utils import hexutil
if TYPE_CHECKING:
    from hivegame.hive import Hive


class AntPiece(HivePiece):
    MAX_STEP_COUNT = 50

    def validate_move(self, hive: 'Hive', end_cell: hexutil.Hex):
        if self.check_blocked(hive):
            return False
        # remove piece temporary
        del hive.level.tiles[self.position]

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

        hive.level.tiles[self.position] = [self]
        return res
    
    def available_moves(self, hive: 'Hive'):
        """
        :return: available moves. The order of the list depends on the distance of the target cell.
        Cells in a shorter distance come first.
        """
        super().available_moves(hive)
        if self.check_blocked(hive):
            return []
        # remove piece temporary
        del hive.level.tiles[self.position]

        toExplore = {self.position}
        visited = {self.position}

        while len(toExplore) > 0:
            found = set()
            for c in toExplore:
                found.update(hive.bee_moves(c))
            found.difference_update(visited)

            visited.update(found)
            toExplore = found
        hive.level.tiles[self.position] = [self]
        return sorted(visited)

    def available_moves_vector(self, hive: 'Hive'):
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