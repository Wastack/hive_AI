from hive_utils import Player
from pieces import piece_factory
from pieces.ant_piece import AntPiece
from pieces.piece import HivePiece

wA1 = AntPiece("w", 1)
wA1_2 = piece_factory.name_to_piece("wA1")

print("wA1 types: {}, {}, {}".format(isinstance(wA1.color, str), isinstance(wA1.kind, str), isinstance(wA1.number, str)))
print("wA1 types: {}, {}, {}".format(isinstance(wA1_2.color, str), isinstance(wA1_2.kind, str), isinstance(wA1_2.number, str)))

#print(AntPiece(Player.WHITE, 1) == piece_factory.name_to_piece("wA1"))
#print(piece_factory.name_to_piece("wA1") == piece_factory.name_to_piece("wA1"))
#print(AntPiece("w", 1) == AntPiece("w", 1))
#
#
#print("compare: {}".format(wA1 == wA1_2))
#print("hash1: {}, hash2: {}".format(wA1.__hash__(), wA1_2.__hash__()))