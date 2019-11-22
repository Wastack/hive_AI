from engine.hive import Hive
from hivegame.AI.player import Player
from hivegame.AI.utils.MCTS import MCTS
from engine import hive_representation as represent

import numpy as np
from engine.hive_utils import Player as PlayerColor
from hivegame.engine.environment.aienvironment import ai_environment


class AlphaPlayer(Player):

    def __init__(self, predictor, args):
        self.mcts = MCTS(predictor, args)

    def step(self, hive: 'Hive'):
        #logging.debug("alpha player steps")
        #logging.debug("\n{}".format(environment.hive))
        if hive.current_player == PlayerColor.BLACK:
            flipped_hive = Hive()
            for hex, p_list in hive.level.tiles.items():
                flipped_hive.level.tiles[hex] = [p._replace(color=PlayerColor.WHITE if p.color == PlayerColor.BLACK else PlayerColor.BLACK) for p in p_list]
            flipped_hive.level.current_player = PlayerColor.WHITE
            board = represent.two_dim_representation(represent.get_adjacency_state(flipped_hive))

            pis = self.mcts.getActionProb(board)
            valids = ai_environment.getValidMoves(board, 1)
            pis = pis * np.array(valids)  # mask invalid moves
            #pis = self.mcts.getActionProb(board, temp=0)
            action_number = np.argmax(pis)
            #logging.debug("Flipped hive:\n{}".format(flipped_hive))
            (piece, end_cell) = flipped_hive.action_from_vector(action_number)
            #logging.debug("Flipped decision: ({}, {})".format(piece, end_cell))
            piece = piece._replace(color=PlayerColor.BLACK)
        else:
            board = represent.two_dim_representation(represent.get_adjacency_state(hive))
            # board = environment.getCanonicalForm(board, player_num)
            pis = self.mcts.getActionProb(board)
            valids = ai_environment.getValidMoves(board, 1)
            pis = pis * np.array(valids)  # mask invalid moves
            # pis = self.mcts.getActionProb(board, temp=0)
            action_number = np.argmax(pis)
            (piece, end_cell) = hive.action_from_vector(action_number)
            #logging.debug("Decision: ({}, {})".format(piece, end_cell))

        return (piece, end_cell)

    def feedback(self, succeeded) -> None:
        pass