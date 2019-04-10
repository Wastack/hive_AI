from hivegame.board import HexBoard

from hivegame.pieces.ant_piece import AntPiece
from hivegame.pieces.beetle_piece import BeetlePiece
from hivegame.pieces.grasshopper_piece import GrassHopperPiece
from hivegame.pieces.spider_piece import SpiderPiece

from hivegame.hive_utils import Direction, HiveException, GameStatus

from hivegame.hive_validation import *

from collections import OrderedDict
import logging

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
        self.unplayedPieces[Player.WHITE] = self._piece_set(Player.WHITE)
        self.unplayedPieces[Player.BLACK] = self._piece_set(Player.BLACK)
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
        if not validate_turn(self, piece, 'move'):
            raise HiveException("Invalid Piece Placement")

        if not validate_move_piece(self, piece, target_cell):
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
        if not validate_turn(self, piece, 'place'):
            raise HiveException("Invalid Piece Placement")

        if not validate_place_piece(self, piece, to_cell):
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
        ref_cell = self.locate(ref_piece)
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
            if (self.is_cell_free(surroundings[(i+1) % 6])
                    != self.is_cell_free(surroundings[i-1])):
                available_moves.append(1)
            else:
                available_moves.append(0)
        return available_moves

    def set_turn(self, turn):
        assert turn >= 1
        self.turn = turn
        self.activePlayer = Player.WHITE if self.turn % 2 == 1 else Player.BLACK

    @staticmethod
    def _piece_set(color):
        """
        Return a full set of hive pieces
        """
        piece_set = OrderedDict()
        for i in range(3):
            ant = AntPiece(color, i+1)
            piece_set[str(ant)] = ant
            grasshopper = GrassHopperPiece(color, i+1)
            piece_set[str(grasshopper)] = grasshopper
        for i in range(2):
            spider = SpiderPiece(color, i+1)
            piece_set[str(spider)] = spider
            beetle = BeetlePiece(color, i+1)
            piece_set[str(beetle)] = beetle
        queen = BeePiece(color, 1)
        piece_set[str(queen)] = queen
        return piece_set

