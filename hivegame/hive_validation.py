from hivegame.hive_utils import Player
from hivegame.pieces.bee_piece import BeePiece

def validate_queen_rules(hive, piece, action):
    """
    Validate rules related to the queen.
    """
    # Tournament rule: no queen in the first move
    if (hive.turn == 1 or hive.turn == 2) and isinstance(piece, BeePiece):
        return False
    white_turn = hive.activePlayer == Player.WHITE
    black_turn = not white_turn

    # Move actions are only allowed after the queen is on the board
    if action == 'move':
        if black_turn and ('bQ1' not in hive.playedPieces):
            return False
        if white_turn and ('wQ1' not in hive.playedPieces):
            return False

    # White Queen must be placed by turn 7 (4th white action)
    if hive.turn == 7:
        if 'wQ1' not in hive.playedPieces:
            if str(piece) != 'wQ1' or action != 'place':
                return False

    # Black Queen must be placed by turn 8 (4th black action)
    if hive.turn == 8:
        if 'bQ1' not in hive.playedPieces:
            if str(piece) != 'bQ1' or action != 'place':
                return False
    return True


def validate_turn(hive, piece, action):
    """
    Verifies if the action is valid on this turn.
    """
    white_turn = hive.activePlayer == Player.WHITE
    black_turn = not white_turn
    if white_turn and piece.color != Player.WHITE:
        return False

    if black_turn and piece.color != Player.BLACK:
        return False

    if not validate_queen_rules(hive, piece, action):
        return False

    return True


def validate_move_piece(hive, moving_piece, target_cell):
    # check if the piece has been placed
    pp = hive.playedPieces.get(str(moving_piece))
    if pp is None:
        print("piece was not played yet")
        return False

    # check if the move it's to a different target_cell
    if moving_piece in hive.piecesInCell.get(target_cell, []):
        print("moving to the same place")
        return False

    # check if moving this piece won't break the hive
    if not validate_one_hive(hive, moving_piece):
        print("break one_hive rule")
        return False

    return moving_piece.validate_move(hive, target_cell)


def validate_place_piece(hive, piece, target_cell):
    """
    Verifies if a piece can be played from hand into a given target_cell.
    The piece must be placed touching at least one piece of the same color
    and can only be touching pieces of the same color.
    """

    # target_cell must be free
    if not hive.is_cell_free(target_cell):
        return False

    # the piece was already played
    if str(piece) in hive.playedPieces:
        return False

    # if it's the first turn we don't need to validate
    if hive.turn == 1:
        return True

    # if it's the second turn we put it without validating touching colors
    if hive.turn == 2:
        return True

    played_color = piece.color

    occupied_cells = hive.occupied_surroundings(target_cell)
    visible_pieces = [
        hive.piecesInCell[oCell][-1] for oCell in occupied_cells
    ]
    res = True
    for piece in visible_pieces:
        if hive.playedPieces[str(piece)].color != played_color:
            res = False
            break

    return res


def validate_one_hive(hive, piece):
    """
    Check if removing a piece doesn't break the one hive rule.
    Returns False if the hive is broken.
    """
    original_pos = hive.locate(str(piece))
    # if the piece is not in the board then moving it won't break the hive
    if original_pos is None:
        return True
    # if there is another piece in the same cell then the one hive rule
    # won't be broken
    pic = hive.piecesInCell[original_pos]
    if len(pic) > 1:
        return True

    # temporarily remove the piece
    del hive.piecesInCell[original_pos]

    # Get all pieces that are in contact with the removed one and try to
    # reach all of them from one of them.
    occupied = hive.occupied_surroundings(original_pos)
    visited = set()
    to_explore = {occupied[0]}
    to_reach = set(occupied[1:])
    res = False

    while len(to_explore) > 0:
        found = []
        for cell in to_explore:
            found += hive.occupied_surroundings(cell)
            visited.add(cell)
        to_explore = set(found) - visited
        if to_reach.issubset(visited):
            res = True
            break

    # restore the removed piece
    hive.piecesInCell[original_pos] = pic
    return res