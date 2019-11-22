from typing import Set, Optional, Dict

from hivegame.utils import hexutil
from engine.hive_utils import Direction, Player
from hivegame.pieces.piece import HivePiece
from hivegame.pieces import piece_factory

import logging


class GameState(object):
    """Represents the state of the game"""

    def __init__(self):
        self.tiles = {}
        self.current_player = Player.WHITE

    def move_to(self, piece: HivePiece, pos:hexutil.Hex, target_cell: hexutil.Hex) -> None:
        old_cell = self.tiles.get(pos)
        assert old_cell  # dangling position
        old_cell.remove(piece)
        if not old_cell:  # no more bugs there
            # remove from dictionary
            del self.tiles[pos]
        pieces = self.get_tile_content(target_cell)
        if not pieces:
            self.tiles[target_cell] = [piece]
        else:
            pieces.append(piece)

    def append_to(self, piece: HivePiece, hexagon: hexutil.Hex) -> None:
        cell = self.tiles.get(hexagon)
        if not cell:
            self.tiles[hexagon] = [piece]
        else:
            cell.append(piece)

    def move_or_append_to(self, piece: HivePiece, hexagon: hexutil.Hex) -> None:
        pos = self.find_piece_position(piece)
        if pos:
            self.move_to(piece, pos, hexagon)
        else:
            self.append_to(piece, hexagon)

    def get_tile_content(self, hexagon):
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

    @staticmethod
    def get_direction_to(hex_from: hexutil.Hex, hex_to:hexutil.Hex) -> Optional[Direction]:
        hex_diff = hex_to - hex_from
        # Check if horizontal
        if hex_diff.y == 0:
            if hex_diff.x > 0:
                return Direction.HX_E
            elif hex_diff.x < 0:
                return Direction.HX_W
            else:
                # same tile
                return Direction.HX_O
        elif abs(hex_diff.x) != abs(hex_diff.y):
            # Not in line
            return None
        elif hex_diff.x > 0:
            if hex_diff.y > 0:
                return Direction.HX_SE
            else:
                return Direction.HX_NE
        else:
            if hex_diff.y > 0:
                return Direction.HX_SW
            else:
                return Direction.HX_NW

    def get_played_pieces(self, player_color: Optional[Player] = None) -> Set[HivePiece]:
        """
        Get pieces in play of the given color.
        :param player_color: Color of the bugs you are interested in. None means both.
        :return: A set of HivePiece items on board.
        """
        if player_color:
            return set([piece for tile in self.tiles.values() for piece in tile if piece.color == player_color])
        else:
            return set([piece for tile in self.tiles.values() for piece in tile])

    @staticmethod
    def _subset(p_set1, p_set2):
        return {p for p in p_set1 if str(p) not in [str(played) for played in p_set2]}

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
        played_p = self.get_played_pieces(player_color)
        return self._subset(all_pieces, played_p)

    def get_all_pieces(self, player_color: Optional[Player] = None) -> Set[HivePiece]:
        """
        Returns all pieces in a set. Those pieces which are already played should contain their position
        :param player_color: Color of the bugs you are interested in. None means both.
        :return: Set of all pieces.
        """
        result =  self.get_played_pieces(player_color).union(self.get_unplayed_pieces(player_color))
        if not len(result) == len(piece_factory.piece_set(Player.WHITE)) * 2:
            logging.error("{} != {}".format(len(result), len(piece_factory.piece_set(Player.WHITE)) * 2))
            assert False
        return result

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

    def occupied_surroundings(self, hexagon: hexutil.Hex):
        if not self.tiles:
            return []
        return [nb for nb in hexagon.neighbours() if nb in self.tiles.keys()]

    _dir_to_hex = {
        Direction.HX_W : hexutil.Hex(-2, 0),
        Direction.HX_E : hexutil.Hex(2, 0),
        Direction.HX_NE : hexutil.Hex(1, -1),
        Direction.HX_SE : hexutil.Hex(1, 1),
        Direction.HX_NW : hexutil.Hex(-1, -1),
        Direction.HX_SW : hexutil.Hex(-1, 1),
        Direction.HX_LOW : hexutil.Hex(0, 0), # under me TODO
        Direction.HX_UP : hexutil.Hex(0, 0), # over me
        Direction.HX_O : hexutil.Hex(0, 0)
    }

    def goto_direction(self, ref_hexagon: hexutil.Hex, poc: Direction) -> hexutil.Hex:
        if not self._dir_to_hex.get(poc):
            raise ValueError("Invalid direction")
        return ref_hexagon + self._dir_to_hex[poc]

    @staticmethod
    def get_mutual_neighbors(hex1: hexutil.Hex, hex2: hexutil.Hex) -> Set[hexutil.Hex]:
        return set(hex1.neighbours()).intersection(hex2.neighbours())

    def is_cell_free(self, hexagon:hexutil.Hex) -> bool:
        return not hexagon in self.tiles.keys()

    def find_piece_position(self, piece_to_find: HivePiece) -> Optional[hexutil.Hex]:
        for hexi, pieces in self.tiles.items():
            if piece_to_find in pieces:
                return hexi
        return None