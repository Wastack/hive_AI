from hivegame.hive_utils import Direction
import logging

# classes that represent generic boards

# Board layout:
#
#  --- --- ---
# |0,0|1,0|2,0|
#  --- --- ---
# |0,1|1,1|2,1|
#  --- --- ---
# |0,2|1,2|2,2|
#  --- --- ---

# HexBoard layout:
#
#  / \ / \ / \ / \ / \
# |0,0|1,0|2,0|3,0|4,0|
#  \ / \ / \ / \ / \ / \
#   |0,1|1,1|2,1|3,1|4,1|
#  / \ / \ / \ / \ / \ /
# |0,2|1,2|2,2|3,2|4,2|
#  \ / \ / \ / \ / \ / \
#   |0,3|1,3|2,3|3,3|4,3|
#  / \ / \ / \ / \ / \ /
# |0,4|1,4|2,4|3,4|4,4|
#  \ / \ / \ / \ / \ /
#
# Point of Contact / Direction:
#
#    2/ \3
#   1|   |4
#    6\ /5
#
# 0 => o (origin/on-top)
# 1 => w (west)
# 2 => nw (north-west)
# 3 => ne (north-east)
# 4 => e (east)
# 5 => se (south-east)
# 6 => sw (south-west)

# A 'cell' is a coordinate representation of a board position (x, y)


class Board(object):
    """
    Representation of the virtual playing Board.
    Dynamic board that will extend to the required size when values are set.
    All positions of the board are initialized with "[]" value.
    """
    def __init__(self):
        # the board starts with one row and a column without pieces
        self.board = [[[]]]
        self.ref0x = 0
        self.ref0y = 0

    def _add_row(self, before=False):
        new_row = []
        row_size = len(self.board[0])
        for _ in range(row_size):
            new_row.append([])
        if not before:
            self.board.append(new_row)
        else:
            self.ref0y += 1
            self.board.insert(0, new_row)

    def _add_column(self, before=False):
        if before:
            self.ref0x += 1
        for row in self.board:
            if not before:
                row.append([])
            else:
                row.insert(0, [])

    def resize(self, x_y):
        """
        Resizes the board to include the position (x, y)
        returns the normalized (x, y)
        """
        (x, y) = x_y
        xx = self.ref0x + x
        yy = self.ref0y + y

        while xx < 0:
            self._add_column(before=True)
            xx += 1
        while xx >= len(self.board[0]):
            self._add_column()
        while yy < 0:
            self._add_row(before=True)
            yy += 1
        while yy >= len(self.board):
            self._add_row()
        return xx, yy

    def get_boundaries(self):
        """returns the coordinates of the board limits."""
        first_col = -self.ref0x
        first_row = -self.ref0y
        last_col = len(self.board[0]) + first_col - 1
        last_row = len(self.board) + first_row - 1
        return first_col, first_row, last_col, last_row
    
    def valid_cell(self, cell):
        (x, y) = cell
        first_col, first_row, last_col, last_row = self.get_boundaries()
        return first_col <= x <= last_col and first_row <= y <= last_row 

    def get_surrounding(self, x_y):
        """
        Returns a list with the surrounding positions sorted clockwise starting
        from the left
        """
        (x, y) = x_y
        return [(x-1, y), (x, y-1), (x+1, y), (x, y+1)]

    @staticmethod
    def get_w_xy(x_y):
        """
        Get X;Y coordinates for the west/left Cell
        """
        (x, y) = x_y
        return x-1, y

    @staticmethod
    def get_e_xy(x_y):
        """
        Get X;Y coordinates for the east/right Cell
        """
        (x, y) = x_y
        return x+1, y


