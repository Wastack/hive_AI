from hivegame.hive_utils import Direction, Player, get_queen_name
import hivegame.hive_validation as valid
import hivegame.pieces.piece_factory as piece_fact
from hivegame.pieces.ant_piece import AntPiece
from hivegame.pieces.spider_piece import SpiderPiece

from hivegame.utils.game_state import GameState

from typing import Dict, List, Set, Tuple
import numpy as np

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from hivegame.hive import Hive


# Adjacency matrix of pieces
# - rows in order: (22 pieces at the moment, i may change when adding extensions)
#   ['wA1', 'wA2', 'wA3', 'wB1', 'wB2', 'wG1', 'wG2', 'wG3', 'wQ1', 'wS1', 'wS2',
#    'bA1', 'bA2', 'bA3', 'bB1', 'bB2', 'bG1', 'bG2', 'bG3', 'bQ1', 'bS1', 'bS2']
# - cells:
#   + 0: it is not set
#   + 7: is lower, 8: is upper
#   + 9: the piece is set, but no neighbours that way
#
#    2/ \3
#   1|   |4
#    6\ /5
#
#   + eg. in row of bA2 and column of bG1 there is a 3.
#     That means bG1 is north-east from bA2.
from pieces.piece import HivePiece
from utils import hexutil


def get_adjacency_state(hive: 'Hive') -> Dict[str, Dict[str, int]]:
    """
    Returns a two dimensional dictionary, where both keys are the string representation of the pieces.
    One cell represents the adjacency of the two pieces. 0 means they are not adjacent.

    The first X rows represents the white pieces. The next X rows contain the black player's pieces.
    """
    pieces = piece_fact.sorted_piece_dict(Player.WHITE)
    pieces.update(piece_fact.sorted_piece_dict(Player.BLACK))

    # Initially nobody is placed
    result: Dict[str, Dict[str, int]] = {}
    for row in pieces:
        result[row] = {}
        for col in pieces:
            if col != row:
                result[row][col] = 0

    for piece, relations in result.items():
        cell = hive.locate(piece)

        # the piece is not set yet
        if not cell:
            continue

        # It is placed, so let's put it to 9
        for k in relations.keys():
            relations[k] = 9

        # check if there are more pieces at the same cell (beetles)
        pieces_in_cell = hive.level.get_tile_content(cell)
        if len(pieces_in_cell) > 1:
            # get index in list
            position = pieces_in_cell.index(piece)
            # set relations to the lower pieces
            for lower_piece in pieces_in_cell[:position]:
                relations[lower_piece] = Direction.HX_LOW
            # set relations to the higher pieces (if any)
            if position + 1 < len(pieces_in_cell):
                for upper_piece in pieces_in_cell[position + 1:]:
                    relations[upper_piece] = Direction.HX_UP

        surrounding_cells = hive.level.occupied_surroundings(cell)
        for neighbor_cell in surrounding_cells:
            # set relation to the neighbour(s - if beetle)
            for p in hive.level.get_tile_content(neighbor_cell):
                direction = GameState.get_direction_to(cell, neighbor_cell)
                assert direction
                relations[str(p)] = direction

    return result


def canonical_adjacency_state(hive: 'Hive') -> Dict[str, Dict[str, int]]:
    """
    Representation of state with adjacency matrix. From the players point of view. Instead of having a white and
    a black player, there are my pieces and the opponent's pieces.

    Practically it means that we have to switch colors of each piece.
    """
    # sorted by their names. That means black piece are at front.
    matrix = get_adjacency_state(hive)
    inverse_matrix = {}
    for (row_name, row) in matrix.items():
        inverse_row = {}
        for (col_name, cell) in row.items():
            inverse_row[_toggle_color(col_name)] = cell
        inverse_matrix[_toggle_color(row_name)] = inverse_row

    return inverse_matrix


def list_representation(adjacency: Dict[str, Dict[str, int]]) -> List[int]:
    directions = []  # current turn number is the first data
    for sorted_row in [v for (k, v) in sorted(adjacency.items(), key=lambda row: row[0])]:
        for sorted_dir in [v for (_k, v) in sorted(sorted_row.items(), key=lambda col: col[0])]:
            directions.append(sorted_dir)
    return directions


