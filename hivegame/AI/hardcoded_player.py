import logging

from engine.hive import Hive
from AI.hardcoded_AI import MiniMaxAI
from AI.player import Player

class MiniMaxPlayer(Player):
    def __init__(self, depth, args):
        self.minimax = MiniMaxAI(depth, args)

    def step(self, hive: 'Hive'):
        return self.minimax.get_best_move(hive)


    def feedback(self, success) -> None:
        if not success:
            logging.error("Invalid action from MiniMax AI")
            raise RuntimeError