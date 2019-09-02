class HiveView(object):
    """Visual representation of the Hive game state."""

    def __init__(self, game):
        """game is an instance of the Hive class."""
        self.game = game

    def __repr__(self):
        """text representation of the board + pieces."""
        first_col, first_row, last_col, last_row = self.game.get_board_boundaries()
        res = "\n"
        for i in range(first_row, last_row + 1):
            p = i % 2
            # Top of the cells is also the bottom of the cells
            # for the previous row.
            if i > first_row:
                res += " \\" * p
            else:
                res += "  " * p
            for j in range(first_col, last_col + 1):
                res += " / \\"
            if i > first_row and p == 0:
                res += " /"
            res += "\n"
            # Center of the cells
            res += "  " * p
            for j in range(first_col, last_col + 1):
                pieces = self.game.get_pieces((j, i))
                if len(pieces) != 0:
                    piece_name = str(pieces[-1])[:3]
                else:
                    piece_name = "   "
                res += "|" + piece_name
            res += "|\n"
        p = last_row % 2
        res += "  " * p
        for j in range(first_col, last_col + 1):
            res += " \\ /"
        res += "\n"

        return res
    
    def print_pieces_with_coords(self):
        """Print coordinates of pieces for debug purposes"""
        first_col, first_row, last_col, last_row = self.game.get_board_boundaries()
        for i in range(first_row, last_row + 1):
            for j in range(first_col, last_col + 1):
                pieces = self.game.get_pieces((j, i))
                if len(pieces) != 0:
                    piece_name = str(pieces[-1])[:3]
                    print("({},{}): {}".format(i, j, piece_name))
