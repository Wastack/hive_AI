from hivegame.pieces.piece import HivePiece
from hivegame.hive_utils import Direction

class GrassHopperPiece(HivePiece):
    directions = [
        Direction.HX_W,
        Direction.HX_NW,
        Direction.HX_NE,
        Direction.HX_E,
        Direction.HX_SE,
        Direction.HX_SW
    ]

    def validate_move(self, hive, endcell):
        return endcell in self.available_moves(hive)
    
    def available_moves(self, hive):
        if self.check_blocked(hive):
            return []
        result = []
        for direction in self.directions:
            next_cell = hive.board.get_dir_cell(self.position, direction)
            if hive.is_cell_free(next_cell):
                # no neighbor, can't jump that way
                continue
            while not hive.is_cell_free(next_cell):
                next_cell = hive.board.get_dir_cell(next_cell, direction)
            result.append(next_cell)
        return result

    def available_moves_vector(self, hive):
        if self.check_blocked(hive):
            return [0] * 6
        result = []
        for direction in self.directions:
            next_cell = hive.board.get_dir_cell(self.position, direction)
            # cannot jump if there is no adjacent tile that way
            result.append(0 if hive.is_cell_free(next_cell) else 1)
        assert len(result) == 6
        return result

    @property
    def kind(self):
        return "G"

    @property
    def move_vector_size(self):
        """
        :return: Size of the fixed-size move vector. Grasshopper can step to a maximum of 6 directions.
        """
        return 6
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "G", self.number)

    def index_to_target_cell(self, hive, number):
        aval_moves = self.available_moves(hive)
        num_in_list = sum(self.available_moves_vector(hive)[:number])
        return aval_moves[num_in_list]
    