# Adjacency matrix of pieces
# - rows in order: (22 pieces at the moment, i may change when adding extensions)
#   ['wA1', 'wA2', 'wA3', 'wB1', 'wB2', 'wG1', 'wG2', 'wG3', 'wQ1', 'wS1', 'wS2',
#    'bA1', 'bA2', 'bA3', 'bB1', 'bB2', 'bG1', 'bG2', 'bG3', 'bQ1', 'bS1', 'bS2']
# - cells:
#   + 0: they are not adjacent
#   + 7: is lower, 8: is upper
#
#    2/ \3
#   1|   |4
#    6\ /5
#
#   + eg. in row of bA2 and column of bG1 there is a 3.
#     That means bG1 is north-east from bA2.

    def get_adjacency_state(self):
        """
        Returns a two dimensional dictionary, where both keys are the string representation of the pieces.
        One cell represents the adjacency of the two pieces. 0 means they are not adjacent.

        The first X rows represents the white pieces. The next X rows contain the black player's pieces.
        """
        pieces = self._piece_set("w")
        pieces.update(self._piece_set("b"))

        # Initially nobody has a neighbor
        result = {}
        for row in pieces:
            result[row] = {}
            for col in pieces:
                if col != row:
                    result[row][col] = 0

        for piece, relations in result.items():
            cell = self.locate(piece)

            # the piece is not set yet
            if not cell:
                continue

            # check if there are more pieces at the same cell (beetles)
            pieces_in_cell = self.piecesInCell[cell]
            if len(pieces_in_cell) > 1:
                position = pieces_in_cell.index(piece)
                for lower_piece in pieces_in_cell[:position]:
                    relations[lower_piece] = Direction.HX_LOW
                if position + 1 < len(pieces_in_cell):
                    for upper_piece in pieces_in_cell[position + 1:]:
                        relations[upper_piece] = Direction.HX_UP

            surrounding_cells = self.occupied_surroundings(cell)
            for neighbor_cell in surrounding_cells:
                # get piece on the top of the neighbor cell
                neighbor_piece = self.piecesInCell[neighbor_cell][-1]
                relations[str(neighbor_piece)] = self.board.get_line_dir(cell, neighbor_cell)
        return result

    def canonical_adjacency_state(self):
        """
        Representation of state with adjacency matrix. From the players point of view. Instead of having a white and
        a black player, there are my pieces and the opponent's pieces.

        Practically it means that we have to switch colors of each piece.
        """

        # sorted by their names. That means black piece are at front.
        matrix = self.get_adjacency_state()
        inverse_matrix = {}
        for (row_name, row) in matrix.items():
            inverse_row = {}
            for (col_name, cell) in row.items():
                inverse_row[self._toggle_color(col_name)] = cell
            inverse_matrix[self._toggle_color(row_name)] = inverse_row

        return inverse_matrix

    @staticmethod
    def list_representation(adjacency):
        directions = []  # current turn number is the first data
        for sorted_row in [v for (k, v) in sorted(adjacency.items(), key=lambda row: row[0])]:
            for sorted_dir in [v for (_k, v) in sorted(sorted_row.items(), key=lambda col: col[0])]:
                directions.append(sorted_dir)
        return directions

    @staticmethod
    def dict_representation(adjacency_list):
        """
        :param adjacency_list: List representation of the state
        :return: Dictionary representation of the state
        """
        print("[DEBUG] dict_representation: len(adjacency_list) == {}".format(len(adjacency_list)))
        # get list of bug names sorted by name alphabetically
        list_of_names = sorted(list(Hive._piece_set(Player.WHITE).keys()) + list(Hive._piece_set(Player.BLACK).keys()))
        print("[DEBUG] dict_representation: len(list_of_names) == {}".format(len(list_of_names)))

        adjacency_iter = iter(adjacency_list)
        # Create a dictionary
        result = {}
        for bug_name in list_of_names:
            column = {}
            result[bug_name] = column
            for inner_name in list_of_names:
                if inner_name == bug_name:
                    break  # adjacency with itself is not stored
                column[inner_name] = next(adjacency_iter)
        return result

    @staticmethod
    def string_representation(adjacency_list_repr):
        # We need to use comma as separator, because turn number can consist of more digits.
        return ",".join(str(x) for x in adjacency_list_repr)

    @staticmethod
    def _toggle_color(piece_name):
        assert(len(piece_name) == 3)
        s = list(piece_name)
        s[0] = Player.BLACK if s[0] == Player.WHITE else Player.WHITE
        return "".join(s)

    def get_all_action_vector(self):
        """
        :return: A one-hot encoded representation of possible actions.
        The size of the vector returned is fixed.
        """
        result = []
        direction_count = 6
        # Pieces not played yet:
        piece_set = self._piece_set(self.activePlayer)
        print("[DEBUG] piece set length: %d" % len(piece_set))
        possible_neighbor_count = len(piece_set) - 1  # it can't be adjacent to itself

        my_pieces = [piece for piece in self.playedPieces.values() if piece.color == self.activePlayer]
        # The first row is about placing the first piece. However, the player in the second turn can place his
        # bug to 6 different places, those states are identical, so the AI can be restricted to only one
        # direction.
        # Also, we do not need action for placing the queen, because that is forbidden in the first turn.
        if not my_pieces:
            result += [1] * (len(piece_set) - 1)
        else:
            result += [0] * (len(piece_set) - 1)

        # Placing pieces
        for piece_name in piece_set.keys():
            if piece_name in self.playedPieces.keys():
                result += [0] * (possible_neighbor_count * direction_count)
            else:
                for adj_piece_name in piece_set.keys():
                    # It cannot move next to itself
                    if adj_piece_name == piece_name:
                        continue
                    adj_piece = self.playedPieces.get(adj_piece_name, None)
                    if adj_piece is None:
                        # neighbor candidate not placed yet
                        result += [0] * direction_count
                        continue
                    # get all boundary free cells
                    surroundings = self.board.get_surrounding(adj_piece.position)
                    for sur in surroundings:
                        if not self.is_cell_free(sur):
                            result.append(0)
                        elif not all(self.is_cell_free(s) or self.piecesInCell.get(s)[-1].color ==
                                     self.activePlayer for s in self.board.get_surrounding(sur)):
                            result.append(0)
                        else:
                            result.append(1)
        print("[DEBUG] result length of placing only: %d" % (len(result)))
        # moving pieces
        for piece_name, piece_without_pos in piece_set.items():
            piece = self.playedPieces.get(piece_name, None)
            if piece is None:
                result += [0] * piece_without_pos.move_vector_size
                continue

            # It cannot move unless queen is already placed
            if self.activePlayer + 'Q1' not in self.playedPieces:
                result += [0] * piece.move_vector_size
                continue

            # It cannot move if that breaks the one_hive rule
            if not validate_one_hive(self, piece):
                result += [0] * piece.move_vector_size
                continue

            result += piece.available_moves_vector(self)

        print("[DEBUG]: Resulting move vector is: {}".format(result))
        expected_len = len(piece_set) - 1 + (possible_neighbor_count * direction_count) * len(piece_set) +\
            1*6 + 3*6 + 3*AntPiece.MAX_STEP_COUNT + 2*SpiderPiece.MAX_STEP_COUNT + 2*6
        print("[DEBUG] len of result: %d, and expected len is: %d" % (len(result), expected_len))
        assert len(result) == expected_len
        return result

    def action_from_vector(self, action_number):
        assert action_number >= 0
        pieces_list = list(self._piece_set(self.activePlayer).values())
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

        if len(self.playedPieces) < 3:
            raise HiveException
        adjacent_bug_bound = len(pieces_list) - 1
        one_bug_bound = adjacent_bug_bound * 6
        placement_bound = init_bound + one_bug_bound*len(pieces_list)
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
            stored_piece = self.unplayedPieces[self.activePlayer][str(piece)]
            target_cell = self.board.get_dir_cell(self.playedPieces[str(adj_piece)], direction)
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
        pieces = list(self._piece_set(self.activePlayer).values())
        return pieces[index]

    def get_all_possible_actions(self):
        result = set()

        # choose the current players played pieces
        my_pieces = [piece for piece in self.playedPieces.values() if piece.color == self.activePlayer]

        if not my_pieces:
            # no piece of that player has been played yet
            if not self.piecesInCell.get((0, 0)):
                return [(piece, (0, 0)) for piece in self.unplayedPieces[self.activePlayer].values() if
                        not isinstance(piece, BeePiece)]
            else:
                for sur in self.board.get_surrounding((0, 0)):
                    result.update([(piece, sur) for piece in self.unplayedPieces[self.activePlayer].values() if
                                   not isinstance(piece, BeePiece)])
                return result

        # pieces which can be put down from hand
        pieces_to_put_down = []
        # cells where the player can put an unplayed piece to
        available_cells = set()

        if self.activePlayer + 'Q1' in self.playedPieces:
            # Actions of pieces already on board
            for piece in my_pieces:
                if not validate_one_hive(self, piece):
                    continue
                end_cells = self._get_possible_end_cells(piece)
                result.update([(piece, end_cell) for end_cell in end_cells if end_cell != piece.position])

        logging.info("Hive: Unplayed pieces: {}".format(self.unplayedPieces[self.activePlayer]))
        if self.turn >= 7 and self.activePlayer + 'Q1' not in self.playedPieces:
            pieces_to_put_down.append(self.unplayedPieces[self.activePlayer][self.activePlayer + 'Q1'])
        else:
            pieces_to_put_down += self.unplayedPieces[self.activePlayer].values()

        # get all boundary free cells
        for piece in my_pieces:
            surroundings = self.board.get_surrounding(piece.position)
            available_cells.update([sur for sur in surroundings if self.is_cell_free(sur)])
        # Keep only those which have no opposite side neighbors
        cells_to_remove = set()
        for cell in available_cells:
            surroundings = self.board.get_surrounding(cell)
            if not all(self.is_cell_free(sur) or self.piecesInCell.get(sur)[-1].color == self.activePlayer
                       for sur in surroundings):
                cells_to_remove.add(cell)
        available_cells.difference_update(cells_to_remove)

        # You can place all of your pieces there
        for piece in pieces_to_put_down:
            result.update([(piece, end_cell) for end_cell in available_cells])
        return result

    def _get_possible_end_cells(self, piece):
        """
        Returns every possible end cells
         in a list which can be done
        with the piece given as parameter.
        """
        return piece.available_moves(self)

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

        # put down the first bug which is already played
        self._place_without_validation(self._name_to_piece(to_be_placed.pop()), (0, 0))

        can_have_new_neighbor = self.playedPieces.keys()
        can_have_next = []
        while len(to_be_placed) > 0:
            for piece_name, row in adjacency_matrix.items():
                if piece_name not in can_have_new_neighbor:
                    continue
                for to_place_name in to_be_placed:
                    if row[to_place_name] > 0:
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

    def load_state_with_player(self, canonical_list_repr, current_player):
        # count number of pieces already on board
        # It is needed in order to guess turn number
        adjacency = Hive.dict_representation(canonical_list_repr)
        played_count = len(Hive._get_piece_names_on_board(adjacency))
        print("[DEBUG]: load_state_with_player: played count: %d" % played_count)

        # turn number is at least that much
        turn = played_count + 1
        assert turn > 0

        # turn should be an even number
        if current_player == Player.BLACK:
            turn += turn % 2

        return self.load_state((adjacency, turn))
