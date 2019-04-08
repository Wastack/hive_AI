from hivegame.pieces.piece import HivePiece

class BeePiece(HivePiece):
    def validate_move(self, hive, endcell):
        if self.check_blocked(hive):
            return False
        return endcell in hive.bee_moves(self.position)

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