class HexBoard(Board):
    """Hexagonal Tile Board"""

    def __init__(self):

        super(HexBoard, self).__init__()
        self.dir2func = {
            Direction.HX_O: lambda x: x,
            Direction.HX_W: self.get_w_xy,
            Direction.HX_NW: self.get_nw_xy,
            Direction.HX_NE: self.get_ne_xy,
            Direction.HX_E: self.get_e_xy,
            Direction.HX_SE: self.get_se_xy,
            Direction.HX_SW: self.get_sw_xy
        }

    def get_surrounding(self, x_y):
        """
        Returns a list with the surrounding positions sorted clockwise starting
        from the left
        """
        (x, y) = x_y
        res = super(HexBoard, self).get_surrounding((x, y))
        # if in a even row we insert NW into position 1 and SW into position 5
        p = y % 2
        if p == 0:
            res.insert(1, (x-1, y-1))
            res.insert(5, (x-1, y+1))
        # if in a odd row we insert NE into position 2 and SE into position 4
        else:
            res.insert(2, (x+1, y-1))
            res.insert(4, (x+1, y+1))
        return res

    def get_dir_cell(self, cell, direction):
        """
        Translates a relative position (cell, direction) to the referred
        cell (x, y).

        direction in [0, 1, 2, 3, 4, 5, 6] and translates to:
        0 => o (origin/on-top)
        1 => w (west)
        2 => nw (north-west)
        3 => ne (north-east)
        4 => e (east)
        5 => se (south-east)
        6 => sw (south-west)
        """
        return self.dir2func[direction](cell)

    @staticmethod
    def get_nw_xy(x_y):
        """
        Get X;Y coordinates for the upper-left Cell
        """
        (x, y) = x_y
        p = y % 2
        nx = x - 1 + p
        ny = y - 1
        return nx, ny

    @staticmethod
    def get_ne_xy(x_y):
        """
        Get X;Y coordinates for the upper-right Cell
        """
        (x, y) = x_y
        p = y % 2
        nx = x + p
        ny = y - 1
        return nx, ny

    @staticmethod
    def get_sw_xy(x_y):
        """
        Get X;Y coordinates for the lower-left Cell
        """
        (x, y) = x_y
        p = y % 2
        nx = x - 1 + p
        ny = y + 1
        return nx, ny

    @staticmethod
    def get_se_xy(x_y):
        """
        Get X;Y coordinates for the lower-right Cell
        """
        (x, y) = x_y
        p = y % 2
        nx = x + p
        ny = y + 1
        return nx, ny

    @staticmethod
    def get_w_xy(x_y):
        """
        Get X;Y coordinates for the left Cell
        """
        (x, y) = x_y
        return x-1, y

    @staticmethod
    def get_e_xy(x_y):
        """
        Get X;Y coordinates for the right Cell
        """
        (x, y) = x_y
        return x+1, y

    def get_line_dir(self, cell0, cell1):
        """
        Returns the direction to take to go from cell0 to cell1 or None if it's
        not possible to go in a straight line.
        """
        # TODO FIXME functionally wrong sometimes

        (sx, sy) = cell0
        (ex, ey) = cell1
        dx = ex - sx
        dy = ey - sy
        p = sy % 2  # starting from an even or odd line?

        # is the same cell
        if dx == dy == 0:
            return Direction.HX_O

        # horizontal jump
        if dy == 0:
            # moving west
            if dx < 0:
                move_dir = Direction.HX_W
            # moving east
            else:
                move_dir = Direction.HX_E

        # diagonal jump (dy != 0)
        else:
            # must move in a diagonal with slope = 2
            nx = (abs(dy) + (1 - p)) // 2

            # TODO probably they should be placed out as a constant
            possible_adjacent_even_delta = {
                (-1, -1): Direction.HX_NW,
                (0, -1): Direction.HX_NE,
                (0, 1): Direction.HX_SE,
                (-1, 1): Direction.HX_SW
            }

            possible_adjacent_odd_delta = {
                (0, -1): Direction.HX_NW,
                (1, -1): Direction.HX_NE,
                (1, 1): Direction.HX_SE,
                (0, 1): Direction.HX_SW
            }

            # adjacent
            if abs(dy) == 1:
                if p == 0:
                    return possible_adjacent_even_delta.get((dx, dy))
                else:
                    return possible_adjacent_odd_delta.get((dx, dy))

            if abs(dx) != abs(nx):
                logging.debug("get_line_dir: abs(dx) != abs(nx). nx = {}".format(nx))
                return None

            if dx < 0:
                if dy < 0:
                    move_dir = Direction.HX_NW
                else:
                    move_dir = Direction.HX_SW
            else:
                if dy < 0:
                    move_dir = Direction.HX_NE
                else:
                    move_dir = Direction.HX_SE

        return move_dir
