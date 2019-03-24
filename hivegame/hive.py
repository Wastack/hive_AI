from hivegame.board import HexBoard

from hivegame.pieces.ant_piece import AntPiece
from hivegame.pieces.bee_piece import BeePiece
from hivegame.pieces.beetle_piece import BeetlePiece
from hivegame.pieces.grasshopper_piece import GrassHopperPiece
from hivegame.pieces.spider_piece import SpiderPiece
from hivegame.pieces.piece import HivePiece

from pprint import pprint
import logging

class HiveException(Exception):
    """Base class for exceptions."""
    pass

class Hive(object):
    """
    The Hive Game.
    This class enforces the game rules and keeps the state of the game.
    """

    # Directions
    O = HexBoard.HX_O    # origin/on-top
    W = HexBoard.HX_W    # west
    NW = HexBoard.HX_NW  # north-west
    NE = HexBoard.HX_NE  # north-east
    E = HexBoard.HX_E    # east
    SE = HexBoard.HX_SE  # south-east
    SW = HexBoard.HX_SW  # south-west

    # End game status
    UNFINISHED = 0
    WHITE_WIN = 1
    BLACK_WIN = 2
    DRAW = 3


    def __init__(self):
        self.turn = 0
        self.activePlayer = 0
        self.players = ['w', 'b']
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
        self.unplayedPieces['w'] = self._piece_set('w')
        self.unplayedPieces['b'] = self._piece_set('b')
        self.turn = 1


    def action(self, actionType, action):
        """Perform the player action.
        return True or ExceptionType
        TODO: elaborate on the exceptions
        """
        if (actionType == 'play'):
            if (isinstance(action, tuple)):
                (actPieceName, refPieceName, direction) = action
            elif (isinstance(action, str)):
                (actPieceName, refPieceName, direction) = (action, None, None)
                
            player = self.get_active_player()

            if refPieceName is None and self.turn == 1:
                targetCell = (0, 0)
            else:
                targetCell = self.poc2cell(refPieceName, direction)

            piece = self.unplayedPieces[player].get(actPieceName, self.playedPieces.get(actPieceName, None))
            if piece is None:
                raise HiveException
            self.action_piece_to(piece, targetCell)

        elif (actionType == 'non_play' and action == 'pass'):
            self.turn += 1
            self.activePlayer ^= 1  # switch active player

        return True

    def get_unplayed_pieces(self, player):
        return self.unplayedPieces[player]


    def get_active_player(self):
        if self.turn <= 0:
            return None

        return self.players[self.activePlayer]

    def get_board_boundaries(self):
        """returns the coordinates of the board limits."""
        return self.board.get_boundaries()


    def get_pieces(self, cell):
        """return the names of pieces that are in the cell (x, y)."""
        return [str(piece) for piece in self.piecesInCell.get(cell, [])]


    def locate(self, pieceName):
        """
        Returns the cell where the piece is positioned.
        pieceName is a piece identifier (string)
        """
        res = None
        pp = self.playedPieces.get(pieceName)
        if pp is not None:
            res = pp.position
        return res
    
    def action_piece_to(self, piece, target_cell):
        """
        Performs an action with the given piece to the given target cell.
        If the place is already on board it meands a movement. Otherwise it
        means a piece placement.
        """
        if(piece.position is None or piece.position[0] is None):
            self._place_piece_to(piece, target_cell)
            del self.unplayedPieces[self.get_active_player()][str(piece)]
        else:
            self._move_piece_to(piece, target_cell)
        self.turn += 1
        self.activePlayer ^= 1  # switch active player

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
        startingCell = pp.position

        # remove the piece from its current location
        self.piecesInCell[startingCell].remove(piece)

        # places the piece at the target location
        self.board.resize(target_cell)
        pp.position = target_cell
        pic = self.piecesInCell.setdefault(target_cell, [])
        pic.append(piece)

        return target_cell

    def move_piece_without_action(self, piece, refPiece, refDirection):
        """
        Moves a piece on the playing board without performing an action.
        """

        targetCell = self.poc2cell(refPiece, refDirection)
        self._move_piece_to(piece, targetCell)

        
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

        # places the piece at the target location
        self.board.resize(to_cell)
        self.playedPieces[str(piece)] = piece
        piece.position = to_cell
        pic = self.piecesInCell.setdefault(to_cell, [])
        pic.append(piece)

        return to_cell

    def place_piece_without_action(self, piece, refPieceName=None, refDirection=None):
        """
        Place a piece on the playing board without performing an action.
        """

        # if it's the first piece we put it at cell (0, 0)
        if refPieceName is None and self.turn == 1:
            targetCell = (0, 0)
        else:
            targetCell = self.poc2cell(refPieceName, refDirection)
        return self._place_piece_to(piece, targetCell)


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
        whiteTurn = self.activePlayer == 0
        blackTurn = self.activePlayer == 1

        # Move actions are only allowed after the queen is on the board
        if action == 'move':
            if blackTurn and ('bQ1' not in self.playedPieces):
                return False
            if whiteTurn and ('wQ1' not in self.playedPieces):
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
        whiteTurn = self.activePlayer == 0
        blackTurn = self.activePlayer == 1
        if whiteTurn and piece.color != 'w':
            return False

        if blackTurn and piece.color != 'b':
            return False


        if not self._validate_queen_rules(piece, action):
            return False
        
        return True


    def _validate_move_piece(self, moving_piece, targetCell):
        # check if the piece has been placed
        pp = self.playedPieces.get(str(moving_piece))
        if pp is None:
            print("piece was not played yet")
            return False

        # check if the move it's to a different targetCell
        if moving_piece in self.piecesInCell.get(targetCell, []):
            print("moving to the same place")
            return False

        # check if moving this piece won't break the hive
        if not self._one_hive(moving_piece):
            print("break _one_hive rule")
            return False

        return moving_piece.validate_move(self, targetCell)

    def _validate_place_piece(self, piece, targetCell):
        """
        Verifies if a piece can be played from hand into a given targetCell.
        The piece must be placed touching at least one piece of the same color
        and can only be touching pieces of the same color.
        """

        # targetCell must be free
        if not self.is_cell_free(targetCell):
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

        playedColor = piece.color

        occupiedCells = self.occupied_surroundings(targetCell)
        visiblePieces = [
            self.piecesInCell[oCell][-1] for oCell in occupiedCells
        ]
        res = True
        for piece in visiblePieces:
            if self.playedPieces[str(piece)].color != playedColor:
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


    def poc2cell(self, refPiece, pointOfContact):
        """
        Translates a relative position (piece, point of contact) into
        a board cell (x, y).
        """
        refCell = self.locate(refPiece)
        return self.board.get_dir_cell(refCell, pointOfContact)


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


    def _piece_set(self, color):
        """
        Return a full set of hive pieces
        """
        pieceSet = {}
        for i in range(3):
            ant = AntPiece(color, i+1)
            pieceSet[str(ant)] = ant
            grasshopper = GrassHopperPiece(color, i+1)
            pieceSet[str(grasshopper)] = grasshopper
        for i in range(2):
            spider = SpiderPiece(color, i+1)
            pieceSet[str(spider)] = spider
            beetle = BeetlePiece(color, i+1)
            pieceSet[str(beetle)] = beetle
        queen = BeePiece(color, 1)
        pieceSet[str(queen)] = queen
        return pieceSet

    def _one_hive(self, piece):
        """
        Check if removing a piece doesn't break the one hive rule.
        Returns False if the hive is broken.
        """
        originalPos = self.locate(str(piece))
        # if the piece is not in the board then moving it won't break the hive
        if originalPos is None:
            return True
        # if there is another piece in the same cell then the one hive rule
        # won't be broken
        pic = self.piecesInCell[originalPos]
        if len(pic) > 1:
            return True

        # temporarily remove the piece
        del self.piecesInCell[originalPos]

        # Get all pieces that are in contact with the removed one and try to
        # reach all of them from one of them.
        occupied = self.occupied_surroundings(originalPos)
        visited = set()
        toExplore = set([occupied[0]])
        toReach = set(occupied[1:])
        res = False

        while len(toExplore) > 0:
            found = []
            for cell in toExplore:
                found += self.occupied_surroundings(cell)
                visited.add(cell)
            toExplore = set(found) - visited
            if toReach.issubset(visited):
                res = True
                break

        # restore the removed piece
        self.piecesInCell[originalPos] = pic
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
        """
        pieces = self._piece_set("w")
        pieces.update(self._piece_set("b"))

        # Initially nobody has a neighbor
        result = {}
        for row in pieces:
            result[row] = {}
            for col in pieces:
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
                    relations[lower_piece] = self.board.HX_LOW
                if position + 1 < len(pieces_in_cell):
                    for upper_piece in pieces_in_cell[position + 1:]:
                        relations[upper_piece] = self.board.HX_UP

            surrounding_cells = self.occupied_surroundings(cell)
            for neighbor_cell in surrounding_cells:
                # get piece on the top of the neighbor cell
                neighbor_piece = self.piecesInCell[neighbor_cell][-1]
                relations[neighbor_piece] = self.board.get_line_dir(cell, neighbor_cell)
        return result
    
    def get_all_possible_actions(self):
        result = set()
        # TODO order of actions can be important here

        # choose the current players played pieces
        turn = "w" if self.activePlayer == 0 else "b"
        my_pieces = [piece for piece in self.playedPieces.values() if piece.color == turn]

        if not my_pieces:
            # no piece of that player has been played yet
            if not self.piecesInCell.get((0,0)):
                return [(piece, (0, 0)) for piece in self.unplayedPieces[turn].values() if not isinstance(piece, BeePiece)]
            else:
                for sur in self.board.get_surrounding((0,0)):
                    result.update([(piece, sur) for piece in self.unplayedPieces[turn].values() if not isinstance(piece, BeePiece)]) 
                return result

        # pieces which can be put down from hand
        pieces_to_put_down = []
        # cells where the player van put an unplayed piece to
        available_cells = set()

        if turn + 'Q1' in self.playedPieces:
            # Actions of pieces already on board
            for piece in my_pieces:
                if not self._one_hive(piece):
                    continue
                end_cells = self._get_possible_end_cells(piece)
                result.update([(piece, end_cell) for end_cell in end_cells if end_cell != piece.position])

        logging.info("Unplayed pieces: {}".format(self.unplayedPieces[turn]))
        if self.turn >= 7 and turn + 'Q1' not in self.playedPieces:
            pieces_to_put_down.append(self.unplayedPieces[turn][turn + 'Q1'])
        else:
            pieces_to_put_down += self.unplayedPieces[turn].values()

        # get all boundary free cells
        for piece in my_pieces:
            surroundings = self.board.get_surrounding(piece.position)
            available_cells.update([sur for sur in surroundings if self.is_cell_free(sur)])
        # Keep only those which have no opposite side neighbors
        cells_to_remove = set()
        for cell in available_cells:
            surroundings = self.board.get_surrounding(cell)
            if not all(self.is_cell_free(sur) or self.piecesInCell.get(sur)[-1].color == turn for sur in surroundings):
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