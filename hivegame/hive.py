from hivegame.board import HexBoard

from hivegame.pieces.ant_piece import AntPiece
from hivegame.pieces.beetle_piece import BeetlePiece
from hivegame.pieces.grasshopper_piece import GrassHopperPiece
from hivegame.pieces.spider_piece import SpiderPiece
from hivegame.pieces.bee_piece import BeePiece

from hivegame.hive_utils import Player, HiveException, GameStatus
from hivegame.view import HiveView

import hivegame.hive_validation as valid
import hivegame.hive_representation as represent
import hivegame.pieces.piece_factory as piece_fact
import sys

letter_to_piece = {
    "A": AntPiece,
    "B": BeetlePiece,
    "G": GrassHopperPiece,
    "Q": BeePiece,
    "S": SpiderPiece
}


class Hive(object):
    """
    The Hive Game.
    This class enforces the game rules and keeps the state of the game.
    """

    def __init__(self):
        self.turn = 0
        self.activePlayer = Player.WHITE
        self.players = [Player.WHITE, Player.BLACK]
        self.board = HexBoard()
        self.playedPieces = {}
        self.piecesInCell = {}
        self.unplayedPieces = {}

    def setup(self):
        """
        Prepare the game to be played
        """
        self.__init__()
        # Add pieces to the players hands
        self.unplayedPieces[Player.WHITE] = piece_fact.piece_set(Player.WHITE)
        self.unplayedPieces[Player.BLACK] = piece_fact.piece_set(Player.BLACK)
        self.turn = 1

    def action(self, action_type, action):
        """Perform the player action.
        return True or ExceptionType
        """
        if action_type == 'play':
            if isinstance(action, tuple):
                (current_piece_name, ref_piece_name, direction) = action
            elif isinstance(action, str):
                (current_piece_name, ref_piece_name, direction) = (action, None, None)
            else:
                raise HiveException("invalid action format", 10004)  # invalid format

            player = self.get_active_player()

            if ref_piece_name is None and self.turn == 1:
                target_cell = (0, 0)
            else:
                target_cell = self.poc2cell(ref_piece_name, direction)

            piece = self.unplayedPieces[player].get(current_piece_name, self.playedPieces.get(current_piece_name, None))
            if piece is None:
                raise HiveException("Invalid piece name", 10005)
            self.action_piece_to(piece, target_cell)

        elif action_type == 'non_play' and action == 'pass':
            self.turn += 1
            self.activePlayer = self._toggle_player(self.activePlayer)  # switch active player

        return True

    def get_unplayed_pieces(self, player):
        return self.unplayedPieces[player]

    def get_active_player(self):
        if self.turn <= 0:
            return None

        return self.activePlayer

    def get_board_boundaries(self):
        """returns the coordinates of the board limits."""
        return self.board.get_boundaries()

    def get_pieces(self, cell):
        """return the names of pieces that are in the cell (x, y)."""
        return [str(piece) for piece in self.piecesInCell.get(cell, [])]

    def locate(self, piece_name):
        """
        Returns the cell where the piece is positioned.
        piece_name is a piece identifier (string)
        """
        res = None
        pp = self.playedPieces.get(piece_name)
        if pp is not None:
            res = pp.position
        return res

    def played_piece_count(self):
        return len(self.playedPieces)

    @staticmethod
    def _toggle_player(player):
        return Player.BLACK if player == Player.WHITE else Player.WHITE

    def action_piece_to(self, piece, target_cell):
        """
        Performs an action with the given piece to the given target cell.
        If the place is already on board it means a movement. Otherwise it
        means a piece placement.
        """

        if piece.position is None or piece.position[0] is None:
            self._place_piece_to(piece, target_cell)
        else:
            self._move_piece_to(piece, target_cell)
        self.turn += 1
        self.activePlayer = self._toggle_player(self.activePlayer)

    def _move_piece_to(self, piece, target_cell):
        """
        Moves the given piece to the target cell.
        It does start a complete action, since it does
        not increment the turn value.
        """
        # is the move valid
        if not valid.validate_turn(self, piece, 'move'):
            raise HiveException("Invalid Piece Movement", 10002)

        if not valid.validate_move_piece(self, piece, target_cell):
            raise HiveException("Invalid Piece Movement", 10002)

        pp = self.playedPieces[str(piece)]
        starting_cell = pp.position

        # remove the piece from its current location
        self.piecesInCell[starting_cell].remove(piece)

        # places the piece at the target location
        self.board.resize(target_cell)
        pp.position = target_cell
        pic = self.piecesInCell.setdefault(target_cell, [])
        pic.append(piece)

        return target_cell

    def move_piece_without_action(self, piece, ref_piece, ref_direction):
        """
        Moves a piece on the playing board without performing an action. That
        means it does not affect turn number or current player
        """

        target_cell = self.poc2cell(ref_piece, ref_direction)
        self._move_piece_to(piece, target_cell)

    def _place_piece_to(self, piece, to_cell):
        """
        Places a piece to the given target cell.
        It does start a complete action, since it does
        not increment the turn value.
        """
        # is the placement valid
        if not valid.validate_turn(self, piece, 'place'):
            raise HiveException("Invalid Piece Placement", 10003)

        if not valid.validate_place_piece(self, piece, to_cell):
            raise HiveException("Invalid Piece Placement", 10003)

        return self._place_without_validation(piece, to_cell)

    def _place_without_validation(self, piece, to_cell):
        # places the piece at the target location
        self.board.resize(to_cell)
        self.playedPieces[str(piece)] = piece
        piece.position = to_cell
        pic = self.piecesInCell.setdefault(to_cell, [])
        pic.append(piece)
        del self.unplayedPieces[str(piece)[0]][str(piece)]

        return to_cell

    def place_piece_without_action(self, piece, ref_piece_name=None, ref_direction=None):
        """
        Place a piece on the playing board without performing an action.
        """

        # if it's the first piece we put it at cell (0, 0)
        if ref_piece_name is None and self.turn == 1:
            target_cell = (0, 0)
        else:
            target_cell = self.poc2cell(ref_piece_name, ref_direction)
        return self._place_piece_to(piece, target_cell)

    def check_victory(self):
        """
        Check if white wins or black wins or draw or not finished
        """
        white = False
        black = False
        res = GameStatus.UNFINISHED

        # if white queen is surrounded => black wins
        queen = self.playedPieces.get('wQ1')
        if(
            queen is not None and
            len(self.occupied_surroundings(queen.position)) == 6
        ):
            black = True
            res = GameStatus.BLACK_WIN

        # if black queen is surrounded => white wins
        queen = self.playedPieces.get('bQ1')
        if(
            queen is not None and
            len(self.occupied_surroundings(queen.position)) == 6
        ):
            white = True
            res = GameStatus.WHITE_WIN

        # if both queens are surrounded
        if white and black:
            res = GameStatus.DRAW

        return res

    def is_cell_free(self, cell):
        pic = self.piecesInCell.get(cell, [])
        return len(pic) == 0

    def occupied_surroundings(self, cell):
        """
        Returns a list of surrounding cells that contain a piece.
        """
        surroundings = self.board.get_surrounding(cell)
        return [c for c in surroundings if not self.is_cell_free(c)]

    def poc2cell(self, ref_piece, point_of_contract):
        """
        Translates a relative position (piece, point of contact) into
        a board cell (x, y).
        """
        assert point_of_contract < 9
        ref_cell = self.locate(ref_piece)
        if point_of_contract > 6:
            return ref_cell  # above or below
        return self.board.get_dir_cell(ref_cell, point_of_contract)

    def bee_moves(self, cell):
        """
        Get possible bee_moves from cell.

        A bee can move to an adjacent target position only if:
        - target position is free
        - and there is a piece adjacent to both the bee and that position
        - and there is a free cell that is adjacent to both the bee and the
          target position.
        """
        available_moves = []
        surroundings = self.board.get_surrounding(cell)
        for i in range(6):
            target = surroundings[i]
            # is the target cell free?
            if not self.is_cell_free(target):
                continue
            # does it have an adjacent free and an adjancent occupied cell that
            # is also adjacent to the starting cell?
            if (
                self.is_cell_free(surroundings[(i+1) % 6])
                != self.is_cell_free(surroundings[i-1])
            ):
                available_moves.append(target)
        return available_moves

    def bee_moves_vector(self, cell):
        # TODO ensure one hive rule
        available_moves = []
        # Clockwise, starting from west
        surroundings = self.board.get_surrounding(cell)
        for i in range(6):
            target = surroundings[i]
            if not self.is_cell_free(target):
                available_moves.append(0)
                continue
            if (self.is_cell_free(surroundings[(i+1) % 6])
                    != self.is_cell_free(surroundings[i-1])):
                available_moves.append(1)
            else:
                available_moves.append(0)
        assert len(available_moves) == 6
        return available_moves

    def set_turn(self, turn):
        assert turn >= 1
        self.turn = turn
        self.activePlayer = Player.WHITE if self.turn % 2 == 1 else Player.BLACK

    def action_from_vector(self, action_number):
        """
        Maps an action number to an actual action. The fixed size action space is explained
        in detail at :func:`.hive_representation.get_all_action_vector``
        :param action_number:  index of the action from the fixed size action space.
        :return: A tuple of (piece, end_cell), where piece is the piece on which the action
        is executed. end_cell is the target location of the action.
        """
        assert action_number >= 0
        pieces_list = list(piece_fact.piece_set(self.activePlayer).values())
        piece_set_count = len(pieces_list)
        init_bound = piece_set_count - 1
        if action_number < init_bound:
            # That's an initial movement
            if len(self.playedPieces) >= 2:
                print("[ERROR]: action vector was: {}".format(represent.get_all_action_vector(self)), file=sys.stderr)
                raise HiveException("Invalid action number, it should not be an initial movement", 10006)
            if not self.piecesInCell.get((0, 0)):
                return pieces_list[action_number], (0, 0)
            else:
                return pieces_list[action_number], (1, 0)

        if len(self.playedPieces) < 2:
            raise HiveException("Invalid action number, it ought to be an initial movement", 10007)
        adjacent_bug_bound = len(pieces_list) - 1
        one_bug_bound = adjacent_bug_bound * 6
        placement_bound = init_bound + one_bug_bound * len(pieces_list)
        if action_number < placement_bound:
            # It is a bug placement
            inner_action_number = action_number - init_bound
            action_type = inner_action_number % one_bug_bound
            piece_number = inner_action_number // one_bug_bound
            adj_piece_number = action_type // 6
            direction = (action_type % 6) + 1  # starting from west, clockwise
            piece = self._piece_from_piece_set(piece_number)
            adj_piece = self._piece_from_piece_set(adj_piece_number, piece)
            # We have to search for the pieces in the stored state, because that way
            # it will also contain the position of the piece
            adj_piece_stored = self.playedPieces.get(str(adj_piece))
            if adj_piece_stored is None:
                raise HiveException("Invalid action number, trying to place piece next to an unplayed piece", 10008)
            stored_piece = self.unplayedPieces[self.activePlayer][str(piece)]
            target_cell = self.board.get_dir_cell(adj_piece_stored.position, direction)
            return stored_piece, target_cell

        # This is a bug movement
        inner_action_number = action_number - placement_bound
        for piece in pieces_list:
            assert inner_action_number >= 0
            if inner_action_number - piece.move_vector_size >= 0:
                inner_action_number -= piece.move_vector_size
                continue
            stored_piece = self.playedPieces.get(str(piece))
            if stored_piece is None:
                # It should be placed if we want to move it
                raise HiveException("Invalid action number, trying to move a piece which is not yet placed", 10009)
            return stored_piece, stored_piece.index_to_target_cell(self, inner_action_number)

        # Index overflow
        raise HiveException("Invalid action number, out of bounds", 10010)

    def _piece_from_piece_set(self, index, excep=None):
        """
        :param index: Index of bug from the piece set given by factory
        :param excep: Exception bug. It is omitted from the list.
        :return:
        """
        pieces = list(piece_fact.piece_set(self.activePlayer).values())
        for p in pieces:
            if str(excep) == str(p):
                pieces.remove(p)
                break
        return pieces[index]

    @staticmethod
    def _get_piece_names_on_board(adjacency):
        result = []
        for (piece_name, row) in adjacency.items():
            if all([cell == 0 for cell in row.values()]):
                continue  # not played, nothing to do here
            result.append(piece_name)
        return result

    @staticmethod
    def _name_to_piece(name):
        letters = list(name)
        assert (len(letters) == 3)  # color, type, number
        return letter_to_piece[letters[1]](letters[0], letters[2])

    def load_state_with_player(self, two_dim_repr, current_player):
        assert current_player == Player.WHITE or current_player == Player.BLACK
        # count number of pieces already on board
        # It is needed in order to guess turn number
        adjacency = represent.dict_representation(two_dim_repr)
        self.__init__()
        self.setup()
        to_be_placed = Hive._get_piece_names_on_board(adjacency)

        if len(to_be_placed) <= 0:
            return True  # initial state

        # put down the first bug which should be placed
        self._place_without_validation(self._name_to_piece(to_be_placed.pop()), (0, 0))

        # BFS on adjacency matrix
        nodes_to_visit = list(self.playedPieces.keys())
        while nodes_to_visit != []:
            name = nodes_to_visit.pop()
            # list need to be reversed, since we want to remove from it
            for to_place_name in reversed(to_be_placed):
                if 9 > adjacency[to_place_name][name] > 0:
                    pos = self.poc2cell(name, adjacency[name][to_place_name])
                    my_new_piece = self._name_to_piece(to_place_name)
                    nodes_to_visit.append(to_place_name)
                    to_be_placed.remove(to_place_name)
                    my_new_piece.position = pos
                    self._place_without_validation(my_new_piece, pos)

        assert to_be_placed == []  # found place for everyone

        self.activePlayer = current_player
        # Setting current player and guessing turn count
        # set current player
        if self.playedPieces.get("wQ1") is not None \
                and self.playedPieces.get("bQ1") is not None:
            self.turn = 9  # not relevant
        elif self.playedPieces.get("wQ1") is None and self.playedPieces.get("bQ1") is None:
            self.turn = len(self.playedPieces) + 1  # bee queen forbidden in turn 1, 2. Moving forbidden
        else:
            # imprecise, but who cares? There is no way to determine it exactly
            self.turn = 9

        return True

    def __str__(self):
        return HiveView(self).__str__()
