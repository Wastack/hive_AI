from utils import hexutil
from utils.game_state import GameState


class HiveView(object):
    """Visual representation of the Hive game state."""

    def __init__(self, level: GameState):
        """game is an instance of the Hive class."""
        self.level = level

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        """text representation of the board + pieces."""

        tiles = self.level.tiles
        if not tiles:
            return "*"
        min_x = min([tile.x for tile in tiles.keys()])
        max_x = max([tile.x for tile in tiles.keys()])
        min_y = min([tile.y for tile in tiles.keys()])
        max_y = max([tile.y for tile in tiles.keys()])
        #print("min_x = {}, max_x= {}, min_y= {}, max_y= {}".format(min_x, max_x, min_y, max_y))

        char_table = [[' ' for x in range((max_x - min_x) * 2 + 6)] for y in range((max_y - min_y) * 2 + 6) ]
        for h, bugs in tiles.items():
            y_og = (h.y-min_y)*2+2
            x_og = (h.x-min_x)*2+2
            b = bugs[-1]
            char_table[y_og][x_og-2] = '|'
            char_table[y_og-1][x_og-1] = '/'
            char_table[y_og-1][x_og+1] = '\\'
            char_table[y_og][x_og-1] = b.color
            char_table[y_og][x_og] = b.kind
            char_table[y_og][x_og+1] = str(b.number)
            char_table[y_og][x_og+2] = '|'
            char_table[y_og+1][x_og+1] = '/'
            char_table[y_og+1][x_og-1] = '\\'
        result = ""
        for row in char_table:
            result += "`{}`\n".format("".join(row))
        return result

