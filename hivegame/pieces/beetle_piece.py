from hivegame.pieces.piece import HivePiece

class BeetlePiece(HivePiece):
    def validate_move(self, hive, endcell):
        return endcell in self.available_moves(hive)

    def available_moves(self, hive):
        if self.check_blocked(hive):
            return []
        # temporarily remove beetle
        hive.piecesInCell[self.position].remove(self)

        res = []
        # are we on top of the hive?
        if len(hive.piecesInCell[self.position]) > 0:
            res = hive.board.get_surrounding(self.position)
        else:
            res = (hive.bee_moves(self.position) +
                hive.occupied_surroundings(self.position)
            )

        # restore beetle to it's original position
        hive.piecesInCell[self.position].append(self)

        return res

    def available_moves_vector(self, hive):
        if self.check_blocked(hive):
            return [0] * 6
        hive.piecesInCell[self.position].remove(self)

        res = []
        # are we on top of the hive?
        if len(hive.piecesInCell[self.position]) > 0:
            res = [1] * 6
        else:
            #  Clockwise, starting from West
            res = hive.bee_moves_vector(self.position)
            #  Clockwise, starting from West
            surroundings = hive.board.get_surrounding(self.position)
            res = [ok if not hive.is_cell_free(sur) else 1 for (ok, sur) in zip(res, surroundings)]

        # restore beetle to it's original position
        hive.piecesInCell[self.position].append(self)
        assert len(res) == 6
        return res
    
    @property
    def kind(self):
        return "B"

    @property
    def move_vector_size(self):
        """
        :return: Size of the fixed-size move vector. Beetle can step to a maximum of 6 directions.
        """
        return 6
            
    def __repr__(self):
        return "%s%s%s" % (self.color, "B", self.number)

    def index_to_target_cell(self, hive, number):
        aval_moves = self.available_moves(hive)
        num_in_list = sum(self.available_moves_vector(hive)[:number])
        return aval_moves[num_in_list]