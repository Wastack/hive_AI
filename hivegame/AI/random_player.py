import random
import logging

from engine.hive import Hive
from engine.environment.aienvironment import ai_environment
from AI.player import Player
import engine.hive_representation as represent

class RandomPlayer(Player):

    def step(self, hive: 'Hive'):
        self._dg_hive = hive
        actions = represent.get_all_possible_actions(hive)
        if not actions:
            logging.info("random player just passed")
            return "pass"
        choosen_one = random.choice(tuple(actions))
        self._dg_last_action = choosen_one
        return choosen_one

        # TODO move this into test
        #action_vector = represent.get_all_action_vector(environment.hive)
        #if not any(action_vector):
        #    logging.info("random player just passed")
        #    return "pass"
        #indices = [i for i, v in enumerate(action_vector) if v > 0]
        #action = random.choice(indices)
        #self._dg_last_action = action
        #return environment.hive.action_from_vector(action)

    def feedback(self, success) -> None:
        if not success:
            logging.error("Invalid action from random player")
            raise RuntimeError