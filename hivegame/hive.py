from hivegame.board import HexBoard

from hivegame.pieces.ant_piece import AntPiece
from hivegame.pieces.bee_piece import BeePiece
from hivegame.pieces.beetle_piece import BeetlePiece
from hivegame.pieces.grasshopper_piece import GrassHopperPiece
from hivegame.pieces.spider_piece import SpiderPiece
from hivegame.utils import Direction

import logging

letter_to_piece = {
    "A": AntPiece,
    "B": BeetlePiece,
    "G": GrassHopperPiece,
    "Q": BeePiece,
    "S": SpiderPiece
}

class HiveException(Exception):
    """Base class for exceptions."""
    pass


class Hive(object):
    """
    The Hive Game.
    This class enforces the game rules and keeps the state of the game.
    """

    # players
    WHITE = 'w'
    BLACK = 'b'

    # End game status
    UNFINISHED = 0
    WHITE_WIN = 1
    BLACK_WIN = 2
    DRAW = 3

    def __init__(self):
        self.turn = 0
        self.activePlayer = self.WHITE
        self.players = [self.WHITE, self.BLACK]
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
        self.unplayedPieces[self.WHITE] = self._piece_set(self.WHITE)
        self.unplayedPieces[self.BLACK] = self._piece_set(self.BLACK)
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
        return Hive.BLACK if player == Hive.WHITE else Hive.WHITE
    
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
        if not self._validate_turn(piece, 'move'):
            raise HiveException("Invalid Piece Placement")

        if not self._validate_move_piece(piece, target_cell):
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
        Moves a piece on the playing board without performing an action.
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
        if not self._validate_turn(piece, 'place'):
            raise HiveException("Invalid Piece Placement")

        if not self._validate_place_piece(piece, to_cell):
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
        res = self.UNFINISHED

        # if white queen is surrounded => black wins
        queen = self.playedPieces.get('wQ1')
        if(
            queen is not None and
            len(self.occupied_surroundings(queen.position)) == 6
        ):
            black = True
            res = self.BLACK_WIN

        # if black queen is surrounded => white wins
        queen = self.playedPieces.get('bQ1')
        if(
            queen is not None and
            len(self.occupied_surroundings(queen.position)) == 6
        ):
            white = True
            res = self.WHITE_WIN

        # if both queens are surrounded
        if white and black:
            res = self.DRAW

        return res

    def _validate_queen_rules(self, piece, action):
        """
        Validate rules related to the queen.
        """
        # Tournament rule: no queen in the first move
        if (self.turn == 1 or self.turn == 2) and isinstance(piece, BeePiece):
            return False
        white_turn = self.activePlayer == self.WHITE
        black_turn = not white_turn

        # Move actions are only allowed after the queen is on the board
        if action == 'move':
            if black_turn and ('bQ1' not in self.playedPieces):
                return False
            if white_turn and ('wQ1' not in self.playedPieces):
                return False

        # White Queen must be placed by turn 7 (4th white action)
        if self.turn == 7:
            if 'wQ1' not in self.playedPieces:
                if str(piece) != 'wQ1' or action != 'place':
                    return False

        # Black Queen must be placed by turn 8 (4th black action)
        if self.turn == 8:
            if 'bQ1' not in self.playedPieces:
                if str(piece) != 'bQ1' or action != 'place':
                    return False
        return True

    def _validate_turn(self, piece, action):
        """
        Verifies if the action is valid on this turn.
        """
        white_turn = self.activePlayer == self.WHITE
        black_turn = not white_turn
        if white_turn and piece.color != self.WHITE:
            return False

        if black_turn and piece.color != self.BLACK:
            return False

        if not self._validate_queen_rules(piece, action):
            return False
        
        return True

    def _validate_move_piece(self, moving_piece, target_cell):
        # check if the piece has been placed
        pp = self.playedPieces.get(str(moving_piece))
        if pp is None:
            print("piece was not played yet")
            return False

        # check if the move it's to a different target_cell
        if moving_piece in self.piecesInCell.get(target_cell, []):
            print("moving to the same place")
            return False

        # check if moving this piece won't break the hive
        if not self._one_hive(moving_piece):
            print("break _one_hive rule")
            return False

        return moving_piece.validate_move(self, target_cell)

    def _validate_place_piece(self, piece, target_cell):
        """
        Verifies if a piece can be played from hand into a given target_cell.
        The piece must be placed touching at least one piece of the same color
        and can only be touching pieces of the same color.
        """

        # target_cell must be free
        if not self.is_cell_free(target_cell):
            return False

        # the piece was already played
        if str(piece) in self.playedPieces:
            return False

        # if it's the first turn we don't need to validate
        if self.turn == 1:
            return True

        # if it's the second turn we put it without validating touching colors
        if self.turn == 2:
            return True

        played_color = piece.color

        occupied_cells = self.occupied_surroundings(target_cell)
        visible_pieces = [
            self.piecesInCell[oCell][-1] for oCell in occupied_cells
        ]
        res = True
        for piece in visible_pieces:
            if self.playedPieces[str(piece)].color != played_color:
                res = False
                break

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
            target = surroundings[i-1]
            # is the target cell free?
            if not self.is_cell_free(target):
                continue
            # does it have an adjacent free and an adjancent occupied cell that
            # is also adjacent to the starting cell?
            if (
                self.is_cell_free(surroundings[i])
                != self.is_cell_free(surroundings[i-2])
            ):
                available_moves.append(target)
        return available_moves

    def set_turn(self, turn):
        assert turn >= 1
        self.turn = turn
        self.activePlayer = Hive.WHITE if self.turn % 2 == 1 else Hive.BLACK

    @staticmethod
    def _piece_set(color):
        """
        Return a full set of hive pieces
        """
        piece_set = {}
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

    def _one_hive(self, piece):
        """
        Check if removing a piece doesn't break the one hive rule.
        Returns False if the hive is broken.
        """
        origional_pos = self.locate(str(piece))
        # if the piece is not in the board then moving it won't break the hive
        if origional_pos is None:
            return True
        # if there is another piece in the same cell then the one hive rule
        # won't be broken
        pic = self.piecesInCell[origional_pos]
        if len(pic) > 1:
            return True

        # temporarily remove the piece
        del self.piecesInCell[origional_pos]

        # Get all pieces that are in contact with the removed one and try to
        # reach all of them from one of them.
        occupied = self.occupied_surroundings(origional_pos)
        visited = set()
        to_explore = {occupied[0]}
        to_reach = set(occupied[1:])
        res = False

        while len(to_explore) > 0:
            found = []
            for cell in to_explore:
                found += self.occupied_surroundings(cell)
                visited.add(cell)
            to_explore = set(found) - visited
            if to_reach.issubset(visited):
                res = True
                break

        # restore the removed piece
        self.piecesInCell[origional_pos] = pic
        return res

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
    def string_representation(state):
        (adjacency_matrix, turn) = state
        directions = [turn]  # current turn number is the first data
        for sorted_row in [v for (k, v) in sorted(adjacency_matrix.items(), key=lambda row: row[0]) ]:
            for sorted_dir in [v for (_k, v) in sorted(sorted_row.items(), key=lambda col: col[0]) ]:
                directions.append(sorted_dir)
        # We need to use comma as separator, because turn number can consist of more digits.
        return ",".join(str(x) for x in directions)

    @staticmethod
    def _toggle_color(piece_name):
        assert(len(piece_name) == 3)
        s = list(piece_name)
        s[0] = Hive.BLACK if s[0] == Hive.WHITE else Hive.WHITE
        return "".join(s)

    def get_all_possible_actions(self):
        result = set()
        # TODO order of actions can be important here

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
        # cells where the player van put an unplayed piece to
        available_cells = set()

        if self.activePlayer + 'Q1' in self.playedPieces:
            # Actions of pieces already on board
            for piece in my_pieces:
                if not self._one_hive(piece):
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
        to_be_placed = Hive._getPieceNamesOnBoard(adjacency_matrix)

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
                        # TODO put that piece down
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
    def _getPieceNamesOnBoard(adjacency):
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

    def load_state_with_player(self, adjacency, current_player):
        # count number of pieces already on board
        # It is needed in order to guess turn number
        played_count = len(Hive._getPieceNamesOnBoard(adjacency))

        # turn number is at least that much
        turn = played_count + 1

        # turn should be an even number
        if current_player == self.BLACK:
            turn += turn % 2

        return self.load_state((adjacency, turn))

