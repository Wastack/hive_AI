from __future__ import annotations
from hivegame.pieces.piece import HivePiece

from typing import TYPE_CHECKING
from hivegame.utils import hexutil
if TYPE_CHECKING:
    from hivegame.hive import Hive


class AntPiece(HivePiece):
    MAX_STEP_COUNT = 50

    def __new__(cls, color, number):
        return super().__new__(cls, color, "A", number)

    def validate_move(self, hive: 'Hive', end_cell: hexutil.Hex, pos: hexutil.Hex):
        if self.check_blocked(hive, pos):
            return False
        # remove piece temporary
        del hive.level.tiles[pos]

        toExplore = {pos}
        visited = {pos}
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

        hive.level.tiles[pos] = [self]
        return res
    
    def available_moves(self, hive: 'Hive', pos: hexutil.Hex):
        """
        :return: available moves. The order of the list depends on the distance of the target cell.
        Cells in a shorter distance come first.
        """
        super().available_moves(hive, pos)
        if self.check_blocked(hive, pos):
            return []
        # remove piece temporary
        del hive.level.tiles[pos]

        toExplore = {pos}
        visited = {pos}

        while len(toExplore) > 0:
            found = set()
            for c in toExplore:
                found.update(hive.bee_moves(c))
            found.difference_update(visited)

            visited.update(found)
            toExplore = found
        hive.level.tiles[pos] = [self]
        # cannot step to the same tile
        visited.remove(pos)
        return sorted(visited)

    def available_moves_vector(self, hive: 'Hive', pos: hexutil.Hex):
        """
        It assumes that the ant can step onto a maximum of pre-specifihive.locate('wA1')ed number of cells
        """
        if self.check_blocked(hive, pos):
            return [0] * self.move_vector_size
        available_moves_count = len(self.available_moves(hive, pos))
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