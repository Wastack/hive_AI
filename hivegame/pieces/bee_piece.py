from hivegame.pieces.piece import HivePiece

class BeePiece(HivePiece):
    def validate_move(self, hive, endcell):
        if self.check_blocked(hive):
            return False
        possible_end_cells = hive.bee_moves(self.position)
        if not endcell in possible_end_cells:
            return False
        return True

    def available_moves(self, hive):
        if self.check_blocked(hive):
            return []
        return hive.bee_moves(self.position)

    def available_moves_vector(self, hive):
        if self.check_blocked(hive):
            return [0] * 6
        return hive.bee_moves_vector(self.position)

    @property
    def kind(self):
        return "Q"

    @property
    def move_vector_size(self):
        """
        :return: Size of the fixed-size move vector. Be can step to a maximum of 6 directions.
        """
        return 6
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "Q", self.number)

    def index_to_target_cell(self, hive, number):
        aval_moves = self.available_moves(hive)
        num_in_list = sum(self.available_moves_vector(hive)[:number])
        return aval_moves[num_in_list]
