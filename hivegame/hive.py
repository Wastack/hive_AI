from __future__ import annotations

from hivegame.utils.game_state import GameState
from hivegame.utils import hexutil

from hivegame.pieces.ant_piece import AntPiece
from hivegame.pieces.beetle_piece import BeetlePiece
from hivegame.pieces.grasshopper_piece import GrassHopperPiece
from hivegame.pieces.spider_piece import SpiderPiece
from hivegame.pieces.bee_piece import BeePiece
from hivegame.pieces.piece import HivePiece

from hivegame.hive_utils import Player, HiveException, GameStatus, Direction
from hivegame.utils.ascii_view import HiveView

import hivegame.hive_validation as valid
import hivegame.hive_representation as represent
import hivegame.pieces.piece_factory as piece_fact

import logging

from typing import List, Tuple, Optional, Union, Any


class Hive(object):
    """
    The Hive Game.
    This class enforces the game rules.
    """

    def __init__(self):
        self.level = GameState()

    def reset(self) -> None:
        """
        Prepare the game to be played
        """
        self.level = GameState()

    @property
    def current_player(self) -> Player:
        """
        :return: The current player
        """
        return self.level.current_player

    def get_piece_by_name(self, piece_name: str) -> HivePiece:
        """
        :param piece_name: 3 digit name of piece. E.g. wQ1
        :return: The piece object
        """
        # Look at the un-played pieces. If not found, look at the played pieces.
        pieces = self.level.get_all_pieces()
        for p in pieces:
            if str(p) == piece_name:
                return p
        raise HiveException("Piece name could not been recognized", 9998)

    def pass_turn(self):
        self.level.current_player = self._toggle_player(self.level.current_player)  # switch active player

    def locate(self, piece_name: str) -> hexutil.Hex:
        """
        Returns the cell where the piece is positioned.
        piece_name is a piece identifier (string)
        """
        p = self.get_piece_by_name(piece_name)
        return p.position

    @staticmethod
    def _toggle_player(player: Player):
        return Player.BLACK if player == Player.WHITE else Player.WHITE

    def action_piece_to(self, piece: HivePiece, target_cell: hexutil.Hex):
        """
        Performs an action with the given piece to the given target cell.
        If the place is already on board it means a movement. Otherwise it
        means a piece placement.
        """

        if piece.position is None:
            self._place_piece_to(piece, target_cell)
        else:
            self._move_piece_to(piece, target_cell)
        self.level.current_player = self._toggle_player(self.level.current_player)

    def validate_action(self, piece: HivePiece, target_cell: hexutil.Hex) -> bool:
        # movement
        if piece.position is None:
            if not valid.validate_turn(self, piece, 'place'):
                logging.info("Turn fault (movement)")
                return False

            if not valid.validate_place_piece(self, piece, target_cell):
                logging.info("Invalid piece placement")
                return False
        # placement
        if not valid.validate_turn(self, piece, 'place'):
            logging.info("Turn fault (placement)")
            return False

        if not valid.validate_place_piece(self, piece, target_cell):
            logging.info("Invalid piece placement")
            return False
        return True

    def _move_piece_to(self, piece: HivePiece, target_cell: hexutil.Hex) -> None:
        """
        Moves the given piece to the target cell.
        It does start a complete action, since it does
        not increment the turn value.
        """
        assert piece.position  # It should be already placed
        # is the move valid
        if not valid.validate_turn(self, piece, 'move'):
            raise HiveException("Invalid Piece Movement", 10002)

        if not valid.validate_move_piece(self, piece, target_cell):
            raise HiveException("Invalid Piece Movement", 10002)

        # Update piece and map
        self.level.move_or_append_to(piece, target_cell)

    def move_piece_without_action(self, piece_name: str, ref_piece_name: str, ref_direction: Direction) -> None:
        """
        Performs a step without action. It means the current player remains. Useful for testing or for console input.
        :param piece_name: The name of the piece to move
        :param ref_piece_name: The name of the piece the bug should be placed next to
        :param ref_direction: The direction which side of the referenced piece the piece should move to.
        """

        target_cell = self.poc2cell(ref_piece_name, ref_direction)
        piece = self.get_piece_by_name(piece_name)
        self._move_piece_to(piece, target_cell)

    def _place_piece_to(self, piece: HivePiece, to_cell: hexutil.Hex) -> None:
        """
        Places a piece to the given target cell.
        It does start a complete action, since it does
        not increment the turn value.
        """
        # is the placement valid
        if not valid.validate_turn(self, piece, 'place'):
            raise HiveException("Invalid Piece Placement", 10003)

        if not valid.validate_place_piece(self, piece, to_cell):
            logging.info("Invalid piece placement")
            raise HiveException("Invalid Piece Placement", 10003)

        self.level.move_or_append_to(piece, to_cell)

    def place_piece_without_action(self, piece_name: str, ref_piece_name: str = None, ref_direction: Direction = None)\
            -> None:
        """
        Place a piece on the playing board without performing an action.
        :param piece_name: The name of the piece to place
        :param ref_piece_name: The name of the piece the bug should be placed next to
        :param ref_direction: The direction which side of the referenced piece the piece should be placed to.
        """

        # if it's the first piece, we put it to cell (0, 0)
        if ref_piece_name is None:
            target_cell = hexutil.origin
        else:
            target_cell = self.poc2cell(ref_piece_name, ref_direction)
        piece = self.get_piece_by_name(piece_name)
        return self._place_piece_to(piece, target_cell)

    def check_victory(self) -> GameStatus:
        """
        Check the status of the game.
        :return: The status of the game (white wins | black wins | draw | unfinished)
        """
        white = False
        black = False
        res = GameStatus.UNFINISHED

        # if white queen is surrounded => black wins
        queen_tile = self.get_piece_by_name('wQ1').position
        if queen_tile and len(self.level.occupied_surroundings(queen_tile)) == 6:
            black = True
            res = GameStatus.BLACK_WIN

        # if black queen is surrounded => white wins
        queen_tile = self.get_piece_by_name('bQ1').position
        if queen_tile and len(self.level.occupied_surroundings(queen_tile)) == 6:
            white = True
            res = GameStatus.WHITE_WIN

        # if both queens are surrounded
        if white and black:
            res = GameStatus.DRAW

        return res

    def poc2cell(self, ref_piece: str, point_of_contract: Direction) -> hexutil.Hex:
        """
        Translates a relative position (piece, point of contact) into
        a hexagon
        """
        assert point_of_contract < 9
        ref_cell = self.locate(ref_piece)
        if not ref_cell:
            logging.error("Cannot find piece by name: {}".format(ref_piece))
            logging.debug(self)
            error_msg = "Cannot locate reference piece by name"
            raise HiveException(error_msg, 9996)

        if point_of_contract > 6:
            return ref_cell  # above or below
        return self.level.goto_direction(ref_cell, point_of_contract)

    def bee_moves(self, cell: hexutil.Hex) -> List[hexutil.Hex]:
        """
        A bee can move to an adjacent target position only if:
        - target position is free
        - and there is a piece adjacent to both the bee and that position
        - and there is a free cell that is adjacent to both the bee and the
          target position.
        :param cell: The hexagon the queen is currently at.
        :return: A list of hexagons where the queen can possibly go
        """
        available_hexes = []
        surroundings = cell.neighbours()
        for nb in surroundings:
            if not self.level.is_cell_free(nb):
                continue
            # does it have an adjacent free and an adjacent occupied cell that
            # is also adjacent to the starting cell
            mutual_nbs = list(GameState.get_mutual_neighbors(cell, nb))
            assert len(mutual_nbs) == 2  # there are always two of them
            if self.level.is_cell_free(mutual_nbs[0]) != self.level.is_cell_free(mutual_nbs[1]):
                available_hexes.append(nb)

        return available_hexes

    @staticmethod
    def _decode_action_number(action_number: int, player: Player) -> Tuple[str, Any]:
        # initial
        pieces = piece_fact.sorted_piece_list(player)
        pc = len(pieces)
        if action_number < pc - 1:
            pieces = [p for p in pieces if p.kind != 'Q']
            return 'init', pieces[action_number]
        action_number -= pc - 1

        # piece placement
        place_bound = pc * (pc - 1) * 6
        if action_number < place_bound:
            one_bug_bound = (pc - 1) * 6
            action_type = action_number % one_bug_bound
            piece_number = action_number // one_bug_bound
            adj_piece_number = action_type // 6
            direction = (action_type % 6) + 1  # starting from west, clockwise
            piece = pieces[piece_number]
            adj_piece = [p for p in pieces if p != piece][adj_piece_number]
            return 'place', (piece, adj_piece, direction)
        action_number -= place_bound

        # movement
        for piece in pieces:
            assert action_number >= 0
            # Find piece
            if action_number - piece.move_vector_size >= 0:
                action_number -= piece.move_vector_size
                continue
            return 'move', (piece, action_number)

        # Index overflow
        error_msg = "Invalid action number, out of bounds"
        logging.error(error_msg)
        raise HiveException(error_msg, 10010)

    def action_from_vector(self, action_number: int) -> (HivePiece, hexutil.Hex):
        """
        Maps an action number to an actual action. The fixed size action space is explained
        in detail at :func:`.hive_representation.get_all_action_vector``
        :param action_number:  index of the action from the fixed size action space.
        :return: A tuple of (piece, end_cell), where piece is the piece on which the action
        is executed. end_cell is the target location of the action.
        """
        assert action_number >= 0
        atype, decoded = Hive._decode_action_number(action_number, self.level.current_player)
        if atype == 'init':
            # That's an initial movement
            if len(self.level.get_played_pieces()) >= 2:
                error_msg = "Invalid action number, it should not be an initial movement"
                logging.error(error_msg)
                raise HiveException(error_msg, 10006)
            # remove queen piece
            if self.level.get_tile_content(hexutil.origin):
                # It's symmetric, so just pick the first neighbor
                return decoded, hexutil.origin.neighbours()[0]
            else:
                return decoded, hexutil.origin
        elif atype == 'place':
            (piece, adj_piece, direction) = decoded
            # We have to search for the pieces in the stored state, because that's how
            # it will also contain the position of the piece
            adj_piece = self.level.find_piece_played(adj_piece)
            if adj_piece is None:
                error_msg = "Invalid action number, trying to place piece next to an unplayed piece"
                logging.error(error_msg)
                raise HiveException(error_msg, 10008)
            target_cell = self.level.goto_direction(adj_piece.position, direction)
            assert not piece.position
            return piece, target_cell
        elif atype == 'move':
            (piece, inner_action) = decoded
            stored_piece = self.level.find_piece_played(piece)
            if stored_piece is None:
                # It should be placed if we want to move it
                error_msg = "Invalid action number, trying to move a piece which is not yet placed"
                logging.error(error_msg)
                raise HiveException(error_msg, 10009)
            assert stored_piece.position
            return stored_piece, stored_piece.index_to_target_cell(self, inner_action)

        # Index overflow
        error_msg = "Invalid action"
        logging.error(error_msg)
        raise HiveException(error_msg, 10010)

    def _piece_from_piece_set(self, index:int, excep: HivePiece=None) -> HivePiece:
        """
        :param index: Index of bug from the piece set given by factory
        :param excep: Exception bug. It is omitted from the list.
        :return: hive peace according to the index number.
        """
        pieces = piece_fact.sorted_piece_list(self.level.current_player)
        if excep:
            pieces.remove(excep)
        return pieces[index]

    @staticmethod
    def _get_piece_names_on_board(adjacency):
        result = []
        for (piece_name, row) in adjacency.items():
            if all([cell == 0 for cell in row.values()]):
                continue  # not played, nothing to do here
            result.append(piece_name)
        return result

    _letter_to_piece = {
        "A": AntPiece,
        "B": BeetlePiece,
        "G": GrassHopperPiece,
        "Q": BeePiece,
        "S": SpiderPiece
    }

    @staticmethod
    def load_state_with_player(two_dim_repr, current_player) -> Hive:
        assert current_player == Player.WHITE or current_player == Player.BLACK
        # count number of pieces already on board
        # It is needed in order to guess turn number
        adjacency = represent.dict_representation(two_dim_repr)

        hive = Hive()

        to_be_placed = Hive._get_piece_names_on_board(adjacency)
        if len(to_be_placed) <= 0:
            return hive  # initial state

        # put down the first bug which should be placed
        first_bug_name = to_be_placed.pop()
        hive.level.move_or_append_to(piece_fact.name_to_piece(first_bug_name), hexutil.origin)

        # BFS on adjacency matrix
        nodes_to_visit = [first_bug_name]
        while nodes_to_visit:
            name = nodes_to_visit.pop()
            # list need to be reversed, since we want to remove from it
            for to_place_name in reversed(to_be_placed):
                if 9 > adjacency[to_place_name][name] > 0:
                    # Calculate position of new bug
                    pos = hive.poc2cell(name, adjacency[name][to_place_name])
                    # create the bug
                    my_new_piece = piece_fact.name_to_piece(to_place_name)
                    # Visit this bug next time
                    nodes_to_visit.append(to_place_name)
                    # remove from remaining pieces
                    to_be_placed.remove(to_place_name)
                    # Put down the piece
                    hive.level.move_or_append_to(my_new_piece, pos)

        assert to_be_placed == []  # found place for everyone
        hive.level.current_player = current_player
        return hive

    def __str__(self):
        return HiveView(self.level).__str__()
