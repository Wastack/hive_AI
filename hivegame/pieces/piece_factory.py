from .spider_piece import SpiderPiece
from .ant_piece import AntPiece
from .bee_piece import BeePiece
from .grasshopper_piece import GrassHopperPiece
from .beetle_piece import BeetlePiece

from collections import OrderedDict
from hivegame.hive_utils import Player
from typing import Set
from hivegame.pieces.piece import HivePiece


def piece_dict(color: Player) -> OrderedDict:
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


def piece_set(color: Player) -> Set[HivePiece]:
    """
    :param color: Color of the pieces you are interested in.
    :return: A list of pieces which are available to play
    """
    pieces = set()
    for i in range(1,4):
        pieces.add(AntPiece(color, i))
        pieces.add(GrassHopperPiece(color, i))
    for i in range(1,3):
        pieces.add(SpiderPiece(color, i))
        pieces.add(BeetlePiece(color, i))
    pieces.add(BeePiece(color, 1))
    return pieces

_kind_to_instance = {
    "A" : AntPiece,
    "Q" : BeePiece,
    "B" : BeetlePiece,
    "G" : GrassHopperPiece,
    "S" : SpiderPiece

}


def create_piece(color: Player, kind: str, number: int) -> HivePiece:
    return _kind_to_instance[kind](color, number)