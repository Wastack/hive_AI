import logging

from engine.hive import Hive
from AI.hardcoded_AI import MiniMaxAI
from AI.player import Player

class MiniMaxPlayer(Player):
    def __init__(self, player_colour):
        self.player_colour = player_colour

    def step(self, hive: 'Hive'):
        minimax = MiniMaxAI(hive, self.player_colour, 5)
        return minimax.get_best_move()


    def feedback(self, success) -> None:
        if not success:
            logging.error("Invalid action from MiniMax AI")
            raise RuntimeError