def two_dim_representation(adjacency) -> np.ndarray:
    directions = []  # current turn number is the first data
    for sorted_row in [v for (k, v) in sorted(adjacency.items(), key=lambda row: row[0])]:
        row = []
        for sorted_dir in [v for (_k, v) in sorted(sorted_row.items(), key=lambda col: col[0])]:
            row.append(sorted_dir)
        directions.append(row)
    return np.array(directions)


def dict_representation(two_dim_list: np.ndarray) -> Dict[str, Dict[str, int]]:
    """
    :param adjacency_list: List representation of the state
    :return: Dictionary representation of the state
    """
    # get list of bug names sorted by name alphabetically
    list_of_names = sorted(list(piece_fact.sorted_piece_dict(Player.WHITE).keys()) + list(
        piece_fact.sorted_piece_dict(Player.BLACK).keys()))

    # Create a dictionary
    result = {}
    for bug_name, relations in zip(list_of_names, two_dim_list):
        adj_row_iter = iter(relations)
        column = {}
        result[bug_name] = column
        for inner_name in list_of_names:
            if inner_name == bug_name:
                continue  # adjacency with itself is not stored
            column[inner_name] = next(adj_row_iter)
    return result


def string_representation(two_dim_repr: np.ndarray):
    """
    :param two_dim_repr: representation of hive
    :return:  Hashable string representation of the current state
    """
    # We need to use comma as separator, because turn number can consist of more digits.
    return ",".join(str(x) for x in (y for y in two_dim_repr))


def _toggle_color(piece_name):
    assert (len(piece_name) == 3)
    s = list(piece_name)
    s[0] = Player.BLACK if s[0] == Player.WHITE else Player.WHITE
    return "".join(s)


def get_all_action_vector(hive: 'Hive') -> List[int]:
    """
    The format of the fix-size action space is the following:
    vector = [init_place | place | move ]

    The vector consists of (0|1) values:

    - length of **init_place** is equal to the number of pieces used by
      one player excluding the bee piece. The order of the actions in *init_place*
      depends from the piece factory. These action are only available in the first
      turn of each player.
    - **place** contains all the possible movements after each player made a
      move at least once. It consists of movements next to each piece which could
      possibly be already placed on board. For each of those bugs, there is a field
      for each direction. A bug can be placed to any of the 6 sides of another bug.

    :return: A one-hot encoded representation of possible actions.
             The size of the vector returned is fixed.
    """
    result = []
    direction_count = 6

    # Pieces not yet played:
    piece_list = piece_fact.sorted_piece_list(hive.current_player)
    piece_count = len(piece_list)
    possible_neighbor_count = piece_count - 1  # it can't be adjacent to itself
    my_pieces = hive.level.get_played_pieces(hive.current_player)

    # The first row is about placing the first piece. However, the player in the second turn can place his
    # bug to 6 different places, those states are identical, so the AI can be restricted to only one
    # direction.
    # Also, we do not need action for placing the queen, because that is forbidden in the first turn.
    if not my_pieces:
        result += [1] * (len(piece_list) - 1)
    else:
        result += [0] * (len(piece_list) - 1)

    # Placing pieces
    for p in piece_list:
        # Cannot place piece if:
        #   - it is already placed or
        #   - If the queen is not yet played in the fourth turn
        if p in my_pieces or (len(my_pieces) == 3 and
                              not hive.get_piece_by_name(get_queen_name(hive.current_player)).position and
                              p.kind != "Q"):
            result += [0] * (possible_neighbor_count * direction_count)
        else:
            for adj_piece in piece_list:
                # It cannot be put next to itself
                if adj_piece == p:
                    continue
                # find position on board
                adj_piece = hive.level.find_piece_played(adj_piece)
                if adj_piece is None:
                    # neighbor candidate not placed yet
                    result += [0] * direction_count
                    continue
                # get all boundary free cells
                surroundings = adj_piece.position.neighbours()
                for sur in surroundings:
                    if hive.level.get_tile_content(sur):
                        result.append(0)  # it is already occupied
                    # cannot place if it is adjacent with the opponent
                    elif   any(hive.level.get_tile_content(nb_of_nb)[-1].color !=
                                 hive.level.current_player for nb_of_nb in hive.level.occupied_surroundings(sur)):
                        result.append(0)
                    else:
                        result.append(1)  # it can be placed
    assert len(result) == piece_count - 1 + piece_count * (possible_neighbor_count * direction_count)

    # moving pieces
    for p in piece_list:
        # find piece on board
        p = hive.level.find_piece_played(p)

        # It cannot move if:
        #  - not yet placed
        #  - queen not yet placed
        #  - If picking up the piece would break the one-hive rule
        if not p or not hive.get_piece_by_name(get_queen_name(hive.current_player)).position or\
                not valid.validate_one_hive(hive, p):
            result += [0] * p.move_vector_size
            continue

        result += p.available_moves_vector(hive)

    expected_len = len(piece_list) - 1 + (possible_neighbor_count * direction_count) * len(piece_list) + \
                   1 * 6 + 3 * 6 + 3 * AntPiece.MAX_STEP_COUNT + 2 * SpiderPiece.MAX_STEP_COUNT + 2 * 6
    assert len(result) == expected_len
    return result


