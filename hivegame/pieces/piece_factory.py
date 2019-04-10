from .spider_piece import SpiderPiece
from .ant_piece import AntPiece
from .bee_piece import BeePiece
from .grasshopper_piece import GrassHopperPiece
from .beetle_piece import BeetlePiece

from collections import OrderedDict


def piece_set(color):
    """
    Return a full set of hive pieces.
    The order of the pieces determines the structure of the action space's
    canonical representation.
    """
    piece_set = OrderedDict()
    for i in range(3):
        ant = AntPiece(color, i + 1)
        piece_set[str(ant)] = ant
        grasshopper = GrassHopperPiece(color, i + 1)
        piece_set[str(grasshopper)] = grasshopper
    for i in range(2):
        spider = SpiderPiece(color, i + 1)
        piece_set[str(spider)] = spider
        beetle = BeetlePiece(color, i + 1)
        piece_set[str(beetle)] = beetle
    queen = BeePiece(color, 1)
    piece_set[str(queen)] = queen
    return piece_set