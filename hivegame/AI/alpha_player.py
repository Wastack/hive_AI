from copy import copy

from hivegame.AI.environment import Environment
from hivegame.hive import Hive
from hivegame.AI.player import Player
from hivegame.AI.utils.MCTS import MCTS
from hivegame import hive_representation as represent

import numpy as np
import logging
from hivegame.hive_utils import Player as PlayerColor, HiveException
from hivegame.pieces import piece_factory

class AlphaPlayer(Player):

    def __init__(self, environment, predictor, args):
        self.mcts = MCTS(environment, predictor, args)
        self.predictor = predictor

    def step(self, environment):
        logging.debug("alpha player steps")
        logging.debug("\n{}".format(environment.hive))
        if environment.current_player == PlayerColor.BLACK:
            flipped_hive = Hive()
            for hex, p_list in environment.hive.level.tiles.items():
                flipped_hive.level.tiles[hex] = [p._replace(color=PlayerColor.WHITE if p.color == PlayerColor.BLACK else PlayerColor.BLACK) for p in p_list]
            flipped_hive.level.current_player = PlayerColor.WHITE
            board = represent.two_dim_representation(represent.get_adjacency_state(flipped_hive))

            pis, _ = self.predictor.predict(board)
            valids = environment.getValidMoves(board, 1)
            pis = pis * valids  # mask invalid moves
            #pis = self.mcts.getActionProb(board, temp=0)
            action_number = np.argmax(pis)
            logging.debug("Flipped hive:\n{}".format(flipped_hive))
            (piece, end_cell) = flipped_hive.action_from_vector(action_number)
            logging.debug("Flipped decision: ({}, {})".format(piece, end_cell))
            piece = piece._replace(color=PlayerColor.BLACK)
        else:
            board = represent.two_dim_representation(represent.get_adjacency_state(environment.hive))
            # board = environment.getCanonicalForm(board, player_num)
            pis, _ = self.predictor.predict(board)
            valids = environment.getValidMoves(board, 1)
            pis = pis * valids  # mask invalid moves
            # pis = self.mcts.getActionProb(board, temp=0)
            action_number = np.argmax(pis)
            (piece, end_cell) = environment.hive.action_from_vector(action_number)
            logging.debug("Decision: ({}, {})".format(piece, end_cell))

        return (piece, end_cell)

    def feedback(self, succeeded) -> None:
        pass