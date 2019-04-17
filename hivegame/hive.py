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
                raise HiveException  # invalid format

            player = self.get_active_player()

            if ref_piece_name is None and self.turn == 1:
                target_cell = (0, 0)
            else:
                target_cell = self.poc2cell(ref_piece_name, direction)

            piece = self.unplayedPieces[player].get(current_piece_name, self.playedPieces.get(current_piece_name, None))
            if piece is None:
                raise HiveException
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
            raise HiveException("Invalid Piece Placement")

        if not valid.validate_move_piece(self, piece, target_cell):
            raise HiveException("Invalid Piece Movement")

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
            raise HiveException("Invalid Piece Placement")

        if not valid.validate_place_piece(self, piece, to_cell):
            raise HiveException("Invalid Piece Placement")

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
        if action_number <= init_bound:
            # That's an initial movement
            if len(self.playedPieces) > 2:
                raise HiveException
            if not self.piecesInCell.get((0, 0)):
                return pieces_list[action_number], (0, 0)
            else:
                return pieces_list[action_number], (1, 0)

        if len(self.playedPieces) < 2:
            raise HiveException
        adjacent_bug_bound = len(pieces_list) - 1
        one_bug_bound = adjacent_bug_bound * 6
        placement_bound = init_bound + one_bug_bound * len(pieces_list)
        if action_number <= placement_bound:
            # It is a bug placement
            inner_action_number = action_number - init_bound
            action_type = inner_action_number % one_bug_bound
            piece_number = inner_action_number // one_bug_bound
            adj_piece_number = action_type // adjacent_bug_bound
            direction = action_type % 6
            piece = self._piece_from_piece_set(piece_number)
            adj_piece = self._piece_from_piece_set(adj_piece_number)
            # We have to search for the pieces in the stored state, because that way
            # it will also contain the position of the piece
            adj_piece_stored = self.playedPieces.get(str(adj_piece))
            if adj_piece_stored is None:
                print("[WARN]: {} is not yet placed.".format(adj_piece))
                print(HiveView(self))
                raise HiveException  # trying to place piece next to an unplayed piece
            stored_piece = self.unplayedPieces[self.activePlayer][str(piece)]
            target_cell = self.board.get_dir_cell(adj_piece_stored, direction)
            return stored_piece, target_cell

        # This is a bug movement
        inner_action_number = action_number - placement_bound
        for piece in pieces_list:
            if inner_action_number < 0:
                raise HiveException
            if inner_action_number - piece.move_vector_size > 0:
                inner_action_number -= piece.move_vector_size
                continue
            stored_piece = self.playedPieces.get(str(piece))
            if stored_piece is None:
                # It should be placed if we want to move it
                raise HiveException
            return stored_piece, stored_piece.target_cell(inner_action_number)

        # Index overflow
        raise HiveException

    def _piece_from_piece_set(self, index):
        pieces = list(piece_fact.piece_set(self.activePlayer).values())
        return pieces[index]

    def load_state(self, state):
        """
        :param state: A tuple consists of an adjacency matrix of the pieces, and a turn number
        :return: True if it succeeded. Raises HiveException else.
        """
        (adjacency_matrix, turn) = state
        self.__init__()
        self.setup()
        to_be_placed = Hive._get_piece_names_on_board(adjacency_matrix)

        if len(to_be_placed) <= 0:
            return True  # initial state

        # put down the first bug which should be placed
        self._place_without_validation(self._name_to_piece(to_be_placed.pop()), (0, 0))

        can_have_new_neighbor = self.playedPieces.keys()
        can_have_next = []
        while len(to_be_placed) > 0:
            for piece_name, row in adjacency_matrix.items():
                if piece_name not in can_have_new_neighbor:
                    continue
                assert any( i !=  0 or i != 9 for i in row)
                for to_place_name in to_be_placed:
                    if 9 > row[to_place_name] > 0:
                        pos = self.poc2cell(piece_name, row[to_place_name])
                        can_have_next.append(to_place_name)
                        to_be_placed.remove(to_place_name)
                        my_new_piece = self._name_to_piece(to_place_name)
                        my_new_piece.position = pos
                        self._place_without_validation(my_new_piece, pos)
            can_have_new_neighbor = can_have_next

        # set current player
        self.set_turn(turn)
        return True

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
        # count number of pieces already on board
        # It is needed in order to guess turn number
        adjacency = represent.dict_representation(two_dim_repr)
        played_count = len(Hive._get_piece_names_on_board(adjacency))

        # turn number is at least that much
        turn = played_count + 1
        assert turn > 0

        # turn should be an even number
        if current_player == Player.BLACK:
            turn += turn % 2

        return self.load_state((adjacency, turn))