def get_all_possible_actions_nonidentical(hive: 'Hive') -> (HivePiece, hexutil.Hex):
    """
    :param hive: The representation of the game.
    :return: All possible actions except the second turn. In the second player's first turn all the directions are
             identical from the AI's point of view
    """
    if len(hive.level.get_played_pieces()) == 1:
        pieces = [p for p in hive.level.get_unplayed_pieces(hive.current_player) if p.kind != "Q"]
        return [(p, hexutil.origin.neighbours()[0]) for p in pieces]
    return get_all_possible_actions(hive)


def get_all_possible_actions(hive: 'Hive') -> Set[Tuple[HivePiece, hexutil.Hex]]:
    """
    Query for all the possible movements in a given state. The list of actions
    is unordered, i.e the order is not specified.

    :param hive: State of the game.
    :return: A set of action = (piece, end_cell) tuples, where piece
             is the bug on which the action would be performed. end_cell is
             the target location of the action.
    """
    result = set()
    print(hive)

    # choose the current players played pieces
    my_pieces = hive.level.get_played_pieces(hive.current_player)

    if not my_pieces:
        # no piece of that player has been played yet
        if not hive.level.get_tile_content(hexutil.origin):
            return {(p, hexutil.origin) for p in hive.level.get_unplayed_pieces(hive.current_player)
                    if not p.kind == 'Q'}
        else:
            for sur in hexutil.origin.neighbours():
                result.update({(p, sur) for p in hive.level.get_unplayed_pieces(hive.current_player)
                               if not p.kind == 'Q'})
            return result

    # Collect action from moving pieces
    # It can only happen if queen is set
    if hive.get_piece_by_name(get_queen_name(hive.current_player)).position:
        # Actions of pieces already on board
        for piece in my_pieces:
            if not valid.validate_one_hive(hive, piece):
                continue
            end_cells = piece.available_moves(hive)
            result.update([(piece, end_cell) for end_cell in end_cells if end_cell != piece.position])

    # pieces which can be put down from hand
    pieces_to_put_down = set()
    # cells where the player can put an unplayed piece to
    available_cells = set()

    queen_piece = hive.get_piece_by_name(get_queen_name(hive.current_player))
    if len(my_pieces) == 3 and not queen_piece.position:
        pieces_to_put_down.add(queen_piece)
    else:
        pieces_to_put_down.update(hive.level.get_unplayed_pieces(hive.current_player))

    # get all boundary free cells
    for p in my_pieces:
        nbs = p.position.neighbours()
        available_cells.update({sur for sur in nbs if not hive.level.get_tile_content(sur)})
    # Keep only those which have no opposite side neighbors
    cells_to_remove = set()
    for cell in available_cells:
        nbs = hive.level.occupied_surroundings(cell)
        if any(hive.level.get_tile_content(sur)[-1].color != hive.current_player for sur in nbs):
            cells_to_remove.add(cell)
    available_cells.difference_update(cells_to_remove)

    # You can place all of your remaining pieces there
    for piece in pieces_to_put_down:
        result.update([(piece, end_cell) for end_cell in available_cells])
    return result