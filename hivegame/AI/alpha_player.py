from hivegame.AI.player import Player
from hivegame.AI.utils.MCTS import MCTS

import numpy as np


class AlphaPlayer(Player):

    def __init__(self, environment, predictor, args):
        self.mcts = MCTS(environment, predictor, args)

    def step(self, environment):
        board = environment.getCanonicalForm()
        return np.argmax(self.mcts.getActionProb(board, temp=0))

    def feedback(self, succeeded):
        pass
