from hivegame.utils import hexutil

class GameState(object):
    """Represents the state of the game"""

    def __init__(self, size):
        tiles = {}
        #tiles[hexutil.Hex(0,0)] = 'S'
        #tiles[hexutil.Hex(2,0)] = 'Q'
        #tiles[hexutil.Hex(-1,1)] = 'B'
        self.tiles = tiles

    def get_tile(self, hexagon):
        return self.tiles.get(hexagon, ' ')

    def is_border(self, hexagon):
        for hexi in self.tiles.keys():
            if hexagon in hexi.neighbours():
                return True
        # If empty, the start point should behave as a border
        if not self.tiles and hexagon == hexutil.Hex(0, 0):
            return True
        return False

    def get_border_tiles(self) -> set:
        if not self.tiles:
            return {hexutil.Hex(0, 0)}
        neighbours = set()
        for hexi in self.tiles.keys():
            neighbours.update(hexi.neighbours())
        neighbours = neighbours.difference(self.tiles.keys())
        return neighbours
