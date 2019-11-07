import random
import logging

from hivegame.AI.player import Player
import hivegame.hive_representation as represent

class RandomPlayer(Player):
    def __init__(self, use_repr=None):
        self.use_repr = use_repr
        self._dg_last_action = None
        self._dg_hive = None

    def step(self, environment):
        self._dg_hive = environment.hive
        if not self.use_repr:
            logging.debug("\n{}".format(environment.hive))
            actions = environment.get_all_possible_actions()
            if not actions:
                logging.info("random player just passed")
                return "pass"
            choosen_one = random.choice(tuple(actions))
            self._dg_last_action = choosen_one
            return choosen_one

        action_vector = represent.get_all_action_vector(environment.hive)
        if not any(action_vector):
            logging.info("random player just passed")
            return "pass"
        indices = [i for i, v in enumerate(action_vector) if v > 0]
        action = random.choice(indices)
        self._dg_last_action = action
        return environment.hive.action_from_vector(action)

    def feedback(self, success) -> None:
        if not success:
            logging.error("RandomAI: Invalid action from " + str(self))
            if self.use_repr:
                logging.error("last action was: {}, which corresponds to: {}".format(self._dg_last_action, self._dg_hive.action_from_vector(self._dg_last_action)))
            else:
                logging.error("Last action was: {}".format(self._dg_last_action))
            logging.error("Game state: {}".format(self._dg_hive))
            raise RuntimeError