from typing import Set, Optional, Dict

from hivegame.utils import hexutil
from hivegame.hive_utils import Direction, Player
from hivegame.pieces.piece import HivePiece
from hivegame.pieces import piece_factory

import logging


class GameState(object):
    """Represents the state of the game"""

    def __init__(self):
        self.tiles = {}
        self.current_player = Player.WHITE

    def move_or_append_to(self, piece, hexagon) -> None:
        # TODO IMPL movement part
        cell = self.tiles.get(hexagon)
        if not cell:
            self.tiles[hexagon] = [piece]
        else:
            cell.append(piece)

    def get_tile(self, hexagon):
        return self.tiles.get(hexagon)

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

    def get_direction_to(self, hex_to):
        hex_diff = hex_to - self
        # Check if horizontal
        if hex_diff.y == 0:
            if hex_diff.x > 0:
                return Direction.HX_E
            elif hex_diff.x < 0:
                return Direction.HX_W
            else:
                return None
        elif abs(hex_diff.x) != abs(hex_diff.y):
            # Not in line
            return ' '
        elif hex_diff.x > 0:
            if hex_diff.y > 0:
                return Direction.HX_NE
            else:
                return Direction.HX_SE
        else:
            if hex_diff.y > 0:
                return Direction.HX_NW
            else:
                return Direction.HX_SW

    def get_played_pieces(self, player_color: Optional[Player] = None) -> Set[HivePiece]:
        """
        Get pieces in play of the given color.
        :param player_color: Color of the bugs you are interested in. None means both.
        :return: A set of HivePiece items on board.
        """
        if player_color:
            if self.tiles:
                print(list(self.tiles.values())[0])
                print(list(self.tiles.values())[0][0])
            print([piece for piece in (tile for tile in self.tiles.values())])
            return set([piece for tile in self.tiles.values() for piece in tile if piece.color == player_color])
        else:
            return set([piece for tile in self.tiles.values() for piece in tile])

    def get_unplayed_pieces(self, player_color: Optional[Player] = None) -> Set[HivePiece]:
        """
        :param player_color: Color of the bugs you are interested in. None means both.
        :return: A set of HivePiece items which are not yet played
        """
        all_pieces = set()
        if player_color:
            all_pieces.update(piece_factory.piece_set(player_color))
        else:
            all_pieces.update(piece_factory.piece_set(Player.WHITE))
            all_pieces.update(piece_factory.piece_set(Player.BLACK))
        return all_pieces.difference(self.get_played_pieces(player_color))

    def available_kinds_to_place(self, player_color: Player) -> Dict[str,int]:
        unplayed = self.get_unplayed_pieces(player_color)
        logging.debug([piece.kind for piece in unplayed])
        result_dict = {}
        for piece in unplayed:
            if result_dict.get(piece.kind):
                result_dict[piece.kind] += 1
            else:
                result_dict[piece.kind] = 1
        return result_dict