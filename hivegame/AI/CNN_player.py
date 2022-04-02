
import numpy as np

from AI.player import Player
from engine.hive import Hive
from AI.utils.MCTS import MCTS

from engine.hive_utils import Player as player_colour
from engine import hive_representation
from engine.environment.aienvironment import ai_environment

class CNN_Player(Player):

    def __init__(self, model, args):
        self.mcts = MCTS(model, args)

    def step(self, hive: 'Hive'):

        if hive.current_player == player_colour.BLACK:
            flipped_hive = Hive()

            # getting coords and piece types in the hive
            for hex, pieces in hive.level.tiles.items():

                #replacing pieces with opposite colour
                for piece in pieces:
                    if piece.color == player_colour.BLACK:
                        flipped_hive.level.tiles[hex] = [piece._replace(color=player_colour.WHITE) for piece in pieces]
                    else:
                        flipped_hive.level.tiles[hex] = [piece._replace(color=player_colour.BLACK) for piece in pieces]

            flipped_hive.level.current_player = player_colour.WHITE
            board = hive_representation.two_dim_representation(hive_representation.get_adjacency_state(flipped_hive))

            pis, v = self.mcts.model.predict(board)
            valid_moves = ai_environment.get_valid_moves(board, 1)
            pis = pis * np.array(valid_moves)  # masking invalid moves
            action_number = np.argmax(pis)
            (piece, end_cell) = flipped_hive.action_from_vector(action_number)
            piece = piece._replace(color=player_colour.BLACK)

        # current player is white
        else:
            board = hive_representation.two_dim_representation(hive_representation.get_adjacency_state(hive))
            # board = environment.getCanonicalForm(board, player_num)
            pis, v = self.mcts.model.predict(board)
            valids = ai_environment.get_valid_moves(board, 1)
            pis = pis * np.array(valids)  # mask invalid moves
            action_number = np.argmax(pis)
            (piece, end_cell) = hive.action_from_vector(action_number)

        return (piece, end_cell)
        

    def feedback(self, succeeded) -> None:
        pass
