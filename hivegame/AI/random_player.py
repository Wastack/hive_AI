import random
import logging

from hivegame.AI.player import Player
import hivegame.hive_representation as represent
from hivegame.view import HiveView

class RandomPlayer(Player):
    def __init__(self, use_repr=None):
        self.use_repr = use_repr

    def step(self, environment):
        if not self.use_repr:
            actions = environment.get_all_possible_actions()
            if not actions:
                logging.info("random player just passed")
                return "pass"
            return random.choice(tuple(actions))

        print(HiveView(environment.hive))
        action_vector = represent.get_all_action_vector(environment.hive)
        if not any(action_vector):
            return "pass"
        indices = [i for i, v in enumerate(action_vector) if v > 0]
        action = random.choice(indices)
        return environment.hive.action_from_vector(action)

    def feedback(self, success):
        if not success:
            logging.warning("RandomAI: Invalid action from " + str(self))