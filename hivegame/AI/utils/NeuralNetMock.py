from .NeuralNet import NeuralNet

from hivegame.environment import Environment
from hivegame.arena import Arena
from hivegame.AI.random_player import RandomPlayer
from hivegame.hive import Hive

class NeuralNetMock(NeuralNet):
    """
    This class replaces the neural network with random decisions. Used for testing.
    """

    def __init__(self, game):
        super(NeuralNetMock, self).__init__(game)
        self.game = game

    def train(self, examples):
        pass

    def predict(self, canonicalListBoard):
        """
        Performs a simulation with Random AI.
        :param canonicalBoard: Canonical list representation of board
        :return: 1 if win, -1 is lose, 0 else.
        """
        env = Environment()
        env.hive.load_state_with_player(canonicalListBoard, 1)
        arena = Arena(RandomPlayer(), RandomPlayer(), env)
        result = arena.playGame()
        if result == Hive.WHITE_WIN:
            v = 1
        elif result == Hive.BLACK_WIN:
            v = -1
        else:
            v = 0
        return [], v

    def save_checkpoint(self, folder, filename):
        pass

    def load_checkpoint(self, folder, filename):
        pass
